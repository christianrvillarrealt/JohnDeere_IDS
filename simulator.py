from tkinter import *
from tkinter import scrolledtext
from tkinter import ttk

from math import pi
import time

import pandas as pd
import matplotlib
import matplotlib.image as image
matplotlib.use("TkAgg")

from matplotlib.figure import Figure

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

try:
    from matplotlib.backends.backend_tkagg import NavigationToolbar2TkAgg
except ImportError:
    from matplotlib.backends.backend_tkagg import NavigationToolbar2Tk as NavigationToolbar2TkAgg

import threading

class App:
    def __init__(self, master):
        self.step_size = 100
        self.x_axis = list(range(self.step_size))
        self.ratio = 10

        self.file_name = 'out.csv'

        self.master = master
        self.master.title("engine simulator")
        self.master.geometry("620x400")
        self.master.configure(bg="green")

        self.master_window = master

        self.buttons_frame = Frame(self.master_window)
        self.buttons_frame.grid(row=0, column=0, sticky=W+E)    

        self.btn_Image = Button(self.buttons_frame, text='generate random data', command=self.generate_random_data)
        self.btn_Image.grid(row=0, column=0, padx=10, pady=10, rowspan=2)

        self.lbl_angular_min = Label(self.buttons_frame, text='(angular) from: ')
        self.lbl_angular_min.grid(row=0, column=1, padx=10, pady=10)
        self.angular_min = Entry(self.buttons_frame, width=10)
        self.angular_min.insert(0, "1") 
        self.angular_min.grid(row=0, column=2, padx=10, pady=10)


        self.lbl_angular_min = Label(self.buttons_frame, text='to: ')
        self.lbl_angular_min.grid(row=0, column=3, padx=10, pady=10)
        self.angular_max = Entry(self.buttons_frame, width=10)
        self.angular_max.insert(0, "10") 
        self.angular_max.grid(row=0, column=4, padx=10, pady=10)

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

        ttk.Separator(self.buttons_frame, orient=VERTICAL).grid(column=5, row=0, rowspan=2, sticky='ns')

        self.btn_File = Button(self.buttons_frame, text='load csv')
        self.btn_File.grid(row=0, column=6, padx=10, pady=10, rowspan=2)

        self.group1 = LabelFrame(self.master_window, text="graph", padx=5, pady=5)
        self.group1.grid(row=1, column=0, columnspan=3, padx=10, pady=10, sticky=E+W+N+S)

        self.master_window.columnconfigure(0, weight=1)
        self.master_window.rowconfigure(1, weight=1)

        self.group1.rowconfigure(0, weight=1)
        self.group1.columnconfigure(0, weight=1)

        f = Figure(figsize=(5,5), dpi=100)
        self.a = f.add_subplot(111)

        self.a.legend(["angular velocity", "radius", "RPM"])

        self.canvas = FigureCanvasTkAgg(f, self.group1)
        self.canvas.get_tk_widget().grid(row=0, column=0, sticky=E+W+N+S)

    def rpm(self, omega, radius, ratio):
        return (omega * 60) / (2 * pi * radius * ratio)
    
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

    def generate_random_data(self):
        angular_min = float(self.angular_min.get())
        angular_max = float(self.angular_max.get())
        radius_min = float(self.radius_min.get())
        radius_max = float(self.radius_max.get())

        if angular_min is None:
            return
        if angular_max is None:
            return
        if radius_min is None:
            return
        if radius_max is None:
            return

        omega_range = self.generate_range(angular_min, angular_max)        
        radius_range = self.generate_range(radius_min, radius_max)
        rpm_range = [self.rpm(omega, radius, self.ratio) for omega, radius in zip(omega_range, radius_range)]

        self.save_csv(omega_range, radius_range, rpm_range)

        self.thread = threading.Thread(
            target=self.animate,
            args=(omega_range, radius_range, rpm_range)
        )

        self.thread.start()

    def save_csv(self, omega_range, radius_range, rpm_range):
        names = ["angular velocity", "radius", "transmission ratio", "rpm"]

        ratio_range = [100] * self.step_size

        df = pd.DataFrame(list(zip(omega_range, radius_range, rpm_range, ratio_range)), columns=names)

        df.to_csv(self.file_name, index=False)

    def animate(self, omega_range, radius_range, rpm_range):
        for i in range(self.step_size):

            self.a.clear()
            self.a.plot(self.x_axis[:i], omega_range[:i])
            self.a.plot(self.x_axis[:i], radius_range[:i])
            self.a.plot(self.x_axis[:i], rpm_range[:i])
            self.a.legend(["angular velocity", "radius", "RPM"])

            self.canvas.draw()
            time.sleep(0.1)


if __name__ == "__main__":
    root = Tk()
    app = App(root)
    root.mainloop()
