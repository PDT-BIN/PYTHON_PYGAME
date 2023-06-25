from pygame.time import get_ticks


class Timer:
    def __init__(self, duration: int):
        self.duration = duration
        self.start_time = 0
        self.is_actived = False

    def activate(self):
        self.is_actived = True
        self.start_time = get_ticks()

    def deactivate(self):
        self.is_actived = False
        self.start_time = 0

    def update(self):
        if self.is_actived and get_ticks() - self.start_time >= self.duration:
            self.deactivate()
