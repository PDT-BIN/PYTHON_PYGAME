from os.path import join
from random import choice

from pygame.image import load
from settings import *


class Preview:
    def __init__(self):
        # MAIN SCREEN.
        self.screen = pg.display.get_surface()
        # PREVIEW DISPLAY.
        size = SIDEBAR_WIDTH, GAME_HEIGHT * PREVIEW_HEIGHT_FRACTION
        offset = WINDOW_WIDTH - PADDING, PADDING
        self.display = pg.Surface(size)
        self.place = self.display.get_rect(topright=offset)
        # GRAPHIC.
        self.PREVIEW_IMAGES = {key: load(
            join('image', f'{key}.png')).convert_alpha() for key in TETROMINOS}
        # SHAPE.
        self.FRAGMENT_POSITIONS = self.display.get_width() / 2, self.display.get_height() / 3
        self.preview_shapes = [choice(list(TETROMINOS)) for _ in range(3)]

    def draw(self, position: tuple[int, int], shape: str) -> None:
        surface = self.PREVIEW_IMAGES[shape]
        place = surface.get_rect(center=position)
        self.display.blit(surface, place)

    def run(self) -> None:
        self.display.fill(GRAY)
        for index, shape in enumerate(self.preview_shapes):
            x = self.FRAGMENT_POSITIONS[0]
            y = self.FRAGMENT_POSITIONS[1] / 2 + \
                index * self.FRAGMENT_POSITIONS[1]
            self.draw((x, y), shape)
        self.screen.blit(self.display, self.place)
        pg.draw.rect(self.screen, LINE_COLOR, self.place, 2, 2)
