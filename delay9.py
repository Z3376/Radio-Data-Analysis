#!/usr/bin/python

from os.path import getsize
from os.path import isfile
import sys
import matplotlib.pyplot as plt
import numpy as np
import time
import pyfftw

t0	=	time.time()

########-----------------------------########
#			Function Definations
########-----------------------------########

def read_file(a,i):
	b		=	[]
	fopen	=	open(a,'r')
	for lines in fopen:
		col	=	lines.split()
		b.append(col[i])
	fopen.close()
	return b

def amplitude(a):
	a	=	(a.imag**2+a.real**2)**0.5
	return a

def mean(a):
	mean_a	=	np.zeros(256, dtype='complex')
	for i in range(256):
		for j in range(a_count):
			mean_a[i]	+=	a[j][i]
		mean_a[i]	=	mean_a[i]/a_count
	return mean_a

########-----------------------------########
#				Input Arguments
########-----------------------------########

if(len(sys.argv)==2 and sys.argv[1]=='-d'):
	file_name		=	'ch00_B0833-45_20150612_191438_010_1'
	avg				=	1
elif(len(sys.argv)==3):
	file_name_1		=	sys.argv[1]
	avg				=	int(sys.argv[3])
elif(len(sys.argv)==2):
	file_name_1		=	sys.argv[1]
	avg				=	int(raw_input('No. of Packets to be averaged: '))
elif(len(sys.argv)==1):
	file_name_1		=	raw_input('.mbr File: ')
	avg				=	int(raw_input('No. of Packets to be averaged: '))
else:
	print('Too many arguments. Enter onyl .mbr File name and No. of Packets to be averaged.')
	exit()

########-----------------------------########
#			Initialising Variables
########-----------------------------########

print 'Reading Files'

buff_x	=	read_file(file_name,0)

print ':Completed'

l			=	len(buff_x)
s_f			=	33000000
o_f			=	16												#oversampling_factor
t_p			=	l/512
a_count		=	t_p/avg							
tbwp		=	avg												#time-bandwidth-product

x_fftw		=	pyfftw.empty_aligned(512,dtype='complex')
y_fftw		=	pyfftw.empty_aligned(512,dtype='complex')
padding		=	np.zeros(256+(512*(o_f-1)))
z			=	np.zeros((10,a_count,256), dtype='complex')
mean_z		=	np.zeros((10,256), dtype='complex')
Z			=	np.zeros((10,o_f*512), dtype='complex')
phase		=	np.zeros((10,256), dtype='complex')
n			=	[0 for i in range(10)]
delay		=	[0 for i in range(10)]
amp			=	[0 for i in range(10)]

x_fftw		=	pyfftw.FFTW(x_fftw,x_fftw)						#FFTW_matrix
y_fftw		=	pyfftw.FFTW(y_fftw,y_fftw)

for k in range(10):
	a=[0 for i in range(k*l/100)]
	buff_y=a+buff_x
	for j in range(a_count):
		for i in range(avg):
			X		=	x_fftw(buff_x[(j)*avg+i*512:(j)*avg+(i+1)*512])
			Y		=	y_fftw(buff_y[(j)*avg+i*512:(j)*avg+(i+1)*512])
			z[k][j]	+=	X[:256]*np.conj(Y[:256])
		z[k][j][0]	=	z[k][j][1]
		z[k][j]	=	z[k][j]/float(avg)

	mean_z[k]	=	mean(z[k])

	Z[k]	=	np.fft.fftshift(np.fft.ifft(np.concatenate((mean_z[k],padding))))

	max_x	=	0
	for x_m in range(len(Z[k])):
		if(Z[k][x_m]==max(Z[k])):
			max_x	=	x_m

	amp[k]	=	max(Z[k])

	n[k]	=	max_x-(o_f*512)/2
	delay[k]=	float(n[k])/float(o_f)/float(s_f)

	for i in range(len(mean_z[k])):
		phase[k][i]=np.angle(mean_z[k][i])

	print k

print "Total Time Elapsed:", time.time()-t0

plt.figure(1)
plt.plot(phase)
plt.figure(2)
plt.plot(delay)
plt.figure(3)
plt.plot(amp,delay)
plt.show()

exit()
