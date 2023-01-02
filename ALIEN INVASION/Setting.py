class Setting:
    """A class to manage all settings for Alien Invasion."""
    def __init__(self):
        #Screen settings.
        self.screen_width, self.screen_height = 1500, 800
        self.bg_color = (230, 230, 230)
        #Ship settings.
        self.life_limit = 3
        #Bullet settings.
        self.bullet_allowed = 3
        #Alien settings.
        self.fleet_drop_speed = 15
        #Point settings.
        self.alien_point = 50
        #Speed up settings.
        self.speed_scale = 1.1
        self.point_scale = 1.5
        #Dynamic settings.
        self.initialize_dynamic_settings()

    def initialize_dynamic_settings(self):
        """Initialize settings that change during the game."""
        self.ship_speed = 2.0
        self.bullet_speed = 3.0
        self.alien_speed = 1.5
        self.fleet_direction = 1 #(1: Right direction || -1: Left direction)

    def increase_speed(self):
        """Increase game speed settings."""
        self.ship_speed *= self.speed_scale
        self.bullet_speed *= self.speed_scale
        self.alien_speed *= self.speed_scale
        self.alien_point = int(self.alien_point * self.point_scale)
        



#Use this codes when play game in full screen.
#self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
#self.setting.screen_width = self.screen.get_rect().width
#self.setting.screen_height = self.screen.get_rect().height