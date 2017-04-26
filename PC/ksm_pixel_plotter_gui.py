from tkinter import *
from tkinter import messagebox
from tkinter.filedialog import askopenfilename
from time import sleep
import rpyc
import json
from PIL import Image

class KsmPixelPlotterGUI(Frame):
    """Main window for ksm_pixel_plotter."""

    def __init__(self, master):
        super().__init__()
        self.master
        self.master.title('ksm_pixel_potter')
        w = 630
        h = 490
        x, y = center_window(self.master, w, h)
        self.master.geometry('%dx%d+%d+%d' % (w, h, x, y))
        #self.master.geometry('630x490')
        self.master.iconbitmap('KSmEV3.ico')

        self.grid()
        self.create_widgets()
        # Connect to EV3.
        #TODO: add combobox to select EV3.
        self.conn = rpyc.classic.connect('192.168.2.64')
        self.conn.modules.sys.path.append('/home/robot')
        # Read settings from file.
        with open('pp_settings.json') as f_obj:
            self.pp_settings = json.load(f_obj)

    def create_widgets(self):
        """Create widgets."""
        # Application name and logo.
        self.logo = PhotoImage(file="KSmEV3.gif")
        self.lbl_app = Label(self.master,
                             text='ksm_pixel_plotter v1.0',
                             fg='navy',
                             font='Helvetica 16 bold')
        self.lbl_app.grid(row=0, column=1)
        self.lbl_title = Label(self.master, image=self.logo)
        self.lbl_title.grid(row=0, column=2, padx=5, pady=5, sticky=E)

        # Menubar.
        menubar = Menu(self.master)
        menubar.add_command(label='Settings', command=self.show_settings_window)
        self.master.config(menu=menubar)

        # Selected imagefile.
        self.lbl_image_file = Label(self.master,
                                    text='Imagefile:')
        self.lbl_image_file.grid(row=1, column=0, padx=5, pady=5, sticky=E)
        self.txt_filename = Entry(self.master, width=66)
        self.txt_filename.grid(row=1, column=1)
        self.btn_open_file = Button(self.master, text='Open file...', width=10,
                                    command=self.btn_open_file_callback)
        self.btn_open_file.grid(row=1, column=2, padx=5, pady=5)

        # Checkbox for image processing only (image will not be plotted)
        self.chk_test = IntVar()
        self.lbl_image_processing_only = Label(self.master,
                                               text='Test image processing')
        self.lbl_image_processing_only.grid(row=2, column=0,
                                            padx=5, pady=5, sticky=E)
        self.chk_image_processing_only = Checkbutton(self.master,
                                                     variable=self.chk_test)
        self.chk_image_processing_only.grid(row=2, column=1,
                                            padx=5, pady=5, sticky=W)

        # Start button.
        self.btn_start = Button(self.master,
                                text='Start plotting',
                                width=68,
                                height=2,
                                command=self.btn_start_callback)
        self.btn_start.grid(row=3, column=1, pady=5, columnspan=2)

        # Information about imageprocessing.
        self.lbl_image_processing = Label(self.master,
                                          text='Processing:',
                                         )
        self.lbl_image_processing.grid(row=4, column=0,
                                       padx=5, pady=5, sticky=NE)
        self.txt_image_processing = Text(self.master,
                                         width=60,
                                         height=15)
        self.txt_image_processing.grid(row=4, column=1, columnspan=2, pady=5)

    def show_settings_window(self):
        """Create and open settings window."""
        self.top = Toplevel()
        self.sw = SettingsGUI(self.top, self.pp_settings)

    def btn_open_file_callback(self):
        """Eventhandler for btn_open_file."""
        filename = askopenfilename(initialdir='D:/Kees/Afbeeldingen',
                                   filetypes=(('All image files',
                                               '*.bmp;*.jpg;*.jpeg;*.png'),
                                              ('Bitmap files', '*.bmp'),
                                              ('JPEG-files', '*.jpg;*.jpeg'),
                                              ('PNG-files', '.png'))
                                  )
        if filename:
            self.txt_filename.configure(state=NORMAL)
            self.txt_filename.delete(0, END)
            # Insert selected file.
            self.txt_filename.insert(END, filename)
            # Update textbox.
            self.txt_filename.update()
            self.txt_filename.configure(state=DISABLED)

    def prepare_image(self, img, pp_settings):
        """
        Prepare image for plotting:
        1. Make sure the imagesize is within plotting range.
        2. Convert to black and white image
        """
        # Rotate image if necessary.
        if img.size[0] > pp_settings['x_max'] and img.size[0] > img.size[1]:
            img = img.rotate(90, expand=True)
            self.write_status('Image rotated: ' + str(img.size[0]) +
                              'x' + str(img.size[1]) + '\n\n')

        # Resize Image.
        if img.size[0] > pp_settings['x_max']:
            factor = pp_settings['x_max'] / img.size[0]
            new_image_size = (int(factor*img.size[0]), int(factor*img.size[1]))
            img = img.resize(new_image_size)
            self.write_status('Image resized: ' + str(img.size[0]) +
                              'x' + str(img.size[1]) + '\n\n')
        else:
            self.write_status('Image size: ' + str(img.size[0]) +
                              'x' + str(img.size[1]) + '\n\n')

        # Convert image to 1-bit pixels, black and white, 1 pixel per byte.
        img = img.convert('1', dither=None)

        return img

    def btn_start_callback(self):
        """Call core function to plot file."""
        # Clear contents of txt_image_processing.
        self.txt_image_processing.delete(1.0, END)

        # Open imagefile.
        image_file = self.txt_filename.get()
        img = Image.open(image_file, mode='r')

        # Prepare image for plotting.
        img = self.prepare_image(img, self.pp_settings)

        # Load pixel access object to read pixels
        pixel_data = img.load()

        if self.chk_test.get() == 0:
            # Plot image om EV3 by calling method from service on EV3.
            self.write_status('Plotting started')
            ev3 = self.conn.modules.ksm_pixel_plotter_ev3
            ev3.plot_file(self.pp_settings, img.size[0],
                          img.size[1], pixel_data)
            self.write_status('\nPlotting finished')
        else:
            # Plot pixel_data to file.
            self.plot_pixel_data_to_file(image_file, img.size[0],
                                         img.size[1], pixel_data)

    def plot_pixel_data_to_file(self, file_path, size_x, size_y, pixel_data):
        """Plot pixeldata to file ('XX' = black, '  ' = white pixel)."""
        # Open file.
        output_file_name = file_path[0:-3] + 'txt'
        output_file = open(output_file_name, 'w')

        # Plot pixel_data.
        for y in range(size_y):
            str_line = ''
            for x in range(size_x):
                if pixel_data[x, y] == 0:
                    str_line = str_line + 'XX'
                else:
                    str_line = str_line + '  '
            output_file.write(str_line + '\n')

        # Close file.
        output_file.close()

        self.write_status('\nPixel data written to file.')

    def write_status(self, msg):
        """Write proces status to txt_image_processing."""
        self.txt_image_processing.insert(END, msg)
        self.txt_image_processing.update()

    def destroy(self):
        """Override default destroy method."""
        # Save settings.
        with open('pp_settings.json', 'w') as f_obj:
            json.dump(self.pp_settings, f_obj)

