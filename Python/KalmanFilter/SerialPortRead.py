import matplotlib.pyplot as plt
import numpy as np
from filterpy.kalman import KalmanFilter
import serial
from math import atan2
import time

ser = serial.Serial('COM4', 115200)

# Kalman-szűrő inicializálása
f = KalmanFilter(dim_x=2, dim_z=1)
f.Q = np.array([[0.1, 0.], [0., .1]])
f.x = np.array([[0.], [0.]])
f.F = np.array([[1., 0.034], [0., 1.]])
f.H = np.array([[1., 0.]])
f.B = np.array([[0.034, 0.]])
f.P = np.array([[5, 0.], [0., 5]])
f.R = np.array([[0.01]])
f.bk = np.array([[0.1]])

def read_sensor():
    b = np.array([[-1084.54496438], [787.58563366], [666.98803669]])
    Ainv = np.array([[3.01590420e-04, 2.13895351e-05, 1.09974562e-05],
                     [2.13895351e-05, 3.29023931e-04, -9.91775689e-06],
                     [1.09974562e-05, -9.91775689e-06, 3.16575957e-04]])

    filtered_values = []
    trp = []
    Alfa = []

    start_time = time.time()

    while time.time() - start_time < 10:  # 10 másodpercig fut a ciklus
        line = ser.readline().decode('utf-8').strip()

        data = line.split(',')
        
        if len(data) >= 11:
            Mag_x = float(data[4])
            Mag_y = float(data[5])
            Mag_z = float(data[6])
            Gyro_z = float(data[10])

            h = np.array([[Mag_x, Mag_y, Mag_z]]).T
            hHat = np.matmul(Ainv, h - b)
            hHat = hHat.reshape((3, 1, 1))
            hHat = hHat[:, :, 0]
            calibratedX = hHat[0]
            calibratedY = hHat[1]
            AlfaK = atan2(calibratedX, calibratedY)
            print(AlfaK)
            Omega = Gyro_z
            Alfa.append(AlfaK)

            # Előrejelzés lépés
            f.predict(Omega)

            # Frissítés lépés
            f.update(AlfaK)

            # Az új becült állapot kiíratása
            filtered_values.append(f.x[1, 0])
            trp.append(np.trace(f.P))

            time.sleep(0.1)  # Adj egy kis időt a rendszernek feldolgozni az adatokat

    return filtered_values, trp, Alfa

# Kalman-szűrő futtatása
filtered_values, trp, Alfa = read_sensor()

# Az eredmények ábrázolása
plt.subplot(211)
plt.plot(filtered_values, 'r', Alfa, 'g')
plt.xlabel('Idő')
plt.ylabel('Szűrt értékek')
plt.title('Kalman-szűrő által becsült értékek')

plt.subplot(212)
plt.plot(trp)
plt.xlabel('')
plt.ylabel('')
plt.title('TRP')
plt.show()

ser.close()
print("Program leállítva.")
