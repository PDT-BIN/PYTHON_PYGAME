from ui import UI


class Data:
    def __init__(self, ui: UI):
        self.ui = ui
        self._health = 5
        self._coins = 0
        self.unlocked_level = 0
        self.current_level = 0
        # CREATE HEART.
        self.ui.update_health(self._health)

    @property
    def coins(self) -> int:
        return self._coins

    @coins.setter
    def coins(self, value: int):
        self._coins = value
        if self._coins >= 100:
            self._coins -= 100
            self.health += 1
        self.ui.update_coins(self._coins)

    @property
    def health(self) -> int:
        return self._health

    @health.setter
    def health(self, value: int):
        self._health = value
        self.ui.update_health(value)
