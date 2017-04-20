class PP_Settings():
    """ A class to store all settings for pixel_plotter."""

    def __init__(self):
        """ Initialize settings """
        self.x_step = 4         # Size of one step in x-direction
        self.x_max = 100        # Maximum value for x-direction
        self.dir_x_right = 1    # Move to the right (x-direction)
        self.dir_x_left = -1    # Move to the left (x-direction)
        self.y_step = 3         # Size of one step in y-direction
        self.dir_y_right = -1   # Move to the right (x-direction)
        self.dir_y_left = 1     # Move to the left (x-direction)
        self.step_pen = 10      # Size of one step for the pen
