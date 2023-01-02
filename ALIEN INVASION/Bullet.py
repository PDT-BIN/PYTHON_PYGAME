import pygame
from pygame.sprite import Sprite


class Bullet(Sprite):
    """A class to manage bullets fired by the ship."""
    def __init__(self, AI_game):
        """Create a bullet object at the ship's current position."""
        super().__init__()
        #Use the default resource from ALIEN_INVASION.py.
        self.screen = AI_game.screen
        self.setting = AI_game.setting
        self.ship_rect = AI_game.ship.rect
        #Initialize bullet attributes.
        self.image = pygame.image.load('images/Bullet.bmp')
        self.rect = self.image.get_rect()
        #Set up that the bullet appears at the top of the ship.
        self.rect.midbottom = self.ship_rect.midtop
        #Co-Ordinate Y used to move the bullet.
        self.y = float(self.rect.y)

    def update(self):
        """Change the position of bullet on the screen."""
        self.y -= self.setting.bullet_speed
        self.rect.y = self.y


    #Use this codes when you don't want to use bullet image.
    #Bullet setting.
    #self.bullet_width, self.bullet_height = 3, 15
    #self.bullet_color = (0, 128, 255)
    ##Set the dimensions and properties of the button.
    #self.bullet_color = self.setting.bullet_color
    ##Initialize the bullet attributes.
    #self.rect = pygame.Rect(0, 0, self.setting.bullet_width, self.setting.bullet_height)
    ##Set up the original position of bullet on screen.
    #self.rect.midbottom = self.ship_rect.midtop
    #def draw_bullet(self):
    #    """Draw the bullet to the screen."""
    #    pygame.draw.rect(self.screen, self.bullet_color, self.rect)
