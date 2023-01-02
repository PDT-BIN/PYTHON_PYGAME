import pygame as pg


class SimpleSprite(pg.sprite.Sprite):

    def __init__(self, surf: pg.Surface, pos: tuple, groups: pg.sprite.Group):
        super().__init__(groups)
        # Core attributes.
        self.image = surf
        self.rect = self.image.get_rect(topleft=pos)
        self.hitbox = self.rect.inflate(0, -self.rect.height / 2)


class LongSprite(pg.sprite.Sprite):

    def __init__(self, surf: pg.Surface, pos: tuple, groups: pg.sprite.Group):
        super().__init__(groups)
        # Core attributes.
        self.image = surf
        self.rect = self.image.get_rect(topleft=pos)
        self.hitbox = self.rect.inflate(-self.rect.width * 0.8, -self.rect.height / 2)
        self.hitbox.bottom = self.rect.bottom - 10
