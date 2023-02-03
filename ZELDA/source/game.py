from sys import exit

import pygame
from level import Level
from settings import *


class Game:
    def __init__(self):
        # SYSTEM.
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGTH))
        pygame.display.set_caption('Zelda')
        self.clock = pygame.time.Clock()
        self.level = Level()

    def run(self):
        while True:
            # EVENT.
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_m:
                        self.level.toggle_menu()
            # PROCESS.
            self.screen.fill(WATER_COLOR)
            self.level.run()
            # SYSTEM.
            pygame.display.update()
            self.clock.tick(60)


if __name__ == '__main__':
    Game().run()
