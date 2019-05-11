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

def rms(a,mean_a):
	rms_a	=	np.zeros(256, dtype='complex')
	for i in range(256):
		for j in range(a_count):
			rms_a[i]	+=	(a[j][i]-mean_a[i])**2
		rms_a[i]	=	np.sqrt(rms_a[i]/a_count)
	return rms_a

########-----------------------------########
#				Input Arguments
########-----------------------------########

if(len(sys.argv)==2 and sys.argv[1]=='-d'):
	file_name_1		=	'ch07_CASOBSTEST_20170301_143236_0001.txt'
	file_name_2		=	'ch07_CASOBSTEST_20170301_143236_0001.txt'
	avg				=	100
elif(len(sys.argv)==4):
	file_name_1		=	sys.argv[1]
	file_name_2		=	sys.argv[2]
	avg				=	int(sys.argv[3])
elif(len(sys.argv)==3):
	file_name_1		=	sys.argv[1]
	file_name_2		=	sys.argv[2]
	avg				=	int(raw_input('No. of Packets to be averaged: '))
elif(len(sys.argv)==2):
	file_name_1		=	sys.argv[1]
	file_name_2		=	raw_input('.mbr File: ')
	avg				=	int(raw_input('No. of Packets to be averaged: '))
elif(len(sys.argv)==1):
	file_name_1		=	raw_input('.mbr File: ')
	file_name_2		=	raw_input('.mbr File: ')
	avg				=	int(raw_input('No. of Packets to be averaged: '))
else:
	print('Too many arguments. Enter onyl .mbr File name and No. of Packets to be averaged.')
	exit()

########-----------------------------########
#			Initialising Variables
########-----------------------------########

print 'Reading Files'

buff_x	=	read_file(file_name_1,0)
buff_y	=	read_file(file_name_2,1)

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
z			=	np.zeros((a_count,256), dtype='complex')
x			=	np.zeros((a_count,256), dtype='complex')
y			=	np.zeros((a_count,256), dtype='complex')
Z			=	np.zeros(o_f*512, dtype='complex')
X_A			=	np.zeros(o_f*512, dtype='complex')
Y_A			=	np.zeros(o_f*512, dtype='complex')
phase		=	np.zeros(o_f*512, dtype='complex')
n			=	0
delay		=	0

x_fftw		=	pyfftw.FFTW(x_fftw,x_fftw)						#FFTW_matrix
y_fftw		=	pyfftw.FFTW(y_fftw,y_fftw)

########-----------------------------########
#		Calculating Cross Correlation
########-----------------------------########


print 'Calculating Cross Correlation'

for j in range(a_count):
	for i in range(avg):
		X		=	np.fft.fft(buff_x[(j)*avg+i*512:(j)*avg+(i+1)*512])
		Y		=	np.fft.fft(buff_y[(j)*avg+i*512:(j)*avg+(i+1)*512])
		z[j]	+=	X[:256]*np.conj(Y[:256])
		x[j]	+=	X[:256]*np.conj(X[:256])
		y[j]	+=	Y[:256]*np.conj(Y[:256])
	z[j][0]	=	z[j][1]
	x[j][0]	=	x[j][1]
	y[j][0]	=	y[j][1]
	z[j]	=	z[j]/float(avg)
	x[j]	=	x[j]/float(avg)
	y[j]	=	y[j]/float(avg)
#	sys.stderr.write('\x1b[2J\x1b[H')
#	print('Calculating Cross Correlation')
#	print 'Progress:',float(j+1)*100/a_count,'%'
print ':Completed'

########-----------------------------########
#			Calculating Efficiency
########-----------------------------########

print 'Calculating Efficiency' 

mean_x_o		=	mean(x)
mean_y_o		=	mean(y)

rms_x_o			=	rms(x,mean_x_o)
rms_y_o			=	rms(y,mean_y_o)

SNR_x_obs		=	mean_x_o/rms_x_o
SNR_y_obs		=	mean_y_o/rms_y_o
SNR_exp			=	float(np.sqrt(tbwp))

efficiency_x	=	SNR_x_obs/SNR_exp
efficiency_y	=	SNR_y_obs/SNR_exp

print ':Completed'

########-----------------------------########
#			Clearing Bad Channels
########-----------------------------########

#print 'Clearing Bad Channels'

#for i in range(256):
#	if(efficiency_x[i]<0.81 or efficiency_y[i]<0.9):
#		for j in range(a_count):
#			z[j][i]	=	0

#print ':Completed'

########-----------------------------########
#			  Hilbert Transform
########-----------------------------########

print 'Performing Hilbert Transform'

Z	=	np.fft.fftshift(np.fft.ifft(np.concatenate((mean(z),padding))))
X_A	=	np.fft.fftshift(np.fft.ifft(np.concatenate((mean_x_o,padding))))
Y_A	=	np.fft.fftshift(np.fft.ifft(np.concatenate((mean_y_o,padding))))

max_x	=	0
for x_m in range(len(Z)):
	if(Z[x_m]==max(Z)):
		max_x	=	x_m

n		=	max_x-(o_f*512)/2
delay	=	float(n)/float(o_f)/float(s_f)
print 'Calculated Relative Delay:',n/float(o_f)
print 'Calculated Delay(ns):',delay*(10**9),"ns"

for i in range(len(Z)):
	phase[i]=np.angle(Z[i])

print ':Completed'

########-----------------------------########

#z_file							=	open('z.dat','w+')							#saving_cross_corr_results
#z_file.write(z)

print "Total Time Elapsed:", time.time()-t0

########-----------------------------########
#			  Plotting Results
########-----------------------------########

plt.figure(1)
plt.plot(efficiency_x)
plt.plot(efficiency_y)
plt.xlabel('Frequency Channels')
plt.ylabel('Efficiency')
plt.figure(2)
plt.plot(phase)
plt.figure(4)
plt.plot(amplitude(Z))
plt.plot(Z.real)
plt.plot(Z.imag)
plt.figure(6)
plt.imshow(amplitude(z.T))
plt.colorbar()
plt.xlabel('Time')
plt.ylabel('Frequency Channels')
#plt.figure(7)
#plt.plot(amplitude(z.T))
plt.figure(8)
plt.plot(amplitude(z[15]))
plt.plot(z[15].real)
plt.plot(z[15].imag)
plt.figure(5)
plt.plot(amplitude(Z))
plt.plot(amplitude(X_A))
plt.plot(amplitude(Y_A))
plt.show()

exit()
