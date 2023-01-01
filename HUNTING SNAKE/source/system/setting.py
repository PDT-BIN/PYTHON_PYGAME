class Setting:
    '''A class to manage default settings.'''

    def __init__(self) -> None:
        '''Initialize core attributes.'''
        self.__dim = (800, 600)
        self.__fps = 60

    @property
    def dim(self) -> tuple[int, int]:
        return self.__dim

    @property
    def fps(self) -> int:
        return self.__fps
