class Status:
    """A class to manage statuses and statistics."""

    def __init__(self):
        # CONTROL FLAGS.
        self.game_active = self.pause_flag = self.challenge_flag = self.end_flag = False
        # INITIALIZE DYNAMIC STATISTCS.
        self.reset_statistic()

    def reset_statistic(self):
        """Reset dynamic statistics."""
        self.point = 100
        self.lines = 0
        self.score = 0
        self.level = 1
        self.speed = 1

    def increase_score(self):
        """Increase score."""
        self.score += self.point
        self.lines += 1
        if self.score % 500 == 0:
            self.level += 1
            self.point *= 1.2
