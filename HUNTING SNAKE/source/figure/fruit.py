from figure.food import *


class Fruit(Food):
    '''A class to manage fruit object.'''

    def __init__(self, screen: Surface) -> None:
        '''Initialize core attributes.'''
        super().__init__(screen, super().get_images('image/FRUIT/F', 11))
        # CREATE AT FIRST.
        self.refresh()

    @property
    def point(self) -> int:
        return self._type[1] * 10
