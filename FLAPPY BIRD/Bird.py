import pygame

class Bird:
    """A class to manage bird object."""
    def __init__(self, FB_game):
        self.setting = FB_game.setting
        self.screen = FB_game.screen
        self.screen_rect = self.screen.get_rect()
        #Bird attributes.
        self.bird_down_image = pygame.transform.scale2x(pygame.image.load('images/bird_downflap.png').convert_alpha())
        self.bird_mid_image = pygame.transform.scale2x(pygame.image.load('images/bird_midflap.png').convert_alpha())
        self.bird_up_image = pygame.transform.scale2x(pygame.image.load('images/bird_upflap.png').convert_alpha())
        self.image_list = [self.bird_down_image, self.bird_mid_image, self.bird_up_image]
        self.image_index = 0
        self.image = self.image_list[self.image_index]
        self.rect = self.image.get_rect(center = (100, self.screen_rect.centery))
        #Co-ordinate X of bird images is used to create movement.
        self.y = 0

    def flap_animation(self):
        """Create the flap effect."""
        self.image_index += 1 if (self.image_index < 2) else -2
        self.image = self.image_list[self.image_index]

    def rotate(self):
        """Create the rotation effect."""
        new_bird = pygame.transform.rotozoom(self.image, -(self.y * 3), 1)
        return new_bird

    def fly_up(self):
        """Make the bird fly up."""
        self.y = 0
        self.y -= 10

    def update(self):
        """Make the bird movement."""
        self.y += self.setting.gravity
        self.rect.centery += int(self.y)

    def reset(self):
        """Reset the position of bird and its movement variable."""
        self.rect.center = (100, self.screen_rect.centery)
        self.y = 0

    def draw(self, bird_image):
        """Draw the bird."""
        self.screen.blit(bird_image, self.rect)