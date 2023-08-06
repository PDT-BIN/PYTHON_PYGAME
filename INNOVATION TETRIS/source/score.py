from os.path import join

from settings import *


class Score:
    def __init__(self) -> None:
        # MAIN SCREEN.
        self.screen = pg.display.get_surface()
        # SCORE DISPLAY.
        size = SIDEBAR_WIDTH, GAME_HEIGHT * SCORE_HEIGHT_FRACTION - PADDING
        offset = WINDOW_WIDTH - PADDING, WINDOW_HEIGHT - PADDING
        self.display = pg.Surface(size)
        self.place = self.display.get_rect(bottomright=offset)
        # FONT.
        self.font = pg.font.Font(join('font', 'RUSSO_ONE.ttf'), 28)
        # SCORE.
        self.FRAGMENT_POSITIONS = self.display.get_width() / 2, self.display.get_height() / 3
        self.level = 1
        self.score = 0
        self.lines = 0

    def draw(self, position: tuple[int, int], content: str) -> None:
        surface = self.font.render(content, True, 'WHITE')
        place = surface.get_rect(center=position)
        self.display.blit(surface, place)

    def run(self) -> None:
        self.display.fill(GRAY)
        for index, content in enumerate(
                (f'SCORE: {self.score}', f'LEVEL: {self.level}', f'LINES: {self.lines}')):
            x = self.FRAGMENT_POSITIONS[0]
            y = self.FRAGMENT_POSITIONS[1] / 2 + \
                index * self.FRAGMENT_POSITIONS[1]
            self.draw((x, y), content)
        self.screen.blit(self.display, self.place)
        pg.draw.rect(self.screen, LINE_COLOR, self.place, 2, 2)
