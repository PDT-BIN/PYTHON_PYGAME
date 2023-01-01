from pygame.image import load
from pygame.transform import scale

from system.button import *


class ButtonGroup:
    '''A class to manage buttons.'''

    def __init__(self, screen: Surface) -> None:
        '''Initialize core attributes.'''
        self.__screen = screen
        self.__items: list[tuple[Button]] = list()
        # IMAGE STORAGE.
        self.__images = tuple(
            load(f'image/BUTTON/BUTTON_{i}.png').convert_alpha() for i in range(3))
        self.__init()

    def __init(self) -> None:
        '''Initialize a manager of buttons.'''
        # ORDINAL: MENU/GUIDE/MODE/RATE/LOST LAYER.
        self.__items.append(self.__group(size=(150, 75), org=Vector2(325, 250), gap=75,
                                         way=True, model=(('PLAY', 1), ('GUIDE', 1), ('QUIT', 1))))
        self.__items.append(self.__group(size=(100, 50), org=Vector2(150, 500), gap=400,
                                         way=False, model=(('PREV', 1), ('NEXT', 1))))
        self.__items.append(self.__group(size=(150, 75), org=Vector2(325, 250), gap=75,
                                         way=True, model=(('FREEDOM', 0), ('LIMITED', 2))))
        self.__items.append(self.__group(size=(150, 75), org=Vector2(325, 200), gap=75,
                                         way=True, model=(('SLOW', 0), ('NORMAL', 1), ('FAST', 2))))
        self.__items.append(self.__group(size=(100, 50), org=Vector2(275, 430), gap=150,
                                         way=False, model=(('YES', 0), ('NO', 2))))

    def __group(self, size: tuple, org: Vector2, gap: int, way: bool, model: tuple) -> tuple[Button]:
        '''Return a group of buttons basing on the model.'''
        return tuple(Button(text, self.__get_surf(index, size), self.__get_rect(org, gap, ordi, way))
                     for ordi, (text, index) in enumerate(model))

    def __get_surf(self, index: int, size: tuple) -> Surface:
        '''Return scaled surface of button basing on the size.'''
        return scale(self.__images[index], size)

    @staticmethod
    def __get_rect(origin: Vector2, gap: int, ordinal: int, way: bool) -> Vector2:
        '''Return position of button in its model basing on the way.'''
        return origin + ((0, ordinal * gap) if way else (ordinal * gap, 0))

    def is_clicked(self, form: int, index: int) -> bool:
        '''Check if a button in group is clicked.'''
        return self.__items[form][index].is_focus()

    def draw(self, form: int) -> None:
        '''Draw a group of buttons.'''
        for button in self.__items[form]:
            button.draw(self.__screen)
