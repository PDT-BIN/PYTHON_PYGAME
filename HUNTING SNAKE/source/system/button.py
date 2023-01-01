from pygame import Surface, Vector2
from pygame.font import Font, init
from pygame.mouse import get_pos


class Button:
    '''A class to create interactive button.'''
    init()
    __font = Font('font/04B_19.ttf', 20)

    def __init__(self, text: str, image: Surface, pos: Vector2) -> None:
        '''Initialize core attributes.'''
        self.__text = text
        # IMAGE CONTAINER.
        self.__surf, self.__rect = image, image.get_rect(topleft=pos)
        self.__text_surf = Button.__font.render(self.__text, True, 'WHITE')
        self.__text_rect = self.__text_surf.get_rect(center=self.__rect.center)

    def is_focus(self) -> bool:
        '''Check if button is focused.'''
        return self.__rect.collidepoint(get_pos())

    def __discolor(self) -> None:
        '''Change text color if button is focused.'''
        self.__text_surf = Button.__font.render(
            self.__text, True, 'BLACK' if self.is_focus() else 'WHITE')

    def draw(self, screen: Surface) -> None:
        '''Draw button object.'''
        self.__discolor()
        screen.blit(self.__surf, self.__rect)
        screen.blit(self.__text_surf, self.__text_rect)
