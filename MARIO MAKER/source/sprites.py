from random import choice, randint

import pygame as pg
from pygame import Surface
from pygame.mask import from_surface as get_mask
from pygame.math import Vector2 as Vector
from pygame.sprite import AbstractGroup, Group, Sprite
from settings import *
from timers import Timer


# GENERAL.
class Generic(Sprite):
    def __init__(self, groups: AbstractGroup, surface: Surface, position: tuple[int, int],
                 z_index: int = LEVEL_LAYERS['main']):
        super().__init__(groups)
        # ORIGINAL.
        self.image = surface
        self.rect = self.image.get_rect(topleft=position)
        # PERSONAL.
        self.z = z_index


class Block(Generic):
    def __init__(self, groups: AbstractGroup, size: tuple[int, int], position: tuple[int, int]):
        super().__init__(groups, Surface(size), position)


class Cloud(Generic):
    def __init__(self, groups: AbstractGroup, surface: Surface, position: tuple[int, int], limit: int):
        super().__init__(groups, surface, position, LEVEL_LAYERS['clouds'])
        # MOVEMENT.
        self.limit = limit
        self.pos = Vector(self.rect.topleft)
        self.speed = randint(20, 30)

    def update(self, delta_time: float):
        # MOVEMENT.
        self.pos.x -= self.speed * delta_time
        self.rect.x = int(self.pos.x)
        # DESTROY.
        if self.pos.x < self.limit:
            self.kill()


# SIMPLE ANIMATION.
class Animate(Generic):
    def __init__(self, groups: AbstractGroup, assets: list[Surface], position: tuple[int, int],
                 z_index: int = LEVEL_LAYERS['main']):
        # PERSONAL.
        self.frames = assets
        self.frame_index = 0
        super().__init__(
            groups, self.frames[self.frame_index], position, z_index)

    def animate(self, delta_time: float):
        self.frame_index += ANIMATION_SPEED * delta_time
        if self.frame_index >= len(self.frames):
            self.frame_index = 0
        self.image = self.frames[int(self.frame_index)]

    def update(self, delta_time: float):
        self.animate(delta_time)


class Coin(Animate):
    def __init__(self, groups: AbstractGroup, assets: list[Surface], position: tuple[int, int], coin_type: str):
        super().__init__(groups, assets, position)
        # OVERRIDE.
        self.rect.center = Vector(position) + COIN_OFFSET
        # PERSONAL.
        self.coin_type = coin_type


class Particle(Animate):
    def __init__(self, groups: AbstractGroup, assets: list[Surface], position: tuple[int, int]):
        super().__init__(groups, assets, position)
        # OVERRIDE.
        self.rect = self.image.get_rect(center=position)

    def animate(self, delta_time: float):
        self.frame_index += ANIMATION_SPEED * delta_time
        if self.frame_index < len(self.frames):
            self.image = self.frames[int(self.frame_index)]
        else:
            self.kill()


# ENEMY.
class Spike(Generic):
    def __init__(self, groups: AbstractGroup, surface: Surface, position: tuple[int, int]):
        super().__init__(groups, surface, position)
        # PERSONAL.
        self.mask = get_mask(self.image)


