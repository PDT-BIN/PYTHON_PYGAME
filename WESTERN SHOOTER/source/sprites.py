import pygame as pg
from pygame import Surface
from pygame.mask import from_surface
from pygame.math import Vector2
from pygame.sprite import Group


class Obstacle(pg.sprite.Sprite):
    '''A class manage obstacle sprites.'''

    def __init__(self, position: tuple, surface: Surface, groups: Group):
        '''Initialize core attributes.'''
        super().__init__(groups)
        # Core.
        self.image = surface
        self.rect = self.image.get_rect(topleft=position)
        # Collision.
        self.hitbox = self.rect.inflate(0, -self.rect.height / 3)


class Bullet(pg.sprite.Sprite):
    '''A class manage bullet sprites.'''

    def __init__(self, position: tuple, direction: Vector2, surface: Surface, groups: Group):
        '''Initialize core attributes.'''
        super().__init__(groups)
        # Core.
        self.image = surface
        self.rect = self.image.get_rect(center=position)
        self.mask = from_surface(self.image)
        # Movement.
        self.pos = Vector2(self.rect.center)
        self.direction, self.speed = direction, 400

    def update(self, delta_time: float):
        self.pos += self.direction * self.speed * delta_time
        self.rect.center = (round(self.pos.x), round(self.pos.y))
