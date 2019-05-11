import multiprocessing as mp
import numpy as np
import pyfftw
import matplotlib.pyplot as plt
import time

def fft(fftw,a):
	global FFT
	FFT.append(fftw(a))

x_fftw		=	pyfftw.empty_aligned(1280,dtype='complex')
y_fftw		=	pyfftw.empty_aligned(1280,dtype='complex')
f_fftw		=	pyfftw.empty_aligned(2560,dtype='complex')
FFT			=	[]

a			=	[np.cos(i) for i in range(2560)]

x_fftw		=	pyfftw.FFTW(x_fftw,x_fftw)
y_fftw		=	pyfftw.FFTW(y_fftw,y_fftw)
f_fftw		=	pyfftw.FFTW(f_fftw,f_fftw)

t0			=	time.time()

fft(x_fftw,a[0::2])
fft(y_fftw,a[1::2])
fft(f_fftw,a)

print time.time()-t0

plt.plot(a)
plt.plot(FFT[2])
plt.plot(FFT[0])
plt.plot(FFT[1])
plt.show()