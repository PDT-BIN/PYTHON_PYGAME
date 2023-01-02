from pygame.image import load
from pygame.transform import scale


class Block:
    """A class to manage block."""
    # BLOCK COLORS.
    COLORS = [
        scale(load(f'image/COLOR/CLR_{i}.png'), (25, 25)) for i in range(8)]

    def __init__(self, TG, character):
        self.screen = TG.screen
        self.setting = TG.setting
        # SHAPE OF BLOCK.
        self.shape = character
        # ROW & COLUMN INDEX FOR SHAPE.
        self.row_idx, self.col_idx = 0, 5

    def __check_boders(self, new_row: int, new_col: int) -> bool:
        """Check if the block touches the boder of play screen."""
        for i, color in enumerate(self.shape):
            if color > 0:
                # ROW & COLUMN INDEX PER BLOCK IN SHAPE.
                col_idx = new_col + i % 4
                row_idx = new_row + i // 4
                if (col_idx < 0 or col_idx >= self.setting.COLUMNS or row_idx >= self.setting.ROWS
                        or self.setting.GIRDS[row_idx * self.setting.COLUMNS + col_idx] > 0):
                    return False
        return True

    def draw_curr(self):
        """Draw current block image."""
        for i, color in enumerate(self.shape):
            if color > 0:
                # CO-ORDINATE PER BLOCK IN SHAPE.
                x = (self.col_idx + i % 4) * self.setting.CELL_SIZE + 250
                y = (self.row_idx + i // 4) * self.setting.CELL_SIZE
                self.screen.blit(Block.COLORS[color], (x, y))

    def draw_next(self):
        """Draw next appearing block image."""
        distance = self.__get_distance(self.shape)
        for i, color in enumerate(self.shape):
            if color > 0:
                # CO-ORDINATE PER BLOCK IN SHAPE.
                x = (i % 4) * self.setting.CELL_SIZE + distance[0]
                y = (i // 4) * self.setting.CELL_SIZE + distance[1]
                self.screen.blit(Block.COLORS[color], (x, y))

    def update(self, ver: int, hor: int) -> bool:
        """Check if current block can move."""
        if self.__check_boders(self.row_idx + ver, self.col_idx + hor):
            self.row_idx += ver
            self.col_idx += hor
            return True
        return False

    def rotate(self):
        """Rotate current block."""
        pre_shape = self.shape.copy()
        for i, color in enumerate(pre_shape):
            self.shape[(2 - (i % 4)) * 4 + (i // 4)] = color

        if not self.__check_boders(self.row_idx, self.col_idx):
            self.shape = pre_shape.copy()

    def __get_distance(self, shape: list) -> tuple[float, float]:
        """Get formatting distance for the next appearing block."""
        if shape[7] > 0:
            return (715, 62.5)
        elif shape[0] == 0 and shape[4] == 0:
            return (715, 75)
        elif shape[9] > 0 or shape[10] > 0:
            return (727.5, 50)
        else:
            return (727.5, 75)
