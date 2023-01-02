import pygame


class Display:
    """A class to manage displays of game."""
    def __init__(self, AI_game):
        #Use the default resource from ALIEN_INVASION.py.
        self.screen = AI_game.screen
        self.screen_rect = AI_game.screen_rect
        self.stats = AI_game.stats
        #Background.
        self.bg_image = pygame.image.load('images/BACKGROUND.bmp')
        self.bg_image_rect = self.bg_image.get_rect(center = self.screen_rect.center)
        #'USER GUIDE' display. (When player clicks the 'ABOUT' button.)
        self.ug_image = pygame.image.load('images/USER_GUIDE.bmp')
        self.ug_image_rect = self.ug_image.get_rect(center = self.screen_rect.center)
        #'GAME OVER' display. (When player has lost.)
        self.go_image = pygame.image.load('images/GAME_OVER.bmp')
        self.go_image_rect = self.go_image.get_rect(center = self.screen_rect.center)
        #Musics and Sounds.
        pygame.mixer.music.load('musics/BACKGROUND_MUSIC.wav')
        self.bullet_sound = pygame.mixer.Sound('musics/BULLET_SOUND.wav')
        #Control flags.
        self.user_guide = False
        self.game_over = False
        self.music = False

    def play_music(self):
        """Play background music."""
        if not self.music and not self.stats.game_active:
            self.music = True
            pygame.mixer.music.play(-1)

    def stop_music(self):
        """Stop background music."""
        if self.music and self.stats.game_active:
            self.music = False
            pygame.mixer.music.stop()

    def play_sound(self, sound_effect):
        """Play sound effect."""
        sound_effect.play()

    def draw_BACKGROUND(self):
        """Draw the background."""
        self.screen.blit(self.bg_image, self.bg_image_rect)
        
    def draw_USER_GUIDE(self):
        """Draw 'USER GUIDE' display."""
        self.screen.blit(self.ug_image, self.ug_image_rect)

    def draw_GAME_OVER(self):
        """Draw 'GAME OVER' display."""
        self.screen.blit(self.go_image, self.go_image_rect)