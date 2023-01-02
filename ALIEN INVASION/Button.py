import pygame


class Button:
    """A class to build button to interact with player."""
    def __init__(self, AI_game, msg, Co_ordinate):
        """Create a button object."""
        #Use the default resource from ALIEN_INVASION.py.
        self.screen = AI_game.screen
        self.screen_rect = AI_game.screen_rect
        #Initialize the message attributes.
        self.text_color = (255, 255, 255)
        self.font = pygame.font.Font('font/04B_19.ttf', 40)
        #Initialize button attributes.
        self.image = pygame.image.load('images/BUTTON_BAR.bmp')
        self.rect = self.image.get_rect()
        #Set up the appointed position of button on screen.
        self.rect.center = Co_ordinate
        #Prepare the initial msg image.
        self._prep_msg(msg)

    def _prep_msg(self, msg):
        """Turn msg into a rendered image."""
        self.msg_image = self.font.render(msg, True, self.text_color)
        self.msg_image_rect = self.msg_image.get_rect()
        #Center the msg on the button.
        self.msg_image_rect.center = self.rect.center

    def draw_button(self):
        """Draw the button to the screen."""
        self.screen.blit(self.image, self.rect)
        self.screen.blit(self.msg_image, self.msg_image_rect)

