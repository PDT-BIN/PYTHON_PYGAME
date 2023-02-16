from collections.abc import Callable

from pygame.time import get_ticks


class Timer:

    def __init__(self, duration: int, action: Callable[[], None] = None):
        # CORE.
        self.start_time = None
        self.is_actived = False
        self.duration = duration
        # INTERACTION.
        self.action = action

    def activate(self):
        self.is_actived = True
        self.start_time = get_ticks()

    def deactivate(self):
        self.is_actived = False
        if self.action:
            self.action()

    def update(self):
        if self.is_actived and get_ticks() - self.start_time >= self.duration:
            self.deactivate()
