#!/usr/bin/python

from os.path import getsize
import sys
from astropy.io import ascii
import time

t=time.time()

if(len(sys.argv)==5):
	file_name		=	sys.argv[1]
	das_id			=	sys.argv[2]
	start			=	int(sys.argv[3])
	end				=	int(sys.argv[4])
else:
	print('Usage:\n ./pascii_sniff.py <file_name> <das_id> <start> <end> \n NOTE: Specify end=0 for reading complete file.')
	exit()


l			=	len(file_name)
ftxt		=	file_name[-l:-4]+'_'+das_id+'.txt'
fopen		=	open(file_name,'rb')							
size		=	getsize(file_name)
t_p			=	size/1056
a			=	[[] for i in range(2)]	
p_c			=	start
ctr			=	0									

if(end==0):
	end=t_p

l_t			=	[i for i in range(256)]							#look-up_table
for j in range(128):
	l_t[j+128]	-=	256

fopen.read(7)
while(p_c<end):
	if(fopen.read(1)==das_id):
		fopen.read(24)
		for i in range(512):
			a[0].append(l_t[int(fopen.read(1).encode('hex'),16)])
			a[1].append(l_t[int(fopen.read(1).encode('hex'),16)])
		ctr+=1
		fopen.read(7)
	else:
		fopen.read(1055)
	p_c		+=	1

ascii.write(a,ftxt,overwrite=True)

print 'No. of packets from DAS_ID:',das_id,'=', ctr
print 'Total Time Elapsed:', time.time()-t