import pygame

class Display:
    """A class to manage game displays."""
    def __init__(self, FB_game):
        #Set up for background.
        self.screen = FB_game.screen
        self.screen_rect = self.screen.get_rect()
        self.bg_image = pygame.transform.scale2x(pygame.image.load('images/background.png').convert_alpha())
        self.bg_rect = self.bg_image.get_rect(center = (self.screen_rect.center))
        #Set up for USER GUIDE display.
        self.ug_image = pygame.transform.scale2x(pygame.image.load('images/user_guide.png').convert_alpha())
        self.ug_rect = self.ug_image.get_rect(center = (self.screen_rect.center))
        #Set up for GAME OVER display.
        self.go_image = pygame.transform.scale2x(pygame.image.load('images/game_over.png').convert_alpha())
        self.go_rect = self.go_image.get_rect(center = (self.screen_rect.centerx, 288))
        #Control flag.
        self.game_active = False
        self.game_over = False
        #Sound.
        self.flap_sound = pygame.mixer.Sound('sounds/flap_sound.wav')
        self.hit_sound = pygame.mixer.Sound('sounds/hit_sound.wav')
        self.point_sound = pygame.mixer.Sound('sounds/point_sound.wav')

    def draw_BACKGROUND(self):
        """Draw the background of game."""
        self.screen.blit(self.bg_image, self.bg_rect)

    def draw_USERGUIDE(self):
        """Draw the USERGUIDE display."""
        self.screen.blit(self.ug_image, self.ug_rect)

    def draw_GAMEOVER(self):
        """Draw the GAMEOVER display."""
        self.screen.blit(self.go_image, self.go_rect)
