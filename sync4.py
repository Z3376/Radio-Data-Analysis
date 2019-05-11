#!/usr/bin/python

import numpy as np
import matplotlib.pyplot as plt
import sys
import os
import pyfftw
from astropy.table import Table

def trans(a):
    if(np.abs(a[0]-a[1])==1):
        return 1
    else:
        return 0

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

def efficiency(a,exp):
	mean_a		=	mean(a)
	rms_a		=	rms(a,mean)
	SNR			=	mean_a/rms_a
	efficiency	=	SNR/exp
	return efficiency

def reject_matrix(eff,a):
	Mean_E		=	np.mean(eff)
	Sigma		=	np.std(eff)
	n_c			=	len(eff)
	R			=	np.zeros(n_c)
	for i in range(n_c):
		if(np.abs(eff-Mean_E)>a*Sigma):
			R[i]	=	1
	return R

def reject(R1,R2,corr):
	n_c			=	len(R1)
	for j in range(n_c):
		if(R1[j]==1 or R2[j]==1):
			for i in range(len(corr)):
				corr[i][j]==0

def hilbert_delay(a_count,Z,z,padding,s_f,o_f,delay):
	for k in range(a_count):
		Z[k]						=	np.fft.fftshift(np.fft.ifft(np.concatenate((z[k],padding))))

		max_x						=	0
		for x in range(len(Z[k])):
			if(Z[k][x]==max(Z[k])):
				max_x				=	x

		n							=	max_x-o_f*512/2
		delay[k]					=	float(n)/float(o_f)/float(s_f)
		print 'Calculated Delay',k,':',delay[k]

if(sys.argv[1]=='-d'):
	file_name_1	=	'raw_ch03_B_P_20170714_042859_000.mbr'
	file_name_2	=	'raw_ch06_B_P_20170714_042859_000.mbr'
else:
	file_name_1	=	raw_input('File_1:')
	file_name_2	=	raw_input('File_2:')

f1	=	open(file_name_1,'rb')
f2	=	open(file_name_2,'rb')

s1	=	os.path.getsize(file_name_1)
s2	=	os.path.getsize(file_name_2)

f1.read(s1-1030)
g_l1	=	int(str(f1.read(2)).encode('hex'),16)
p_l1	=	int(str(f1.read(4)).encode('hex'),16)

f2.read(s2-1030)
g_l2	=	int(str(f2.read(2)).encode('hex'),16)
p_l2	=	int(str(f2.read(4)).encode('hex'),16)

flag	=	1
p_num1	=	np.zeros(2)
p_num2	=	np.zeros(2)

f1.seek(0)
f2.seek(0)
f1.read(26)
f2.read(26)

while(flag):
	gps1	=	int(str(f1.read(2)).encode('hex'),16)
	gps2	=	int(str(f2.read(2)).encode('hex'),16)
	if(gps1==gps2):
		p_num1[0]	=	int(str(f1.read(4)).encode('hex'),16)
		p_num2[0]	=	int(str(f2.read(4)).encode('hex'),16)
		o_t		=	g_l1-gps1
		n_p		=	p_l1-p_num1[0]
		flag	=	0
	elif(gps1>gps2):
		while(gps2==gps1):
			f2.read(1054)
			gps2	=	int(str(f2.read(2)).encode('hex'),16)
		p_num1[0]	=	int(str(f1.read(4)).encode('hex'),16)
		p_num2[0]	=	int(str(f2.read(4)).encode('hex'),16)
		o_t		=	g_l2-gps1
		n_p		=	p_l2-p_num2[0]
		flag	=	0
	else:
		while(gps1==gps2):
			f2.read(1054)
			gps1	=	int(str(f1.read(2)).encode('hex'),16)
		p_num1[0]	=	int(str(f1.read(4)).encode('hex'),16)
		p_num2[0]	=	int(str(f2.read(4)).encode('hex'),16)
		o_t		=	g_l1-gps1
		n_p		=	p_l1-p_num1[0]
		flag	=	0

a_count	=	int(n_p/o_t)
#n	=	int(1056*(1-(a_count-int(a_count))))
#print a_count, n

o_t			=	4		##############!!!!!!!!!!!!################

tbwp		=	a_count							#time-bandwidth-product
o_f			=	16								#oversampling_factor
s_f			=	33000000						#sampling_frequency
b_w			=	s_f/2							#bandwidth
padding		=	np.zeros(256+(512*(o_f-1)))

