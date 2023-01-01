from pygame import Surface
from pygame.font import Font


class Board:
    '''A class to manage statistics display.'''

    def __init__(self, screen: Surface) -> None:
        '''Initialize core attributes.'''
        self.__screen = screen
        self.__font = Font('font/04B_19.ttf', 20)
        # SPEED LEVEL.
        self.__levels = (('MASTER', '#DC143C'), ('FAST', '#FF6347'),
                         ('NORMAL', '#DAA520'), ('SLOW', '#7FFF00'), ('AMATEUR', '#7FFFD4'))
        # IMAGE CONTAINER.
        self.__labels = tuple((surf := self.__render(text, '#FFE4C4'), surf.get_rect(x=x_pos, y=5))
                              for text, x_pos in (('MODE: ', 355), ('SPEED', 725), ('SCORE: ', 5)))
        self.__values = [None] * len(self.__labels)

    def convert_mode(self, mode: str) -> None:
        '''Convert mode into image.'''
        self.__values[0] = (surf := self.__render(mode, '#87CEFA'),
                            surf.get_rect(midleft=self.__labels[0][1].midright))

    def convert_speed(self, speed: int) -> None:
        '''Convert speed into image.'''
        self.__values[1] = (surf := self.__render(* self.__levels[speed // 30]),
                            surf.get_rect(midtop=self.__labels[1][1].midbottom))

    def convert_score(self, score: int) -> None:
        '''Convert score into image.'''
        self.__values[2] = (surf := self.__render(f'{score:05}', '#FFFAFA'),
                            surf.get_rect(midleft=self.__labels[2][1].midright))

    def __render(self, text: str, color: str) -> Surface:
        '''Convert text into image.'''
        return self.__font.render(text, True, color)

    def draw(self) -> None:
        '''Draw statistic notifications.'''
        self.__screen.blits(self.__labels)
        self.__screen.blits(self.__values)
