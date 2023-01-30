import pygame as pg
from support import load_image_folder


class Tile(pg.sprite.Sprite):

    def __init__(self, size: int, place: tuple[int, int]):
        super().__init__()
        # CORE.
        self.image = pg.Surface((size, size))
        self.rect = self.image.get_rect(topleft=place)

    def update(self, x_shift):
        self.rect.x += x_shift


class StaticTile(Tile):

    def __init__(self, size: int, place: tuple[int, int], surface: pg.Surface):
        super().__init__(size, place)
        # CORE.
        self.image = surface


class Crate(StaticTile):

    def __init__(self, size: int, place: tuple[int, int]):
        super().__init__(size, place, pg.image.load(
            'image/terrain/crate.png').convert_alpha())
        # OFFSET.
        offset_y = place[1] + size
        # OVERRIDE RECT.
        self.rect = self.image.get_rect(bottomleft=(place[0], offset_y))


class AnimatingTile(Tile):

    def __init__(self, size: int, place: tuple[int, int], path: str):
        super().__init__(size, place)
        # ANIMATIONS.
        self.animations = load_image_folder(path)
        self.frame_index, self.SPEED = 0, 0.15
        # OVERRIDE IMAGE.
        self.image = self.animations[self.frame_index]

    def animate(self):
        self.frame_index += self.SPEED
        if self.frame_index >= len(self.animations):
            self.frame_index = 0
        self.image = self.animations[int(self.frame_index)]

    def update(self, x_shift):
        super().update(x_shift)
        self.animate()


class Coin(AnimatingTile):

    def __init__(self, size: int, place: tuple[int, int], path: str, value: int):
        super().__init__(size, place, path)
        # CORE.
        self.value = value
        # OFFSET.
        offset = (place[0] + size / 2, place[1] + size / 2)
        # OVERRIDE RECT.
        self.rect = self.image.get_rect(center=offset)


class Palm(AnimatingTile):

    def __init__(self, size: int, place: tuple[int, int], path: str, offset: int):
        super().__init__(size, place, path)
        # OFFSET.
        offset_y = place[1] - offset
        # OVERRIDE RECT.
        self.rect.topleft = (place[0], offset_y)
