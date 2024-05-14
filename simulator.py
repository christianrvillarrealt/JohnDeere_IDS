from tkinter import *
from tkinter import ttk
from tkinter import filedialog
import csv
import time
import pandas as pd
import matplotlib
import matplotlib.image as image
matplotlib.use("TkAgg")
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import serial
import struct
import threading

class App:
    def __init__(self, master):
        self.step_size = 100
        self.x_axis = list(range(self.step_size))
        self.ratio = 10

        self.master = master
        self.master.title("engine simulator")
        self.master.geometry("620x400")
        self.master.configure(bg="green")
        self.master_window = master

        self.buttons_frame = Frame(self.master_window)
        self.buttons_frame.grid(row=0, column=0, sticky=W+E)

        self.btn_Image = Button(self.buttons_frame, text='Start Serial Reception', command=self.start_serial_reception)
        self.btn_Image.grid(row=0, column=0, padx=10, pady=10, rowspan=2)

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

        self.btn_File = Button(self.buttons_frame, text='Load CSV', command=self.load_csv)
        self.btn_File.grid(row=0, column=6, padx=10, pady=10, rowspan=2)

        self.group1 = LabelFrame(self.master_window, text="RPM", padx=5, pady=5)
        self.group1.grid(row=1, column=0, columnspan=3, padx=10, pady=10, sticky=E+W+N+S)

        self.group2 = LabelFrame(self.master_window, text="Radius", padx=5, pady=5)
        self.group2.grid(row=2, column=0, columnspan=3, padx=10, pady=10, sticky=E+W+N+S)

        self.group3 = LabelFrame(self.master_window, text="Transmission", padx=5, pady=5)
        self.group3.grid(row=3, column=0, columnspan=3, padx=10, pady=10, sticky=E+W+N+S)

        self.group4 = LabelFrame(self.master_window, text="Angular Velocity", padx=5, pady=5)
        self.group4.grid(row=4, column=0, columnspan=3, padx=10, pady=10, sticky=E+W+N+S)

        self.master_window.columnconfigure(0, weight=1)
        self.master_window.rowconfigure(1, weight=1)

        self.group1.rowconfigure(0, weight=1)
        self.group1.columnconfigure(0, weight=1)
        self.group2.rowconfigure(0, weight=1)
        self.group2.columnconfigure(0, weight=1)
        self.group3.rowconfigure(0, weight=1)
        self.group3.columnconfigure(0, weight=1)
        self.group4.rowconfigure(0, weight=1)
        self.group4.columnconfigure(0, weight=1)

        f1 = Figure(figsize=(1,1), dpi=100)
        self.a = f1.add_subplot(111)

        f2 = Figure(figsize=(1,1), dpi=100)
        self.b = f2.add_subplot(111)

        f3 = Figure(figsize=(1,1), dpi=100)
        self.c = f3.add_subplot(111)

        f4 = Figure(figsize=(1,1), dpi=100)
        self.d = f4.add_subplot(111)

        self.a.legend(["RPM"])
        self.b.legend(["Radius"])
        self.c.legend(["Transmission"])
        self.d.legend(["Angular Velocity"])

        self.canvas1 = FigureCanvasTkAgg(f1, self.group1)
        self.canvas2 = FigureCanvasTkAgg(f2, self.group2)
        self.canvas3 = FigureCanvasTkAgg(f3, self.group3)
        self.canvas4 = FigureCanvasTkAgg(f4, self.group4)

        self.canvas1.get_tk_widget().grid(row=0, column=0, sticky=E+W+N+S)
        self.canvas2.get_tk_widget().grid(row=0, column=0, sticky=E+W+N+S)
        self.canvas3.get_tk_widget().grid(row=0, column=0, sticky=E+W+N+S)
        self.canvas4.get_tk_widget().grid(row=0, column=0, sticky=E+W+N+S)

        self.receiver = None  # Initialize the receiver attribute

        self.csv_filename = "data.csv"
        self.create_csv()

        self.update_plot()

    def create_csv(self):
        with open(self.csv_filename, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["angular_velocity", "radius", "transmission_ratio", "rpm"])

    def start_serial_reception(self):
        if self.receiver is not None:
            print("Stopping existing receiver.")
            self.receiver.stop()
            self.receiver = None

        print("Starting new receiver.")
        self.receiver = SerialDataReceiver('COM3', 9600, self)

    def rpm(self, omega, radius, ratio):
        try:
            return (omega * 60) / (2 * pi * radius * ratio)
        except:
            return 0

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

    def save_csv(self, omega, radius, transmission, rpm):
        with open(self.csv_filename, mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([omega, radius, transmission, rpm])

    def update_plot(self):
        try:
            columns = self.read_csv(self.csv_filename)

            if len(columns["angular_velocity"]) > 0:
                self.animate(columns["angular_velocity"], columns["radius"], columns["rpm"], columns["transmission_ratio"])
        except Exception as e:
            print(f"Error updating plot: {e}")

        self.master.after(1000, self.update_plot)

    def animate(self, omega_range, radius_range, rpm_range, ratio_range):
        self.a.clear()
        self.d.clear()
        self.c.clear()
        self.b.clear()

        # Plot the data
        self.d.plot(range(len(omega_range)), omega_range, label="Angular Velocity", marker='o')
        self.b.plot(range(len(radius_range)), radius_range, label="Radius", marker='o')
        self.c.plot(range(len(ratio_range)), ratio_range, label="Transmission", marker='o')
        self.a.plot(range(len(rpm_range)), rpm_range, label="RPM", marker='o')

        # Set axis limits dynamically
        if len(rpm_range) > 0:
            self.a.set_xlim(0, len(rpm_range))
            y_min = min(rpm_range)
            y_max = max(rpm_range)
            if y_min == y_max:
                y_min -= 1
                y_max += 1
            self.a.set_ylim(y_min, y_max)

        if len(radius_range) > 0:
            self.b.set_xlim(0, len(radius_range))
            y_min = min(radius_range)
            y_max = max(radius_range)
            if y_min == y_max:
                y_min -= 1
                y_max += 1
            self.b.set_ylim(y_min, y_max)

        if len(ratio_range) > 0:
            self.c.set_xlim(0, len(ratio_range))
            y_min = min(ratio_range)
            y_max = max(ratio_range)
            if y_min == y_max:
                y_min -= 1
                y_max += 1
            self.c.set_ylim(y_min, y_max)

        if len(omega_range) > 0:
            self.d.set_xlim(0, len(omega_range))
            y_min = min(omega_range)
            y_max = max(omega_range)
            if y_min == y_max:
                y_min -= 1
                y_max += 1
            self.d.set_ylim(y_min, y_max)

        # Add legends
        self.a.legend()
        self.b.legend()
        self.c.legend()
        self.d.legend()

        # Draw the canvas
        self.canvas1.draw()
        self.canvas2.draw()
        self.canvas3.draw()
        self.canvas4.draw()

    def read_csv(self, file_path):
        with open(file_path, 'r', newline='') as csvfile:
            reader = csv.reader(csvfile)
            header = next(reader)
            columns = {col: [] for col in header}
            for row in reader:
                for col, value in zip(header, row):
                    columns[col].append(float(value))
        return columns

    def load_csv(self):
        file_path = filedialog.askopenfilename()
        columns = self.read_csv(file_path)
        self.animate(columns["angular_velocity"], columns["radius"], columns["rpm"], columns["transmission_ratio"])

class SerialDataReceiver:
    def __init__(self, port, baud_rate, app):
        self.ser = None
        try:
            self.ser = serial.Serial(port, baud_rate)
            self.app = app
            self.running = True

            # Initialize variables
            self.omega = None
            self.radius = None
            self.rpm = None
            self.transmission = None

            threading.Thread(target=self.read_serial_data).start()
        except serial.SerialException as e:
            print(f"Failed to open serial port {port}: {e}")
            self.running = False
        self.receiver = None

    def read_serial_data(self):
        while self.running and self.ser:
            try:
                data = self.ser.read(1)
                if data == b'\xff':
                    type_byte = self.ser.read(1)
                    if type_byte:
                        type_value = struct.unpack('B', type_byte)[0]
                        value_byte = self.ser.read(1)
                        if value_byte:
                            value = struct.unpack('B', value_byte)[0]
                            if type_value >= 0x80:
                                self.omega = value
                                print(f"Received Angular Velocity: {value}")
                            elif type_value >= 0x40:
                                self.radius = value
                                print(f"Received Radius: {value}")
                            elif type_value >= 0x20:
                                self.rpm = value
                                print(f"Received RPM: {value}")
                            elif type_value >= 0x10:
                                self.transmission = value
                                print(f"Received Transmission Ratio: {value}")

                            if self.omega is not None and self.radius is not None and self.rpm is not None and self.transmission is not None:
                                self.app.save_csv(self.omega, self.radius, self.transmission, self.rpm)
                                # Reset variables
                                self.omega = self.radius = self.rpm = self.transmission = None

            except serial.SerialException as e:
                print(f"Serial port error: {e}")
                self.stop()

    def stop(self):
        if self.running and self.ser:
            self.running = False
            try:
                print("Closing serial port.")
                self.ser.close()
            except serial.SerialException as e:
                print(f"Error closing serial port: {e}")
            self.ser = None

if __name__ == "__main__":
    root = Tk()
    app = App(root)
    root.mainloop()
    if app.receiver:
        app.receiver.stop()
