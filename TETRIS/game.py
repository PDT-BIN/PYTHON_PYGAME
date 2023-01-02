from random import choice, randint
from sys import exit

import pygame as pg

from Block import Block
from Board import Board
from Button import Button
from Display import Dislay
from Music import Music
from Setting import Setting
from Status import Status


class Tetris:
    """A class to manage behaviors and asserts."""

    def __init__(self):
        pg.mixer.pre_init(44100, -16, 2, 512)
        pg.init()
        # SET UP FOR SETTINGS.
        self.clock = pg.time.Clock()
        self.setting = Setting()
        # SET UP FOR SCREEN.
        self.screen = pg.display.set_mode(
            (self.setting.WIDTH_SCREEN, self.setting.HEIGHT_SCREEN))
        self.screen_rect = self.screen.get_rect()
        pg.display.set_caption("Tetris Game")
        # SET UP FOR SPECIAL EVENTS.
        self.BLOCK_DOWN = pg.USEREVENT + 1
        pg.time.set_timer(self.BLOCK_DOWN, 300)
        pg.key.set_repeat(1, 100)
        # SET UP FOR STATUS.
        self.status = Status()
        # SET UP FOR BOARD.
        self.board = Board(self)
        # SET UP FOR DISPLAY.
        self.display = Dislay(self)
        # SET UP FOR SOUND.
        self.sound = Music(self)
        # SET UP FOR BLOCKS.
        self.curr_block = Block(self, choice(self.setting.CHARACTERS).copy())
        self.next_block = Block(self, choice(self.setting.CHARACTERS).copy())
        # SET UP FOR CHOICE BUTTONS.
        self.choice_continue = Button(
            self, 'CONTINUE', 'BLACK', 2, (300, 100), (290, 200))
        self.choice_restart = Button(
            self, 'RESTART', 'BLACK',  1, (300, 100), (290, 300))
        self.choice_home = Button(
            self, 'HOME', 'BLACK',  0, (300, 100), (290, 400))
        self.choice_yes = Button(self, 'YES', 'BLUE', 2, (150, 50), (250, 425))
        self.choice_no = Button(self, 'NO', 'RED', 1, (150, 50), (475, 425))
        # SET UP FOR MAIN BUTTONS.
        self.button_play = Button(
            self, 'PLAY', 'WHITE', 0, (200, 100), (347.5, 300))
        self.button_continue = Button(
            self, 'CONTINUE', 'WHITE', 0, (200, 100), (347.5, 400))
        self.button_challenge = Button(
            self, 'CHALLENGE', 'WHITE', 0, (200, 100), (347.5, 500))
        self.button_quit = Button(
            self, 'QUIT', 'WHITE', 0, (200, 100), (347.5, 600))

    def run_game(self):
        """Run the main loop."""
        while True:
            pg.time.delay(100)
            self.__check_event()
            self.__draw_screen()
            pg.display.flip()
            self.clock.tick(60)

    def __check_event(self):
        """Check events."""
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.__quit()
            if (self.status.game_active and not self.status.pause_flag) and event.type == self.BLOCK_DOWN:
                self.__check_block_event()
            if event.type == pg.MOUSEBUTTONDOWN:
                self.__check_mouse_event()
            if event.type == pg.KEYDOWN:
                self.__check_key_event(event.key)

    def __check_block_event(self):
        """Check block down events."""
        if not self.curr_block.update(self.status.speed, 0):
            self.__load_into_girds()
            if not self.__check_game_over():
                self.__break_lines()
                self.__load_blocks()

    def __check_game_over(self) -> bool:
        """Check if the current block can't move from start."""
        if self.curr_block.row_idx == 0:
            self.sound.play_sound(1)
            self.__restart()
            self.status.end_flag = True
            self.status.game_active = False
            return True
        return False

    def __check_mouse_event(self):
        """Check mouse events."""
        self.__check_start_event()
        self.__check_pause_event()
        self.__check_end_event()

    def __check_start_event(self):
        """Check if PLAY, GUIDE or QUIT button is clicked."""
        if not (self.status.game_active or self.status.end_flag):
            self.__check_play_button()
            self.__check_continue_button()
            self.__check_challenge_button()
            self.__check_quit_button()

    def __check_play_button(self):
        """Check if PLAY button is clicked."""
        if self.button_play.is_clicked():
            self.__restart()
            self.status.challenge_flag = False
            self.status.game_active = True

    def __check_continue_button(self):
        """Check if CONTINUE button is clicked."""
        if self.button_continue.is_clicked():
            self.status.game_active = True

    def __check_challenge_button(self):
        """Check if CHALLENGE button is clicked."""
        if self.button_challenge.is_clicked():
            self.__restart()
            self.__random_block()
            self.status.challenge_flag = True
            self.status.game_active = True

    def __check_quit_button(self):
        """Check if QUIT button is clicked."""
        if self.button_quit.is_clicked():
            self.__quit()

    def __check_pause_event(self):
        """Check if CONTINUE or RESTART button is clicked."""
        if self.status.pause_flag:
            if self.choice_continue.is_clicked():
                self.status.pause_flag = False
            elif self.choice_restart.is_clicked():
                self.__restart()
                self.status.pause_flag = False
                if self.status.challenge_flag:
                    self.__random_block()
            elif self.choice_home.is_clicked():
                self.status.pause_flag = False
                self.status.game_active = False

    def __check_end_event(self):
        """Check if YES or NO button is clicked."""
        if self.status.end_flag:
            if self.choice_yes.is_clicked():
                self.status.end_flag = False
                self.status.game_active = True
                if self.status.challenge_flag:
                    self.__random_block()
            elif self.choice_no.is_clicked():
                self.status.end_flag = False
                self.status.challenge_flag = False

    def __check_key_event(self, key):
        """Check key down events."""
        if not (self.status.pause_flag or self.status.end_flag) and key == pg.K_m:
            self.sound.play_music()
        if self.status.game_active:
            if key == pg.K_p:
                self.status.pause_flag = not self.status.pause_flag
            self.__check_movement_key(key)

    def __check_movement_key(self, key):
        """Check if movement keys are clicked."""
        if not self.status.pause_flag:
            if key == pg.K_LEFT:
                self.curr_block.update(0, -self.status.speed)
            if key == pg.K_RIGHT:
                self.curr_block.update(0, self.status.speed)
            if key == pg.K_DOWN:
                self.curr_block.update(self.status.speed, 0)
            if key == pg.K_SPACE:
                self.curr_block.rotate()

    def __random_block(self):
        """Random blocks for challenge mode."""
        [self.setting.GIRDS.insert(randint(75, 375), randint(1, 7))
         for i in range(5)]

    def __restart(self):
        """Restart game."""
        self.status.reset_statistic()
        self.board.convert_statistic()
        self.__clear_girds()
        self.__refresh_blocks()

    def __quit(self):
        """Quit game."""
        pg.quit()
        exit()

    def __draw_screen(self):
        """Draw game screen."""
        if self.status.game_active and not self.status.pause_flag:
            self.__draw_play_display()
        elif self.status.pause_flag:
            self.__draw_pause_display()
        elif self.status.end_flag:
            self.__draw_end_display()
        else:
            self.__draw_start_display()
        self.sound.draw_speaker()

    def __draw_play_display(self):
        """Draw play display."""
        self.display.draw_play()
        self.__draw_girds()
        self.board.draw_message()
        self.board.draw_statistic()
        self.curr_block.draw_curr()
        self.next_block.draw_next()

    def __draw_start_display(self):
        """Draw menu display."""
        self.display.draw_start()
        self.button_play.draw()
        self.button_continue.draw()
        self.button_challenge.draw()
        self.button_quit.draw()

    def __draw_pause_display(self):
        """Draw pause display."""
        self.choice_continue.draw()
        self.choice_restart.draw()
        self.choice_home.draw()

    def __draw_end_display(self):
        """Draw game over display."""
        self.display.draw_end()
        self.choice_yes.draw()
        self.choice_no.draw()

    def __refresh_blocks(self):
        """Refresh blocks."""
        self.curr_block = Block(self, choice(self.setting.CHARACTERS).copy())
        self.next_block = Block(self, choice(self.setting.CHARACTERS).copy())

    def __load_blocks(self):
        """Change blocks."""
        self.curr_block = self.next_block
        self.next_block = Block(self, choice(
            self.setting.CHARACTERS).copy())

    def __break_lines(self):
        """Break lines filled up with blocks."""
        for row in range(self.setting.ROWS):
            beg_idx = row * self.setting.COLUMNS
            for column in range(self.setting.COLUMNS):
                cur_idx = beg_idx + column
                if self.setting.GIRDS[cur_idx] == 0:
                    break
            else:
                del self.setting.GIRDS[beg_idx: cur_idx + 1]
                self.setting.GIRDS[0: 0] = [0] * self.setting.COLUMNS
                self.status.increase_score()
                self.board.convert_statistic()
                self.sound.play_sound(0)

    def __draw_girds(self):
        """Draw blocks loaded into girds."""
        for i, color in enumerate(self.setting.GIRDS):
            if color > 0:
                x = i % self.setting.COLUMNS * self.setting.CELL_SIZE + 250
                y = i // self.setting.COLUMNS * self.setting.CELL_SIZE
                self.screen.blit(Block.COLORS[color], (x, y))

    def __load_into_girds(self):
        """Load block touching the bottom of screen into girds."""
        for i, color in enumerate(self.curr_block.shape):
            if color > 0:
                self.setting.GIRDS[(self.curr_block.row_idx + i // 4) *
                                   self.setting.COLUMNS + (self.curr_block.col_idx + i % 4)] = color

    def __clear_girds(self):
        """Clear all blocks in girds."""
        self.setting.GIRDS = [0] * self.setting.COLUMNS * self.setting.ROWS


if __name__ == '__main__':
    TG = Tetris()
    TG.run_game()
