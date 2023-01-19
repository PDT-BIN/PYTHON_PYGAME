# USE EXIT() TO QUIT PROGRAM IMMEDIATELY.
from sys import exit

import pygame as pg
from bullet import Bullet, FireAnimation
from enemy import Enemy
from overlay import Overlay
from player import Player
# USE LOAD_PYGAME() TO LOAD THE DATA FROM .TMX FILE.
from pytmx.util_pygame import load_pygame
from settings import *
from tile import CollisionTile, MovingPlatform, Tile


class AllSprites(pg.sprite.Group):
    '''Class to manage all sprites & play a role as Camera.'''

    def __init__(self):
        super().__init__()
        self.screen = pg.display.get_surface()
        self.offset = pg.math.Vector2()
        # BACKGROUND IMAGE.
        self.bg_sky = pg.image.load('image/sky/bg_sky.png').convert_alpha()
        self.fg_sky = pg.image.load('image/sky/fg_sky.png').convert_alpha()
        # MAP.
        tmx_map = load_pygame('data/map.tmx')
        # DIMENSION.
        self.PADDING = WINDOW_WIDTH / 2
        self.sky_width = self.bg_sky.get_width()
        map_width = tmx_map.tilewidth * tmx_map.width + (2 * self.PADDING)
        # QUANTITY.
        self.sky_quantity = int(map_width / self.sky_width)

    def draws(self, player: Player):
        '''Customize draw.'''
        # UPDATE OFFSET.
        self.offset.update(player.rect.centerx - WINDOW_WIDTH / 2,
                           player.rect.centery - WINDOW_HEIGHT / 2)
        # DRAW BACKGROUND.
        for index in range(self.sky_quantity):
            offset_pos = (-self.PADDING + index * self.sky_width, 850)
            self.screen.blit(self.bg_sky, offset_pos - self.offset / 2.5)
            self.screen.blit(self.fg_sky, offset_pos - self.offset / 2)
        # DRAW ENTITIES.
        for sprite in sorted(self.sprites(), key=lambda e: e.ORDINAL):
            offset_rect = sprite.rect.copy()
            offset_rect.center -= self.offset
            self.screen.blit(sprite.image, offset_rect)


class Game:
    '''Class to manage game assets & behaviors.'''

    def __init__(self):
        pg.init()
        # DISPLAY.
        self.display = pg.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pg.display.set_caption('Contra')
        # TIME.
        self.clock = pg.time.Clock()
        # GROUP.
        self.all_sprites = AllSprites()
        self.obstacles = pg.sprite.Group()
        self.platforms = pg.sprite.Group()
        self.bullets = pg.sprite.Group()
        self.vulnerables = pg.sprite.Group()
        # SETUP.
        self.load()
        self.overlay = Overlay(self.player)
        # ANOTHER ASSETS.
        self.bullet_surf = pg.image.load('image/bullet.png').convert_alpha()
        self.fire_surfs = [pg.image.load(f'image/fire/{name}.png').convert_alpha()
                           for name in range(2)]
        # MUSIC.
        pg.mixer.music.load('audio/MUSIC.wav')
        pg.mixer.music.play(-1)
        # SOUND.
        self.shoot_sound = pg.mixer.Sound('audio/BULLET.wav')
        self.shoot_sound.set_volume(0.2)
        self.hit_sound = pg.mixer.Sound('audio/HIT.wav')
        self.hit_sound.set_volume(0.2)

    def load(self):
        '''Initialize all sprites.'''
        tmx_map = load_pygame('data/map.tmx')
        # COLLISION TILES.
        for x, y, surface in tmx_map.get_layer_by_name('Level').tiles():
            CollisionTile((x * 64, y * 64), surface,
                          (self.all_sprites, self.obstacles))
        # LANDSCAPE TILES.
        for layer in ('BG', 'BG Detail', 'FG Detail Bottom', 'FG Detail Top'):
            for x, y, surface in tmx_map.get_layer_by_name(layer).tiles():
                Tile((x * 64, y * 64), surface,
                     self.all_sprites, LAYERS[layer])
        # CHARACTER OBJECTS.
        for obj in tmx_map.get_layer_by_name('Entities'):
            if obj.name == 'Enemy':
                Enemy((obj.x, obj.y), (self.all_sprites, self.vulnerables),
                      'image/enemy', self.obstacles, self.player, self.shoot)
            else:
                self.player = Player((obj.x, obj.y), (self.all_sprites, self.vulnerables),
                                     'image/player', self.obstacles, self.shoot)
        # PLATFORMS OBJECTS.
        self.platform_boders: list[pg.Rect] = list()
        for obj in tmx_map.get_layer_by_name('Platforms'):
            if obj.name == 'Platform':
                MovingPlatform((obj.x, obj.y), obj.image,
                               (self.all_sprites, self.obstacles, self.platforms))
            else:
                self.platform_boders.append(
                    pg.Rect(obj.x, obj.y, obj.width, obj.height))

    def collide_platform(self):
        '''Check platform collision.'''
        for platform in self.platforms:
            for boder in self.platform_boders:
                # PLATFORM & ITS BODERS.
                if platform.rect.colliderect(boder):
                    # UP COLLISION.
                    if platform.direction.y < 0:
                        platform.rect.top = boder.bottom
                    # DOWN COLLISION.
                    else:
                        platform.rect.bottom = boder.top
                    # UPDATE.
                    platform.pos.y = platform.rect.y
                    # INVERT DIRECTION.
                    platform.direction *= -1
            # PLATFORM & PLAYER. (GO DOWN -> GO UP)
            if self.player.rect.colliderect(platform.rect) and self.player.rect.centery > platform.rect.centery:
                platform.rect.bottom = self.player.rect.top
                platform.pos.y = platform.rect.y
                platform.direction.y = -1

    def collide_bullet(self):
        '''Check bullet collision.'''
        # BULLET & OBSTACLE.
        pg.sprite.groupcollide(self.bullets, self.obstacles, True, False)
        # BULLET & VULNERABLE.
        for sprite in self.vulnerables.sprites():
            if pg.sprite.spritecollide(sprite, self.bullets, True, pg.sprite.collide_mask):
                sprite.hurt()
                self.hit_sound.play()

    def shoot(self, place: tuple[int, int], direction: pg.math.Vector2, entity):
        '''Shooting.'''
        # CREATE BULLET.
        Bullet(place, self.bullet_surf, direction,
               (self.all_sprites, self.bullets))
        # SHOOTING ANIMATION.
        FireAnimation(direction, self.fire_surfs, self.all_sprites, entity)
        self.shoot_sound.play()

    def run(self):
        '''Run the main loop containing the entire logic.'''
        while True:
            # EVENT.
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                    exit()
            self.display.fill('black')
            # DELTA TIME.
            delta_time = self.clock.tick() / 1000
            self.display.fill((249, 131, 103))
            # UPDATE.
            self.collide_platform()
            self.all_sprites.update(delta_time)
            self.collide_bullet()
            # DRAW.
            self.all_sprites.draws(self.player)
            self.overlay.display()
            pg.display.update()


if __name__ == '__main__':
    Game().run()
