#!/Users/harsh/anaconda2/bin/python

from os.path import getsize,isfile
import sys
import matplotlib.pyplot as plt
import numpy as np
import time
import pyfftw
import threading

t0	=	time.time()

########-------------------------------########
#			 Function Definations
########-------------------------------########

def fft(fftw,a,k):
	global FFT
	FFT[k].append(fftw(a))

def corr(n,k):
	global file_name,avg,t_p,l_t,a_count,z,x,y,buff
	b_c						=	k*(a_count/n)*avg*1024
	fopen					=	open(file_name,'rb')							
	fopen.read(32)
	for j in range(k*a_count/n,(k+1)*a_count/n):
		while(b_c<(j+1)*avg*1024):
			buff[b_c%1024]	=	l_t[int(str(fopen.read(1)).encode('hex'),16)]
			b_c				+=	1

			if(b_c%1024==0):
				fft(x_fftw,buff[0::2],k)
				fft(y_fftw,buff[1::2],k)
				i			=	2*((b_c-k*(a_count/n)*avg*1024)/1024)-2
				z[j]		+=	FFT[k][i][:256]*np.conj(FFT[k][i+1][:256])
				x[j]		+=	FFT[k][i][:256]*np.conj(FFT[k][i][:256])
				y[j]		+=	FFT[k][i+1][:256]*np.conj(FFT[k][i+1][:256])
				fopen.read(32)
		z[j][0]				=	z[j][1]
		x[j][0]				=	x[j][1]
		y[j][0]				=	y[j][1]
		z[j]				=	z[j]/float(avg)/np.sqrt(x[j]*y[j])
		x[j]				=	x[j]/float(avg)
		y[j]				=	y[j]/float(avg)
		print 'Progress',k+1,':',float(j+1)*100/(k+1)/(a_count/n),'%'
	fopen.close()

def amplitude(a):
	a	=	(a.imag**2+a.real**2)**0.5
	return a

def mean(a):
	mean_a	=	np.zeros(256, dtype='complex')
	for i in range(256):
		for j in range(a_count):
			mean_a[i]			+=	a[j][i]
		mean_a[i]				=	mean_a[i]/a_count
	return mean_a

def rms(a,mean_a):
	rms_a	=	np.zeros(256, dtype='complex')
	for i in range(256):
		for j in range(a_count):
			rms_a[i]			+=	(a[j][i]-mean_a[i])**2
		rms_a[i]				=	np.sqrt(rms_a[i]/a_count)
	return rms_a

########-------------------------------########
#				Input Arguments
########-------------------------------########

if(len(sys.argv)==2 and sys.argv[1]=='-d'):
	file_name	=	'ch07_CASOBSTEST_20170301_143236_000.mbr'
	avg			=	1000
	n_th		=	10
elif(len(sys.argv)==4):
	file_name	=	sys.argv[1]										#.mbr_file
	avg			=	int(sys.argv[2])								#no._of packets_to_be_averaged
	n_th		=	int(sys.argv[3])								#no._of_threads_to_be_created
elif(len(sys.argv)==3):
	file_name	=	sys.argv[1]
	avg			=	int(sys.argv[2])
	n_th		=	int(raw_input('No. of Threads to be created (Eg. 10) : '))
elif(len(sys.argv)==2):
	file_name	=	sys.argv[1]
	avg			=	int(raw_input('No. of Packets to be averaged (Eg. 1000) : '))
	n_th		=	int(raw_input('No. of Threads to be created (Eg. 10) : '))
elif(len(sys.argv)==1):
	file_name	=	raw_input('.mbr File: ')
	avg			=	int(raw_input('No. of Packets to be averaged (Eg. 1000) : '))
	n_th		=	int(raw_input('No. of Threads to be created (Eg. 10) : '))
else:
	print 'Enter onyl .mbr File name and No. of Packets to be averaged and No. of Threads to be created.'
	exit()

########-------------------------------########
#		Initialising Variables/Matrices
########-------------------------------########

