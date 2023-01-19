import pygame as pg


class Overlay:
    '''Class to manage health of player.'''

    def __init__(self, player):
        # AIM.
        self.player = player
        # CORE.
        self.screen = pg.display.get_surface()
        self.health_image = pg.image.load('image/health.png')
        self.health_width = self.health_image.get_width()

    def display(self):
        '''Display health quantity.'''
        for index in range(self.player.health):
            self.screen.blit(self.health_image,
                             (index * (self.health_width + 5) + 10, 10))
