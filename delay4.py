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

def amplitude(a):
	a							=	(a.imag**2+a.real**2)**0.5
	return a

def mean(a):
	mean_a						=	np.zeros(256, dtype='complex')
	for i in range(256):
		for j in range(a_count):
			mean_a[i]			+=	a[j][i]
		mean_a[i]				=	mean_a[i]/a_count
	return mean_a

def rms(a,mean_a):
	rms_a						=	np.zeros(256, dtype='complex')
	for i in range(256):
		for j in range(a_count):
			rms_a[i]			+=	(a[j][i]-mean_a[i])**2
		rms_a[i]				=	np.sqrt(rms_a[i]/a_count)
	return rms_a

########-----------------------------########
#				Input Arguments
########-----------------------------########

if(len(sys.argv)==2 and sys.argv[1]=='-d'):
	file_name					=	'ch07_CASOBSTEST_20170301_143236_000.mbr'
	avg							=	1000
elif(len(sys.argv)==3):
	file_name					=	sys.argv[1]
	avg							=	int(sys.argv[2])
elif(len(sys.argv)==2):
	file_name					=	sys.argv[1]
	avg							=	int(raw_input('No. of Packets to be averaged: '))
elif(len(sys.argv)==1):
	file_name					=	raw_input('.mbr File: ')
	avg							=	int(raw_input('No. of Packets to be averaged: '))
else:
	print('Too many arguments. Enter onyl .mbr File name and No. of Packets to be averaged.')
	exit()

########-----------------------------########
#			Initialising Variables
########-----------------------------########

size							=	getsize(file_name)
t_p								=	size/1056										#total_packets
b_c								=	0												#byte_counter
#s_c								=	0											#sample_counter
o_f								=	16												#oversampling_factor
s_f								=	33000000										#sampling_frequency
b_w								=	s_f/2											#bandwidth
a_count							=	t_p/avg							
tbwp							=	avg												#time-bandwidth-product
p_1s							=	t_p/30											#packets_in_1s
s_avg							=	p_1s/avg										#no._of_avg_in_1_sec
s_count							=	t_p/p_1s
buff							=	np.zeros(1024,dtype='complex')
x_fftw							=	pyfftw.empty_aligned(512,dtype='complex')
y_fftw							=	pyfftw.empty_aligned(512,dtype='complex')
padding							=	np.zeros(256+(512*(o_f-1)))
z								=	np.zeros((a_count,256), dtype='complex')
x								=	np.zeros((a_count,256), dtype='complex')
y								=	np.zeros((a_count,256), dtype='complex')
z_sec							=	np.zeros((s_count,256), dtype='complex')
Z								=	np.zeros((s_count,o_f*512), dtype='complex')
delay							=	np.zeros(s_count)

x_fftw							=	pyfftw.FFTW(x_fftw,x_fftw)						#FFTW_matrix
y_fftw							=	pyfftw.FFTW(y_fftw,y_fftw)

l_t								=	[i for i in range(256)]							#look-up_table
for j in range(128):
	l_t[j+128]					-=	256

########-----------------------------########
#		Calculating Cross Correlation
########-----------------------------########

print('Calculating Cross Correlation')

fopen							=	open(file_name,'rb')							#reading_mbr_file_starts
fopen.read(32)

for j in range(a_count):
	while(b_c<(j+1)*avg*1024):
		buff[b_c%1024]			=	l_t[int(str(fopen.read(1)).encode('hex'),16)]
		b_c						+=	1

		if(b_c%1024==0):
			X					=	x_fftw(buff[0::2])
			Y					=	y_fftw(buff[1::2])
			z[j]				+=	X[:256]*np.conj(Y[:256])
			x[j]				+=	X[:256]*np.conj(X[:256])
			y[j]				+=	Y[:256]*np.conj(Y[:256])
			fopen.read(32)
	z[j][0]						=	z[j][1]
	x[j][0]						=	x[j][1]
	y[j][0]						=	y[j][1]
	z[j]						=	z[j]/float(avg)/np.sqrt(x[j]*y[j])
	x[j]						=	x[j]/float(avg)
	y[j]						=	y[j]/float(avg)
	sys.stderr.write('\x1b[2J\x1b[H')
	print('Calculating Cross Correlation')
	print 'Progress:',float(j+1)*100/a_count,'%'

fopen.close()

########-----------------------------########
#			Calculating Efficiency
########-----------------------------########

print('Calculating Efficiency')

mean_x_o						=	mean(x)
mean_y_o						=	mean(y)

rms_x_o							=	rms(x,mean_x_o)
rms_y_o							=	rms(y,mean_y_o)

SNR_x_obs						=	mean_x_o/rms_x_o
SNR_y_obs						=	mean_y_o/rms_y_o
SNR_exp							=	float(np.sqrt(tbwp))

efficiency_x					=	SNR_x_obs/SNR_exp
efficiency_y					=	SNR_y_obs/SNR_exp

########-----------------------------########
#			Clearing Bad Channels
########-----------------------------########

print('Clearing Bad Channels')

for i in range(256):
	if(efficiency_x[i]<0.81 or efficiency_y[i]<0.9):
		for j in range(a_count):
			z[j][i]				=	0

for i in range(s_count):
	for j in range(s_avg):
		z_sec[i]				+=	z[(s_avg*i)+j]
	z_sec[i]					/=	s_avg

########-----------------------------########
#			  Hilbert Transform
########-----------------------------########

print('Performing Hilbert Transform')

for k in range(s_count):
	Z[k]						=	np.fft.fftshift(np.fft.ifft(np.concatenate((z_sec[k],padding))))

	max_x						=	0
	for x in range(len(Z[k])):
		if(Z[k][x]==max(Z[k])):
			max_x				=	x

	n							=	max_x-o_f*512/2
	delay[k]					=	float(n)/float(o_f)/float(s_f)
	print 'Calculated Delay',k,':',delay[k]

########-----------------------------########

z_file							=	open('z.dat','w+')							#saving_cross_corr_results
z_file.write(z)

print "Total Time Elapsed:", time.time()-t0

########-----------------------------########
#			  Plotting Results
########-----------------------------########

plt.figure(1)
plt.plot(efficiency_x)
plt.plot(efficiency_y)
plt.plot([0.81 for y in range(256)])
plt.plot([0.9 for y in range(256)])
plt.xlabel('Frequency Channels')
plt.ylabel('Efficiency')
plt.figure(3)
plt.imshow(amplitude(Z))
plt.figure(4)
plt.plot(delay*(10**9))
plt.xlabel('Time(s)')
plt.ylabel('Delay(ns)')
plt.figure(2)
plt.plot(amplitude(Z[5]))
plt.figure(5)
plt.plot(amplitude(Z[-5]))
plt.figure(6)
plt.imshow(amplitude(z_sec.T))
plt.colorbar()
plt.xlabel('Time(s)')
plt.ylabel('Frequency Channels')
plt.figure(7)
plt.plot(amplitude(z_sec.T))
plt.figure(8)
plt.plot(amplitude(z_sec[15]))
plt.plot(z_sec[15].real)
plt.plot(z_sec[15].imag)
plt.show()

exit()