class Tooth(Generic):
    def __init__(self, groups: AbstractGroup, assets: dict[str, list[Surface]], position: tuple[int, int],
                 collidable_sprites: Group):
        # PERSONAL.
        self.frames, self.frame_index = assets, 0
        surface = self.frames[f'run_right'][self.frame_index]
        super().__init__(groups, surface, position)
        self.mask = get_mask(self.image)
        # OVERRIDE.
        self.rect.midbottom = Vector(position) + ENEMY_OFFSET
        # MOVEMENT.
        self.pos = Vector(self.rect.topleft)
        self.direction = Vector(choice((-1, 1)), 0)
        self.orientation = 'left' if self.direction.x < 0 else 'right'
        self.speed = 120
        # COLLISION.
        self.collidable_sprites = collidable_sprites
        # DESTROY IF NOT ON FLOOR.
        if not self.check_collide_point(self.rect.midbottom + Vector(0, 10)):
            self.kill()

    def check_collide_point(self, point: Vector):
        for sprite in self.collidable_sprites:
            if sprite.rect.collidepoint(point):
                return True
        return False

    def move(self, delta_time: float):
        # REVERSE DIRECTION WHEN THERE IS A CLIFF IN FRONT OR WALL COLLISION.
        if self.direction.x > 0:
            if self.check_collide_point(self.rect.midright + Vector(1, 0)) \
                    or not self.check_collide_point(self.rect.bottomright + Vector(1, 1)):
                self.direction.x = -1
                self.orientation = 'left'
        else:
            if self.check_collide_point(self.rect.midleft + Vector(-1, 0)) \
                    or not self.check_collide_point(self.rect.bottomleft + Vector(-1, 1)):
                self.direction.x = 1
                self.orientation = 'right'
        # MOVEMENT.
        self.pos.x += self.speed * delta_time * self.direction.x
        self.rect.x = round(self.pos.x)

    def animate(self, delta_time: float):
        self.frame_index += ANIMATION_SPEED * delta_time
        if self.frame_index >= len(frames := self.frames[f'run_{self.orientation}']):
            self.frame_index = 0
        self.image = frames[int(self.frame_index)]
        self.mask = get_mask(self.image)

    def update(self, delta_time: float):
        self.move(delta_time)
        self.animate(delta_time)


class Shell(Generic):
    def __init__(self, groups: AbstractGroup, assets: dict[str, list[Surface]], position: tuple[int, int],
                 orientation: str, pearl_surface: Surface, damage_sprites: Group):
        # PERSONAL.
        self.frame_index = 0
        self.status, self.orientation = 'idle', orientation
        self.frames = {key: list(map(lambda e: pg.transform.flip(e, True, False), value))
                       for key, value in assets.items()} if orientation == 'right' else assets
        surface = self.frames[self.status][self.frame_index]
        super().__init__(groups, surface, position)
        # OVERRIDE.
        self.rect.midbottom = Vector(position) + ENEMY_OFFSET
        # ATTACK.
        self.damage_sprites = damage_sprites
        self.pearl_surf = pearl_surface
        self.has_shot = False
        self.cooldown = Timer(2000)
        self.player: Player

    def check_status(self):
        self.status = 'attack' if not self.cooldown.is_actived and Vector(
            self.rect.center).distance_to(self.player.rect.center) < 500 else 'idle'

    def animate(self, delta_time: float):
        self.frame_index += ANIMATION_SPEED * delta_time
        if self.frame_index >= len(frames := self.frames[self.status]):
            self.frame_index = 0
            # COOLDOWN.
            if self.has_shot:
                self.cooldown.activate()
                self.has_shot = False
        self.image = frames[int(self.frame_index)]
        # ATTACK.
        if self.status == 'attack' and int(self.frame_index) == 2 and not self.has_shot:
            direction = Vector(-1 if self.orientation == 'left' else 1, 0)
            offset_pos = self.rect.center + \
                (direction * (50 if self.orientation == 'left' else 20) + (0, -10))
            Pearl((self.groups()[0], self.damage_sprites),
                  self.pearl_surf, offset_pos, direction)
            self.has_shot = True

    def update(self, delta_time: float):
        self.check_status()
        self.animate(delta_time)
        self.cooldown.update()


class Pearl(Generic):
    def __init__(self, groups: AbstractGroup, surface: Surface, position: tuple[int, int], direction: Vector):
        super().__init__(groups, surface, position)
        self.mask = get_mask(self.image)
        # MOVEMENT.
        self.pos = Vector(self.rect.topleft)
        self.direction, self.speed = direction, 150
        # DESTRUCT.
        self.life_timer = Timer(6000)
        self.life_timer.activate()

    def update(self, delta_time: float):
        # MOVEMENT.
        self.pos.x += self.speed * delta_time * self.direction.x
        self.rect.x = round(self.pos.x)
        self.life_timer.update()
        # DESTRUCTION.
        if not self.life_timer.is_actived:
            self.kill()


