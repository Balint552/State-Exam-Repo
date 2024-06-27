import tkinter as tk
import serial
import math
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import threading
from filterpy.kalman import KalmanFilter
import numpy as np
import mplcursors

# Soros port beallitasai
ser = serial.Serial('COM7', 115200)

# Kezdeti koordinatak
lat1 = 46.5777591
lon1 = 24.3762672

# Adatok tarolasa
x_values = []
y_values = []
reading_data = False

# Kalman-szuro inicializalasa
f = KalmanFilter(dim_x=2, dim_z=1)
f.Q = np.array([[0.1, 0.], [0., 0.01]])
f.x = np.array([[0.], [0.]])
f.F = np.array([[1, 0.034], [0., 1.]])  
f.H = np.array([[1., 0.]])
f.B = np.array([[0.034, 0.], [0., 0.]])  
f.P = np.array([[1000., 0.], [0., 1.]])
f.R = np.array([[0.1]])

# Kalman-szuro adatainak tarolasa
filtered_values = []
trp_values = []
alfa_values = []

# GUI ablak letrehozasa
root = tk.Tk()
root.title("GPS Adatgyűjtés")

# Matplotlib abra letrehozasa
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))

line_gps, = ax1.plot([], [], 'bo-')
ax1.set_xlabel('X elmozdulás [km]')
ax1.set_ylabel('Y elmozdulás [km]')
ax1.set_title('Elmozdulások')
ax1.grid(True)

line_kalman, = ax2.plot([], [], 'r-', label='Kalman-szűrt értékek')
line_alfa, = ax2.plot([], [], 'g-', label='Mért értékek')
ax2.set_xlabel('Minta index')
ax2.set_ylabel('Szög értékek [fok]')
ax2.set_title('Kalman-szűrő által becsült és mért szögértékek')
ax2.legend(loc='upper right')

# Abrak  megjelenitese a tkinter ablakban
canvas = FigureCanvasTkAgg(fig, master=root)
canvas_widget = canvas.get_tk_widget()
canvas_widget.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

# Toolbar hozzaadasa a zoomolashoz
toolbar = NavigationToolbar2Tk(canvas, root)
toolbar.update()
canvas_widget.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

# Zoomolas lehetove tetele
mplcursors.cursor(hover=True)

def update_plot(frame):
    # Atalakttas fokba
    filtered_values_deg = [math.degrees(rad) for rad in filtered_values]
    alfa_values_deg = [math.degrees(rad) for rad in alfa_values]
    
    #Adatok frissitese a grafikonon
    #GPS ertekei 
    line_gps.set_data(x_values, y_values) 
    #Kalman szuro erteke
    line_kalman.set_data(range(len(filtered_values_deg)), filtered_values_deg)
    #A nyers adat 
    line_alfa.set_data(range(len(alfa_values_deg)), alfa_values_deg)

    ax1.relim()
    ax1.autoscale_view()
    ax2.relim()
    ax2.autoscale_view()

    return line_gps, line_kalman, line_alfa

def read_data():
    global reading_data
    while reading_data:
        line = ser.readline().decode('utf-8').strip()
        data = line.split(',')
        if len(data) >= 11:
            GPS_X = float(data[7])
            GPS_Y = float(data[8])
            lat2 = round(GPS_X * 1 / 100, 6)
            lon2 = round(GPS_Y * 1 / 100, 6)
            dx = (lon1 - lon2) * 40000 * math.cos((lat1 + lat2) * math.pi / 360) / 360
            dy = (lat1 - lat2) * 40000 / 360
            x_values.append(dx)
            y_values.append(dy)

            Mag_x = float(data[4])
            Mag_y = float(data[5])
            Mag_z = float(data[6])
            Gyro_z = float(data[11])

            b = np.array([[-1084.54496438], [787.58563366], [666.98803669]])
            Ainv = np.array([[3.01590420e-04, 2.13895351e-05, 1.09974562e-05],
                            [2.13895351e-05, 3.29023931e-04, -9.91775689e-06],
                            [1.09974562e-05, -9.91775689e-06, 3.16575957e-04]])

            h = np.array([[Mag_x, Mag_y, Mag_z]]).T
            hHat = np.matmul(Ainv, h - b)
            hHat = hHat.reshape((3, 1, 1))
            hHat = hHat[:, :, 0]
            calibratedX = hHat[0]
            calibratedY = hHat[1]

            AlfaK = math.atan2(calibratedX, calibratedY)
            Omega = Gyro_z
            alfa_values.append(AlfaK)

            f.predict(Omega)
            f.update(AlfaK)

            filtered_values.append(f.x[0, 0])
            trp_values.append(np.trace(f.P))

def start_reading():
    global reading_data
    reading_data = True
    threading.Thread(target=read_data).start()

def stop_reading():
    global reading_data
    reading_data = False

# Stilus beallitasa a gombokhoz
button_style = {
    "font": ("Helvetica", 16),
    "bg": "lightgreen",
    "fg": "black",
    "width": 10,
    "height": 2,
    "relief": tk.RAISED,
    "borderwidth": 5
}

# Gombok letrehozasa
button_frame = tk.Frame(root)
button_frame.pack(side=tk.BOTTOM, pady=20)

start_button = tk.Button(button_frame, text="Start", command=start_reading, **button_style)
start_button.pack(side=tk.LEFT, padx=20)

stop_button = tk.Button(button_frame, text="Stop", command=stop_reading, **button_style)
stop_button.pack(side=tk.RIGHT, padx=20)

# Animacio beallitasa
ani = animation.FuncAnimation(fig, update_plot, frames=None, blit=True, cache_frame_data=False)

# GUI futtatasa
root.mainloop()

# Soros port bezarasa
ser.close()
