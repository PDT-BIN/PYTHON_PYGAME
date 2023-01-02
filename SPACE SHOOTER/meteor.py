from random import randint, uniform

from pygame.image import load
from pygame.mask import from_surface
from pygame.math import Vector2
from pygame.sprite import Sprite
from pygame.transform import rotate, scale


class Meteor(Sprite):

    def __init__(self, pos, groups):
        super().__init__(groups)
        # CORE ATTRIBUTES.
        self.image = self.surf = Meteor.scaled()
        self.rect = self.image.get_rect(center=pos)
        self.mask = from_surface(self.image)
        # MOVEMENT.
        self.pos = Vector2(self.rect.topleft)
        self.direction = Vector2(uniform(-0.5, 0.5), 1)
        self.speed = randint(400, 600)
        # ROTATION.
        self.angle, self.rate = 0, randint(20, 50)

    @staticmethod
    def scaled():
        surf = load('image/METEOR.png').convert_alpha()
        scal = Vector2(surf.get_size()) * uniform(0.5, 1.5)
        return scale(surf, scal)

    def rotated(self, delta: float):
        self.angle += self.rate * delta
        self.image = rotate(self.surf, self.angle)
        self.rect = self.image.get_rect(center=self.rect.center)
        self.mask = from_surface(self.image)

    def dokill(self, height: int):
        if self.rect.top > height:
            self.kill()

    def update(self, delta: float, height: int):
        self.pos += self.direction * self.speed * delta
        self.rect.topleft = (round(self.pos.x), round(self.pos.y))
        self.rotated(delta)
        self.dokill(height)
