class GameStats:
    """A class to manage game statistics."""
    def __init__(self, AI_game):
        """Create a game statistics object."""
        #Use the default resource from ALIEN_INVASION.py.
        self.setting = AI_game.setting
        #Control the active of game. (Check if MENU display is slideshowing.)
        self.game_active = False
        #Initialize static game statistics.
        self.highest_score = 0
        #Initialize dynamic game statistics.
        self.reset_statistic()

    def reset_statistic(self):
        """Reset the dynamic game statistics when GAME OVER."""
        self.life_points = self.setting.life_limit
        self.score = 0
        self.level = 1