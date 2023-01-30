import pygame as pg


class Tile(pg.sprite.Sprite):

    def __init__(self, place, groups):
        super().__init__(groups)
        # CORE.
        self.image = pg.image.load('image/rock.png').convert_alpha()
        self.rect = self.image.get_rect(topleft=place)
        # COLLIDING RECT.
        self.hitbox = self.rect.inflate(0, -10)
