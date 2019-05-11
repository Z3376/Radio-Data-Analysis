#!/usr/bin/python

from os.path import getsize
import sys
import matplotlib.pyplot as plt
import numpy as np
import scipy.fftpack.fft

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

if(len(sys.argv)==2 and sys.argv[1]=='-d'):
	file_name					=	'ch07_CASOBSTEST_20170301_143236_000.mbr'
	avg							=	1000										#number_of_packets_to_be_integrated/averaged
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

size							=	getsize(file_name)
t_p								=	size/1056										#total_packets
b_c								=	0												#byte_counter
a_count							=	t_p/avg							
tbwp							=	avg												#time-bandwidth-product
buff_x							=	np.zeros(512,dtype='complex')
buff_y							=	np.zeros(512,dtype='complex')
x								=	np.zeros((a_count,256), dtype='complex')
y								=	np.zeros((a_count,256), dtype='complex')

l_t								=	[i for i in range(256)]							#look-up_table
for j in range(128):
	l_t[j+128]					-=	256

print('Calculating Auto Correlation')

fopen							=	open(file_name,'rb')							#reading_mbr_file_starts
fopen.read(32)

for j in range(a_count):
	while(b_c<(j+1)*avg*512):
		buff_x[b_c%512]			=	l_t[int(str(fopen.read(1)).encode('hex'),16)]
		buff_y[b_c%512]			=	l_t[int(str(fopen.read(1)).encode('hex'),16)]
		b_c						+=	1

		if(b_c%512==0):
			X					=	np.fft.fft(buff_x)
			Y					=	np.fft.fft(buff_y)
			x[j]				+=	X[:256]*np.conj(X[:256])						
			y[j]				+=	Y[:256]*np.conj(Y[:256])
			fopen.read(32)
	x[j][0]						=	x[j][1]
	y[j][0]						=	y[j][1]
	x[j]						=	x[j]/float(avg)
	y[j]						=	y[j]/float(avg)
	sys.stderr.write('\x1b[2J\x1b[H')												#to_show_progress(may_slow_down_the_code)
	print('Calculating Auto Correlation')
	print('Progress:',float(j+1)*100/a_count,'%')

fopen.close()

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

plt.figure(1)
plt.plot(efficiency_x)
plt.plot(efficiency_y)
plt.plot([0.81 for y in range(256)])
plt.plot([0.9 for y in range(256)])
plt.xlabel('Frequency Channels')
plt.ylabel('Efficiency')
plt.show()

exit()
