from pygame.font import Font


class Setting:
    """A class to manage settings."""

    def __init__(self):
        # LETTER FONT.
        self.FONT = Font('font/04B_19.ttf', 25)
        # ROW & COLUMN QUANTITY OF PLAY SCREEN.
        self.ROWS, self.COLUMNS = 30, 15
        self.CELL_SIZE = 25
        # PLAY SCREEN.
        self.WIDTH_PLAY = self.COLUMNS * self.CELL_SIZE
        self.HEIGHT_PLAY = self.ROWS * self.CELL_SIZE
        # GAME SCREEN.
        self.WIDTH_SCREEN = self.WIDTH_PLAY + 20 + 500
        self.HEIGHT_SCREEN = self.HEIGHT_PLAY + 10
        # BLOCK GIRDS.
        self.GIRDS = [0] * self.COLUMNS * self.ROWS
        # BLOCK SHAPES.
        self.CHARACTERS = [[0, 1, 1, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # O
                           [0, 0, 0, 0, 2, 2, 2, 2, 0, 0, 0, 0, 0, 0, 0, 0],  # I
                           [0, 0, 0, 0, 3, 3, 3, 0, 0, 0, 3, 0, 0, 0, 0, 0],  # J
                           [0, 0, 4, 0, 4, 4, 4, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # L
                           [0, 5, 5, 0, 5, 5, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # S
                           [6, 6, 0, 0, 0, 6, 6, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # Z
                           [0, 0, 0, 0, 7, 7, 7, 0, 0, 7, 0, 0, 0, 0, 0, 0]]  # T
