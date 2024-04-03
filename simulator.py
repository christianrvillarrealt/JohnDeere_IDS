###############################################################################
## Entregable de reto 1. Visualización gráfica de comportamiento del tractor ##
###############################################################################

# Christian Raúl Villarreal Treviño A01285465
# Rodrigo Jose Monterroso Bandy     A00837948
# Alejandro Rodríguez del Bosque    A01722329
# Eduardo Hernandez Valdez          A01285233

# GUI library
from tkinter import *
from tkinter import scrolledtext
from tkinter import ttk
from tkinter import filedialog

# library to read csv files
import csv

# import the pi value
from math import pi

# library for generating delays
import time

# library for data manipulation
import pandas as pd

# library for plotting
import matplotlib
import matplotlib.image as image
matplotlib.use("TkAgg")
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)

# library for creating threads
import threading

# main class having all the GUI and the functions
class App:
    def __init__(self, master):

        # total number of steps
        self.step_size = 100

        # list of 100 elements from 0 to 99 (used for the x axis)
        self.x_axis = list(range(self.step_size))
        
        # engine ratio
        self.ratio = 10

        # GUI stuff
        self.master = master
        self.master.title("engine simulator")
        self.master.geometry("620x400")
        self.master.configure(bg="green")
        self.master_window = master

        # top frame that has the inoput fields and buttons
        self.buttons_frame = Frame(self.master_window)
        self.buttons_frame.grid(row=0, column=0, sticky=W+E)    

        # button that starts the data generation
        self.btn_Image = Button(self.buttons_frame, text='generate data', command=self.generate_data)
        self.btn_Image.grid(row=0, column=0, padx=10, pady=10, rowspan=2)

        # input fields for the angular velocity
        self.lbl_angular_min = Label(self.buttons_frame, text='(angular) from: ')
        self.lbl_angular_min.grid(row=0, column=1, padx=10, pady=10)
        self.angular_min = Entry(self.buttons_frame, width=10)
        self.angular_min.insert(0, "0") 
        self.angular_min.grid(row=0, column=2, padx=10, pady=10)

        self.lbl_angular_min = Label(self.buttons_frame, text='to: ')
        self.lbl_angular_min.grid(row=0, column=3, padx=10, pady=10)
        self.angular_max = Entry(self.buttons_frame, width=10)
        self.angular_max.insert(0, "10") 
        self.angular_max.grid(row=0, column=4, padx=10, pady=10)

        # input fields for the radius
        self.lbl_angular_min = Label(self.buttons_frame, text='(radius) from:')
        self.lbl_angular_min.grid(row=1, column=1, padx=10, pady=10)
        self.radius_min = Entry(self.buttons_frame, width=10)
        self.radius_min.insert(0, "0.1") 
        self.radius_min.grid(row=1, column=2, padx=10, pady=10)

        self.lbl_angular_min = Label(self.buttons_frame, text='to:')
        self.lbl_angular_min.grid(row=1, column=3, padx=10, pady=10)
        self.radius_max = Entry(self.buttons_frame, width=10)
        self.radius_max.insert(0, "0.8") 
        self.radius_max.grid(row=1, column=4, padx=10, pady=10)

        # gui separator (vertical line)
        ttk.Separator(self.buttons_frame, orient=VERTICAL).grid(column=5, row=0, rowspan=2, sticky='ns')

        # button that loads a csv file and animate it
        self.btn_File = Button(self.buttons_frame, text='load csv', command = self.load_csv)
        self.btn_File.grid(row=0, column=6, padx=10, pady=10, rowspan=2)

        # frame containing the graph
        self.group1 = LabelFrame(self.master_window, text="graph", padx=5, pady=5)
        self.group1.grid(row=1, column=0, columnspan=3, padx=10, pady=10, sticky=E+W+N+S)

        # GUI stuff
        self.master_window.columnconfigure(0, weight=1)
        self.master_window.rowconfigure(1, weight=1)
        self.group1.rowconfigure(0, weight=1)
        self.group1.columnconfigure(0, weight=1)

        # create the graph
        f = Figure(figsize=(5,5), dpi=100)
        self.a = f.add_subplot(111)
        
        # add the legend to the graph
        self.a.legend(["angular velocity", "radius", "RPM"])

        self.canvas = FigureCanvasTkAgg(f, self.group1)
        self.canvas.get_tk_widget().grid(row=0, column=0, sticky=E+W+N+S)

    # function to calculate the RPM
    def rpm(self, omega, radius, ratio):
        return (omega * 60) / (2 * pi * radius * ratio)
    
    # function to generate the range of values
    # it takes the min and max values and returns a list of 100 elements
    def generate_range(self, min, max):
        quantity = abs(max - min)
        steps = quantity / (self.step_size-1)

        range = []
        current_value = min
        while len(range) < self.step_size:
            range.append(current_value)
            current_value += steps
            current_value = round(current_value, 3)

        return range

    # function to generate the data
    # takes the values from the input fields
    # calculates the RPM with each iteration of the value
    # saves the data to a csv file
    # and runs the animation
    def generate_data(self):

        # get the values from the input fields
        angular_min = float(self.angular_min.get())
        angular_max = float(self.angular_max.get())
        radius_min = float(self.radius_min.get())
        radius_max = float(self.radius_max.get())

        # if any of these is empty, return
        if angular_min is None:
            return
        if angular_max is None:
            return
        if radius_min is None:
            return
        if radius_max is None:
            return

        # get the filename for the potential savefile
        f = filedialog.asksaveasfile(
            initialfile = 'data.csv',
            defaultextension=".csv",
            filetypes=[ ("All Files","*.*"), ("CSV Files","*.csv") ]
        )

        # if we dont have a file, return
        if f is None:
            return

        # generate the ranges, swap them if needed
        omega_range = []
        if angular_min < angular_max:
            omega_range = self.generate_range(angular_min, angular_max)
        else:
            omega_range = self.generate_range(angular_max, angular_min)
            omega_range = omega_range[::-1]

        radius_range = []
        if radius_min < radius_max:
            radius_range = self.generate_range(radius_min, radius_max)
        else:
            radius_range = self.generate_range(radius_max, radius_min)
            radius_range = radius_range[::-1]

        # calculate the RPM
        rpm_range = [self.rpm(omega, radius, self.ratio) for omega, radius in zip(omega_range, radius_range)]

        # save the data to the csv file
        self.filename = f.name
        self.save_csv(omega_range, radius_range, rpm_range)

        # run the animation
        self.thread = threading.Thread(
            target=self.animate,
            args=(omega_range, radius_range, rpm_range)
        )
        self.thread.start()

    # function to save the lists into a dataframe and then to a csv file
    def save_csv(self, omega_range, radius_range, rpm_range):

        # the column names for the csv file
        names = ["angular velocity", "radius", "transmission ratio", "rpm"]

        # create a list of step_size with 100, to be used as the transmission ratio
        ratio_range = [self.ratio] * self.step_size

        # create the dataframe
        df = pd.DataFrame(list(zip(omega_range, radius_range, ratio_range, rpm_range)), columns=names)

        # save the dataframe to a csv file
        df.to_csv(self.filename, index=False)

    # function to animate the graph
    def animate(self, omega_range, radius_range, rpm_range):

        # iterate over the range of values and plot them
        for i in range(self.step_size):
            self.a.clear() # we first clear the graph

            # plot the 3 lines
            self.a.plot(self.x_axis[:i], omega_range[:i])
            self.a.plot(self.x_axis[:i], radius_range[:i])
            self.a.plot(self.x_axis[:i], rpm_range[:i])

            # add the legend
            self.a.legend(["angular velocity", "radius", "RPM"])

            # draw the graph
            self.canvas.draw()
            time.sleep(0.1)
    
    # function to read the csv and return all data from each column as a dictionary
    def read_csv(self, file_path):
        with open(file_path, 'r', newline='') as csvfile:
            reader = csv.reader(csvfile)
            header = next(reader)  
            columns = {col: [] for col in header} 
            for row in reader:
                for col, value in zip(header, row):
                    columns[col].append(float(value)) 
        return columns
    
    # function to load a csv prompting for a file opener window and graphing it
    def load_csv(self):
        file_path = filedialog.askopenfilename()
        
        columns = self.read_csv(file_path)
        
        self.thread = threading.Thread(
            target=self.animate,
            args=(columns["angular velocity"], columns["radius"], columns["rpm"])
        )

        self.thread.start()


if __name__ == "__main__":
    root = Tk()
    app = App(root)
    root.mainloop()
