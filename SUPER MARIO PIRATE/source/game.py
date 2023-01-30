from sys import exit

import pygame
from level import Level
from overworld import Overworld
from settings import *
from ui import UI


# CONTROLLER.
class Game:

    def __init__(self):
        # CORE.
        self.MAX_LEVEL = 0
        self.MAX_HEALTH, self.cur_health = 100, 100
        self.coins = 0
        # SOUND EFFECT.
        self.music_overworld = pygame.mixer.Sound('audio/overworld_music.wav')
        self.music_level = pygame.mixer.Sound('audio/level_music.wav')
        # USER INTERFACE.
        self.ui = UI()
        # OVERWORLD.
        self.overworld = Overworld(0, self.MAX_LEVEL, self.load_level)
        self.status = 'OVERWORLD'
        self.music_overworld.play(-1)

    def load_level(self, level: int):
        self.level = Level(level, self.load_overworld,
                           self.update_coins, self.update_health)
        self.status = 'LEVEL'
        # SWITCH MUSIC.
        self.music_overworld.stop()
        self.music_level.play(-1)

    def load_overworld(self, level: int, unlocked_level: int):
        if self.MAX_LEVEL < unlocked_level:
            self.MAX_LEVEL = unlocked_level
        self.overworld = Overworld(level, self.MAX_LEVEL, self.load_level)
        self.status = 'OVERWORLD'
        # SWITCH MUSIC.
        self.music_level.stop()
        self.music_overworld.play(-1)

    def update_coins(self, quantity: int):
        self.coins += quantity

    def update_health(self, quantity: int):
        self.cur_health += quantity

    def check_game_over(self):
        if self.cur_health <= 0:
            # RESTART.
            self.cur_health, self.coins = self.MAX_HEALTH, 0
            # BACK TO OVERWORLD.
            self.overworld = Overworld(0, 0, self.load_level)
            self.status = 'OVERWORLD'
            # SWITCH MUSIC.
            self.music_level.stop()
            self.music_overworld.play(-1)

    def run(self):
        if self.status == 'OVERWORLD':
            self.overworld.run()
        else:
            self.level.run()
            self.ui.run(self.cur_health, self.MAX_HEALTH, self.coins)
            self.check_game_over()


# DISPLAY
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Super Mario Pirate')
pygame.display.set_icon(pygame.image.load('image/character/hat.png'))

# SYSTEM.
clock = pygame.time.Clock()
system = Game()

# MAIN.
while True:
    # EVENT.
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
    # HANDLE.
    system.run()
    # UPDATE.
    pygame.display.update()
    clock.tick(60)
