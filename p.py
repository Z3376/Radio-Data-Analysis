#!/Users/harsh/anaconda2/bin/python

import sys
from os.path import getsize
from os.path import isfile
import matplotlib.pyplot as plt
import numpy as np

def double_arr_to_list(a):
	b					=	[]
	for i in range(len(a)):
		for j in range(len(a[i])):
			b.append(a[i][j])
	return b

def julday_conv(s,mnt,hr,d,mon,yr):
	mnt					+=	float(s)/60
	hr					+=	mnt/60
	hr_d				=	hr/24
	
	if (mon<2):
		mon				+=	12
		yr				-=	1
	else:
		mon				+=	1

	p					=	yr*365.25
	q					=	30.6001*mon
	r					=	yr*0.01
	s					=	r*0.25
	jul_day				=	p+q+s+d-r+1720995+2+hr_d				

	return jul_day

def slope(a,b):
	s					=	[0 for i in range(len(a)-1)]
	for i in range(len(a)-1):
		s[i]			=	float(b[i+1]-b[i])/(a[i+1]-a[i])
	return s

if(len(sys.argv)==2):
	file_name			=	sys.argv[1]
elif(len(sys.argv)==1):
	file_name			=	raw_input(".hdr_File: ")
else:
	print("Too many arguments. Enter only .hdr_File name.")
	exit()

if (not(isfile(file_name))):
	exit()
		
size				=	getsize(file_name)
i					=	26
q					=	0
fpga				=	np.empty(2)
gps					=	np.empty(2)
p_num 				=	np.empty(2)
g_blip				=	[]
p_blip				=	[]
f_g_blip 			=	[]
f_p_blip 			=	[]

file				=	open(file_name,"rb")
while(i < size):
	file.read(24)
	fpga[q%2]		=	int(str(file.read(2)).encode('hex'),16)
	gps[q%2]		=	int(str(file.read(2)).encode('hex'),16)
	p_num[q%2]		=	int(str(file.read(4)).encode('hex'),16)
	if (gps[q%2]-gps[(q+1)%2]==1 and p_num[q%2]-p_num[(q+1)%2]==1):
		g_blip.append(gps[q%2])
		p_blip.append(p_num[q%2])
		if (fpga[q%2]!=fpga[(q+1)%2]):
			f_g_blip.append(gps[q%2])
			f_p_blip.append(p_num[q%2])
	i				+=	32
	q				+=	1
file.close()

s					=	slope(g_blip,p_blip)

z 					=	np.polyfit(g_blip, p_blip, 1)
r 					= 	np.poly1d(z)
g_blip_new			=	np.linspace(g_blip[0], g_blip[-1], len(g_blip))
p_blip_new			= 	r(g_blip_new)

z_s					=	np.polyfit(f_g_blip, f_p_blip, 1)
r_s 				= 	np.poly1d(z_s)
f_g_blip_new		= 	np.linspace(f_g_blip[0], f_p_blip[-1], len(f_g_blip))
f_p_blip_new		= 	r_s(f_g_blip_new)

print("\nFile Name:\t\t\t\t\t"+file_name)
print("\nGPS counter for first transition:\t\t"+str(p_blip[0]))
print("\nP_Num for first transition:\t\t\t"+str(p_blip[0]))
print("\nEstimate of P_Num for first transition:\t\t"+str(p_blip_new[0]))
print("\nEstimated Packets/Sec:\t\t\t\t"+str(np.mean(slope(g_blip_new,p_blip_new))))
print("\nEstimated Packets/Sec(FPGA Blip):\t\t"+str(np.mean(slope(f_g_blip_new,f_p_blip_new))))
print("\nEstimated Sampling Freq.:\t\t\t"+str(np.mean(slope(g_blip_new,p_blip_new))*512))
print("\nEstimated Sampling Freq.(FPGA Blip):\t\t"+str(np.mean(slope(f_g_blip_new,f_p_blip_new))*512))

plt.plot(s)
plt.show()
