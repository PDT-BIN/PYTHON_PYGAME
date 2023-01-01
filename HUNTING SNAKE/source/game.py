from sys import exit

import pygame as pg
from figure import *
from system import *


class Game:
    '''A class to manage game assets and behaviors.'''

    def __init__(self) -> None:
        '''Initialize core attributes.'''
        pg.mixer.pre_init(44100, -16, 2, 512)
        pg.init()
        self.clock = pg.time.Clock()
        # SETTING.
        self.setting = Setting()
        # DISPLAY.
        self.screen = pg.display.set_mode(self.setting.dim)
        pg.display.set_icon(pg.image.load('image/ICON.png').convert_alpha())
        pg.display.set_caption('Hunting Snake')
        # MUSIC FOR THE ENTIRE GAME PROCESS.
        pg.mixer.music.load('audio/MUSIC.wav')
        pg.mixer.music.play(-1)
        # OBJECTS.
        self.__init()

    def __init(self) -> None:
        '''Initialize objects.'''
        # STAGE IMAGES & SOUND EFFECTS.
        self.layer, self.audio = Layer(self.screen), Audio()
        # STATISTICS & STATUSES.
        self.board, self.state = Board(self.screen), State()
        # ENTITIES.
        self.snake = Snake(self.screen)
        self.fruit, self.drink = Fruit(self.screen), Drink(self.screen)
        # BUTTON GROUP.
        self.group = ButtonGroup(self.screen)
        # CUSTOM EVENT.
        self.DRINK_UP, self.SPEED_UP = pg.USEREVENT + 1, pg.USEREVENT + 2
        pg.time.set_timer(self.DRINK_UP, 5_000)
        pg.time.set_timer(self.SPEED_UP, 15_000)

    def run(self) -> None:
        '''Run main loop containing the logic of game.'''
        while True:
            pg.time.delay(self.snake.speed)
            self.__check_event()
            self.__update()
            self.__draw_screen()
            pg.display.update()
            self.clock.tick(self.setting.fps)

# EVENT:
    def __check_event(self) -> None:
        '''Check player & system events.'''
        for event in pg.event.get():
            if event.type == pg.QUIT:
                Game.__quit()
            if event.type == pg.KEYDOWN:
                self.__check_key_event(event.key)
            if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                self.__check_mouse_event()
            if self.state.stage == 'PLAY' and event.type in (self.DRINK_UP, self.SPEED_UP):
                self.__check_custom_event(event.type)

    def __check_key_event(self, key: int) -> None:
        '''Check pressed key.'''
        match key:
            case pg.K_ESCAPE:
                Game.__quit()
            case pg.K_m:
                self.__exec_music()
            case default if self.state.stage == 'PLAY':
                match default:
                    case pg.K_LEFT:
                        self.snake.shifter = 'L'
                    case pg.K_RIGHT:
                        self.snake.shifter = 'R'
                    case pg.K_UP:
                        self.snake.shifter = 'U'
                    case pg.K_DOWN:
                        self.snake.shifter = 'D'

    def __check_mouse_event(self) -> None:
        '''Check mouse click.'''
        match self.state.stage:
            case 'MENU':
                self.__check_menu()
            case 'GUIDE':
                self.__check_guide()
            case 'MODE':
                self.__check_mode()
            case 'RATE':
                self.__check_rate()
            case 'LOST':
                self.__check_lost()

    def __check_custom_event(self, event: int) -> None:
        """Check system event."""
        match event:
            case self.DRINK_UP:
                self.drink.refresh()
            case self.SPEED_UP:
                self.snake.speed -= 5
                self.board.convert_speed(self.snake.speed)

    def __check_menu(self) -> None:
        '''Choices: PLAY/GUIDE/QUIT.'''
        if self.group.is_clicked(form=0, index=0):
            self.state.stage = 'MODE'
        elif self.group.is_clicked(form=0, index=1):
            self.state.stage = 'GUIDE'
        elif self.group.is_clicked(form=0, index=2):
            Game.__quit()

    def __check_guide(self) -> None:
        '''Choices: PREV/NEXT.'''
        if self.group.is_clicked(form=1, index=0):
            self.state.page -= 1
        elif self.group.is_clicked(form=1, index=1):
            self.state.page += 1
        else:
            self.state.page = 0
            self.state.stage = 'MENU'

    def __check_mode(self) -> None:
        '''Choices: FREEDOM/LIMITED.'''
        if self.group.is_clicked(form=2, index=0):
            self.__exec_mode('FREEDOM')
        elif self.group.is_clicked(form=2, index=1):
            self.__exec_mode('LIMITED')
        else:
            self.state.stage = 'MENU'

    def __check_rate(self) -> None:
        '''Choices: SLOW/NORMAL/FAST.'''
        if self.group.is_clicked(form=3, index=0):
            self.__exec_rate(100)
        elif self.group.is_clicked(form=3, index=1):
            self.__exec_rate(75)
        elif self.group.is_clicked(form=3, index=2):
            self.__exec_rate(50)
        else:
            self.state.stage = 'MODE'

    def __check_lost(self) -> None:
        '''Choices: YES/NO.'''
        if self.group.is_clicked(form=4, index=0):
            self.__exec_lost(True)
        elif self.group.is_clicked(form=4, index=1):
            self.__exec_lost(False)

