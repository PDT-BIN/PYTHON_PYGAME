from collections.abc import Callable

import pygame as pg
from player import Player
from settings import SCREEN_HEIGHT, SCREEN_WIDTH


class Transistion:

    def __init__(self, player: Player, reset: Callable[[], None]):
        # CORE.
        self.screen = pg.display.get_surface()
        self.image = pg.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.color, self.speed = 255, -2
        self.player = player
        # INTERACTION.
        self.reset = reset

    def play(self):
        self.color += self.speed
        # COLOR CONSTRAINTS.
        if self.color < 0:
            self.color = 0
            self.speed *= -1
            # 1. RESET DAY.
            self.reset()
            self.player.status = 'down_idle'
        elif self.color > 255:
            self.color = 255
            # 2. WAKE UP PLAYER.
            self.player.is_sleeping = False
            # 3. RESET THE SPEED.
            self.speed = -2
        self.image.fill((self.color, self.color, self.color))
        self.screen.blit(self.image, (0, 0), special_flags=pg.BLEND_RGBA_MULT)
