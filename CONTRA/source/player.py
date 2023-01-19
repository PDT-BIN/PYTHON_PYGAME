import pygame as pg
from entity import Entity
from settings import *


class Player(Entity):
    '''Class to manage player object.'''

    def __init__(self, place: tuple[int, int], groups: tuple[pg.sprite.Group],
                 graphic_path: str, obstacles: pg.sprite.Group, shoot_method):
        super().__init__(place, groups, graphic_path, shoot_method)
        # MOVEMENT.
        self.direction, self.SPEED = pg.math.Vector2(), 400
        self.pos = pg.math.Vector2(self.rect.topleft)
        # COLLISION.
        self.obstacles = obstacles
        # GRAVITY.
        self.GRAVITY, self.JUMP_SPEED = 15, 1000
        self.is_on_floor = False
        # PLATFORM STOOD BY PLAYER.
        self.stood_platform = None
        # OVERRIDE.
        self.health = 10

    def input(self):
        '''Inputting.'''
        keys = pg.key.get_pressed()
        # MOVING.
        if keys[pg.K_LEFT]:
            self.direction.x = -1
            self.status = 'left'
        elif keys[pg.K_RIGHT]:
            self.direction.x = 1
            self.status = 'right'
        else:
            self.direction.x = 0
        # JUMPING.
        if keys[pg.K_UP] and self.is_on_floor:
            self.direction.y = -self.JUMP_SPEED
        # DUCKING.
        self.is_ducking = keys[pg.K_DOWN] and self.is_on_floor
        # SHOOTING.
        if keys[pg.K_SPACE] and self.can_shoot:
            direction = pg.math.Vector2(-1 if self.status.split('_')
                                        [0] == 'left' else 1, 0)
            y_offset = (0, -16 if not self.is_ducking else 10)
            place = self.rect.center + direction * 60
            self.shoot(place + y_offset, direction, self)
            # CHARGING.
            self.can_shoot, self.shoot_time = False, pg.time.get_ticks()

    def get_status(self):
        '''Special statuses.'''
        # IDLE. (IDLE WHEN DON'T MOVE & ON FLOOR)
        if self.direction.x == 0:
            self.status = self.status.split('_')[0] + '_idle'
        # JUMP. (JUMP WHEN NOT ON FLOOR)
        if not self.is_on_floor:
            self.status = self.status.split('_')[0] + '_jump'
        # DUCK. (DUCK WHEN ON FLOOR)
        if self.is_ducking:
            self.status = self.status.split('_')[0] + '_duck'

    def check_contact(self):
        '''Block the approximate case.'''
        # AN INVISIBLE RECT UNDER THE PLAYER.
        below_rect = pg.Rect(0, 0, self.rect.width, 5)
        below_rect.midtop = self.rect.midbottom
        for obstacle in self.obstacles:
            if obstacle.rect.colliderect(below_rect):
                # STATIC.
                if self.direction.y > 0:
                    self.is_on_floor = True
                # DYNAMIC.
                if hasattr(obstacle, 'direction'):
                    self.stood_platform = obstacle

    def collide(self, directionection: str):
        '''Colliding.'''
        for obstacle in self.obstacles.sprites():
            if obstacle.rect.colliderect(self.rect):
                if directionection == 'horizontal':
                    # LEFT COLLISION.
                    if self.rect.left <= obstacle.rect.right and self.old_rect.left >= obstacle.old_rect.right:
                        self.rect.left = obstacle.rect.right
                    # RIGHT COLLISION.
                    if self.rect.right >= obstacle.rect.left and self.old_rect.right <= obstacle.old_rect.left:
                        self.rect.right = obstacle.rect.left
                    # UPDATE.
                    self.pos.x = self.rect.x
                else:
                    # UP COLLISION.
                    if self.rect.top <= obstacle.rect.bottom and self.old_rect.top >= obstacle.old_rect.bottom:
                        self.rect.top = obstacle.rect.bottom
                    # DOWN COLLISION.
                    if self.rect.bottom >= obstacle.rect.top and self.old_rect.bottom <= obstacle.old_rect.top:
                        self.rect.bottom = obstacle.rect.top
                        # ON FLOOR.
                        self.is_on_floor = True
                    # UPDATE.
                    self.pos.y = self.rect.y
                    # RESET TO FALL DOWN.
                    self.direction.y = 0
        # JUMPING & FALLING.
        if self.is_on_floor and self.direction.y != 0:
            self.is_on_floor = False

    def move(self, delta_time: float):
        '''Moving.'''
        # DON'T MOVE WHEN DUCKING.
        if self.is_ducking:
            self.direction.x = 0
        # HORIZONTAL.
        self.pos.x += self.direction.x * self.SPEED * delta_time
        self.rect.x = round(self.pos.x)
        self.collide('horizontal')
        # VERTICAL.
        self.direction.y += self.GRAVITY
        self.pos.y += self.direction.y * delta_time
        # GLUE THE PLAYER TO THE PLATFORM.
        if self.stood_platform and self.stood_platform.direction.y > 0 and self.direction.y > 0:
            self.direction.y, self.is_on_floor = 0, True
            self.rect.bottom = self.stood_platform.rect.top
            self.pos.y = self.rect.y
        self.rect.y = round(self.pos.y)
        self.collide('vertical')
        # RESET GLUE.
        self.stood_platform = None

    def die(self):
        '''Override.'''
        if self.health <= 0:
            pg.quit()
            exit()

    def update(self, delta_time: float):
        '''Update all activities.'''
        # STORE THE PREVIOUS RECT.
        self.old_rect = self.rect.copy()
        # UPDATE.
        self.input()
        self.get_status()
        self.move(delta_time)
        self.check_contact()
        self.animate(delta_time)
        self.blink()
        # TIMER.
        self.shoot_timer()
        self.hurt_timer()
