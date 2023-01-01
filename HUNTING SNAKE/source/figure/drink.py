from figure.food import *


class Drink(Food):
    '''A class to manage drink object.'''

    def __init__(self, screen: Surface) -> None:
        '''Initialize core attributes.'''
        super().__init__(screen, super().get_images('image/DRINK/D', 5))
        self.__existed = False

    @property
    def existed(self) -> bool:
        return self.__existed

    @existed.setter
    def existed(self, value: bool) -> None:
        self.__existed = value

    def refresh(self) -> None:
        '''Refresh type, form & appearance position of drink.'''
        self.__existed = True
        super().refresh()

    def draw(self) -> None:
        '''Draw drink object.'''
        if self.__existed:
            super().draw()

    def affect(self) -> tuple[int, int]:
        '''Get effects on SPEED & SCORE.'''
        self.__existed = False
        match self._type[1]:
            case 1:
                return randint(1, 10), 0
            case 2:
                return -randint(1, 10), 0
            case 3:
                return 0, randint(100, 200)
            case 4:
                return randint(1, 5), -randint(100, 200)
