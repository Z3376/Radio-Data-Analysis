#!/Users/harsh/anaconda2/bin/python

from os.path import getsize
import sys
import matplotlib.pyplot as plt
import numpy as np
import pyfftw
import threading

FFT			=	[]

def fft(fftw,a):
	global FFT
	FFT.append(fftw(a))

def amplitude(a):
	a							=	(a.imag**2+a.real**2)**0.5
	return a

if(len(sys.argv)==2):
	file_name					=	sys.argv[1]
elif(len(sys.argv)==1):
	file_name					=	raw_input('.mbr File: ')
else:
	print('Too many arguments. Enter onyl .mbr File name.')
	exit()

size							=	getsize(file_name)
t_p								=	size/1056						#total_packets
b_c								=	1024							#bit_counter
s_c								=	0								#sample_counter
p_1s							=	t_p/32							#packets_in_1s
s_count							=	t_p/p_1s
buff							=	np.zeros((t_p,1024),dtype='complex')
x_fftw							=	pyfftw.empty_aligned(512,dtype='complex')
y_fftw							=	pyfftw.empty_aligned(512,dtype='complex')
z								=	np.zeros((s_count,256), dtype='complex')

l_t								=	[i for i in range(256)]
for j in range(128):
	l_t[j+128]					-=	256

x_fftw							=	pyfftw.FFTW(x_fftw,x_fftw)
y_fftw							=	pyfftw.FFTW(y_fftw,y_fftw)

p1			=	threading.Thread(target=fft,args=(x_fftw,buff[0::2],))
p2			=	threading.Thread(target=fft,args=(y_fftw,buff[1::2],))

fopen							=	open(file_name,'rb')
fopen.read(32)

for j in range(s_count):
	while(b_c<(j+1)*p_1s*1024):
		buff[b_c%1024]			=	l_t[int(str(fopen.read(1)).encode('hex'),16)]
		b_c						+=	1

		if(b_c%1024==0):
			X					=	fft(x_fftw,buff[0::2])
			Y					=	fft(y_fftw,buff[1::2])
			z[j]				+=	X[:256]*np.conj(Y[:256])
			x[j]				+=	X[:256]*np.conj(X[:256])
			y[j]				+=	Y[:256]*np.conj(Y[:256])
			fopen.read(32)
	z[j][0]						=	z[j][1]
	x[j][0]						=	x[j][1]
	y[j][0]						=	y[j][1]
	z[j]						=	z[j]/float(p_1s)/np.sqrt(x[j]*y[j])
	x[j]						=	x[j]/float(p_1s)
	y[j]						=	y[j]/float(p_1s)
	sys.stderr.write('\x1b[2J\x1b[H')
	print('Calculating Cross Correlation')
	print 'Progress:',float(j+1)*100/s_count,'%'

fopen.close()

sys.stderr.write('\x1b[2J\x1b[H')
print('Calculating Cross Correlation')
print 'Progress: 100 %'

z_file							=	open('z_corr.dat','w+')
z_file.write(z)

plt.figure()
plt.imshow(amplitude(z.T))
plt.colorbar()
plt.xlabel('Frequency Channels')
plt.ylabel('Time')
plt.show()

exit()
