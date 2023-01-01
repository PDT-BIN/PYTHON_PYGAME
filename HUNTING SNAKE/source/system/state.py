class State:
    '''A class to manage status flags.'''

    def __init__(self) -> None:
        '''Initialize core attributes.'''
        self.__page = self.__rate = self.__score = 0
        self.__mode, self.__voice, self.__stage = None, True, 'MENU'

    @property
    def page(self) -> int:
        return self.__page

    @page.setter
    def page(self, value: int) -> None:
        if 0 <= value < 4:
            self.__page = value

    @property
    def rate(self) -> int:
        return self.__rate

    @rate.setter
    def rate(self, value: int) -> None:
        self.__rate = value

    @property
    def score(self) -> int:
        return self.__score

    @score.setter
    def score(self, value: int) -> None:
        self.__score = value

    @property
    def mode(self) -> str:
        return self.__mode

    @mode.setter
    def mode(self, value: str) -> None:
        self.__mode = value

    @property
    def voice(self) -> bool:
        return self.__voice

    @voice.setter
    def voice(self, value: bool) -> None:
        self.__voice = value

    @property
    def stage(self) -> str:
        return self.__stage

    @stage.setter
    def stage(self, value: str) -> None:
        self.__stage = value
