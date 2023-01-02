class Setting:
    """A class to manage settings of game."""
    def __init__(self):
        #Default settings of screen.
        self.screen_width, self.screen_height = 432, 768
        #Gravity force.
        self.gravity = 0.25
        #Pipe height position.
        self.pipe_height_list = [300, 350, 400]