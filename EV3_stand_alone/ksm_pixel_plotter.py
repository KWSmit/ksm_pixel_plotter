#!/usr/bin/env python3
import ksm_pixel_plotter_ev3 as ev3
from ev3dev.ev3 import *
from ksm_pixel_plotter_settings import PP_Settings
import ksm_pixel_plotter_functions as ppf

pp_settings = PP_Settings()

# Read values of debug-setting and image filename from command-line.
dbg, img_file = ppf.process_command_line()

# Goto start position
ev3.goto_start(pp_settings)

# Plot imagefile.
ppf.plot_file(dbg, img_file, pp_settings)

# Inform that plotting is ready.
Sound.beep()
Sound.speak("Image plotter is ready")
