from os.path import getsize
import sys
from astropy.io import ascii
import time

t=time.time()

file_name	=	'ch07_CASOBSTEST_20170301_143236_000'
ftxt		=	file_name+'2.txt'
fopen		=	open(file_name+'.mbr','rb')							
size		=	getsize(file_name+'.mbr')
t_p			=	size/1056										
b_c			=	0
a			=	[[] for i in range(2)]	

l_t			=	[i for i in range(256)]							#look-up_table
for j in range(128):
	l_t[j+128]	-=	256

fopen.read(32)
while(b_c<512*3):		
	a[0].append(l_t[int(fopen.read(1).encode('hex'),16)])
	a[1].append(l_t[int(str(fopen.read(1)).encode('hex'),16)])
	b_c		+=	1
	if(b_c%512==0):
		fopen.read(32)

ascii.write(a,'ch07_CASOBSTEST_20170301_143236_000.txt',overwrite=True)

print 'Total Time Elapsed:', time.time()-t