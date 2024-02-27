import csv
import matplotlib.pyplot as plt
import numpy as np
from numpy import linalg
from scipy.linalg import sqrtm

select_columns = [4,5,6]
data_Mag_x = []
data_Mag_y = []
data_Mag_z = [] 

with open('MagnetometerDate.csv', mode='r', newline='') as file:
    reader = csv.reader(file)
    for row in reader:
        select_data = [row[i] for i in select_columns]  
        data_Mag_x.append(select_data[0])
        data_Mag_y.append(select_data[1]) 
        data_Mag_z.append(select_data[2])
      
del  data_Mag_x[0]
del  data_Mag_y[0]
del  data_Mag_z[0]


#Mag_X=list(map(float, data_Mag_x))
#Mag_Y=list(map(float, data_Mag_y))
#Mag_Z=list(map(float, data_Mag_z))

MagX = np.array(data_Mag_x,dtype=int)
MagY = np.array(data_Mag_y,dtype=int)
MagZ = np.array(data_Mag_z,dtype=int)

print(len(MagX), len(MagY), len(MagZ)) 
print(MagX.dtype, MagY.dtype, MagZ.dtype) 

def Calibrate_Mag(magX, magY, magZ):
    x2 = (magX ** 2)
    y2 = (magY ** 2)
    z2 = (magZ ** 2)
    yz = 2*np.multiply(magY, magZ)
    xz = 2*np.multiply(magX, magZ)
    xy = 2*np.multiply(magX, magY)
    x = 2*magX
    y = 2*magY
    z = 2*magZ
    d_tmp = np.ones(len(magX))
    d = np.expand_dims(d_tmp, axis=1)
    matrix = d
    vector = matrix.flatten()
    D = np.array([x2, y2, z2, yz, xz, xy, x, y, z, vector])
    D_3d = D.reshape((D.shape[0], D.shape[1], 1))
    D_3d= D_3d[:,:, 0]
    C1 = np.array([[-1, 1, 1, 0, 0, 0],
                   [1, -1, 1, 0, 0, 0],
                   [1, 1, -1, 0, 0, 0],
                   [0, 0, 0, -4, 0, 0],
                   [0, 0, 0, 0, -4, 0],
                   [0, 0, 0, 0, 0, -4]])
    
    # Equation 11 --- S = D(D.T)
    #D_T = np.transpose(D, (1, 0, 2))
    S = np.matmul(D_3d, D_3d.T)
    print("S Shape: ", S.shape)
    S11 = S[:6, :6]
    S12 = S[:6, 6:]
    S21 = S[6:, :6]
    S22 = S[6:, 6:]
    print(S22.shape)
    # Equation 15
    tmp1 = np.matmul(S12, np.matmul(np.linalg.inv(S22), S12.T))
    tmp = np.matmul(np.linalg.inv(C1), S11 - tmp1)
    eigenValue, eigenVector = np.linalg.eig(tmp)
    v1 = eigenVector[:, np.argmax(eigenValue)]
    if v1[0] < 0: v1 = -v1
    
    # Equation 13
    v2 = np.matmul(-np.matmul(np.linalg.inv(S22), S12.T), v1)
    
    # Equation 11 (part 2)
    v = np.concatenate([v1, v2]).T
    
    M = np.array([[v[0], v[5], v[4]],
                  [v[5], v[1], v[3]],
                  [v[4], v[3], v[2]]])
    
    n = np.array([[v[6]],
                  [v[7]],
                  [v[8]]])
    d = v[9]
    
    Minv = np.linalg.inv(M)
    b = -np.dot(Minv, n)
    #Ainv = np.real(1 / np.sqrt(np.dot(n.T, np.dot(Minv, n)) - d) * linalg.sqrtm(M))
    Ainv = np.real(1 / np.sqrt(np.dot(n.T, np.dot(Minv, n)) - d) * sqrtm(M))

    return Minv, b, Ainv

Minv, b, Ainv = Calibrate_Mag(MagX, MagY, MagZ)
print("Minv:", Minv)
print("b:", b)
print("Ainv:", Ainv)

fig = plt.figure(1)
ax = fig.add_subplot(111, projection='3d')
ax.scatter(MagX, MagY, MagZ, s=5, color='r')
ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.set_zlabel('Z')

u = np.linspace(0, 2 * np.pi, 100)
v = np.linspace(0, np.pi, 100)
x = np.outer(np.cos(u), np.sin(v))
y = np.outer(np.sin(u), np.sin(v))
z = np.outer(np.ones(np.size(u)), np.cos(v))
ax.plot_wireframe(x, y, z, rstride=10, cstride=10, alpha=0.5)
ax.plot_surface(x, y, z, alpha=0.3, color='b')

calibratedX = np.zeros(MagX.shape)
calibratedY = np.zeros(MagY.shape)
calibratedZ = np.zeros(MagZ.shape)

totalError = 0
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
    mag = np.dot(hHat.T, hHat)
    err = (mag[0][0] - 1)**2
    totalError += err
print("Total Error: %f" % totalError)

fig2 = plt.figure(2)
ax2 = fig2.add_subplot(111, projection='3d')

ax2.scatter(calibratedX, calibratedY, calibratedZ, s=1, color='r')
ax2.set_xlabel('X')
ax2.set_ylabel('Y')
ax2.set_zlabel('Z')

# plot unit sphere
u = np.linspace(0, 2 * np.pi, 100)
v = np.linspace(0, np.pi, 100)
x = np.outer(np.cos(u), np.sin(v))
y = np.outer(np.sin(u), np.sin(v))
z = np.outer(np.ones(np.size(u)), np.cos(v))
ax2.plot_wireframe(x, y, z, rstride=10, cstride=10, alpha=0.5)
ax2.plot_surface(x, y, z, alpha=0.3, color='b')

plt.show()