from random import choice, randint

from pygame import Rect, Surface
from pygame.image import load


class Food:
    '''A class to be inherited by food objects.'''

    def __init__(self, screen: Surface, images: tuple[tuple[Surface, int]]) -> None:
        '''Initialize core attributes.'''
        self._screen = screen
        # IMAGE STORAGE.
        self._images = images

    @property
    def rect(self) -> Rect:
        return self._rect

    def refresh(self) -> None:
        '''Refresh type, form & appearance position of food.'''
        self._type = choice(self._images)
        # IMAGE CONTAINER.
        self._surf = self._type[0]
        self._rect = self._surf.get_rect(
            x=randint(0, 76) * 10, y=randint(0, 56) * 10)

    def draw(self) -> None:
        '''Draw doof object.'''
        self._screen.blit(self._surf, self._rect)

    @staticmethod
    def get_images(path: str, numb: int) -> tuple[tuple[Surface, int]]:
        '''Get images from directory.'''
        return tuple((load(f'{path}_{i}.png').convert_alpha(), i) for i in range(1, numb))
