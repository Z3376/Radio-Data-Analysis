import multiprocessing as mp
import numpy as np
import pyfftw
import matplotlib.pyplot as plt
import time

FFT			=	[]

def fft(fftw,a):
	FFT.append(fftw(a))

x_fftw		=	pyfftw.empty_aligned(1280,dtype='complex')
y_fftw		=	pyfftw.empty_aligned(1280,dtype='complex')
f_fftw		=	pyfftw.empty_aligned(2560,dtype='complex')

a			=	[np.cos(i) for i in range(2560)]

x_fftw	=	pyfftw.FFTW(x_fftw,x_fftw)
y_fftw	=	pyfftw.FFTW(y_fftw,y_fftw)
f_fftw	=	pyfftw.FFTW(f_fftw,f_fftw)

plt.figure(1)

t1			=	time.time()

p1			=	mp.Process(target=fft,args=(x_fftw,a[0::2],))
p2			=	mp.Process(target=fft,args=(y_fftw,a[1::2],))
p3			=	mp.Process(target=fft,args=(f_fftw,a,))

p1.start()
p2.start()
p3.start()
p1.join()
p2.join()
p3.join()

print time.time()-t1

plt.plot(a)
plt.plot(FFT[2])
plt.plot(FFT[0])
plt.plot(FFT[1])
plt.show()