# DRAW:
    def __draw_screen(self) -> None:
        '''Draw screen.'''
        match self.state.stage:
            case 'PLAY':
                self.layer.draw(form=0, index=1)
                self.__draw_entity()
            case 'LOST':
                self.layer.draw(form=3, index=0)
                self.group.draw(form=4)
            case default:
                self.layer.draw(form=0, index=0)
                match default:
                    case 'MENU':
                        self.layer.draw(form=1, index=self.state.voice)
                        self.group.draw(form=0)
                    case 'GUIDE':
                        self.layer.draw(form=2, index=self.state.page)
                        self.group.draw(form=1)
                    case 'MODE':
                        self.group.draw(form=2)
                    case 'RATE':
                        self.group.draw(form=3)

    def __draw_entity(self) -> None:
        '''Draw food, snake & board.'''
        self.fruit.draw()
        self.drink.draw()
        self.snake.draw()
        self.board.draw()

# UPDATE:
    def __update(self) -> None:
        '''Update movement.'''
        if self.state.stage == 'PLAY':
            self.snake.update()
            self.__check_dead()
            self.__check_grow()

    def __check_grow(self) -> None:
        '''Check if the snake is growing.'''
        self.__check_fruit()
        self.__check_drink()

    def __check_dead(self) -> None:
        '''Check if the snake is dead.'''
        if self.snake.is_died(mode=self.state.mode):
            self.audio.play_sound(2)
            self.drink.existed = False
            self.state.stage = 'LOST'
            pg.mouse.set_visible(True)

    def __check_fruit(self) -> None:
        '''Check if the snake ate fruit.'''
        if self.snake.is_ate(self.fruit.rect):
            self.audio.play_sound(0)
            self.__bonus_fruit()
            self.fruit.refresh()

    def __bonus_fruit(self) -> None:
        '''Get bonus from fruits.'''
        award = 2 if self.state.mode == 'LIMITED' else 1
        self.state.score += self.fruit.point + (150 - self.snake.speed) * award
        self.board.convert_score(self.state.score)

    def __check_drink(self) -> None:
        '''Check if the snake drank drink.'''
        if self.drink.existed and self.snake.is_drank(self.drink.rect):
            self.audio.play_sound(1)
            self.__bonus_drink()

    def __bonus_drink(self) -> None:
        '''Get bonus from drinks.'''
        effect = self.drink.affect()
        self.snake.speed += effect[0]
        self.state.score += effect[1]
        self.board.convert_speed(self.snake.speed)
        self.board.convert_score(self.state.score)

# SUPPORTING FUNCTION:
    def __exec_mode(self, value: str) -> None:
        '''Execute FREEDOM/LIMITED choice.'''
        self.state.mode = value
        self.state.stage = 'RATE'

    def __exec_rate(self, value: int) -> None:
        '''Execute SLOW/NORMAL/FAST choice.'''
        self.snake.speed = self.state.rate = value
        self.board.convert_mode(self.state.mode)
        self.board.convert_speed(self.snake.speed)
        self.board.convert_score(self.state.score)
        self.state.stage = 'PLAY'
        pg.mouse.set_visible(False)

    def __exec_lost(self, value: bool) -> None:
        '''Execute YES/NO choice.'''
        self.__exec_reset()
        match value:
            case True:
                self.snake.speed = self.state.rate
                self.board.convert_speed(self.snake.speed)
                self.board.convert_score(self.state.score)
                self.state.stage = 'PLAY'
                pg.mouse.set_visible(False)
            case _:
                self.state.mode, self.state.rate = None, 0
                self.state.stage = 'MENU'

    def __exec_music(self) -> None:
        '''Execute PAUSE/UNPAUSE choice.'''
        self.state.voice = not self.state.voice
        pg.mixer.music.unpause() if self.state.voice else pg.mixer.music.pause()

    def __exec_reset(self) -> None:
        '''Execute RESTART.'''
        self.state.score = 0
        self.snake.refresh()
        self.fruit.refresh()

    @staticmethod
    def __quit() -> None:
        '''Quit game.'''
        pg.quit()
        exit()


if __name__ == '__main__':
    Game().run()
