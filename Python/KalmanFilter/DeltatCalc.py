import csv
import numpy as np

select_columns = [0]
Time =[]
DeltaT = []
with open('Kalmanfilter.csv', mode='r', newline='') as file:
    reader = csv.reader(file)
    for row in reader:
        select_data = [row[i] for i in select_columns]
        Time.append(select_data[0])
            
del Time[0]
Time_ok=np.array(Time, dtype=int)
for i in range(len(Time_ok)-1): #2383
   DeltaT.append((Time_ok[i+1]-Time_ok[i])/1000)
   if(DeltaT[i]<0):
       print("Poz",i+3)
print(DeltaT)
print("Sum:",sum(DeltaT))
print("Lenght",len(DeltaT))
print("Avrage :",sum(DeltaT)/len(DeltaT))

#DELTAT = 0.033