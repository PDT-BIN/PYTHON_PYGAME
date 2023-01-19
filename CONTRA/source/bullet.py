import pygame as pg
from settings import *


class Bullet(pg.sprite.Sprite):
    '''Class to manage bullet objects.'''

    def __init__(self, place: tuple[int, int], surface: pg.Surface, direction: pg.math.Vector2,
                 groups: tuple[pg.sprite.Group]):
        super().__init__(groups)
        # LAYER ORDINAL.
        self.ORDINAL = LAYERS['Level']
        # CORE.
        self.image = pg.transform.flip(surface, direction.x < 0, False)
        self.rect = self.image.get_rect(center=place)
        self.mask = pg.mask.from_surface(self.image)
        # MOVEMENT.
        self.direction, self.speed = direction, 1000
        self.pos = pg.math.Vector2(self.rect.center)
        # TIMER.
        self.init_time = pg.time.get_ticks()

    def update(self, delta_time: float):
        '''Update movement.'''
        self.pos.x += self.direction.x * self.speed * delta_time
        self.rect.centerx = round(self.pos.x)
        # DESTROY.
        if pg.time.get_ticks() - self.init_time > 1000:
            self.kill()


class FireAnimation(pg.sprite.Sprite):
    '''Class to create shooting animation.'''

    def __init__(self, direction: pg.math.Vector2, surfaces: list[pg.Surface],
                 groups: tuple[pg.sprite.Group], entity):
        super().__init__(groups)
        # LAYER ORDINAL.
        self.ORDINAL = LAYERS['Level']
        # ENTITY. (WHO FIRED!)
        self.entity = entity
        # ANIMATION.
        self.frame_index = 0
        self.animations = surfaces if direction.x > 0 else [
            pg.transform.flip(surface, True, False) for surface in surfaces]
        # OFFSET.
        self.offset_rect = pg.math.Vector2(
            60 * direction.x, 10 if entity.is_ducking else -16)
        # CORE.
        self.image = self.animations[self.frame_index]
        self.rect = self.image.get_rect(
            center=self.entity.rect.center + self.offset_rect)

    def animate(self, delta_time: float):
        '''Animating.'''
        # INCREASE.
        self.frame_index += 15 * delta_time
        # DESTROY.
        if self.frame_index >= len(self.animations):
            self.kill()
        # UPDATE.
        else:
            self.image = self.animations[int(self.frame_index)]

    def update(self, delta_time: float):
        '''Update animation.'''
        self.animate(delta_time)
        # FOLLOW THE ENTITY POSITION.
        self.rect.center = self.entity.rect.center + self.offset_rect
