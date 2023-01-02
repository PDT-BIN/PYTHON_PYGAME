from random import choice, randint
from sys import exit

import pygame as pg
from car import Car
from player import Player
from settings import *
from sprite import SimpleSprite, LongSprite


class AllSprites(pg.sprite.Group):

    def __init__(self):
        super().__init__()
        self.bg = pg.image.load('image/main/map.png').convert()
        self.fg = pg.image.load('image/main/overlay.png').convert_alpha()
        self.offset = pg.math.Vector2()

    def customize_draw(self):
        # Change offset.
        self.offset.x = player.rect.centerx - WINDOW_WIDTH / 2
        self.offset.y = player.rect.centery - WINDOW_HEIGHT / 2
        # Blit entities.
        screen.blit(self.bg, -self.offset)
        for sprite in sorted(self.sprites(), key=lambda e: e.rect.centery):
            offset_pos = sprite.rect.topleft - self.offset
            screen.blit(sprite.image, offset_pos)
        screen.blit(self.fg, -self.offset)


pg.init()
screen = pg.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pg.display.set_caption('Frogger')
clock = pg.time.Clock()

# Groups.
all_sprites = AllSprites()
obstacle_sprites = pg.sprite.Group()
# Sprite.
start = (2062, 3274)
player = Player(start, all_sprites, obstacle_sprites)
# Timers.
car_timer = pg.USEREVENT + 1
pg.time.set_timer(car_timer, 50)
pos_list = []
# Sprite setup.
for file_name, pos_list in SIMPLE_OBJECTS.items():
    path = f'image/objects/simple/{file_name}.png'
    surf = pg.image.load(path).convert_alpha()
    for pos in pos_list:
        SimpleSprite(surf, pos, (all_sprites, obstacle_sprites))

for file_name, pos_list in LONG_OBJECTS.items():
    path = f'image/objects/long/{file_name}.png'
    surf = pg.image.load(path).convert_alpha()
    for pos in pos_list:
        LongSprite(surf, pos, (all_sprites, obstacle_sprites))
# Font.
font = pg.font.Font('font/SUBATOMIC.ttf', 50)
vict_surf = font.render('YOUR VICTORY!', True, 'WHITE')
vict_rect = vict_surf.get_rect(center=(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2))
lost_surf = font.render('YOUR LOSS!', True, 'WHITE')
lost_rect = lost_surf.get_rect(center=(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2))
# Music.
pg.mixer.music.load('audio/music.mp3')
pg.mixer.music.play(-1)
# Stage flag.
flag = True

# Game loop.
while True:
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            exit()
        if event.type == pg.MOUSEBUTTONDOWN and flag == False:
            flag = True
            player.pos.update(start)
            player.speed = 200
            for sprite in all_sprites.sprites():
                if hasattr(sprite, 'name'):
                    sprite.kill()
        if event.type == car_timer:
            random_pos = choice(CAR_START_POSITIONS)
            if random_pos not in pos_list:
                pos_list.append(random_pos)
                pos = (random_pos[0], random_pos[1] + randint(-8, 8))
                Car(pos, (all_sprites, obstacle_sprites))
            if len(pos_list) > 5:
                del pos_list[0]
    # Delta time.
    dt = clock.tick() / 1000
    if player.speed == 0:
        screen.fill('BLACK')
        screen.blit(lost_surf, lost_rect)
        flag = False
    else:
        if player.pos.y >= 1180:
            # Update.
            all_sprites.update(dt)
            # Draw.
            all_sprites.customize_draw()
        else:
            screen.fill('TEAL')
            screen.blit(vict_surf, vict_rect)
            flag = False
    # Update display surface.
    pg.display.update()
