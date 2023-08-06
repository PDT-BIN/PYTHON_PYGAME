from random import choice
from sys import exit

from game import Game
from preview import Preview
from score import Score
from settings import *


class Main:
    def __init__(self):
        # GENERAL.
        pg.init()
        self.screen = pg.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.clock = pg.time.Clock()
        pg.display.set_caption('Tetris')
        pg.display.set_icon(pg.image.load('image/LOGO.png').convert_alpha())
        # COMPONENT.
        self.game = Game(self.get_next_shape, self.update_score)
        self.score = Score()
        self.preview = Preview()
        # MUSIC.
        pg.mixer.pre_init()
        pg.mixer.music.set_volume(0.1)
        pg.mixer.music.load('audio/MUSIC.wav')
        pg.mixer.music.play(-1)

    def get_next_shape(self) -> str:
        self.preview.preview_shapes.append(choice(list(TETROMINOS)))
        return self.preview.preview_shapes.pop(0)

    def update_score(self, level: int, score: int, lines: int) -> None:
        self.score.level = level
        self.score.score = score
        self.score.lines = lines

    def run(self):
        while True:
            # EVENT.
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                    exit()
            # DISPLAY.
            self.screen.fill(GRAY)
            self.game.run()
            self.score.run()
            self.preview.run()
            # UPDATE.
            pg.display.update()
            self.clock.tick()


if __name__ == '__main__':
    Main().run()
