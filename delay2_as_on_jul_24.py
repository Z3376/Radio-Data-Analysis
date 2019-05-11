#!/Users/harsh/anaconda2/bin/python

from os.path import getsize
from os.path import isfile
import sys
import matplotlib.pyplot as plt
import numpy as np

def amplitude(a):
	a							=	(a.imag**2+a.real**2)**0.5
	return a

def derivative(a):
	s							=	[0 for i in range(len(a)-1)]
	for i in range(len(a)-1):
		s[i]					=	a[i+1]-a[i]
	return s

if(len(sys.argv)==3):
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
t_p								=	size/1056						#total_packets
b_c								=	0								#bit_counter
s_c								=	0								#smple_counter
o_f								=	16								#oversampling_factor
s_f								=	33000000						#sampling_frequency
b_w								=	s_f/2							#bandwidth
#a_count							=	t_p/avg
a_count							=	9
tbwp							=	avg								#time-bandwidth-product
p_1s							=	67584							#packets_in_1s
#s_avg							=	p_1s/avg
s_avg							=	3
#s_count							=	t_p/s_avg/avg
s_count							=	6
buff							=	[0 for i in range(1024)]
z								=	np.zeros((a_count,256), dtype='complex')
x								=	np.zeros((a_count,256), dtype='complex')
y								=	np.zeros((a_count,256), dtype='complex')
mean_x_o						=	np.zeros(256, dtype='complex')
rms_x_o							=	np.zeros(256, dtype='complex')
mean_y_o						=	np.zeros(256, dtype='complex')
rms_y_o							=	np.zeros(256, dtype='complex')
z_min							=	np.zeros((s_count,256))
#Z								=	np.zeros((s_count,o_f*512), dtype='complex')
Z								=	np.zeros((a_count,o_f*512), dtype='complex')
delay							=	np.zeros(s_count)
Z_mean							=	np.zeros(o_f*512, dtype='complex')

fopen							=	open(file_name,'rb')

for j in range(a_count):
	while(b_c<(j+1)*avg*1056):
		if(not(b_c%1056)):
			fopen.read(32)
			b_c					+=	32
		buff[s_c%1024]			=	int(str(fopen.read(1)).encode('hex'),16)
		b_c						+=	1
		s_c						+=	1

		if(buff[(s_c-1)%1024]>127):
			buff[(s_c-1)%1024]	=	buff[(s_c-1)%1024]-256

		if(s_c%1024==0):
			X					=	np.fft.fft(buff[::2])
			Y					=	np.fft.fft(buff[1::2])
			z[j]				+=	X[:256]*np.conj(Y[:256])
			x[j]				+=	X[:256]*np.conj(X[:256])
			y[j]				+=	Y[:256]*np.conj(Y[:256])
	z[j][0]						=	0
	x[j][0]						=	x[j][1]
	y[j][0]						=	y[j][1]
	z[j]						=	z[j]/float(avg)
	x[j]						=	x[j]/float(avg)
	y[j]						=	y[j]/float(avg)
	print j

fopen.close()

for i in range(256):
	for j in range(a_count):
		mean_x_o[i]				+=	x[j][i]
	mean_x_o[i]					=	mean_x_o[i]/a_count

for i in range(256):
	for j in range(a_count):
		mean_y_o[i]				+=	y[j][i]
	mean_y_o[i]					=	mean_y_o[i]/a_count

for i in range(256):
	for j in range(a_count):
		rms_x_o[i]				+=	(x[j][i]-mean_x_o[i])**2
	rms_x_o[i]					=	np.sqrt(rms_x_o[i]/a_count)

for i in range(256):
	for j in range(a_count):
		rms_y_o[i]				+=	(y[j][i]-mean_y_o[i])**2
	rms_y_o[i]					=	np.sqrt(rms_y_o[i]/a_count)


SNR_x_obs						=	mean_x_o/rms_x_o
SNR_y_obs						=	mean_y_o/rms_y_o
SNR_exp							=	float(np.sqrt(tbwp))

efficiency_x					=	SNR_x_obs/SNR_exp
efficiency_y					=	SNR_y_obs/SNR_exp

for i in range(256):
	if(efficiency_x[i]<0.8 or efficiency_y[i]<0.8):
		for j in range(a_count):
			z[j][i]				=	0

# working fine till here
plt.figure()
plt.plot(efficiency_x)
plt.plot(efficiency_y)
plt.figure()
plt.imshow(amplitude(z.T))
plt.show()
exit()


padding							=	np.zeros(256+(512*(o_f-1)))

j								=	0
for k in range(s_count):
	for i in range(256):
        #while(j<k*s_avg):
		while(j<9):
			z_min[k][i]			+=	z[j][i]
			j					+=	1
	z_min[k]					/=	s_avg

for k in range(s_count):
	Z[k]						=	np.fft.fftshift(np.fft.ifft(np.concatenate((z_min[k],padding))))
for k in range(a_count):
	Z[k]						=	np.fft.fftshift(np.fft.ifft(np.concatenate((z[k],padding))))

	max_x						=	0
	for x in range(len(Z[k])):
		if(Z[k][x]==max(Z[k])):
			max_x				=	x

	n							=	max_x-o_f*512/2
	delay[k]					=	float(n)/float(o_f)/float(s_f)

	print 'Calculated Delay',k,':',delay[k]

for i in range(o_f*512):
	for k in range(s_count):
		Z_mean[i]				+=	Z[k][i]
	Z_mean[i]					=	Z_mean[i]/s_count


plt.figure()
plt.plot(efficiency_x)
plt.plot(efficiency_y)
plt.figure()
plt.imshow(amplitude(z.T))
plt.figure()
plt.plot(delay)
#plt.figure()
#plt.plot(Z_mean)
plt.figure()
plt.plot(Z[0])
plt.figure()
plt.plot(Z[-1])
plt.show()