# PLAYER.
class Player(Generic):
    def __init__(self, groups: AbstractGroup, assets: dict[str, list[Surface]],
                 position: tuple[int, int], collidable_sprites: Group, jump_sound: pg.mixer.Sound):
        # ANIMATION.
        self.frames, self.frame_index = assets, 0
        self.status, self.orientation = 'idle', 'right'
        surface = self.frames[f'{self.status}_{self.orientation}'][self.frame_index]
        super().__init__(groups, surface, position)
        self.mask = get_mask(self.image)
        # MOVEMENT.
        self.pos, self.direction = Vector(self.rect.center), Vector()
        self.speed = 300
        # GRAVITY.
        self.gravity, self.is_on_floor = 4, False
        # COLLISION.
        self.colliable_sprites = collidable_sprites
        self.hitbox = self.rect.inflate(-50, 0)
        self.gap_to_floor = pg.Rect(
            self.hitbox.bottomleft, (self.hitbox.width, 2))
        self.invul_timer = Timer(200)
        # SOUND.
        self.jump_sound = jump_sound
        self.jump_sound.set_volume(0.3)

    # INPUT.
    def input(self):
        keys = pg.key.get_pressed()
        # MOVE.
        if keys[pg.K_RIGHT]:
            self.direction.x = 1
            self.orientation = 'right'
        elif keys[pg.K_LEFT]:
            self.direction.x = -1
            self.orientation = 'left'
        else:
            self.direction.x = 0
        # JUMP.
        if keys[pg.K_SPACE] and self.is_on_floor:
            self.jump_sound.play()
            self.direction.y = -2

    # ANIMATION.
    def check_status(self):
        if self.direction.y < 0:
            self.status = 'jump'
        elif self.direction.y > 1:
            self.status = 'fall'
        else:
            self.status = 'idle' if self.direction.x == 0 else 'run'

    def animate(self, delta_time: float):
        self.frame_index += ANIMATION_SPEED * delta_time
        if self.frame_index >= len(frames := self.frames[f'{self.status}_{self.orientation}']):
            self.frame_index = 0
        self.image = frames[int(self.frame_index)]
        self.mask = get_mask(self.image)
        # self.rect = self.image.get_rect(midbottom=self.rect.midbottom)
        # self.hitbox.center = self.pos = Vector(self.rect.center)
        if self.invul_timer.is_actived:
            mask = self.mask.to_surface()
            mask.set_colorkey('BLACK')
            self.image = mask

    # MOVEMENT & COLLISION.
    def move(self, delta_time: float):
        # HORIZONTAL.
        self.pos.x += self.speed * delta_time * self.direction.x
        self.rect.centerx = self.hitbox.centerx = round(self.pos.x)
        self.check_collision('horizontal')
        # VERTICAL.
        self.pos.y += self.speed * delta_time * self.direction.y
        self.rect.centery = self.hitbox.centery = round(self.pos.y)
        self.check_collision('vertical')

    def apply_gravity(self, delta_time: float):
        self.direction.y += self.gravity * delta_time
        self.rect.y += int(self.direction.y)

    def check_on_floor(self):
        self.gap_to_floor.topleft = self.hitbox.bottomleft
        for sprite in self.colliable_sprites:
            if sprite.rect.colliderect(self.gap_to_floor):
                self.is_on_floor = True
                break
        else:
            self.is_on_floor = False

    def check_collision(self, direction: str):
        for sprite in self.colliable_sprites:
            if sprite.rect.colliderect(self.hitbox):
                if direction == 'horizontal':
                    if self.direction.x > 0:  # MOVING RIGHT.
                        self.hitbox.right = sprite.rect.left
                    if self.direction.x < 0:  # MOVING LEFT.
                        self.hitbox.left = sprite.rect.right
                    self.pos.x = self.rect.centerx = self.hitbox.centerx
                else:
                    if self.direction.y < 0:  # JUMPING.
                        self.hitbox.top = sprite.rect.bottom
                    if self.direction.y > 0:  # FALLING.
                        self.hitbox.bottom = sprite.rect.top
                    self.pos.y = self.rect.centery = self.hitbox.centery
                    # RESET GRAVITY DIRECTION.
                    self.direction.y = 0

    def get_damage(self):
        if not self.invul_timer.is_actived:
            self.invul_timer.activate()
            self.direction.y = -1.5
            return True
        return False

    # UPDATE.
    def update(self, delta_time: float):
        self.input()
        self.apply_gravity(delta_time)
        self.move(delta_time)
        self.check_on_floor()
        self.invul_timer.update()
        self.check_status()
        self.animate(delta_time)
