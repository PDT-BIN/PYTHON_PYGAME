from sys import exit

import pygame as pg
from level import Level
from settings import *


class Game:

    def __init__(self):
        # LOAD ALL SUB-MODULES INTO PROGRAM.
        pg.init()
        # CORE.
        self.screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pg.display.set_caption('Pydew Valley')
        self.clock = pg.time.Clock()
        self.level = Level()

    def run(self):
        while True:
            # EVENT PROCESS.
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                    exit()
            # DELTA TIME STATISTIC.
            delta_time = self.clock.tick() / 1000
            # CORE PROCESS.
            self.level.run(delta_time)
            # WINDOW UPDATE.
            pg.display.update()


if __name__ == '__main__':
    Game().run()