size			=	getsize(file_name)
t_p				=	size/1056										#total_packets
b_c				=	0												#byte_counter
o_f				=	16												#oversampling_factor
s_f				=	33000000										#sampling_frequency
b_w				=	s_f/2											#bandwidth
a_count			=	t_p/avg											#total_no._of_avg's_in_the_file
tbwp			=	avg												#time-bandwidth-product
p_1s			=	t_p/30											#packets_in_1s
s_avg			=	p_1s/avg										#no._of_avg's_in_1_sec
s_count			=	t_p/p_1s										#total_no._of_s_avg's_in_the_file
FFT				=	[[]for k in range(n_th)]
th				=	[]
buff			=	np.zeros(1024,dtype='complex')
x_fftw			=	pyfftw.empty_aligned(512,dtype='complex')
y_fftw			=	pyfftw.empty_aligned(512,dtype='complex')
padding			=	np.zeros(256+(512*(o_f-1)))
z				=	np.zeros((a_count,256), dtype='complex')
x				=	np.zeros((a_count,256), dtype='complex')
y				=	np.zeros((a_count,256), dtype='complex')
z_sec			=	np.zeros((s_count,256), dtype='complex')
Z				=	np.zeros((s_count,o_f*512), dtype='complex')
delay			=	np.zeros(s_count)

x_fftw			=	pyfftw.FFTW(x_fftw,x_fftw)						#FFTW_matrix
y_fftw			=	pyfftw.FFTW(y_fftw,y_fftw)

l_t				=	[i for i in range(256)]							#look-up_table
for j in range(128):
	l_t[j+128]	-=	256

########-------------------------------########
#		 Calculating Cross Correlation
########-------------------------------########

print 'Calculating Cross Correlation'

t	=	time.time()

for k in range(n_th):
	th.append(threading.Thread(target=corr,args=(n_th,k)))
for k in range(n_th):
	th[k].start()
for k in range(n_th):
	th[k].join()

print 'Time_Taken =', time.time()-t,'\n---------------------'

########-------------------------------########
#			Calculating Efficiency
########-------------------------------########

print 'Calculating Efficiency'

t	=	time.time()

mean_x_o		=	mean(x)
mean_y_o		=	mean(y)

rms_x_o			=	rms(x,mean_x_o)
rms_y_o			=	rms(y,mean_y_o)

SNR_x_obs		=	mean_x_o/rms_x_o
SNR_y_obs		=	mean_y_o/rms_y_o
SNR_exp			=	float(np.sqrt(tbwp))

efficiency_x	=	SNR_x_obs/SNR_exp
efficiency_y	=	SNR_y_obs/SNR_exp

print 'Time_Taken =', time.time()-t,'\n---------------------'

########-------------------------------########
#			 Clearing Bad Channels
########-------------------------------########

print('Clearing Bad Channels')

t	=	time.time()

for i in range(256):
	if(efficiency_x[i]<0.81 or efficiency_y[i]<0.9):
		for j in range(a_count):
			z[j][i]	=	0

for i in range(s_count):
	for j in range(s_avg):
		z_sec[i]	+=	z[(s_avg*i)+j]
	z_sec[i]		/=	s_avg

print 'Time_Taken =', time.time()-t,'\n---------------------'

#ch_p	=	40
#pi		=	np.arccos(-1)

#for j in range(len(z_sec)):
#	for i in range(256):
#		z_sec[j][i]	=	np.cos(i*2*pi/ch_p)+np.sin(i*2*pi/ch_p)*1j

########-------------------------------########
#		 Performing Hilbert Transforms
########-------------------------------########

print('Performing Hilbert Transforms')

t	=	time.time()

for k in range(s_count):
	Z[k]			=	np.fft.fftshift(np.fft.ifft(np.concatenate((z_sec[k],padding))))

	max_x			=	0
	for x in range(len(Z[k])):
		if(Z[k][x]==max(Z[k])):
			max_x	=	x

	n				=	max_x-o_f*512/2
	delay[k]		=	float(n)/float(o_f)/float(s_f)
	print 'Calculated Delay',k,':',delay[k]

print 'Time_Taken =', time.time()-t,'\n---------------------'

########-------------------------------########
#		   Saving Cross_Corr Results
########-------------------------------########

z_file	=	open('z.dat','w+')	
z_file.write(z)

########-------------------------------########

print "Total Time Elapsed:", time.time()-t0

########-------------------------------########
#				Plotting Results
########-------------------------------########

plt.figure(1)
plt.plot(efficiency_x)
plt.plot(efficiency_y)
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
