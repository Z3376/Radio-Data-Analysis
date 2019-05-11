#!/Users/harsh/anaconda2/bin/python

from os.path import getsize
from os.path import isfile
import sys
import matplotlib.pyplot as plt
import numpy as np
import pyqtgraph as pqt

def amplitude(a):
	a						=	(a.imag**2+a.real**2)**0.5
	return a

def derivative(a):
	s						=	[0 for i in range(len(a)-1)]
	for i in range(len(a)-1):
		s[i]				=	a[i+1]-a[i]
	return s

if(len(sys.argv)==3):
	file_name				=	sys.argv[1]
	p_count					=	int(sys.argv[2])
elif(len(sys.argv)==2):
	file_name				=	sys.argv[1]
	p_count					=	int(raw_input("No. of Packets: "))
elif(len(sys.argv)==1):
	file_name				=	raw_input("MBR File: ")
	p_count					=	int(raw_input("No. of Packets: "))
else:
	exit()

size						=	getsize(file_name)
b_c							=	0								#bit_counter
p_c							=	0								#bit_counter_in_a_packet
o_f							=	16								#oversampling_factor
s_f							=	33000000						#sampling_frequency
buff						=	[0 for i in range(1024)]
z							=	np.zeros(256, dtype='complex')
x_A							=	np.zeros(256, dtype='complex')
y_A							=	np.zeros(256, dtype='complex')

fopen						=	open(file_name,'rb')

while(b_c<p_count*1056):
	if(not(b_c%1056)):
		fopen.read(32)
		b_c					+=	32
	buff[p_c%1024]			=	int(str(fopen.read(1)).encode('hex'),16)
	b_c						+=	1
	p_c						+=	1

	if(buff[(p_c-1)%1024]>255):
		print buff[(p_c-1)%1024]

	if(buff[(p_c-1)%1024]>127):
		buff[(p_c-1)%1024]	=	buff[(p_c-1)%1024]-256

	if(p_c%1024==0):
		X					=	np.fft.fft(buff[::2])
		Y					=	np.fft.fft(buff[1::2])
		z					+=	X[:256]*np.conj(Y[:256])
		x_A					+=	X[:256]*np.conj(X[:256])
		y_A					+=	Y[:256]*np.conj(Y[:256])

fopen.close()

z							=	z/p_count
z[0]						=	0
x_A							=	x_A/p_count
y_A							=	y_A/p_count
padding						=	np.zeros(256+(512*(o_f-1)))

Z							=	np.fft.fftshift(np.fft.ifft(np.concatenate((z,padding))))
Z_amp						=	np.fft.fftshift(np.fft.ifft(np.concatenate((amplitude(z),padding))))
X_A							=	np.fft.fftshift(np.fft.ifft(np.concatenate((x_A,padding))))
Y_A							=	np.fft.fftshift(np.fft.ifft(np.concatenate((y_A,padding))))

max_x						=	0
for x in range(len(Z)):
	if(Z[x]==max(Z)):
		max_x				=	x

n							=	max_x-o_f*512/2
delay						=	float(n)/float(o_f)/float(s_f)

print "Calculated Delay: ", delay

plt.figure()
plt.plot(amplitude(Z))
plt.figure()
plt.plot(amplitude(Z_amp))
plt.figure()
plt.plot(amplitude(Z_amp))
plt.plot(amplitude(Z),"k")
plt.plot(amplitude(X_A),"b")
plt.plot(amplitude(Y_A),"r")
plt.figure()
plt.plot(Z.imag,"b")
plt.figure()
plt.plot(amplitude(z))
plt.plot(z.real,"r")
plt.plot(z.imag,"b")
plt.figure()
plt.plot(np.angle(z))
plt.show()
