from typing import Callable

from pygame.time import get_ticks


class Timer:
    def __init__(
        self, duration: int, function: Callable[[], None] = None, is_repeatable=False
    ):
        self.duration = duration
        self.function = function
        self.is_repeatable = is_repeatable
        self.start_time = 0
        self.is_active = False

    def activate(self):
        self.is_active = True
        self.start_time = get_ticks()

    def deactivate(self):
        self.is_active = False
        self.start_time = 0
        if self.is_repeatable:
            self.activate()

    def update(self):
        if self.is_active:
            current_time = get_ticks()
            if current_time - self.start_time >= self.duration:
                if self.function:
                    self.function()
                self.deactivate()
