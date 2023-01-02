import pygame


class LifePoint:
    """A class to manage life points."""
    def __init__(self):
        """Create a life point object."""
        #Initialize life point attributes.
        self.alive_image = pygame.image.load('images/Alive_Point.bmp')
        self.death_image = pygame.image.load('images/Death_Point.bmp')
        self.rect = self.alive_image.get_rect()

class Ship:
    """A class to manage the ship."""
    def __init__(self, AI_game):
        """Create a ship object."""
        #Use the default resource from ALIEN_INVASION.py.
        self.screen = AI_game.screen
        self.setting = AI_game.setting
        self.screen_rect = AI_game.screen_rect
        #Initialize ship attributes.
        self.image = pygame.image.load('images/Ship.png').convert_alpha()
        self.rect = self.image.get_rect()
        #Set up that the ship appears in the middle of the bottom of the screen.
        self.rect.midbottom = self.screen_rect.midbottom
        #Co-Ordinate X used to move the ship.
        self.x = float(self.rect.x)
        #Movement flags.
        self.moving_left = False
        self.moving_right = False

    def update(self):
        """Manage the position of ship."""
        if self.moving_left and self.rect.left > 0:
            self.x -= self.setting.ship_speed
        if self.moving_right and self.rect.right < self.screen_rect.right:
            self.x += self.setting.ship_speed
        self.rect.x = self.x

    def center_ship(self):
        """Reset to the orginal position of the ship."""
        self.rect.midbottom = self.screen_rect.midbottom
        self.x = float(self.rect.x)

    def draw_ship(self):
        """Draw the ship at its current position."""
        self.screen.blit(self.image, self.rect)
