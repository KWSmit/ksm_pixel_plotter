# ksm_pixel_plotter

ksm_pixel_plotter is a pixel plotter inspired by work of the Seshan Brothers,
see for example this [video](https://www.youtube.com/watch?v=kFiWumBILwU).

The plotter is build using [LEGO Mindstorms EV3](https://www.lego.com/en-us/mindstorms) and programmed in Python 
using [ev3dev](http://www.ev3dev.org). It consists of two parts:
1. Scripts for PC (`ksm_pixel_plotter_pc.py` and 
`ksm_pixel_plotter_gui.py`)
2. Script for EV3 (`ksm_pixel_plotter_ev3`)

The PC script is an application to select the imagefile to plot and to change 
any settings when needed. When the user has selected the imagefile and presses 
the Start-button, the script on the EV3 is started via RPyC.

All the imageprocessing takes place on your PC. The resulting pixeldata is
send to the script on the EV3 together with the settings. All EV3 related 
functionality is part of the EV3 script.


#### Using ksm_pixel_plotter

1. Start the script on the EV3 in the terminal: 
`python3 ksm_pixel_plotter_ev3.py`. 
Wait a few seconds to be sure there are no errors shown. The EV3 now 
acts as a RPyC server and waits for calls from your PC.
2. Start the script ksm_pixel_plotter_pc on your computer. Change settings 
when needed and select an imagefile anywhere on your computer. 
Then press the Start-button.

When the Start-button is pressed any desired imageprocessing takes place on 
your computer (rotating, resizing and converting to 1-bit black-and-white image). 
The resulting pixeldata and settings are send to the running script on you EV3. 
When finished, you're informed in the user-interface on your computer.


#### !Note:
In this version the ip-address of your EV3 is hard coded, so you need to 
change the code in `ksm_pixel_plotter_gui.py` (line 24).
