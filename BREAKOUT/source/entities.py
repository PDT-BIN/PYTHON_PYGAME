from collections.abc import Callable
from random import choice, randint

import pygame as pg
from blockmaker import BlockMaker
from settings import *


class Upgrade(pg.sprite.Sprite):
    def __init__(self, place: tuple[int, int], form: str, groups):
        super().__init__(groups)
        # GENERAL.
        self.form = form
        self.image = pg.image.load(
            f'image/upgrades/{form}.png').convert_alpha()
        self.rect = self.image.get_rect(midtop=place)
        # MOVEMENT.
        self.pos = pg.math.Vector2(self.rect.topleft)
        self.direction, self.speed = pg.math.Vector2(0, 1), 200

    def update(self, delta_time: float):
        self.pos.y += self.direction.y * self.speed * delta_time
        self.rect.y = round(self.pos.y)

        if self.rect.top > WINDOW_HEIGHT + 100:
            self.kill()


class Projectile(pg.sprite.Sprite):

    def __init__(self, place: tuple[int, int], image: pg.Surface, groups):
        super().__init__(groups)
        # GENERAL.
        self.image = image
        self.rect = self.image.get_rect(midbottom=place)
        # MOVEMENT.
        self.pos = pg.math.Vector2(self.rect.topleft)
        self.direction, self.speed = pg.math.Vector2(0, -1), 300

    def update(self, delta_time: float):
        self.pos.y += self.direction.y * self.speed * delta_time
        self.rect.y = round(self.pos.y)

        if self.rect.bottom < -100:
            self.kill()


