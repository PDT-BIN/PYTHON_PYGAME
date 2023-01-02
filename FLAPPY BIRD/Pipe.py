import pygame
from pygame.sprite import Sprite

class Pipe(Sprite):
    """A class to manage pipe object."""
    def __init__(self, FB_game):
        super().__init__()
        self.setting = FB_game.setting
        self.screen = FB_game.screen
        #Pipe attributes.
        self.image = pygame.transform.scale2x(pygame.image.load('images/pipe.png').convert_alpha())
        self.rect = self.image.get_rect()

    def update(self):
        """Make the pipe movement."""
        self.rect.centerx -= 5