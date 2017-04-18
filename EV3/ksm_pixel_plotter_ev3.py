from time import sleep
from ev3dev.ev3 import *
import rpyc
from rpyc.utils.server import ThreadedServer
import PIL.Image

class PP_Service(rpyc.Service):
    """RPyC service for ksm_pixel_plotter. Start service on EV3."""

    def connect_motors_sensors(self):

        """Connect motors and sensors."""
        # Connect motor to move pen up- and down.
        self.pen_motor = LargeMotor(OUTPUT_A)
        assert self.pen_motor.connected, "ERROR connecting LargeMotor (pen-movement)"

        # Connect motor for movement in x-direction
        self.x_motor = LargeMotor(OUTPUT_D)
        assert self.x_motor.connected, "ERROR connection LargeMotor (x-direction)"

        # Connect motor 1 for movement in y-direction
        self.y1_motor = LargeMotor(OUTPUT_B)
        assert self.y1_motor.connected, "ERROR connection LargeMotor (y-direction nr.1)"

        # Connect motor 2 for movement in y-direction
        self.y2_motor = LargeMotor(OUTPUT_C)
        assert self.y2_motor.connected, "ERROR connection LargeMotor (y-direction nr.2)"

        # Connect TouchSensor for stopping the program
        self.ts_stop_program = TouchSensor(INPUT_1)
        assert self.ts_stop_program.connected, "ERROR connection TouchSensor (stop program)"

        # Connect Touch for indicating startposition
        self.ts_stop = TouchSensor(INPUT_2)
        assert self.ts_stop.connected, "Error connecting TouchSensor (startposition)"

    def goto_start(self, pp_settings):
        """Set plotter in starting position."""
        # Pull the pen up.
        self.pen_up(pp_settings)
        # Move to the start position (x=0).
        self.goto_stop()
        sleep(0.1)
        # Move 10 steps forwards in y direction.
        self.step_number_y(pp_settings, -1, 10)
        sleep(0.1)

    def step_x(self, pp_settings, direction):
        """Move one step in x-direction."""
        self.x_motor.run_to_rel_pos(position_sp=direction*pp_settings['x_step'],
                                    speed_sp=50, stop_action='hold')
        self.x_motor.wait_while('running')

    def step_number_x(self, pp_settings, direction, number_of_steps):
        """Move number_of_steps steps in x-direction."""
        for i in range(number_of_steps):
            self.x_motor.run_to_rel_pos(position_sp=direction*pp_settings['x_step'],
                                        speed_sp=200, stop_action='hold')
            self.x_motor.wait_while('running')

    def step_y(self, pp_settings, direction):
        """Move one step in y-direction."""
        self.y1_motor.run_to_rel_pos(position_sp=direction*pp_settings['y_step'],
                                     speed_sp=50, stop_action='hold')
        self.y2_motor.run_to_rel_pos(position_sp=-1*direction*(pp_settings['y_step'] + 1),
                                     speed_sp=50, stop_action='hold')
        self.y1_motor.wait_while('running')
        self.y2_motor.wait_while('running')

    def step_number_y(self, pp_settings, direction, number_of_steps):
        """Move number_of_steps steps in y-direction."""
        for i in range(number_of_steps):
            self.y1_motor.run_to_rel_pos(position_sp=direction*pp_settings['y_step'],
                                         speed_sp=50, stop_action='hold')
            self.y2_motor.run_to_rel_pos(position_sp=-1*direction*(pp_settings['y_step'] + 1),
                                         speed_sp=50, stop_action='hold')
            self.y1_motor.wait_while('running')
            self.y2_motor.wait_while('running')

    def pen_up(self, pp_settings):
        """Move pen up."""
        self.pen_motor.run_to_rel_pos(position_sp=-1*pp_settings['step_pen'],
                                      speed_sp=50, stop_action='hold')
        self.pen_motor.wait_while('running')

    def pen_down(self, pp_settings):
        """Move pen down."""
        self.pen_motor.run_to_rel_pos(position_sp=pp_settings['step_pen'],
                                      speed_sp=50, stop_action='hold')
        self.pen_motor.wait_while('running')

    def goto_stop(self):
        """Move to start position."""
        while not self.ts_stop.value():
            self.x_motor.run_forever(speed_sp=-800)
            self.x_motor.stop(stop_action='hold')

    def exposed_plot_file(self, pp_settings, size_x, size_y, pixel_data):
        """Plot the imagefile."""

        # Connect motors and sensors.
        self.connect_motors_sensors()

        # Let pen go to start position.
        self.goto_start(pp_settings)

        # Start plotting
        for y in range(size_y):
            for x in range(size_x):
                if pixel_data[x, y] == 0:
                    self.pen_down(pp_settings)
                    self.pen_up(pp_settings)
                    sleep(0.1)
                    self.step_x(pp_settings, 1)
                else:
                    self.step_x(pp_settings, 1)
            self.goto_stop()
            self.step_y(pp_settings, -1)

if __name__ == '__main__':
    # Start service for ksm_pixel_plotter.
    s = ThreadedServer(PP_Service, port=18812)
    s.start()
