import csv
import matplotlib.pyplot as plt
import numpy as np
from filterpy.kalman import KalmanFilter
import numpy as np
from math import atan2

def return_magnetometer_arrays():
    select_columns = [4, 5, 6, 11]
    data_Mag_x = []
    data_Mag_y = []
    data_Mag_z = []
    data_Gyro_z =[]

    with open('Kalmanfilter.csv', mode='r', newline='') as file:
        reader = csv.reader(file)
        for row in reader:
            select_data = [row[i] for i in select_columns]
            data_Mag_x.append(select_data[0])
            data_Mag_y.append(select_data[1])
            data_Mag_z.append(select_data[2])
            data_Gyro_z.append(select_data[3])
    del data_Mag_x[0]
    del data_Mag_y[0]
    del data_Mag_z[0]
    del data_Gyro_z[0]
    
    MagX = np.array(data_Mag_x, dtype=int)
    MagY = np.array(data_Mag_y, dtype=int)
    MagZ = np.array(data_Mag_z, dtype=int)
    GyroZ = np.array(data_Mag_z, dtype=int)

    return MagX, MagY, MagZ,GyroZ

# Kalman-szűrő inicializálása
f = KalmanFilter(dim_x=2, dim_z=1)
f.Q = np.array([[0.1, 0.], [0., .1]])
f.x = np.array([[0.], [0.]])
f.F = np.array([[1., 0.034], [0., 1.]])  # Állapotátmenet mátrix masodik DeltaT
f.H = np.array([[1., 0.]])
f.B = np.array([[0.034, 0.]])  # Vezérlési átmenet mátrix  DeltaT felso elem
f.P = np.array([[5, 0.], [0., 5]])
f.R = np.array([[0.01]])
f.bk = np.array([[0.1]])  # Offset

def read_sensor():
    b=np.array([[-1084.54496438],
                [  787.58563366],
                [  666.98803669]])
    
    Ainv =np.array([[ 3.01590420e-04 , 2.13895351e-05 , 1.09974562e-05],
                    [ 2.13895351e-05 , 3.29023931e-04, -9.91775689e-06],
                    [ 1.09974562e-05, -9.91775689e-06 , 3.16575957e-04]])
    
    MagX,MagY,MagZ,GyroZ =return_magnetometer_arrays()
    
    calibratedX = np.zeros(MagX.shape)
    calibratedY = np.zeros(MagY.shape)
    calibratedZ = np.zeros(MagZ.shape)
    #alpha_store = []
    #omega_store = []
    filtered_values = []
    trp = []
    Alfa =[]
    for i in range(len(MagX)):
        h = np.array([[MagX[i], MagY[i], MagZ[i]]]).T
        hHat = np.matmul(Ainv, h-b)
        #print(hHat)
        hHat = hHat.reshape((3, 1, 1))
        #print(hHat.shape)
        hHat = hHat[:, :, 0]
        calibratedX[i] = hHat[0]
        calibratedY[i] = hHat[1]
        calibratedZ[i] = hHat[2]
        AlfaK = atan2(calibratedX[i],calibratedY[i])
        Omega = (GyroZ[i] * 250) / (2**15)
        Alfa.append(AlfaK)
        # Előrejelzés lépés
        f.predict(Omega) #omagak
    

        # Frissítés lépés
        f.update(AlfaK) #AlfaK
    
        # Az új becült állapot kiíratása
        #print("Becült állapot:",f.x)
        filtered_values.append(f.x[1,0])
        trp.append(np.trace(f.P))
        
    return filtered_values, trp,Alfa

# Kalman-szűrő futtatása
filtered_values, trp ,Alfa = read_sensor()

plt.subplot(211)
plt.plot(filtered_values,'r',Alfa,'g')
plt.xlabel('Idő')
plt.ylabel('Szűrt értékek')
plt.title('Kalman-szűrő által becsült értékek')

plt.subplot(212)
plt.plot(trp)
plt.xlabel('')
plt.ylabel('')
plt.title('TRP')
plt.show()
