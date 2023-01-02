import pygame
from pygame.sprite import Sprite


class Alien(Sprite):
    """A class to manage the aliens."""
    def __init__(self, AI_game):
        """Create a alien object."""
        super().__init__()
        #Use the default resource from ALIEN_INVASION.py.
        self.screen = AI_game.screen
        self.setting = AI_game.setting
        self.screen_rect = AI_game.screen_rect
        #Initialize alien attributes.
        self.image = pygame.image.load('images/Alien.bmp')
        self.rect = self.image.get_rect()
        #Co-Ordinate X used to move the alien.
        self.x = float(self.rect.x)

    def update(self):
        """Change the position of alien on the screen."""
        self.x += (self.setting.alien_speed * self.setting.fleet_direction)
        self.rect.x = self.x

    def check_edge(self):
        """Check if any aliens reach the edge of screen."""
        return (self.rect.right >= self.screen_rect.right or self.rect.left <= 0)