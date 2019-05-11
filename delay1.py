from os.path import getsize
from os.path import isfile
import matplotlib.pyplot as plt
import numpy as np

#file_name				=	raw_input('File: ')
file_name				=	"ch07_CASOBSTEST_20170301_143236"
for j in range(999):
	j_d					=	j/10
	d					=	1
	while(j_d):
		j_d				=	j_d/10
		d				+=	1
	st					=	('_'+'0'*(3-d))+str(j)

	if (not(isfile(file_name+st+".mbr"))):
		break
	print "Reading file "+st
	
	size				=	getsize(file_name+st+".mbr")
	i					=	0
	p_c					=	0
	x					=	[0 for i in range(512)]
	y					=	[0 for i in range(512)]
	x_j					=	0
	y_j					=	0
	z					=	[0 for i in range(256)]

	fopen				=	open(file_name+st+".mbr",'rb')
	while(i<3168):
		if(not(i%1056)):
			fopen.read(32)
			i			+=	32
		
		buff[p_c%1024]	=	int(str(fopen.read(1)).encode('hex'),16)
		i				+=	1
		p_c				+=	1
		X				=	np.fft.fft(buff[::2])
		Y				=	np.fft.fft(buff[1::2])
		z				+=	np.array(X*np.conj(Y))
	fopen.close()

padding					=	np.zeros(256+(512*15))

Z						=	np.fft.ifft(np.concatenate((z,padding)))

plt.plot(Z)
plt.show()