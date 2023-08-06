from collections.abc import Callable
from random import choice
from sys import exit

from pygame.math import Vector2
from pygame.sprite import AbstractGroup
from settings import *
from timers import Timer


class Game:
    def __init__(self, get_next_shape: Callable[[], str], update_score: Callable[[int, int, int], None]):
        # MAIN SCREEN.
        self.screen = pg.display.get_surface()
        # GAME DISPLAY.
        self.display = pg.Surface((GAME_WIDTH, GAME_HEIGHT))
        self.place = self.display.get_rect(topleft=(PADDING, PADDING))
        # GRIDLINES DISPLAY.
        self.gridlines = self.display.copy()
        self.gridlines.fill('GREEN')
        self.gridlines.set_colorkey('GREEN')
        self.gridlines.set_alpha(120)
        # GRID DATA.
        self.grid: list[list[Block]] = [
            [None for _ in range(COLUMNS)] for _ in range(ROWS)]
        # INTERACTIVE FUNCTION.
        self.get_next_shape = get_next_shape
        self.update_score = update_score
        # SHARED DATA.
        Tetromino.initialize = self.build
        Tetromino.grid_data = self.grid
        # BLOCK & TETROMINO.
        self.block_group = pg.sprite.Group()
        self.tetromino = Tetromino(choice(list(TETROMINOS)), self.block_group)
        # SPEED CONTROL.
        self.down_speed = UPDATE_START_SPEED
        self.down_speed_faster = self.down_speed * 0.3
        self.is_pressed_down = False
        # TIMER.
        self.timers = {
            # SYSTEM TIMER.
            'BLOCK DOWN': Timer(self.down_speed, True, self.block_down, True),
            # USER TIMER.
            'MOVE': Timer(MOVE_WAIT_TIME),
            'ROTATE': Timer(ROTATE_WAIT_TIME)
        }
        # SCORE CONTROL.
        self.current_level = 1
        self.current_score = 0
        self.current_lines = 0
        # SOUND.
        self.land_sound = pg.mixer.Sound('audio/LANDING.wav')

    # SYSTEM & USER EVENT.
    def block_down(self) -> None:
        self.tetromino.y_move()

    def input(self) -> None:
        keys = pg.key.get_pressed()
        # MOVE.
        if not self.timers['MOVE'].is_actived:
            if keys[pg.K_LEFT]:
                self.tetromino.x_move(-1)
                self.timers['MOVE'].activate()
            if keys[pg.K_RIGHT]:
                self.tetromino.x_move(1)
                self.timers['MOVE'].activate()
        # ROTATE.
        if not self.timers['ROTATE'].is_actived:
            if keys[pg.K_UP]:
                self.tetromino.rotate()
                self.timers['ROTATE'].activate()
        # SPEED UP.
        if not self.is_pressed_down and keys[pg.K_DOWN]:
            self.is_pressed_down = True
            self.timers['BLOCK DOWN'].duration = self.down_speed_faster
        # SLOW DOWN.
        if self.is_pressed_down and not keys[pg.K_DOWN]:
            self.is_pressed_down = False
            self.timers['BLOCK DOWN'].duration = self.down_speed

    # BLOCK CONTROL.
    def build(self) -> None:
        self.land_sound.play()
        self.check_game_over()
        self.destroy()
        self.tetromino = Tetromino(self.get_next_shape(), self.block_group)

    def destroy(self) -> None:
        # DELETE ALL ROWS THAT FULL OF BLOCKS.
        if milestones := [index for index, data in enumerate(self.grid) if all(data)]:
            for milestone in milestones:
                # BREAK THE LINK BETWEEN BLOCK & GROUP.
                for block in self.grid[milestone]:
                    block.kill()
                # SHIFT ALL BLOCKS ABOVE DOWNWARD.
                for data in self.grid[:milestone]:
                    for block in data:
                        if block:
                            block.pos.y += 1
            # RE-BUILD GRID DATA IN GAME CLASS.
            self.grid = [
                [None for _ in range(COLUMNS)] for _ in range(ROWS)]
            for block in self.block_group:
                self.grid[int(block.pos.y)][int(block.pos.x)] = block
            # RE-LINK GRID DATA IN TETROMINO CLASS.
            Tetromino.grid_data = self.grid
            # UPDATE SCORE.
            self.calculate_score(len(milestones))

    def calculate_score(self, lines: int) -> None:
        self.current_lines += lines
        self.current_score += SCORE_DATA[lines] * self.current_level
        # LEVEL UP.
        if self.current_lines / 10 > self.current_level:
            self.current_level += 1
            # SPEED UP.
            self.down_speed *= 0.75
            self.down_speed_faster = self.down_speed * 0.3
            self.timers['BLOCK DOWN'].duration = self.down_speed
        # UPDATE SCORE.
        self.update_score(
            self.current_level, self.current_score, self.current_lines)

    def check_game_over(self):
        for block in self.tetromino.blocks:
            if block.pos.y == 0:
                exit()

    def update_timers(self) -> None:
        for timer in self.timers.values():
            timer.update()

    def draw_gridlines(self) -> None:
        for col_idx in range(1, COLUMNS):
            x_pos = col_idx * CELL_SIZE
            pg.draw.line(self.gridlines, LINE_COLOR,
                         (x_pos, 0), (x_pos, GAME_HEIGHT))
        for row_idx in range(1, ROWS):
            y_pos = row_idx * CELL_SIZE
            pg.draw.line(self.gridlines, LINE_COLOR,
                         (0, y_pos), (GAME_WIDTH, y_pos))
        self.display.blit(self.gridlines, (0, 0))

    def run(self) -> None:
        # GET USER INPUT.
        self.input()
        # UPDATE TIMERS.
        self.update_timers()
        # UPDATE BLOCKS.
        self.block_group.update()
        # FILL DISPLAY.
        self.display.fill(GRAY)
        # DRAW BLOCKS.
        self.block_group.draw(self.display)
        # DRAW GRIDLINES.
        self.draw_gridlines()
        # DRAW DISPLAY.
        self.screen.blit(self.display, self.place)
        # DRAW BORDER.
        pg.draw.rect(self.screen, LINE_COLOR, self.place, 2, 2)


