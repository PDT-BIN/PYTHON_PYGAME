# USE SIN() TO FIND WAVE VALUES FOR BLINKING ANIMATIONS.
from math import sin
# USE WALK() TO BROWSE ALL THE FILES IN THE ROOT FOLDER.
from os import walk

import pygame as pg
from settings import *


class Entity(pg.sprite.Sprite):
    '''Class to be inherited by Player & Enemy.'''

    def __init__(self, place: tuple[int, int], groups: tuple[pg.sprite.Group], graphic_path: str, shoot_method):
        super().__init__(groups)
        # LAYER ORDINAL.
        self.ORDINAL = LAYERS['Level']
        # ANIMATIONS.
        self.status, self.frame_index = 'right', 0
        self.import_assets(graphic_path)
        # CORE.
        self.image = self.animations[self.status][self.frame_index]
        self.rect = self.image.get_rect(topleft=place)
        self.mask = pg.mask.from_surface(self.image)
        # COLLISION. (ENEMY DOESN'T USE THIS)
        self.old_rect = self.rect.copy()
        # ACTION. (ENEMY DOESN'T DUCK BUT USE FOR FIRE ANIMATION)
        self.is_ducking = False
        # INTERACTIVE METHOD.
        self.shoot = shoot_method
        self.can_shoot, self.shoot_time = True, None
        self.shoot_cooldown = 200
        # HEALTH.
        self.health = 3
        # VULNERABLE.
        self.can_hurt, self.hurt_time = True, None
        self.hurt_cooldown = 500

    def import_assets(self, pathname: str):
        '''Import external images.'''
        for index, (path, folders, files) in enumerate(walk(pathname)):
            if index != 0:
                status = path.split('\\')[-1]
                images = [pg.image.load(f'{path}/{file}').convert_alpha()
                          for file in sorted(files, key=lambda e: int(e.split('.')[0]))]
                self.animations[status] = images
            else:
                self.animations: dict[str, list[pg.Surface]] = {
                    folder: None for folder in folders}

    def animate(self, delta_time: float):
        '''Animating.'''
        # INCREASE.
        self.frame_index += 7 * delta_time
        # RESTART.
        if self.frame_index >= len(self.animations[self.status]):
            self.frame_index = 0
        # UPDATE.
        self.image = self.animations[self.status][int(self.frame_index)]
        self.mask = pg.mask.from_surface(self.image)

    def shoot_timer(self):
        '''Reset shooting status.'''
        if not self.can_shoot and pg.time.get_ticks() - self.shoot_time > self.shoot_cooldown:
            self.can_shoot = True

    def hurt_timer(self):
        '''Reset hurt status.'''
        if not self.can_hurt and pg.time.get_ticks() - self.hurt_time > self.hurt_cooldown:
            self.can_hurt = True

    def blink(self):
        '''Blinking.'''
        if not self.can_hurt and sin(pg.time.get_ticks()) > 0:
            blinking_mask = pg.mask.from_surface(self.image).to_surface()
            blinking_mask.set_colorkey('BLACK')
            self.image = blinking_mask

    def hurt(self):
        '''Be hurt.'''
        if self.can_hurt:
            self.health -= 1
            # CAN'T BE VULNERABLE.
            self.can_hurt = False
            self.hurt_time = pg.time.get_ticks()
            self.die()

    def die(self):
        '''Be dead.'''
        if self.health <= 0:
            self.kill()
