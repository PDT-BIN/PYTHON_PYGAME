from random import randint
from sys import exit
from time import time

import pygame as pg
from blockmaker import BlockMaker
from entities import Ball, Block, Player, Projectile, Upgrade
from settings import *


class CRT:

    def __init__(self):
        # GENERAL.
        self.screen = pg.display.get_surface()
        surf_vignette = pg.image.load('image/other/tv.png').convert_alpha()
        self.scaled_vignette = pg.transform.scale(
            surf_vignette, (WINDOW_WIDTH, WINDOW_HEIGHT))
        self.load_crt_lines()

    def load_crt_lines(self):
        for index in range(WINDOW_HEIGHT // (line_height := 4)):
            y = index * line_height
            pg.draw.line(self.scaled_vignette, 'BLACK',
                         (0, y), (WINDOW_WIDTH, y))

    def draw(self):
        self.scaled_vignette.set_alpha(randint(60, 75))
        self.screen.blit(self.scaled_vignette, (0, 0))


class Game:

    def __init__(self):
        pg.init()
        # GENERAL SETUP.
        self.screen = pg.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pg.display.set_caption('Breakout')
        # BACKGROUND.
        self.bg = self.load_background()
        # GROUPS.
        self.all_sprites = pg.sprite.Group()
        self.group_block = pg.sprite.Group()
        self.group_upgrade = pg.sprite.Group()
        self.group_projectile = pg.sprite.Group()
        # STAGE SETUP.
        self.block_maker = BlockMaker()
        self.load_stage()
        # ENTITY.
        self.player = Player(self.all_sprites, self.block_maker)
        self.ball = Ball(self.all_sprites, self.player, self.group_block)
        # HEART.
        self.surf_heart = pg.image.load(
            'image/other/heart.png').convert_alpha()
        # PROJECTILE.
        self.surf_projectile = pg.image.load(
            'image/other/projectile.png').convert_alpha()
        # SHOOTING.
        self.can_shoot, self.COOLDOWN = True, 1000
        self.shoot_time = None
        # CRT.
        self.crt = CRT()
        # AUDIO.
        self.sound_powerup = pg.mixer.Sound('audio/powerup.wav')
        self.sound_powerup.set_volume(0.1)
        self.sound_laser_hit = pg.mixer.Sound('audio/laser_hit.wav')
        self.sound_laser_hit.set_volume(0.1)
        self.sound_laser = pg.mixer.Sound('audio/laser_hit.wav')
        self.sound_laser.set_volume(0.02)
        # MUSIC.
        pg.mixer.music.load('audio/music.wav')
        pg.mixer.music.set_volume(0.1)
        pg.mixer.music.play(-1)

    def load_background(self):
        original_bg = pg.image.load('image/other/bg.png').convert()
        # CALCULATE THE ZOOM RATIO.
        ratio = WINDOW_HEIGHT / original_bg.get_height()
        # GET THE ZOOMED BACKGROUND.
        return pg.transform.rotozoom(original_bg, 0, ratio)

    def load_stage(self):
        for row_index, row in enumerate(BLOCK_MAP):
            for col_index, col in enumerate(row):
                if col != ' ':
                    x = col_index * (BLOCK_WIDTH + GAP_SIZE) + GAP_SIZE // 2
                    y = row_index * (BLOCK_HEIGHT + GAP_SIZE) + \
                        GAP_SIZE // 2 + TOP_OFFSET
                    Block((x, y), col, (self.all_sprites, self.group_block),
                          self.block_maker, self.create_upgrade)

    def display_heart(self):
        for index in range(self.player.hearts):
            x = 2 + index * (self.surf_heart.get_width() + 2)
            self.screen.blit(self.surf_heart, (x, 4))

    def create_upgrade(self, form: str, place: tuple[int, int]):
        Upgrade(place, form, (self.all_sprites, self.group_upgrade))

    def check_upgrade_collision(self):
        collided_sprites: list[Upgrade] = pg.sprite.spritecollide(
            self.player, self.group_upgrade, True)

        for sprite in collided_sprites:
            self.player.upgrade(sprite.form)
            self.sound_powerup.play()

    def cooldown(self):
        if not self.can_shoot:
            if pg.time.get_ticks() - self.shoot_time >= self.COOLDOWN:
                self.can_shoot = True

    def create_projectile(self):
        self.sound_laser.play()
        for laser_rect in self.player.laser_rects:
            place = laser_rect.midtop - pg.math.Vector2(0, 30)
            Projectile(place, self.surf_projectile,
                       (self.all_sprites, self.group_projectile))

    def check_projectile_collision(self):
        for projectile in self.group_projectile.sprites():
            collided_sprites: list[Block] = pg.sprite.spritecollide(
                projectile, self.group_block, False)

            if collided_sprites:
                for sprite in collided_sprites:
                    sprite.get_damage(1)
                projectile.kill()
                self.sound_laser_hit.play()

    def check_close(self):
        if self.player.hearts < 0 or not self.group_block:
            pg.quit()
            exit()

    def run(self):
        previous_time = time()
        while True:
            # DELTA TIME.
            delta_time = time() - previous_time
            previous_time = time()
            # EVENT PROCESS.
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                    exit()
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_SPACE:
                        self.ball.is_active = True
                        if self.can_shoot:
                            self.create_projectile()
                            self.can_shoot = False
                            self.shoot_time = pg.time.get_ticks()
            # BACKGROUND.
            self.screen.blit(self.bg, (0, 0))
            # ENTITY PROCESS: UPDATE.
            self.all_sprites.update(delta_time)
            self.check_upgrade_collision()
            self.check_projectile_collision()
            self.check_close()
            self.cooldown()
            # ENTITY PROCESS: DRAW.
            self.all_sprites.draw(self.screen)
            self.display_heart()
            self.crt.draw()
            # UPDATE WINDOW.
            pg.display.update()


if __name__ == '__main__':
    Game().run()
