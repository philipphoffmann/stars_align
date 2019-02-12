import logging
import re
from typing import NamedTuple

from PIL import Image
import pytesseract

logging.basicConfig(format="%(asctime)-15s %(message)s")
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class Point(NamedTuple):
    x: int
    y: int

    def __add__(self, other) -> 'Point':
        return Point(self.x + other.x, self.y + other.y)


class Star(NamedTuple):
    pos: Point
    vel: Point

    @classmethod
    def from_string(cls, string: str) -> 'Star':
        match = re.search("position=<\s*(-?\d+),\s*(-?\d+)> velocity=<\s*(-?\d+),\s*(-?\d+)>", string)
        return Star(Point(int(match.group(1)), int(match.group(2))), Point(int(match.group(3)), int(match.group(4))))


def parse_input(file: str) -> [Star]:
    with open(file) as f:
        return [Star.from_string(line) for line in f]


def move_stars(stars: [Star]) -> [Star]:
    return [Star(star.pos + star.vel, star.vel) for star in stars]


stars = parse_input("input.txt")
additional_img_border = 3  # we need some border around the text, otherwise tesseract will not recognize the text
seconds_passed = 0

while True:
    seconds_passed += 1
    stars = move_stars(stars)

    min_x = min(star.pos.x for star in stars)
    min_y = min(star.pos.y for star in stars)
    max_x = max(star.pos.x for star in stars)
    max_y = max(star.pos.y for star in stars)

    image_width = (max_x - min_x) + (2 * additional_img_border)
    image_height = (max_y - min_y) + (2 * additional_img_border)

    # we will skip large images because they are expensive to render
    if image_width < 500:
        logger.debug("Rendering frame (%s, %s) ...", image_width, image_height)
        frame = Image.new("1", (image_width, image_height), color=255)
        for star in stars:
            frame.putpixel((star.pos.x - min_x + additional_img_border, star.pos.y - min_y + additional_img_border), 0)
        frame.save("frame.png")
        logger.debug("... done")

        msg = pytesseract.image_to_string(Image.open('frame.png'))

        if msg:
            logger.info("After %s seconds message says: %s", seconds_passed, msg)
            break
        else:
            logger.debug("No message found")
