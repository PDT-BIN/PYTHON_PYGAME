from collections.abc import Callable

from pygame.time import get_ticks


class Timer:
    def __init__(self, duration: int, is_repeatable: bool = False, activity: Callable[[], None] = None,
                 is_automatic: bool = False):
        # INFORMATION.
        self.duration = duration
        self.is_repeatable = is_repeatable
        self.activity = activity
        # TIME.
        self.start_time = None
        self.is_actived = False
        # AUTO-ACTIVATE.
        if is_automatic:
            self.activate()

    def activate(self) -> None:
        self.is_actived = True
        self.start_time = get_ticks()

    def deactivate(self) -> None:
        self.is_actived = False
        self.start_time = None

    def update(self) -> None:
        if self.is_actived and get_ticks() - self.start_time >= self.duration:
            # DO ACTIVITY.
            if self.activity:
                self.activity()
            # RESET TIMER.
            self.deactivate()
            # REPEAT TIMER.
            if self.is_repeatable:
                self.activate()
