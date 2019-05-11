#!/Users/harsh/anaconda2/bin/python

import sys
from os.path import getsize
from os.path import isfile
import matplotlib.pyplot as plt
import numpy as np

def slope(a,b):
	s						=	[0 for i in range(len(a)-1)]
	for i in range(len(a)-1):
		s[i]				=	float(b[i+1]-b[i])/(a[i+1]-a[i])
	return s

if(len(sys.argv)==2):
	file_name				=	sys.argv[1]
elif(len(sys.argv)==1):
	file_name				=	raw_input('.hdr_File: ')
else:
	print('Too many arguments. Enter onyl .hdr_File name.')
	exit()

g_blip						=	np.array([], dtype="int64")
p_blip						=	np.array([], dtype="int64")
f_g_blip 					=	np.array([], dtype="int64")
f_p_blip 					=	np.array([], dtype="int64")
l							=	np.array([], dtype="int64")
flag						=	0

for j in range(999):
	j_d						=	j/10
	d						=	1
	while(j_d):
		j_d					=	j_d/10
		d					+=	1
	st						=	('_'+'0'*(3-d))+str(j)
		
	if (not(isfile(file_name+st+".hdr"))):
		break
		
	print "Reading file "+st

	size					=	getsize(file_name+st+".hdr")
	i						=	26
	q						=	0
	fpga					=	np.empty(2)
	gps						=	np.empty(2)
	p_num 					=	np.empty(2)

	file					=	open(file_name+st+".hdr","rb")
	while(i < size):
		file.read(24)
		fpga[q%2]			=	int(str(file.read(2)).encode('hex'),16)
		gps[q%2]			=	int(str(file.read(2)).encode('hex'),16)
		p_num[q%2]			=	int(str(file.read(4)).encode('hex'),16)
		if (gps[q%2]-gps[(q+1)%2]==1 and p_num[q%2]-p_num[(q+1)%2]==1):
			g_blip			=	np.append(g_blip,gps[q%2])
			p_blip			=	np.append(p_blip,p_num[q%2])
			if (fpga[q%2]!=fpga[(q+1)%2]):
				f_g_blip	=	np.append(f_g_blip,gps[q%2])
				f_p_blip	=	np.append(f_p_blip,p_num[q%2])
		i					+=	32
		q					+=	1
	file.close()

s							=	slope(g_blip,p_blip)

z 							=	np.polyfit(g_blip, p_blip, 1)
r 							= 	np.poly1d(z)
g_blip_new					= 	np.linspace(g_blip[0], g_blip[-1], len(g_blip))
p_blip_new					= 	r(g_blip_new)

z_s							=	np.polyfit(f_g_blip, f_p_blip, 1)
r_s 						= 	np.poly1d(z_s)
f_g_blip_new				= 	np.linspace(f_g_blip[0], f_p_blip[-1], len(f_g_blip))
f_p_blip_new				= 	r_s(f_g_blip_new)

print "\nP_Num for first transition:\t\t\t",p_blip[0]
print "\nEstimate of P_Num for first transition:\t\t",p_blip_new[0]
print "\nEstimated Packets/Sec:\t\t\t\t",np.mean(slope(f_g_blip_new,f_p_blip_new)) 
print "\nEstimated Sampling Freq.:\t\t\t",np.mean(slope(g_blip_new,p_blip_new))*512
print "\nEstimated Sampling Freq.(with FPGA blip):\t",np.mean(slope(f_g_blip_new,f_p_blip_new))*512

plt.figure()
plt.plot(g_blip,p_blip,"ro")
plt.plot(g_blip_new,p_blip_new)
plt.figure()
plt.plot(s)
plt.show()
