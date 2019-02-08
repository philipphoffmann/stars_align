import logging
import re

from PIL import Image
import pytesseract

logging.basicConfig(format="%(asctime)-15s %(message)s")
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class Star:
    def __init__(self, pos_x: int, pos_y: int, velocity_x: int, velocity_y: int):
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.velocity_x = velocity_x
        self.velocity_y = velocity_y

    def __repr__(self):
        return "<" + str(self.pos_x) + ", " + str(self.pos_y) + "><" + str(self.velocity_x) + ", " + str(
            self.velocity_y) + ">"


def parse_input(file: str) -> [Star]:
    stars = []
    with open(file) as f:
        for line in f:
            line = line.replace("\n", "")
            logger.debug("read: %s", line)
            match = re.search("position=<\s*(-?\d+),\s*(-?\d+)> velocity=<\s*(-?\d+),\s*(-?\d+)>", line)
            if match:
                stars.append(Star(
                    int(match.group(1)),
                    int(match.group(2)),
                    int(match.group(3)),
                    int(match.group(4))
                ))
            else:
                logger.warning("Unable to parse line: '%s'", line)

    return stars


def move_stars(stars: [Star]) -> [Star]:
    return [Star(star.pos_x + star.velocity_x, star.pos_y + star.velocity_y, star.velocity_x, star.velocity_y) for star in stars]


stars = parse_input("input.txt")
additional_img_border = 3 # we need some border around the text, otherwise tesseract will not recognize the text
seconds_passed = 0

while True:
    seconds_passed += 1
    stars = move_stars(stars)

    min_x = min([star.pos_x for star in stars])
    min_y = min([star.pos_y for star in stars])
    max_x = max([star.pos_x for star in stars])
    max_y = max([star.pos_y for star in stars])

    image_width = (max_x - min_x) + (2 * additional_img_border)
    image_height = (max_y - min_y) + (2 * additional_img_border)

    # we will skip large images because they are expensive to render
    if image_width < 500:
        logger.debug("Rendering frame (%s, %s) ...", image_width, image_height)
        frame = Image.new("1", (image_width, image_height), color=255)
        for star in stars:
            frame.putpixel((star.pos_x - min_x + additional_img_border, star.pos_y - min_y + additional_img_border), 0)
        frame.save("frame.png")
        logger.debug("... done")

        msg = pytesseract.image_to_string(Image.open('frame.png'))

        if msg:
            logger.info("After %s seconds message says: %s", seconds_passed, msg)
            break
        else:
            logger.debug("No message found")
