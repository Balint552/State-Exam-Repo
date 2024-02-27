import numpy as np
from numpy import linalg

magX=[1, 2, 3]
print(magX)
magY=[4, 5, 6]
print(magY)
magZ=[7, 8, 9]
print(magZ)

magX=np.array(magX,dtype=int)
magY=np.array(magY,dtype=int)
magZ=np.array(magZ,dtype=int)
print(magX)
print(magY)
print(magZ)
x2 = (magX ** 2)
print("X2")
print(x2)
y2 = (magY ** 2)
print("y2")
print(y2)
z2 = (magZ ** 2)
print("Z2")
print(z2)
yz = 2*np.multiply(magY, magZ)
print("yz")
print(yz)
xz = 2*np.multiply(magX, magZ)
print("xz")
print(xz)
xy = 2*np.multiply(magX, magY)
print("xy")
print(xy)
x = 2*magX
print(x)
y = 2*magY
print(y)
z = 2*magZ
print(z)

d_tmp = np.ones(len(magX))
print(d_tmp)
d = np.expand_dims(d_tmp, axis=1)
print(d)
matrix = d
vector = matrix.flatten()
print(vector)

D=np.array([x2,y2,z2,yz,xz,xy,x,y,z,vector])
print("D = ")
print(D)
D_3d = D.reshape((D.shape[0], D.shape[1], 1))
D_3d= D_3d[:,:, 0]
print("D_3d = ")
print(D_3d)

