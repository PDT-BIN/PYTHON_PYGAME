from pygame import Surface
from pygame.image import load


class Layer:
    '''A class to manage display.'''

    def __init__(self, screen: Surface) -> None:
        '''Initialize core attributes.'''
        self.__screen = screen
        # IMAGE STORAGE.
        self.__images = tuple(tuple(load(f'image/{P}/{P}_{i}.png').convert_alpha() for i in range(N))
                              for P, N in (('LAYER', 2), ('MUSIC', 2), ('GUIDE', 4),  ('LOST', 1)))
        self.__places = ((0, 0), (5, 5), (175, 25),  (225, 125))

    def draw(self, form: int, index: int) -> None:
        '''Draw layer of each stages.'''
        self.__screen.blit(self.__images[form][index], self.__places[form])
