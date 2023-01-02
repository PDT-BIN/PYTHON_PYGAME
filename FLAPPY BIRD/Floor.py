import pygame

class Floor:
    """A class to mange the floor of game."""
    def __init__(self, FB_game):
        self.screen = FB_game.screen
        self.screen_width = self.screen.get_rect().width
        #Floor attributes.
        self.image = pygame.transform.scale2x(pygame.image.load('images/floor.png').convert_alpha())
        #Co-ordinate X of the floor image is used to create movement.
        self.x = 0

    def update(self):
        """Make the floor movement."""
        self.x -= 1
        if self.x == -self.screen_width:
            self.x = 0

    def draw(self):
        """Draw the floor."""
        self.screen.blit(self.image, (self.x, 650))
        self.screen.blit(self.image, (self.x + self.screen_width, 650))