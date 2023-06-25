from collections.abc import Callable
from os import walk

import pygame as pg
from editor import Editor
from level import Level
from pygame.math import Vector2 as Vector
from settings import *
from supports import *


class Transition:
    def __init__(self, toggle: Callable[[], None]):
        self.screen = pg.display.get_surface()
        self.toggle = toggle
        self.is_actived = False
        # TRANSITION.
        self.border_width, self.direction = 0, 1
        self.center = WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2
        self.radius = Vector(self.center).magnitude()
        self.threshold = self.radius + 100

    def execute(self, delta_time: float):
        if self.is_actived:
            self.border_width += 500 * delta_time * self.direction
            # CHECK TO REVERSE ANIMATION & TOGGLE.
            if self.direction > 0 and self.border_width >= self.threshold:
                self.direction = -1
                self.toggle()
            # CHECK TO STOP ANIMATION & RESET.
            if self.border_width <= 0:
                self.is_actived = False
                self.border_width, self.direction = 0, 1
            # DRAW ANIMATION.
            pg.draw.circle(self.screen, 'BLACK', self.center,
                           self.radius, int(self.border_width))


class Main:
    def __init__(self):
        # START-UP.
        pg.init()
        self.screen = pg.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pg.display.set_caption('Mario Maker')
        pg.display.set_icon(load_an_image('image/other/icon.png'))
        self.clock = pg.time.Clock()
        # CONTROL CURSOR.
        cursor_image = load_an_image('image/cursors/mouse.png')
        cursor = pg.cursors.Cursor((0, 0), cursor_image)
        pg.mouse.set_cursor(cursor)
        # MAIN OBJECT.
        self.upload_general_data()
        self.editor_active = True
        self.editor = Editor(self.land_tiles, self.switch)
        self.transition = Transition(self.toggle)

    def upload_general_data(self):
        # TERRAIN.
        self.land_tiles = load_folder_dict('image/terrain/land')
        self.water_bot = load_an_image('image/terrain/water/water_bottom.png')
        self.water_top = load_folder_list('image/terrain/water/animation')
        # COIN.
        self.gold = load_folder_list('image/items/gold')
        self.silver = load_folder_list('image/items/silver')
        self.diamond = load_folder_list('image/items/diamond')
        self.particle = load_folder_list('image/items/particle')
        # PALM TREE.
        self.palms = {folder: load_folder_list(f'image/terrain/palm/{folder}')
                      for folder in list(walk('image/terrain/palm'))[0][1]}
        # ENEMY.
        self.spike = load_an_image('image/enemies/spikes/spikes.png')
        self.tooth = {folder: load_folder_list(f'image/enemies/tooth/{folder}')
                      for folder in list(walk('image/enemies/tooth'))[0][1]}
        self.shell = {folder: load_folder_list(f'image/enemies/shell_left/{folder}')
                      for folder in list(walk('image/enemies/shell_left'))[0][1]}
        self.pearl = load_an_image('image/enemies/pearl/pearl.png')
        # PLAYER.
        self.player = {folder: load_folder_list(f'image/player/{folder}')
                       for folder in list(walk('image/player'))[0][1]}
        # CLOUDS.
        self.clouds = load_folder_list('image/clouds')
        # LEVEL MUSIC & SOUND.
        self.sounds = {
            'music': pg.mixer.Sound('audio/SuperHero.ogg'),
            'coin': pg.mixer.Sound('audio/coin.wav'),
            'jump': pg.mixer.Sound('audio/jump.wav'),
            'hit': pg.mixer.Sound('audio/hit.wav')
        }
        # MISSION.
        self.heart = load_an_image('image/other/heart.png')
        self.complete = load_an_image('image/other/complete.png')
        self.success = load_an_image('image/other/success.png')
        self.fail = load_an_image('image/other/fail.png')

    def toggle(self):
        self.editor_active = not self.editor_active
        # RESTART MUSIC OF EDITOR.
        if self.editor_active:
            self.editor.music.play(-1)

    def switch(self, layers: dict[str, dict] = None):
        self.transition.is_actived = True
        # SWITCH FROM EDITOR TO LEVEL.
        if layers:
            self.level = Level(layers, self.switch, {
                'land': self.land_tiles,
                'water_bot': self.water_bot, 'water_top': self.water_top,
                'gold': self.gold, 'silver': self.silver, 'diamond': self.diamond, 'particle': self.particle,
                'palms': self.palms,
                'spike': self.spike, 'tooth': self.tooth, 'shell': self.shell, 'pearl': self.pearl,
                'player': self.player,
                'clouds': self.clouds,
                'heart': self.heart, 'complete': self.complete, 'success': self.success, 'fail': self.fail
            }, self.sounds)

    def run(self):
        while True:
            delta_time = self.clock.tick() / 1000
            # HANDLE THE STATISTIC.
            if self.editor_active:
                self.editor.run(delta_time)
            else:
                self.level.run(delta_time)
            # UPDATE THE FRAME.
            self.transition.execute(delta_time)
            pg.display.update()


if __name__ == '__main__':
    Main().run()
