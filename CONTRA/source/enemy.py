import pygame as pg
from entity import Entity
from settings import *


class Enemy(Entity):
    '''Class to be manage enemy objects.'''

    def __init__(self, place: tuple[int, int], groups: tuple[pg.sprite.Group], graphic_path: str,
                 obstacles: pg.sprite.Group, player, shoot_method):
        super().__init__(place, groups, graphic_path, shoot_method)
        # AIM.
        self.player = player
        # OVERRIDE RECT.
        for obstacle in obstacles:
            if obstacle.rect.collidepoint(self.rect.midbottom):
                self.rect.bottom = obstacle.rect.top
        # OVERRIDE COOLDOWN.
        self.cooldown = 1000

    def get_status(self):
        '''Facing status.'''
        self.status = 'left' if self.player.rect.x < self.rect.x else 'right'

    def check_shoot(self):
        '''Shooting.'''
        # SHOOTING INFORMATION.
        player_pos = pg.math.Vector2(self.player.rect.center)
        enemy_pos = pg.math.Vector2(self.rect.center)
        # SHOOTING CONDITION.
        is_on_range = (player_pos - enemy_pos).magnitude() < 600
        is_on_line = self.rect.top - 20 < self.player.rect.y < self.rect.bottom + 20
        # SHOOTING.
        if is_on_line and is_on_range and self.can_shoot:
            direction = pg.math.Vector2(-1 if self.status == 'left' else 1, 0)
            y_offset = (0, -16)
            place = self.rect.center + direction * 60
            self.shoot(place + y_offset, direction, self)
            # CHARGING.
            self.can_shoot, self.shoot_time = False, pg.time.get_ticks()

    def update(self, delta_time: float):
        '''Update all activities.'''
        self.get_status()
        self.check_shoot()
        self.animate(delta_time)
        self.blink()
        # TIMER.
        self.shoot_timer()
        self.hurt_timer()
