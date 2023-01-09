from math import sin
from os import walk

from pygame import Surface
from pygame.image import load
from pygame.mask import from_surface
from pygame.math import Vector2
from pygame.mixer import Sound
from pygame.sprite import Group, Sprite
from pygame.time import get_ticks


class Entity(Sprite):
    '''A class to be inherited by Player & Enemy.'''

    def __init__(self, position: tuple, groups: Group, image_path: str, obstacles: Group):
        '''Initialize core attributes.'''
        super().__init__(groups)
        # Asset.
        self.get_asset(image_path)
        self.status, self.frame_index = 'down', 0
        # Core.
        self.image = self.animations[self.status][self.frame_index]
        self.rect = self.image.get_rect(center=position)
        # Movement.
        self.pos = Vector2(self.rect.center)
        self.direction, self.speed = Vector2(), 200
        # Collision.
        self.hitbox = self.rect.inflate(-self.rect.width / 2,
                                        -self.rect.height / 2)
        self.mask = from_surface(self.image)
        self.obstacles = obstacles
        # Attacking.
        self.attacking = False
        # Health.
        self.health = 3
        self.is_vulnerable, self.hit_timer = True, None
        # Sound.
        self.hit_sound = Sound('audio/hit.mp3')
        self.hit_sound.set_volume(0.1)
        self.shoot_sound = Sound('audio/bullet.wav')
        self.shoot_sound.set_volume(0.2)

    def get_asset(self, image_path: str):
        '''Get images.'''
        self.animations: dict[str, list[Surface]] = dict()
        for index, folders in enumerate(walk(image_path)):
            if index != 0:
                surfs = [load(f'{folders[0]}/{name}').convert_alpha()
                         for name in sorted(folders[2], key=lambda e: int(e.split('.')[0]))]
                self.animations[folders[0].split('\\')[1]] = surfs
            else:
                self.animations = {name: None for name in folders[1]}

    def blink(self):
        '''Get blinking if be attacked at wave values.'''
        if not self.is_vulnerable and sin(get_ticks()) >= 0:
            mask = from_surface(self.image)
            mask_surf = mask.to_surface()
            mask_surf.set_colorkey('BLACK')
            self.image = mask_surf

    def damage(self):
        '''Get damage from being attacked.'''
        if self.is_vulnerable:
            self.health -= 1
            self.is_vulnerable = False
            self.hit_timer = get_ticks()
            self.hit_sound.play()

    def check_death(self):
        '''Check if out of health.'''
        if self.health <= 0:
            self.kill()

    def vulnerability_timer(self):
        '''Reset hit timer.'''
        if not self.is_vulnerable:
            current_time = get_ticks()
            if current_time - self.hit_timer > 400:
                self.is_vulnerable = True

    def collide(self, direction: str):
        '''Check collision.'''
        for sprite in self.obstacles:
            if sprite.hitbox.colliderect(self.hitbox):
                if direction == 'horizontal':
                    if self.direction.x > 0:  # Moving right.
                        self.hitbox.right = sprite.hitbox.left
                    if self.direction.x < 0:  # Moving left.
                        self.hitbox.left = sprite.hitbox.right
                    self.pos.x = self.rect.centerx = self.hitbox.centerx
                else:
                    if self.direction.y > 0:  # Moving down.
                        self.hitbox.bottom = sprite.hitbox.top
                    if self.direction.y < 0:  # Moving up.
                        self.hitbox.top = sprite.hitbox.bottom
                    self.pos.y = self.rect.centery = self.hitbox.centery

    def move(self, dt: float):
        '''Move the object.'''
        # Balance directions.
        if self.direction.magnitude() != 0:
            self.direction = self.direction.normalize()
        # Horizontal movement.
        self.pos.x += self.direction.x * self.speed * dt
        self.rect.centerx = self.hitbox.centerx = round(self.pos.x)
        self.collide('horizontal')
        # Vertical movement.
        self.pos.y += self.direction.y * self.speed * dt
        self.rect.centery = self.hitbox.centery = round(self.pos.y)
        self.collide('vertical')
