#!/usr/bin/env python3
from time import sleep
from ev3dev.ev3 import *

# Connect motor to move pen up- and down.
pen_motor = LargeMotor(OUTPUT_A)
assert pen_motor.connected, "ERROR connecting LargeMotor (pen-movement)"

# Connect motor for movement in x-direction
x_motor = LargeMotor(OUTPUT_D)
assert x_motor.connected, "ERROR connection LargeMotor (x-direction)"

# Connect motor 1 for movement in y-direction
y1_motor = LargeMotor(OUTPUT_B)
assert y1_motor.connected, "ERROR connection LargeMotor (y-direction nr.1)"

# Connect motor 2 for movement in y-direction
y2_motor = LargeMotor(OUTPUT_C)
assert y2_motor.connected, "ERROR connection LargeMotor (y-direction nr.2)"

# Connect TouchSensor for stopping the program
ts_stop_program = TouchSensor(INPUT_1)
assert ts_stop_program.connected, "ERROR connection TouchSensor (stop program)"

# Connect Touch for indicating startposition
ts_stop = TouchSensor(INPUT_2)
assert ts_stop.connected, "Error connecting TouchSensor (startposition)"

def goto_start(pp_settings):
    """Set plotter in starting position."""
    # Pull the pen up.
    pen_up(pp_settings)
    # Move to the start position (x=0).
    goto_stop()
    sleep(0.1)
    # Move 10 steps forwards in y direction.
    step_number_y(pp_settings, -1, 10)
    sleep(0.1)

def step_x(pp_settings, direction):
    """Move one step in x-direction."""
    x_motor.run_to_rel_pos(position_sp=direction*pp_settings['x_step'],
                           speed_sp=50, stop_action='hold')
    x_motor.wait_while('running')

def step_number_x(pp_settings, direction, number_of_steps):
    """Move number_of_steps steps in x-direction."""
    for i in range(number_of_steps):
        x_motor.run_to_rel_pos(position_sp=direction*pp_settings['x_step'],
                               speed_sp=200, stop_action='hold')
        x_motor.wait_while('running')

def step_y(pp_settings, direction):
    """Move one step in y-direction."""
    y1_motor.run_to_rel_pos(position_sp=direction*pp_settings['y_step'],
                            speed_sp=50, stop_action='hold')
    y2_motor.run_to_rel_pos(position_sp=-1*direction*(pp_settings['y_step'] + 1),
                            speed_sp=50, stop_action='hold')
    y1_motor.wait_while('running')
    y2_motor.wait_while('running')

def step_number_y(pp_settings, direction, number_of_steps):
    """Move number_of_steps steps in y-direction."""
    for i in range(number_of_steps):
        y1_motor.run_to_rel_pos(position_sp=direction*pp_settings['y_step'],
                                speed_sp=50, stop_action='hold')
        y2_motor.run_to_rel_pos(position_sp=-1*direction*(pp_settings['y_step'] + 1),
                                speed_sp=50, stop_action='hold')
        y1_motor.wait_while('running')
        y2_motor.wait_while('running')

def pen_up(pp_settings):
    """Move pen up."""
    pen_motor.run_to_rel_pos(position_sp=-1*pp_settings['step_pen'],
                             speed_sp=50, stop_action='hold')
    pen_motor.wait_while('running')

def pen_down(pp_settings):
    """Move pen down."""
    pen_motor.run_to_rel_pos(position_sp=pp_settings['step_pen'],
                             speed_sp=50, stop_action='hold')
    pen_motor.wait_while('running')

def goto_stop():
    """Move to start position."""
    while not ts_stop.value():
        x_motor.run_forever(speed_sp=-300)
    x_motor.stop(stop_action='hold')

def plot_file(pp_settings, size_x, size_y, pixel_data):
    """Plot the imagefile."""

    # Let pen go to start position.
    goto_start(pp_settings)

    # Start plotting
    for y in range(size_y):
        for x in range(size_x):
            if pixel_data[x, y] == 0:
                pen_down(pp_settings)
                sleep(0.1)
                pen_up(pp_settings)
                sleep(0.1)
                step_x(pp_settings, 1)
            else:
                sleep(0.1)
                step_x(pp_settings, 1)
        goto_stop()
        step_y(pp_settings, -1)
