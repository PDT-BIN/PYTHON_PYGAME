from pygame.mixer import Sound


class Audio:
    '''A class to manage music & sound effects.'''

    def __init__(self) -> None:
        '''Initialize core attributes.'''
        # SOUND STORAGE.
        self.__sounds = tuple(Sound(f'audio/S_{i}.wav') for i in range(3))

    def play_sound(self, index: int) -> None:
        '''Perform sound effects.'''
        self.__sounds[index].play()
