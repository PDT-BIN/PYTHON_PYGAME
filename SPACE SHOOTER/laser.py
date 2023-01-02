from pygame.image import load
from pygame.mask import from_surface
from pygame.math import Vector2
from pygame.sprite import Sprite


class Laser(Sprite):

    def __init__(self, pos, groups):
        super().__init__(groups)
        self.image = load('image/LASER.png').convert_alpha()
        self.rect = self.image.get_rect(midbottom=pos)
        self.mask = from_surface(self.image)
        # MOVEMENT.
        self.pos = Vector2(self.rect.topleft)
        self.direction, self.speed = Vector2(0, -1), 600

    def dokill(self):
        if self.rect.bottom < 0:
            self.kill()

    def update(self, delta: float):
        self.pos += self.direction * self.speed * delta
        self.rect.topleft = (round(self.pos.x), round(self.pos.y))
        self.dokill()
