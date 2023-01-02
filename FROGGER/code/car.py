from os import walk
from random import choice

import pygame as pg


class Car(pg.sprite.Sprite):

    def __init__(self, pos: tuple, groups: pg.sprite.Group):
        super().__init__(groups)
        self.name = 'car'
        # Core attributes.
        for _, _, files in walk('image/cars'):
            path = f'image/cars/{choice(files)}'
            self.image = pg.image.load(path).convert_alpha()
        self.rect = self.image.get_rect(center=pos)
        # Movement.
        self.pos = pg.math.Vector2(self.rect.center)
        match self.pos.x:
            case -100:
                self.direction = pg.math.Vector2(+1, 0)
            case _:
                self.direction = pg.math.Vector2(-1, 0)
                self.image = pg.transform.flip(self.image, True, False)
        self.speed = 300
        self.hitbox = self.rect.inflate(0, -self.rect.height / 2)

    def update(self, dt: float):
        self.pos += self.direction * self.speed * dt
        self.hitbox.center = (round(self.pos.x), round(self.pos.y))
        self.rect.center = self.hitbox.center
        if not -200 < self.rect.x < 3400:
            self.kill()
