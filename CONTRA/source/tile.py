import pygame as pg
from settings import *


class Tile(pg.sprite.Sprite):
    '''Class to manage tiles.'''

    def __init__(self, place: tuple[int, int], surface: pg.Surface, groups: tuple[pg.sprite.Group], ordinal: int):
        super().__init__(groups)
        # LAYER ORDINAL.
        self.ORDINAL = ordinal
        # CORE.
        self.image = surface
        self.rect = self.image.get_rect(topleft=place)


class CollisionTile(Tile):
    '''Class to manage collision tiles.'''

    def __init__(self, place: tuple[int, int], surface: pg.Surface, groups: tuple[pg.sprite.Group]):
        super().__init__(place, surface, groups, LAYERS['Level'])
        # COLLISION.
        self.old_rect = self.rect.copy()


class MovingPlatform(CollisionTile):
    '''Class to manage platform objects.'''

    def __init__(self, place: tuple[int, int], surface: pg.Surface, groups: tuple[pg.sprite.Group]):
        super().__init__(place, surface, groups)
        # MOVEMENT.
        self.direction, self.speed = pg.math.Vector2(0, -1), 200
        self.pos = pg.math.Vector2(self.rect.topleft)

    def update(self, delta_time: float):
        '''Update movement.'''
        # STORE THE PREVIOUS RECT.
        self.old_rect = self.rect.copy()
        # UPDATE.
        self.pos.y += self.direction.y * self.speed * delta_time
        self.rect.y = round(self.pos.y)
