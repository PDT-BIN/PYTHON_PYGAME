from math import sin

import pygame as pg


class Entity(pg.sprite.Sprite):

    def __init__(self, groups: tuple[pg.sprite.Group], group_obstacle: pg.sprite.Group):
        super().__init__(groups)
        # ANIMATION.
        self.frame_index, self.ANIMATION_SPEED = 0, 0.15
        # MOVEMENT.
        self.direction = pg.math.Vector2()
        # COLLISION.
        self.group_obstacle = group_obstacle

    def collide(self, direction: str):
        if direction == 'Horizontal':
            for sprite in self.group_obstacle.sprites():
                if sprite.hitbox.colliderect(self.hitbox):
                    if self.direction.x < 0:
                        self.hitbox.left = sprite.hitbox.right
                    else:
                        self.hitbox.right = sprite.hitbox.left
        else:
            for sprite in self.group_obstacle.sprites():
                if sprite.hitbox.colliderect(self.hitbox):
                    if self.direction.y < 0:
                        self.hitbox.top = sprite.hitbox.bottom
                    else:
                        self.hitbox.bottom = sprite.hitbox.top

    def move(self, speed: int):
        if self.direction.magnitude() != 0:
            self.direction = self.direction.normalize()

        self.hitbox.x += self.direction.x * speed
        self.collide('Horizontal')

        self.hitbox.y += self.direction.y * speed
        self.collide('Vertical')

        self.rect.center = self.hitbox.center

    def get_alpha_value(self):
        return 255 * (sin(pg.time.get_ticks()) > 0)
