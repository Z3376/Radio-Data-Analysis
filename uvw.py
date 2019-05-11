import numpy as np
import matplotlib.pyplot as plt

def read_file(a,i):
	b		=	[]
	fopen	=	open(a,'r')
	for lines in fopen:
		col	=	lines.split()
		b.append(col[i])
	fopen.close()
	return b

ra=23.38
dec=58.8
lst=1.19
h=ra-lst

x=[0 for i in range(21)]
y=[0 for i in range(21)]
z=[0 for i in range(21)]


t=[[0 for j in range(3)] for i in range(3)]
t[0][0]=np.sin(h)
t[0][1]=np.cos(h)
t[1][0]=-1*np.sin(dec)*np.cos(h)
t[1][1]=np.sin(dec)*np.sin(h)
t[1][2]=np.cos(dec)
t[2][0]=np.cos(dec)*np.cos(h)
t[2][1]=-1*np.cos(dec)*np.sin(h)
t[2][2]=np.sin(dec)


u=read_file("xyz.txt",0)
v=read_file("xyz.txt",1)

a=[[0 for i in range(len(u))] for i in range(2)]

a[0]=u
a[1]=v

z=np.fft.fft(a)

plt.imshow(np.real(z))
plt.show()



