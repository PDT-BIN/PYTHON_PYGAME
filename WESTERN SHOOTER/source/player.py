from sys import exit

import pygame as pg
from enitity import Entity
from pygame.mask import from_surface
from pygame.math import Vector2
from pygame.sprite import Group


class Player(Entity):
    '''A class to manage player.'''

    def __init__(self, position: tuple, groups: Group, image_path: str,
                 obstacles: Group, shoot_method):
        '''Initialize core attributes.'''
        super().__init__(position, groups, image_path, obstacles)
        # Shooting.
        self.shoot = shoot_method
        self.is_shot = False

    def get_status(self):
        '''Get status.'''
        # Idling.
        if self.direction.magnitude() == 0:
            self.status = self.status.split('_')[0] + '_idle'
        # Attacking.
        if self.attacking:
            self.status = self.status.split('_')[0] + '_attack'

    def input(self):
        '''Check User's movement keys.'''
        keys = pg.key.get_pressed()
        # Move.
        if not self.attacking:
            # Horizontal direction.
            if keys[pg.K_LEFT]:
                self.direction.x = -1
                self.status = 'left'
            elif keys[pg.K_RIGHT]:
                self.direction.x = 1
                self.status = 'right'
            else:
                self.direction.x = 0
            # Vertical direction.
            if keys[pg.K_UP]:
                self.direction.y = -1
                self.status = 'up'
            elif keys[pg.K_DOWN]:
                self.direction.y = 1
                self.status = 'down'
            else:
                self.direction.y = 0
        # Attacking
        if keys[pg.K_SPACE] and not self.attacking:
            # Attack mode & Charge bullet.
            self.attacking, self.is_shot = True, False
            # Lock moving & Restart animation.
            self.direction, self.frame_index = Vector2(), 0
            # Store the direction.
            match self.status.split('_')[0]:
                case 'left': self.shoot_direction = Vector2(-1, 0)
                case 'right': self.shoot_direction = Vector2(1, 0)
                case 'up': self.shoot_direction = Vector2(0, -1)
                case 'down': self.shoot_direction = Vector2(0, 1)

    def animate(self, dt: float):
        '''Animate the player.'''
        current_animation = self.animations[self.status]
        self.frame_index += 7 * dt
        # Shooting time.
        if self.attacking and int(self.frame_index) == 2 and not self.is_shot:
            bullet_offset = self.rect.center + self.shoot_direction * 80
            self.shoot(bullet_offset, self.shoot_direction)
            self.is_shot = True
            self.shoot_sound.play()
        # Animation.
        if self.frame_index >= len(current_animation):
            self.frame_index = 0
            if self.attacking:
                self.attacking = False
        self.image = current_animation[int(self.frame_index)]
        self.mask = from_surface(self.image)

    def check_death(self):
        if self.health <= 0:
            pg.quit()
            exit()

    def update(self, delta_time: float):
        '''Update all activities.'''
        self.input()
        self.get_status()
        self.move(delta_time)
        self.animate(delta_time)
        self.blink()
        self.vulnerability_timer()
        self.check_death()
