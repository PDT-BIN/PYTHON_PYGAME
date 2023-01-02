from pygame import Color


class Board:
    """A class to manage game text."""

    def __init__(self, TG):
        self.screen = TG.screen
        self.setting = TG.setting
        self.status = TG.status
        # GAME MESSAGES.
        self.msg_frame_image = self.setting.FONT.render(
            "NEXT BLOCK", True, Color('BLACK'))
        self.msg_score_image = self.setting.FONT.render(
            "SCORE", True, Color('BLACK'))
        self.msg_frame_rect = self.msg_frame_image.get_rect(x=700, y=25)
        self.msg_score_rect = self.msg_score_image.get_rect(x=80, y=50)
        # GAME STATISTICS.
        self.convert_statistic()

    def draw_message(self):
        """Draw messages to announce game infomations."""
        self.screen.blit(self.msg_frame_image, self.msg_frame_rect)
        self.screen.blit(self.msg_score_image, self.msg_score_rect)

    def draw_statistic(self):
        """Draw statistics to announce player process."""
        self.screen.blit(self.score_image, self.score_rect)
        self.screen.blit(self.level_image, self.level_rect)
        self.screen.blit(self.lines_image, self.lines_rect)

    def convert_statistic(self):
        """Convert statistics into a rendered image."""
        # SCORE.
        self.score_image = self.setting.FONT.render(
            f'{round(self.status.score):_}', True, Color('BLACK'))
        self.score_rect = self.score_image.get_rect(
            midtop=self.msg_score_rect.midbottom)
        # LEVEL.
        self.level_image = self.setting.FONT.render(
            f'LEVEL {self.status.level}', True, Color('BLACK'))
        self.level_rect = self.level_image.get_rect(x=725, y=175)
        # LINES.
        self.lines_image = self.setting.FONT.render(
            f'LINES {self.status.lines}', True, Color('BLACK'))
        self.lines_rect = self.lines_image.get_rect(x=75, y=125)
