from pygame import Surface
from pygame.image import load
from pygame.mask import from_surface
from pygame.mixer import Sound
from pygame.mouse import get_pos, get_pressed
from pygame.sprite import (Group, Sprite, collide_mask, groupcollide,
                           spritecollide)
from pygame.time import get_ticks

from laser import Laser


class Ship(Sprite):

    def __init__(self, screen: Surface, groups):
        super().__init__(groups)
        self.screen = screen
        self.image = load('image/SHIP.png').convert_alpha()
        self.rect = self.image.get_rect(center=screen.get_rect().center)
        self.mask = from_surface(self.image)
        # LASER.
        self.group_laser = Group()
        self.fired, self.fire_time = False, None
        # SOUND EFFECTS.
        self.laser_sound = Sound('music/LASER.wav')
        self.explosion_sound = Sound('music/EXPLOSION.wav')

    def laser_collision(self, group_meteor: Group):
        if groupcollide(self.group_laser, group_meteor, True, True, collide_mask):
            self.explosion_sound.play()

    def ship_collision(self, group_meteor: Group):
        return spritecollide(self, group_meteor, False, collide_mask)

    def load(self):
        if self.fired and get_ticks() - self.fire_time > 500:
            self.laser_sound.play()
            self.fired = False

    def fire(self):
        if get_pressed()[0] and not self.fired:
            Laser(self.rect.midtop, self.group_laser)
            self.fired, self.fire_time = True, get_ticks()

    def update(self, delta: float, group_meteor: Group):
        self.rect.center = get_pos()
        # CHARGE & SHOOT LASER.
        self.load()
        self.fire()
        # COLLISION.
        self.laser_collision(group_meteor)
        # UPDATE & DRAW LASER GROUP.
        self.group_laser.update(delta)
        self.group_laser.draw(self.screen)
