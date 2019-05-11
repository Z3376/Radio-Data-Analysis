from mpl_toolkits.mplot3d import axes3d
import matplotlib.pyplot as plt
import cv2
import numpy as np

def amplitude(a):
	a							=	(a.imag**2+a.real**2)**0.5
	return a

f=np.loadtxt('xyz.txt')
u=f[:,0]
v=f[:,1]
w=f[:,2]

plt.figure()
plt.plot(u,v,'.')
plt.savefig('uv.png')

plt.figure()
img=cv2.imread('uv11.png')

fft=np.fft.fft2(img)

plt.imshow(amplitude(fft))

fig=plt.figure()
ax=fig.add_subplot(111,projection='3d')
ax.scatter(u,v,w)

plt.show()