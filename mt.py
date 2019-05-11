import threading
import numpy as np
import pyfftw
import matplotlib.pyplot as plt
import time

def fft(fftw,a):
	global FFT
	FFT.append(fftw(a))
	print 1

FFT		=	[]

x_fftw	=	pyfftw.empty_aligned(1280,dtype='complex')
y_fftw	=	pyfftw.empty_aligned(1280,dtype='complex')
f_fftw	=	pyfftw.empty_aligned(2560,dtype='complex')

a		=	[np.cos(i) for i in range(2560)]
p		=	[]

x_fftw	=	pyfftw.FFTW(x_fftw,x_fftw)
y_fftw	=	pyfftw.FFTW(y_fftw,y_fftw)
f_fftw	=	pyfftw.FFTW(f_fftw,f_fftw)

plt.figure(1)

for i in range(2):
	p.append(threading.Thread(target=fft,args=(x_fftw,a[i::2])))
#p3			=	threading.Thread(target=fft,args=(f_fftw,a))

t1=time.time()

for i in range(2):
	p[i].start()

for i in range(2):
	p[i].join()

print time.time()-t1

plt.plot(a)
#plt.plot(FFT[2])
plt.plot(FFT[0])
plt.plot(FFT[1])
plt.show()