class Player(pg.sprite.Sprite):

    def __init__(self, groups, block_maker: BlockMaker):
        super().__init__(groups)
        # GENERAL.
        self.screen = pg.display.get_surface()
        self.image = block_maker.get_image(
            'player', (WINDOW_WIDTH // 10, WINDOW_HEIGHT // 20))
        self.rect = self.image.get_rect(midbottom=(
            WINDOW_WIDTH // 2, WINDOW_HEIGHT - 20))
        self.old_rect = self.rect.copy()
        # MOVEMENT.
        self.pos = pg.math.Vector2(self.rect.topleft)
        self.direction, self.speed = pg.math.Vector2(), 300
        # BLOCK CREATOR.
        self.block_marker = block_maker
        # HEARTS.
        self.hearts = 3
        # LASERS.
        self.laser_surf = pg.image.load(
            'image/other/laser.png').convert_alpha()
        self.laser_quantity = 2
        self.laser_rects: list[pg.Rect] = []

    def input(self):
        keys = pg.key.get_pressed()

        if keys[pg.K_LEFT]:
            self.direction.x = -1
        elif keys[pg.K_RIGHT]:
            self.direction.x = 1
        else:
            self.direction.x = 0

    def move(self, delta_time: float):
        self.pos.x += self.direction.x * self.speed * delta_time
        self.rect.x = round(self.pos.x)

    def constraint(self):
        if self.rect.left < 0:
            self.rect.left = 0
            self.pos.x = self.rect.x
        elif self.rect.right > WINDOW_WIDTH:
            self.rect.right = WINDOW_WIDTH
            self.pos.x = self.rect.x

    def upgrade(self, form: str):
        match form:
            case 'heart':
                self.hearts += 1
            case 'speed':
                self.speed += 50
            case 'size':
                widen_width = self.rect.width * 1.1
                self.image = self.block_marker.get_image(
                    'player', (widen_width, self.rect.height))
                self.rect = self.image.get_rect(center=self.rect.center)
                self.pos.x = self.rect.x
            case 'laser':
                self.laser_quantity += 1

    def display_laser(self):
        if self.laser_quantity > 0:
            self.laser_rects.clear()
            gap_size = self.rect.width / (self.laser_quantity + 1)

            for index in range(1, self.laser_quantity + 1):
                x = self.rect.left + index * gap_size
                self.laser_rects.append(self.laser_surf.get_rect(
                    midbottom=(x, self.rect.top)))

            for laser_rect in self.laser_rects:
                self.screen.blit(self.laser_surf, laser_rect)

    def update(self, delta_time: float):
        # STORE THE CURRENT RECT.
        self.old_rect = self.rect.copy()
        # UPDATE THE NEW RECT.
        self.input()
        self.move(delta_time)
        self.constraint()
        self.display_laser()


class Block(pg.sprite.Sprite):

    def __init__(self, place: tuple[int, int], form: str, groups,
                 block_maker: BlockMaker, create_upgrade: Callable[[tuple[int, int]], None]):
        super().__init__(groups)
        # GENERAL.
        self.image = block_maker.get_image(
            COLOR_LEGEND[form], (BLOCK_WIDTH, BLOCK_HEIGHT))
        self.rect = self.image.get_rect(topleft=place)
        self.old_rect = self.rect.copy()
        # HEALTH.
        self.health = int(form)
        # BLOCK CREATOR.
        self.block_maker = block_maker
        # UPGRADE CREATOR.
        self.create_upgrade = create_upgrade

    def get_damage(self, amount: int):
        self.health -= amount

        if self.health > 0:
            self.image = self.block_maker.get_image(
                COLOR_LEGEND[str(self.health)], (BLOCK_WIDTH, BLOCK_HEIGHT))
        else:
            if randint(0, 10) < 4:
                self.create_upgrade(choice(UPGRADES), self.rect.center)
            self.kill()


class Ball(pg.sprite.Sprite):

    def __init__(self, groups, player: Player, blocks: pg.sprite.Group):
        super().__init__(groups)
        # GENERAL.
        self.image = pg.image.load('image/other/ball.png').convert_alpha()
        self.rect = self.image.get_rect(midbottom=player.rect.midtop)
        self.old_rect = self.rect.copy()
        # MOVEMENT.
        self.pos = pg.math.Vector2(self.rect.topleft)
        self.direction, self.speed = pg.math.Vector2(choice((-1, 1)), -1), 400
        # COLLISION.
        self.player = player
        self.blocks = blocks
        # START STATUS.
        self.is_active = False
        # AUDIO.
        self.sound_impact = pg.mixer.Sound('audio/impact.wav')
        self.sound_impact.set_volume(0.1)
        self.sound_fail = pg.mixer.Sound('audio/fail.wav')
        self.sound_fail.set_volume(0.1)

    def constraint(self, direction: str):
        if direction == 'horizontal':
            if self.rect.left < 0:
                self.rect.left = 0
                self.pos.x = self.rect.x
                self.direction.x *= -1
            elif self.rect.right > WINDOW_WIDTH:
                self.rect.right = WINDOW_WIDTH
                self.pos.x = self.rect.x
                self.direction.x *= -1
        else:
            if self.rect.top < 0:
                self.rect.top = 0
                self.pos.y = self.rect.y
                self.direction.y *= -1
            elif self.rect.bottom > WINDOW_HEIGHT:
                self.is_active = False
                self.direction.y = -1
                self.player.hearts -= 1
                self.sound_fail.play()

    def collide(self, direction: str):
        collided_sprites: list[Player | Block] = pg.sprite.spritecollide(
            self, self.blocks, False)
        if self.rect.colliderect(self.player.rect):
            collided_sprites.append(self.player)

        if collided_sprites:
            for sprite in collided_sprites:
                if direction == 'horizontal':
                    if self.rect.right >= sprite.rect.left and self.old_rect.right <= sprite.old_rect.left:
                        self.rect.right = sprite.rect.left - 1
                        self.pos.x = self.rect.x
                        self.direction.x *= -1
                        self.sound_impact.play()
                    elif self.rect.left <= sprite.rect.right and self.old_rect.left >= sprite.old_rect.right:
                        self.rect.left = sprite.rect.right + 1
                        self.pos.x = self.rect.x
                        self.direction.x *= -1
                        self.sound_impact.play()

                    if hasattr(sprite, 'health'):
                        sprite.get_damage(1)
                else:
                    if self.rect.bottom >= sprite.rect.top and self.old_rect.bottom <= sprite.old_rect.top:
                        self.rect.bottom = sprite.rect.top - 1
                        self.pos.y = self.rect.y
                        self.direction.y *= -1
                        self.sound_impact.play()
                    elif self.rect.top <= sprite.rect.bottom and self.old_rect.top >= sprite.old_rect.bottom:
                        self.rect.top = sprite.rect.bottom + 1
                        self.pos.y = self.rect.y
                        self.direction.y *= -1
                        self.sound_impact.play()

                    if hasattr(sprite, 'health'):
                        sprite.get_damage(1)

    def update(self, delta_time: float):
        if self.is_active:
            # STORE THE CURRENT RECT.
            self.old_rect = self.rect.copy()
            # UPDATE THE NEW RECT.
            if self.direction.magnitude() != 0:
                self.direction = self.direction.normalize()
            # HORIZONTAL PROCESS.
            self.pos.x += self.direction.x * self.speed * delta_time
            self.rect.x = round(self.pos.x)
            self.constraint('horizontal')
            self.collide('horizontal')
            # VERTICAL PROCESS.
            self.pos.y += self.direction.y * self.speed * delta_time
            self.rect.y = round(self.pos.y)
            self.constraint('vertical')
            self.collide('vertical')
        else:
            self.rect.midbottom = self.player.rect.midtop
            self.pos.update(self.rect.topleft)
