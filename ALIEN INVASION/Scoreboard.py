import pygame

from Ship import LifePoint


class Scoreboard:
    """A class to manage the score of player."""
    def __init__(self, AI_game):
        """Create a scoreboard object."""
        #Use the default resource from ALIEN_INVASION.py.
        self.screen = AI_game.screen
        self.setting = AI_game.setting
        self.stats = AI_game.stats
        self.screen_rect = AI_game.screen_rect
        #Initialize score attributes.
        self.text_color = (30, 30, 30)
        self.font = pygame.font.Font('font/04B_19.ttf', 25)
        #Read the highest_score from file.
        self._read_score()
        #Prepare the inital images.
        self._prep_life_points()
        self._prep_bar_images()
        self.prep_images()

    def save_score(self):
        """Save the highest score to a file."""
        with open('Score.txt', 'w') as file_object:
            file_object.write(str(self.stats.highest_score))

    def _read_score(self):
        """Read the highest score from file to the game statistic."""
        with open('Score.txt', 'r') as file_object:
            self.stats.highest_score = int(file_object.read())

    def check_highest_score(self):
        """Record the score if the highest score was defeated."""
        self.stats.highest_score = max(self.stats.score, self.stats.highest_score)

    def _prep_life_points(self):
        """Create a life points object to show the player how many ship they have."""
        self.life_points = []
        for life_point_number in range(self.stats.life_points):
            life_point = LifePoint()
            #Put the life point on the left of the screen.
            life_point.rect.topleft = (10 + (life_point.rect.width * life_point_number), 10)
            #Add a life point element to the life point list.
            self.life_points.append(life_point)

    def prep_highest_score(self):
        """Turn the highest score into a rendered image."""
        rounded_highest_score = round(self.stats.highest_score)
        highest_score_str = "{:,}".format(rounded_highest_score)
        self.highest_score_image = self.font.render(highest_score_str, True, self.text_color)
        self.highest_score_image_rect = self.highest_score_image.get_rect()
        #Put the highest score in the center of highest score bar image.
        self.highest_score_image_rect.center = self.highest_score_bar_image_rect.center

    def prep_score(self):
        """Turn the score into a rendered image."""
        rounded_score = round(self.stats.score)
        score_str = "{:,}".format(rounded_score)
        self.score_image = self.font.render(score_str, True, self.text_color)
        self.score_image_rect = self.score_image.get_rect()
        #Put the score in the center of score bar image
        self.score_image_rect.center = self.score_bar_image_rect.center

    def prep_level(self):
        """Turn the level into a rendered image."""
        level_str = "LV " + str(self.stats.level)
        self.level_image = self.font.render(level_str, True, self.text_color)
        self.level_image_rect = self.level_image.get_rect()
        #Put the level image below the score.
        self.level_image_rect.midtop = self.score_image_rect.midbottom

    def prep_images(self):
        """Prepare (starting) images for the game."""
        self.prep_score()
        self.prep_highest_score()
        self.prep_level()

    def _prep_bar_images(self):
        """Prepare the bar images for score and highest score."""
        #Score bar.
        self.score_bar_image = pygame.image.load('images/SCORE_BAR.bmp')
        self.score_bar_image_rect = self.score_bar_image.get_rect()
        self.score_bar_image_rect.topright = self.screen_rect.topright
        #Highest score bar.
        self.highest_score_bar_image = pygame.image.load('images/HIGHEST_SCORE_BAR.bmp')
        self.highest_score_bar_image_rect = self.highest_score_bar_image.get_rect()
        self.highest_score_bar_image_rect.midtop = self.screen_rect.midtop

    def _draw_bar(self):
        """Draw the bar images."""
        self.screen.blit(self.score_bar_image, self.score_bar_image_rect)
        self.screen.blit(self.highest_score_bar_image, self.highest_score_bar_image_rect)

    def _draw_life_points(self):
        """Draw the life points."""
        for life_point_number in range(self.stats.life_points):
            self.screen.blit(self.life_points[life_point_number].alive_image, self.life_points[life_point_number].rect)
        for life_point_number in range(self.stats.life_points, self.setting.life_limit):
            self.screen.blit(self.life_points[life_point_number].death_image, self.life_points[life_point_number].rect)

    def draw_scoreboard(self):
        """Draw the information about scoreboard to the screen."""
        self._draw_bar()
        self.screen.blit(self.score_image, self.score_image_rect)
        self.screen.blit(self.highest_score_image, self.highest_score_image_rect)
        self.screen.blit(self.level_image, self.level_image_rect)
        self._draw_life_points()