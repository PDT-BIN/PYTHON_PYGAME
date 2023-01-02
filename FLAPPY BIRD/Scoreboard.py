import pygame

class Scoreboard:
    """A class to manage score."""
    def __init__(self, FB_game):
        self.screen = FB_game.screen
        #Score attributes.
        self.high_score = 0
        self.reset_score()
        #Score effects.
        self.text_color = (255, 255, 255)
        self.font = pygame.font.Font('04B_19.ttf', 40)
        #Prepare initial images.
        self.prep_image()

    def reset_score(self):
        """Reset the dynamic attributes."""
        self.score = 0

    def update_score(self):
        """Check if the score is higher than high score."""
        if self.high_score < self.score:
            self.high_score = self.score
            self._prep_high_score()

    def prep_score(self):
        """Turn the score into image."""
        score_str = f'{self.score}'
        self.score_image = self.font.render(score_str, True, self.text_color)
        self.score_rect = self.score_image.get_rect(center = (210, 100))

    def _prep_high_score(self):
        """turn the high score into image."""
        high_score_str = f'High score: {self.high_score}'
        self.high_score_image = self.font.render(high_score_str, True, self.text_color)
        self.high_score_rect = self.high_score_image.get_rect(center = (210, 620))

    def prep_image(self):
        """Prepare initial images."""
        self.prep_score()
        self._prep_high_score()

    def draw(self, status):
        """Draw the scoreboard."""
        self.screen.blit(self.score_image, self.score_rect)
        if not status:
            self.screen.blit(self.high_score_image, self.high_score_rect)