buff_1      =   np.zeros(1024,dtype='complex')
buff_2      =   np.zeros(1024,dtype='complex')
x_fftw_1    =   pyfftw.empty_aligned(512,dtype='complex')
y_fftw_1    =   pyfftw.empty_aligned(512,dtype='complex')
x_fftw_2    =   pyfftw.empty_aligned(512,dtype='complex')
y_fftw_2    =   pyfftw.empty_aligned(512,dtype='complex')
x_fftw_1    =   pyfftw.FFTW(x_fftw_1,x_fftw_1)
y_fftw_1    =   pyfftw.FFTW(y_fftw_1,y_fftw_1)
x_fftw_2    =   pyfftw.FFTW(x_fftw_2,x_fftw_2)
y_fftw_2    =   pyfftw.FFTW(y_fftw_2,y_fftw_2)
XX          =   np.zeros((o_t,256),dtype='complex')
YY          =   np.zeros((o_t,256),dtype='complex')
XY          =   np.zeros((o_t,256),dtype='complex')
YX          =   np.zeros((o_t,256),dtype='complex')
X_A1		=   np.zeros((o_t,256),dtype='complex')
Y_A1		=   np.zeros((o_t,256),dtype='complex')
X_A2		=   np.zeros((o_t,256),dtype='complex')
Y_A2		=   np.zeros((o_t,256),dtype='complex')
Z_XX		=	np.zeros((o_t,o_f*512), dtype='complex')
Z_XY		=	np.zeros((o_t,o_f*512), dtype='complex')
Z_YY		=	np.zeros((o_t,o_f*512), dtype='complex')
Z_YX		=	np.zeros((o_t,o_f*512), dtype='complex')
Z_X1		=	np.zeros((o_t,o_f*512), dtype='complex')
Z_X2		=	np.zeros((o_t,o_f*512), dtype='complex')
Z_Y1		=	np.zeros((o_t,o_f*512), dtype='complex')
Z_Y2		=	np.zeros((o_t,o_f*512), dtype='complex')
Z_XX_C		=	np.zeros((o_t,o_f*512), dtype='complex')
Z_XY_C		=	np.zeros((o_t,o_f*512), dtype='complex')
Z_YY_C		=	np.zeros((o_t,o_f*512), dtype='complex')
Z_YX_C		=	np.zeros((o_t,o_f*512), dtype='complex')
delay_XX	=	np.zeros(o_t)
delay_XY	=	np.zeros(o_t)
delay_YY	=	np.zeros(o_t)
delay_YX	=	np.zeros(o_t)

l_t     =   [i for i in range(256)]
for j in range(128):
    l_t[128+j]  -=  256

q           =   0

print 'Starting Corr'

for i in range(o_t):
	for j in range(1024*a_count):
		buff_1[j%1024]	=	l_t[int(str(f1.read(1)).encode('hex'),16)]
		buff_2[j%1024]	=	l_t[int(str(f2.read(1)).encode('hex'),16)]
		if(j%1024==1023):
			X_1			=	x_fftw_1(buff_1[::2])
			Y_1			=	y_fftw_1(buff_1[1::2])
			X_2			=	x_fftw_2(buff_2[::2])
			Y_2			=	y_fftw_2(buff_2[1::2])
			X_A1[i]		+=	X_1[:256]*np.conj(X_1[:256])
			Y_A1[i]		+=	Y_1[:256]*np.conj(Y_1[:256])
			X_A2[i]		+=	X_2[:256]*np.conj(X_2[:256])
			Y_A2[i]		+=	Y_2[:256]*np.conj(Y_2[:256])
			XX[i]		+=	X_1[:256]*np.conj(X_2[:256])
			YY[i]		+=	Y_1[:256]*np.conj(Y_2[:256])
			XY[i]		+=	X_1[:256]*np.conj(Y_2[:256])
			YX[i]		+=	Y_1[:256]*np.conj(X_2[:256])
			f1.read(28)
			f2.read(28)
			q			+=	1
			p_num1[q%2]	=	int(str(f1.read(4)).encode('hex'),16)
			p_num2[q%2]	=	int(str(f2.read(4)).encode('hex'),16)
			if(not(trans(p_num1)) or not(trans(p_num2))):
				print 'slip at:',p_num1[q%2],p_num2[q%2]
				if(not(trans(p_num1))):
					e	=	np.abs(p_num1[0]-p_num1[1])
					j	+=	e*1024
					print e
					f2.read(int(1056*e-4))
					p_num2[q%2]	=	int(str(f2.read(4)).encode('hex'),16)
				elif(not(trans(p_num2))):
					e	=	np.abs(p_num2[0]-p_num2[1])
					j	+=	e*1024
					print e
					f1.read(int(1056*e-4))
					p_num1[q%2]	=	int(str(f1.read(4)).encode('hex'),16)
				else:
					e1	=	np.abs(p_num1[0]-p_num1[1])
					e2	=	np.abs(p_num2[0]-p_num2[1])
					if(e1>e2):
						j	+=	e1*1024
						print e1
						f2.read(int(1056*(e1-e2)-4))
						p_num2[q%2]	=	int(str(f2.read(4)).encode('hex'),16)
					elif(e1<e2):
						j	+=	e2*1024
						print e2
						f1.read(int(1056*(e2-e1)-4))
						p_num1[q%2]	=	int(str(f1.read(4)).encode('hex'),16)
					else:
						j	+=	e1*1024
						print e1
	XX[i][0]	=	XX[i][1]
	XY[i][0]	=	XY[i][1]
	YY[i][0]	=	YY[i][1]
	YX[i][0]	=	YX[i][1]
	X_A1[i][0]	=	X_A1[i][1]
	X_A2[i][0]	=	X_A2[i][1]
	Y_A1[i][0]	=	Y_A1[i][1]
	Y_A2[i][0]	=	Y_A2[i][1]
	print i

