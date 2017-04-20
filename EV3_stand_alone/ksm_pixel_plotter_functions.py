import argparse, sys
from PIL import Image
from time import sleep
import ksm_pixel_plotter_ev3 as ev3

def process_command_line():
    """Read command-line options"""
    # Define command-line arguments.
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--debug", help="run program in debug mode",
                        default=False, action="store_true")
    parser.add_argument("-f", "--file", help="filename of image to be plotted",
                        type=str, required=True, default=None)

    # Parse command line options.
    args = parser.parse_args()
    dbg = args.debug
    img_file = args.file
    if img_file == None:
        print('ERROR: no imagefile specified!')
        sys.exit()

    # Return dbg-option and image filename.
    return dbg, img_file

def prepare_image(dbg, img, pp_settings):
    """
    Prepare image for plotting:
    1. Make sure the imagesize is within plotting range.
    2. Convert to black and white image
    """
    x_max = pp_settings.x_max

    # Rotate image if necessary.
    if img.size[0] > pp_settings.x_max and img.size[0] > img.size[1]:
        img = img.rotate(90, expand=True)
        if dbg:
            print('\nImage rotated: ', img.size[0], img.size[1])

    # Resize Image.
    if img.size[0] > pp_settings.x_max:
        factor = pp_settings.x_max / img.size[0]
        new_image_size = (int(factor*img.size[0]), int(factor*img.size[1]))
        img = img.resize(new_image_size)
        if dbg:
            print('Image resized: ', img.size[0], img.size[1])

    # Convert image to 1-bit pixels, black and white, 1 pixel per byte.
    img = img.convert('1', dither=None)

    return img

def plot_file(dbg, img_file, pp_settings):
    """Plot the imagefile."""
    if dbg:
        print('Plotting file: ', img_file)
    
    # Open imagefile
    img = Image.open('pics/' + img_file)

    # Prepare image for plotting.
    img = prepare_image(dbg, img, pp_settings)

    # Open file for debugging information of image processing.
    if dbg:
        debug_file = open("files/" + img_file[:len(img_file)-4] + '.txt', "w")

    # Load pixel access object to read pixels
    pixel_data = img.load()

    # Start plotting
    if dbg:
        print('Resolution: x=' + str(img.size[0]) + '  y=' + str(img.size[1]))
    for y in range(img.size[1]):
        strdata = ""
        if dbg:
            print('Printing line: ', str(y+1))
        for x in range(img.size[0]):
            if pixel_data[x,y] == 0:
                ev3.pen_down(pp_settings)
                sleep(0.1)
                ev3.pen_up(pp_settings)
                sleep(0.1)
                ev3.step_x(pp_settings, 1)
                strdata += "XX"
            else:
                ev3.step_x(pp_settings, 1)
                strdata += "  "
        if dbg:
            debug_file.write(strdata + "\n")
        ev3.goto_stop()
        ev3.step_y(pp_settings, -1)

    if dbg:
        print('Ready plotting file')
        debug_file.close()