class Block(pg.sprite.Sprite):
    def __init__(self, groups: AbstractGroup, position: tuple[int, int], color: str):
        super().__init__(groups)
        # IMAGE.
        self.image = pg.Surface((CELL_SIZE, CELL_SIZE))
        self.image.fill(color)
        # PLACE.
        self.pos = Vector2(position) + BLOCK_OFFSET
        self.rect = self.image.get_rect(topleft=self.pos * CELL_SIZE)

    def update(self) -> None:
        self.rect.topleft = self.pos * CELL_SIZE

    def rotate(self, pivot_position: Vector2) -> Vector2:
        # GET THE DISTANCE VECTOR.
        distance = self.pos - pivot_position
        # GET THE ROTATED POSITION.
        return pivot_position + distance.rotate(90)

    def y_collide(self, y_pos: int, grid_data: list[list[int]]) -> bool:
        return y_pos >= ROWS or y_pos >= 0 and grid_data[y_pos][int(self.pos.x)]

    def x_collide(self, x_pos: int, grid_data: list[list[int]]) -> bool:
        return not 0 <= x_pos < COLUMNS or grid_data[int(self.pos.y)][x_pos]


class Tetromino:
    # SHARED DATA.
    grid_data: list[list[Block]]
    initialize: Callable[[], None]

    def __init__(self, key: str, group: AbstractGroup):
        # BLOCK INFORMATION.
        self.style = key
        self.shape = TETROMINOS[key]['shape']
        color = TETROMINOS[key]['color']
        # BUILD BLOCK.
        self.blocks = [Block(group, pos, color) for pos in self.shape]

    def fill_data(self) -> None:
        for block in self.blocks:
            Tetromino.grid_data[int(block.pos.y)][int(block.pos.x)] = block
        Tetromino.initialize()

    def y_move(self) -> None:
        if not self.y_move_collide():
            for block in self.blocks:
                block.pos.y += 1
        else:
            self.fill_data()

    def x_move(self, step: int) -> None:
        if not self.x_move_collide(step):
            for block in self.blocks:
                block.pos.x += step

    def y_move_collide(self) -> bool:
        for block in self.blocks:
            if block.y_collide(int(block.pos.y + 1), Tetromino.grid_data):
                return True

    def x_move_collide(self, step: int) -> bool:
        for block in self.blocks:
            if block.x_collide(int(block.pos.x + step), Tetromino.grid_data):
                return True

    def rotate(self) -> None:
        if self.style != 'O':
            # GET THE POSITION OF PIVOT BLOCK IN TETROMINO.
            pivot_pos = self.blocks[0].pos
            # EXECUTE ROTATION.
            new_shape = [block.rotate(pivot_pos) for block in self.blocks]
            # CHECK COLLISION OF NEW SHAPE.
            for pos in new_shape:
                # HORIZONTAL & VERTICAL.
                if not 0 <= int(pos.x) < COLUMNS or int(pos.y) >= ROWS:
                    return
                # EXISTED BLOCK.
                if Tetromino.grid_data[int(pos.y)][int(pos.x)]:
                    return
            # RE-BUILD THE TETROMINO WITH NEW SHAPE.
            for block, new_pos in zip(self.blocks, new_shape):
                block.pos = new_pos
