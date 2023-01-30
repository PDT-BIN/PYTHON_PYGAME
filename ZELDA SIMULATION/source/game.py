from sys import exit

import pygame as pg
from level import Level
from settings import *


class Game:

    def __init__(self):
        # SYSTEM.
        pg.init()
        self.screen = pg.display.set_mode((WIDTH, HEIGTH))
        pg.display.set_caption('Zelda Simulation')
        self.clock = pg.time.Clock()
        self.level = Level()

    def run(self):
        while True:
            # EVENT.
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                    exit()
            # HANDLE.
            self.screen.fill('BLACK')
            self.level.run()
            # SYSTEM.
            pg.display.update()
            self.clock.tick(60)


if __name__ == '__main__':
    Game().run()