print 'Calculating Efficiency'

SNR_exp			=	float(np.sqrt(tbwp))

efficiency_x1	=	efficiency(X_A1,SNR_exp)
efficiency_x2	=	efficiency(X_A2,SNR_exp)
efficiency_y1	=	efficiency(Y_A1,SNR_exp)
efficiency_y2	=	efficiency(Y_A2,SNR_exp)

print 'Rejecting Bad Channels'

R_X1		=	reject_matrix(efficiency_x1,3)
R_X2		=	reject_matrix(efficiency_x2,3)
R_Y1		=	reject_matrix(efficiency_y1,3)
R_Y2		=	reject_matrix(efficiency_y2,3)

reject(R_X1,R_X2,XX)
reject(R_X1,R_Y2,XY)
reject(R_Y1,R_Y2,YY)
reject(R_Y1,R_X2,YX)

print 'Performing Hilbert Transform'

hilbert_delay(a_count,Z_XX,XX,padding,s_f,o_f,delay_XX)
hilbert_delay(a_count,Z_XY,XY,padding,s_f,o_f,delay_XY)
hilbert_delay(a_count,Z_YY,YY,padding,s_f,o_f,delay_YY)
hilbert_delay(a_count,Z_YX,YX,padding,s_f,o_f,delay_YX)


Z_X1	=	np.fft.fftshift(np.fft.ifft(np.concatenate((mean(X_A1),padding))))
Z_X2	=	np.fft.fftshift(np.fft.ifft(np.concatenate((mean(X_A2),padding))))
Z_Y1	=	np.fft.fftshift(np.fft.ifft(np.concatenate((mean(Y_A1),padding))))
Z_Y2	=	np.fft.fftshift(np.fft.ifft(np.concatenate((mean(Y_A2),padding))))

Z_XX_C	=	np.fft.fftshift(np.fft.ifft(np.concatenate((mean(XX),padding))))
Z_XY_C	=	np.fft.fftshift(np.fft.ifft(np.concatenate((mean(XY),padding))))
Z_YY_C	=	np.fft.fftshift(np.fft.ifft(np.concatenate((mean(YY),padding))))
Z_YX_C	=	np.fft.fftshift(np.fft.ifft(np.concatenate((mean(YX),padding))))

print 'Saving Results'

XX_t	=	Table(XX)
XX_t.write(file_name_1[:-4]+'=X='+file_name_2[:-4]+'.dat',format='ascii',overwrite='true')
fw		=	open(file_name_1[:-4]+'=X='+file_name_2[:-4]+'.dat',mode='a')
fw.seek(0,os.SEEK_END)
XY_t	=	Table(XY)
XY_t.write(fw,format='ascii.no_header')
YY_t	=	Table(YY)
YY_t.write(fw,format='ascii.no_header')
YX_t	=	Table(YX)
YX_t.write(fw,format='ascii.no_header')
fw.close()

print 'Plotting Results'

fig		=	plt.figure(1)
plt.subplot(221)
plt.plot(XX)
plt.ylabel('XX')
plt.subplot(222)
plt.plot(XY)
plt.ylabel('XY')
plt.subplot(223)
plt.plot(YX)
plt.ylabel('YX')
plt.subplot(224)
plt.plot(YY)
plt.ylabel('YY')
fig.savefig(file_name_1[:-4]+'=X='+file_name_2[:-4]+'.png')

