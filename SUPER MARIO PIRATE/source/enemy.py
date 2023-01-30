from random import randint

import pygame as pg
from tiles import AnimatingTile


class Enemy(AnimatingTile):

    def __init__(self, size, place):
        super().__init__(size, place, 'image/enemy/run')
        # OVERRIDE RECT.
        self.rect.y += size - self.image.get_height()
        # MOVEMENT.
        self.direction, self.MOVE_SPEED = 1, randint(2, 4)

    def move(self):
        self.rect.x += self.direction * self.MOVE_SPEED

    def flip(self):
        if self.direction > 0:
            self.image = pg.transform.flip(self.image, True, False)

    def reverse(self):
        self.direction *= -1

    def update(self, x_shift: int):
        super().update(x_shift)
        self.move()
        self.flip()