class SettingsGUI(Frame):
    """Settings window."""
    def __init__(self, master, pp_settings):
        super().__init__()
        self.master = master
        self.master.title('Settings')
        w = 275
        h = 310
        x, y = center_window(self.master, w, h)
        self.master.geometry('%dx%d+%d+%d' % (w, h, x, y))
        self.master.transient(self)
        self.master.iconbitmap('KSmEV3.ico')
        self.master.protocol('WM_DELETE_WINDOW', self.delete_window)
        self.frame = Frame(self.master)
        self.pp_settings = pp_settings
        self.create_widgets()

    def create_widgets(self):
        """Create widgets on settings window."""
        self.lbl_x_step = Label(self.master,
                                text='x_step:',
                                anchor='e')
        self.lbl_x_step.grid(row=0, column=0, padx=5, pady=5, sticky=E)
        self.entry_x_step = Entry(self.master)
        self.entry_x_step.grid(row=0, column=1, padx=5, pady=5, sticky=W)
        self.entry_x_step.insert(END, self.pp_settings['x_step'])

        self.lbl_x_max = Label(self.master,
                               text='x_max:',
                               anchor=E)
        self.lbl_x_max.grid(row=1, column=0, padx=5, pady=5, sticky=E)
        self.entry_x_max = Entry(self.master)
        self.entry_x_max.grid(row=1, column=1, padx=5, pady=5, sticky=W)
        self.entry_x_max.insert(END, self.pp_settings['x_max'])

        self.lbl_dir_x_right = Label(self.master,
                                     text='dir_x_right:',
                                     anchor=E)
        self.lbl_dir_x_right.grid(row=2, column=0, padx=5, pady=5, sticky=E)
        self.entry_dir_x_right = Entry(self.master)
        self.entry_dir_x_right.grid(row=2, column=1, padx=5, pady=5, sticky=W)
        self.entry_dir_x_right.insert(END, self.pp_settings['dir_x_right'])

        self.lbl_dir_x_left = Label(self.master,
                                    text='dir_x_left:',
                                    anchor=E)
        self.lbl_dir_x_left.grid(row=3, column=0, padx=5, pady=5, sticky=E)
        self.entry_dir_x_left = Entry(self.master)
        self.entry_dir_x_left.grid(row=3, column=1, padx=5, pady=5, sticky=W)
        self.entry_dir_x_left.insert(END, self.pp_settings['dir_x_left'])

        self.lbl_y_step = Label(self.master,
                                text='y_step:',
                                anchor=E)
        self.lbl_y_step.grid(row=4, column=0, padx=5, pady=5, sticky=E)
        self.entry_y_step = Entry(self.master)
        self.entry_y_step.grid(row=4, column=1, padx=5, pady=5, sticky=W)
        self.entry_y_step.insert(END, self.pp_settings['y_step'])

        self.lbl_dir_y_right = Label(self.master,
                                     text='dir_y_right:',
                                     anchor=E)
        self.lbl_dir_y_right.grid(row=5, column=0, padx=5, pady=5, sticky=E)
        self.entry_dir_y_right = Entry(self.master)
        self.entry_dir_y_right.grid(row=5, column=1, padx=5, pady=5, sticky=W)
        self.entry_dir_y_right.insert(END, self.pp_settings['dir_y_right'])

        self.lbl_dir_y_left = Label(self.master,
                                    text='dir_y_left:',
                                    anchor=E)
        self.lbl_dir_y_left.grid(row=6, column=0, padx=5, pady=5, sticky=E)
        self.entry_dir_y_left = Entry(self.master)
        self.entry_dir_y_left.grid(row=6, column=1, padx=5, pady=5, sticky=W)
        self.entry_dir_y_left.insert(END, self.pp_settings['dir_y_left'])

        self.lbl_step_pen = Label(self.master,
                                  text='step_pen:',
                                  anchor=E)
        self.lbl_step_pen.grid(row=7, column=0, padx=5, pady=5, sticky=E)
        self.entry_step_pen = Entry(self.master)
        self.entry_step_pen.grid(row=7, column=1, padx=5, pady=5, sticky=W)
        self.entry_step_pen.insert(END, self.pp_settings['step_pen'])

        self.btn_save = Button(self.master,
                               text='Save',
                               width=15,
                               height=2,
                               command=self.on_btn_save_click)
        self.btn_save.grid(row=8, column=0, padx=10, pady=10, sticky=E)

        self.btn_cancel = Button(self.master,
                                 text='Cancel',
                                 width=15,
                                 height=2,
                                 command=self.on_btn_cancel_click)
        self.btn_cancel.grid(row=8, column=1, padx=10, pady=10, sticky=E)

    def on_btn_save_click(self):
        """Save settings and close window."""
        self.save_settings()
        self.master.destroy()

    def on_btn_cancel_click(self):
        """Close window without saving settings."""
        self.master.destroy()

    def save_settings(self):
        """Save settings."""
        self.pp_settings['x_step'] = int(self.entry_x_step.get())
        self.pp_settings['x_max'] = int(self.entry_x_max.get())
        self.pp_settings['dir_x_right'] = int(self.entry_dir_x_right.get())
        self.pp_settings['dir_x_left'] = int(self.entry_dir_x_left.get())
        self.pp_settings['y_step'] = int(self.entry_y_step.get())
        self.pp_settings['dir_y_right'] = int(self.entry_dir_y_right.get())
        self.pp_settings['dir_y_left'] = int(self.entry_dir_y_left.get())
        self.pp_settings['step_pen'] = int(self.entry_step_pen.get())

    def delete_window(self):
        """User pressed X in title bar."""
        var = messagebox.askyesno('Close window',
                                  'Window is closing, do you want to ' +
                                  'save the settings?')
        if var:
            # User pressed yes, save settings.
            self.save_settings()
        self.master.destroy()

def center_window(root, w, h):
    """Center window on the screen."""
    # Get screen width and height.
    ws = root.winfo_screenwidth()
    hs = root.winfo_screenheight()
    # Calculate position x, y.
    x = (ws/2) - (w/2)
    y = (hs/2) - (h/2)
    return x, y