fig2	=	plt.figure(2)
plt.subplot(221)
plt.imshow(amplitude(XX),interpolation='nearest',aspect='auto')
plt.ylabel('XX')
plt.subplot(222)
plt.imshow(amplitude(XY),interpolation='nearest',aspect='auto')
plt.ylabel('XY')
plt.subplot(223)
plt.imshow(amplitude(YX),interpolation='nearest',aspect='auto')
plt.ylabel('YX')
plt.subplot(224)
plt.imshow(amplitude(YY),interpolation='nearest',aspect='auto')
plt.ylabel('YY')
fig2.savefig(file_name_1[:-4]+'=X='+file_name_2[:-4]+'_im.png')

fig3	=	plt.figure(3)
plt.subplot(221)
plt.plot(X_A1)
plt.ylabel('X_A1')
plt.subplot(222)
plt.plot(X_A2)
plt.ylabel('X_A2')
plt.subplot(223)
plt.plot(Y_A1)
plt.ylabel('Y_A1')
plt.subplot(224)
plt.plot(Y_A2)
plt.ylabel('Y_A2')
fig3.savefig(file_name_1[:-4]+'=X='+file_name_2[:-4]+'_auto_corr.png')

fig4	=	plt.figure(4)
plt.subplot(221)
plt.plot(efficiency_x1)
plt.plot([3*np.std(efficiency_x1) for i in range(len(efficiency_x1))])
plt.ylabel('Efficiency_X1')
plt.subplot(222)
plt.plot(efficiency_x2)
plt.plot([3*np.std(efficiency_x2) for i in range(len(efficiency_x2))])
plt.ylabel('Efficiency_X2')
plt.subplot(223)
plt.plot(efficiency_y1)
plt.plot([3*np.std(efficiency_y1) for i in range(len(efficiency_y1))])
plt.ylabel('Efficiency_Y1')
plt.subplot(224)
plt.plot(efficiency_y2)
plt.plot([3*np.std(efficiency_y2) for i in range(len(efficiency_y2))])
plt.ylabel('Efficiency_Y2')
fig4.savefig(file_name_1[:-4]+'=X='+file_name_2[:-4]+'_efficiency.png')

fig5	=	plt.figure(5)
plt.subplot(221)
plt.plot(Z_X1,label='X1')
plt.plot(Z_X2,label='X2')
plt.plot(Z_XX_C,label='Cross Corr')
plt.legend(bbox_to_anchor=(0.,1.02,1.,.102),loc=3,ncol=2,mode="expand",borderaxespad=0.)
plt.xlabel('Hilbert Transform: XX')
plt.subplot(222)
plt.plot(Z_X1,label='X1')
plt.plot(Z_Y2,label='Y2')
plt.plot(Z_XY_C,label='Cross Corr')
plt.legend(bbox_to_anchor=(0.,1.02,1.,.102),loc=3,ncol=2,mode="expand",borderaxespad=0.)
plt.xlabel('Hilbert Transform: XX')
plt.subplot(223)
plt.plot(Z_Y1,label='Y1')
plt.plot(Z_Y2,label='Y2')
plt.plot(Z_YY_C,label='Cross Corr')
plt.legend(bbox_to_anchor=(0.,1.02,1.,.102),loc=3,ncol=2,mode="expand",borderaxespad=0.)
plt.xlabel('Hilbert Transform: XX')
plt.subplot(224)
plt.plot(Z_Y1,label='Y1')
plt.plot(Z_X2,label='X2')
plt.plot(Z_YX_C,label='Cross Corr')
plt.legend(bbox_to_anchor=(0.,1.02,1.,.102),loc=3,ncol=2,mode="expand",borderaxespad=0.)
plt.xlabel('Hilbert Transform: XX')
fig5.savefig(file_name_1[:-4]+'=X='+file_name_2[:-4]+'_hilbert.png')

fig6	=	plt.figure(6)
plt.subplot(221)
plt.plot(delay_XX)
plt.ylabel('Delay(XX)')
plt.xlabel('Time')
plt.subplot(222)
plt.plot(delay_XY)
plt.ylabel('Delay(XY)')
plt.xlabel('Time')
plt.subplot(223)
plt.plot(delay_YY)
plt.ylabel('Delay(YY)')
plt.xlabel('Time')
plt.subplot(224)
plt.plot(delay_YX)
plt.ylabel('Delay(YX)')
plt.xlabel('Time')
fig6.savefig(file_name_1[:-4]+'=X='+file_name_2[:-4]+'_delay.png')


plt.show()
exit()
