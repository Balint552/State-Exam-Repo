from math import atan2
import serial
import csv

ser = serial.Serial('COM4', 115200)
g = 9.81

with open('Kalmanfilter.csv', mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(["Timestamp", "Accel_X", "Accel_Y", "Gyro_Z", "Mag_X", "Mag_Y", "Mag_Z", "GPS_x", "GPS_Y","Calc_Accel_X","Calc_Accel_Y","Calc_Gyro_Z","Calc_Mag_X_Y"])

    while True:
        line = ser.readline().decode('utf-8').strip()
        data = line.split(',')

        if len(data) == 9:  
            #TIME_STAP
            #time_stamp = float(data[0])
            #Calc_TIME_STAP = (time_stamp/1000)
            #data.append(Calc_TIME_STAP)
            
            # ACCEL_X
            accel_x = float(data[1])
            Calc_Accel_X = (accel_x * g) / (2**15)
            data.append(Calc_Accel_X)
            
             # ACCEL_X
            accel_y = float(data[2])
            Calc_Accel_Y = (accel_y * g) / (2**15)
            data.append(Calc_Accel_Y)
            
            # GYRO_z
            gyro_z = float(data[3])
            Calc_Gyro_Z = (gyro_z * 250) / (2**15)
            data.append(Calc_Gyro_Z)
            
            # MAG_X_Y
            mag_x = float(data[4])
            mag_y = float(data[5])
            Calc_Mag_X_Y = atan2(mag_x,mag_y)
            data.append(Calc_Mag_X_Y)
            
            writer.writerow(data)
            print(data)
