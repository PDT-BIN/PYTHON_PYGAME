from pygame.transform import scale
from pygame.image import load


class Dislay:
    """A class to manage displays."""

    def __init__(self, TG):
        self.screen = TG.screen
        self.setting = TG.setting
        # BACKGROUND.
        self.BACKGROUNDS = [scale(load(f'image/BACKGROUND/BG_{i}.png'), (
            self.setting.WIDTH_SCREEN, self.setting.HEIGHT_SCREEN)) for i in range(2)]
        self.BACKGROUNDS_RECT = (0, 0)
        # FOREGROUND.
        self.FOREGROUNDS = list()
        self.FOREGROUNDS.append((scale(
            load('image/FOREGROUND/FG_0.png'), (self.setting.WIDTH_PLAY, self.setting.HEIGHT_PLAY / 3)), (255, 200)))
        # BLOCK FRAME.
        self.FRAMES = list()
        self.FRAMES.append((scale(load('image/FRAME/FRAME_0.png'),
                                  (self.setting.WIDTH_PLAY + 20, self.setting.HEIGHT_PLAY + 10)), (240, 0)))
        self.FRAMES.append(
            (scale(load('image/FRAME/FRAME_1.png'), (200, 100)), (665, 50)))

    def draw_start(self):
        """Draw start display."""
        self.screen.blit(self.BACKGROUNDS[0], self.BACKGROUNDS_RECT)

    def draw_play(self):
        """Draw play displays."""
        self.screen.blit(self.BACKGROUNDS[1], self.BACKGROUNDS_RECT)
        self.screen.blit(self.FRAMES[0][0], self.FRAMES[0][1])
        self.screen.blit(self.FRAMES[1][0], self.FRAMES[1][1])

    def draw_end(self):
        """Draw end display."""
        self.screen.blit(self.FOREGROUNDS[0][0], self.FOREGROUNDS[0][1])
