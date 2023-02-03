import pygame as pg
from settings import *


class Tile(pg.sprite.Sprite):

    def __init__(self, place: tuple[int, int], groups: tuple[pg.sprite.Group], form: str,
                 image=pg.Surface((TILESIZE, TILESIZE))):
        super().__init__(groups)
        y_offset = HITBOX_OFFSET[form]
        # CORE.
        self.form = form
        self.image = image
        if form == 'Object':
            offset_place = (place[0], place[1] - TILESIZE)
            self.rect = self.image.get_rect(topleft=offset_place)
        else:
            self.rect = self.image.get_rect(topleft=place)
        self.hitbox = self.rect.inflate(0, y_offset)
