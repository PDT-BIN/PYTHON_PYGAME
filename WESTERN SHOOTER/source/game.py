from sys import exit

import pygame as pg
from enemy import Cactus, Coffin
from player import Player
from pytmx.util_pygame import load_pygame
from setting import *
from sprites import Bullet, Obstacle


class AllSprites(pg.sprite.Group):
    '''A class to manage all sprites.'''

    def __init__(self):
        '''Initialize core attributes.'''
        super().__init__()
        self.offset = pg.math.Vector2()
        self.screen = pg.display.get_surface()
        self.bg = pg.image.load('image/other/bg.png').convert_alpha()

    def draws(self, player: Player):
        '''Customize draw.'''
        # Calculate the offset.
        self.offset.x = player.rect.centerx - WINDOW_WIDTH / 2
        self.offset.y = player.rect.centery - WINDOW_HEIGHT / 2
        # Draw the background.
        self.screen.blit(self.bg, -self.offset)
        # Draw all sprites.
        for sprite in sorted(self.sprites(), key=lambda e: e.rect.centery):
            offset_rect = sprite.rect.copy()
            offset_rect.center -= self.offset
            self.screen.blit(sprite.image, offset_rect)


class Game:
    '''A class to manage game assets and behaviors.'''

    def __init__(self):
        '''Initialize core attributes.'''
        pg.init()
        # Set up for SCREEN.
        self.screen = pg.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pg.display.set_caption('Western Shooter')
        # Set up for TIMING.
        self.clock = pg.time.Clock()
        # Bullet image.
        self.bullet_surf = pg.image.load(
            'image/other/particle.png').convert_alpha()
        # Set up for GROUPS.
        self.all_sprites = AllSprites()
        self.obstacles = pg.sprite.Group()
        self.bullets = pg.sprite.Group()
        self.enemies = pg.sprite.Group()
        # Entities.
        self.init()
        # Music.
        pg.mixer.music.load('audio/music.mp3')
        pg.mixer.music.play(-1)

    def init(self):
        '''Initialize entities.'''
        tmx_map = load_pygame('data/map.tmx')
        # Tile (Obstacle).
        for tile in tmx_map.get_layer_by_name('Fence').tiles():
            x, y, surf = tile
            Obstacle((x * 64, y * 64), surf,
                     (self.all_sprites, self.obstacles))
        # Object (Obstacle).
        for obj in tmx_map.get_layer_by_name('Objects'):
            Obstacle((obj.x, obj.y), obj.image,
                     (self.all_sprites, self.obstacles))
        # Object (Entity).
        for obj in tmx_map.get_layer_by_name('Entities'):
            pos = (obj.x, obj.y)
            match obj.name:
                case 'Coffin':
                    Coffin(pos, (self.all_sprites, self.enemies),
                           PATHS['coffin'], self.obstacles, self.player)
                case 'Cactus':
                    Cactus(pos, (self.all_sprites, self.enemies),
                           PATHS['cactus'], self.obstacles, self.player, self.shoot)
                case 'Player':
                    self.player = Player(pos, self.all_sprites,
                                         PATHS['player'], self.obstacles, self.shoot)

    def run(self):
        '''Run the main loop containing the logic of game.'''
        while True:
            # Event.
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                    exit()
            # Delta time.
            delta_time = self.clock.tick() / 1000
            # Update.
            self.all_sprites.update(delta_time)
            self.bullet_collision()
            # Draw.
            self.all_sprites.draws(self.player)
            pg.display.update()

    def shoot(self, position: tuple, direction: pg.math.Vector2):
        '''Shoot bullet.'''
        Bullet(position, direction, self.bullet_surf,
               (self.all_sprites, self.bullets))

    def bullet_collision(self):
        '''Check bullet collision.'''
        # Bullet & Obstacle.
        pg.sprite.groupcollide(self.bullets, self.obstacles,
                               True, False, pg.sprite.collide_mask)
        # Bullet & Enemy.
        if collisions := pg.sprite.groupcollide(
                self.bullets, self.enemies, True, False, pg.sprite.collide_mask):
            for _, enemies in collisions.items():
                for enemy in enemies:
                    enemy.damage()
        # Bullet & Player.
        if pg.sprite.spritecollide(self.player, self.bullets, True, pg.sprite.collide_mask):
            self.player.damage()


if __name__ == '__main__':
    Game().run()
