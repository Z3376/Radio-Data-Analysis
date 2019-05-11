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

g_blip					=	[]
p_blip					=	[]
f_g_blip 				=	[]
f_p_blip 				=	[]
G_BLIP					=	[]
P_BLIP					=	[]
F_G_BLIP				=	[]
F_P_BLIP				=	[]
start					=	[]
stop					=	[]
SLOPE					=	[]
stability				=	[]
stability_fpga			=	[]

if(isfile(file_name+"_packet_info.txt")):
	txt_file			=	open(file_name+"_packet_info.txt","a")
else:
	txt_file			=	open(file_name+"_packet_info.txt","w+")

start.append(0)
stop.append(0)

for j in range(999):
	j_d					=	j/10
	d					=	1
	while(j_d):
		j_d				=	j_d/10
		d				+=	1
	st					=	('_'+'0'*(3-d))+str(j)
		
	if (not(isfile(file_name+st+".hdr"))):
		break
		
	print "Reading file "+st

	start.append(len(g_blip))

	size				=	getsize(file_name+st+".hdr")
	i					=	26
	q					=	0
	fpga				=	np.empty(2)
	gps					=	np.empty(2)
	p_num 				=	np.empty(2)
	time_s				=	int(file_name[-2:])+stop[j]-start[j]
	time_min			=	int(file_name[-4:-2])
	time_hr				=	int(file_name[-6:-4])
	time_day			=	int(file_name[-9:-7])
	time_month			=	int(file_name[-11:-9])
	time_yr				=	int(file_name[-15:-11])

	julian_day			=	julday_conv(time_s,time_min,time_hr,time_day,time_month,time_yr)

	file				=	open(file_name+st+".hdr","rb")
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

	stop.append(len(g_blip))

	if(j==0 or j%2):

		s				=	slope(g_blip,p_blip)

		z 				=	np.polyfit(g_blip, p_blip, 1)
		r 				= 	np.poly1d(z)
		g_blip_new		= 	np.linspace(g_blip[0], g_blip[-1], len(g_blip))
		p_blip_new		= 	r(g_blip_new)

		z_s				=	np.polyfit(f_g_blip, f_p_blip, 1)
		r_s 			= 	np.poly1d(z_s)
		f_g_blip_new	= 	np.linspace(f_g_blip[0], f_p_blip[-1], len(f_g_blip))
		f_p_blip_new	= 	r_s(f_g_blip_new)

		txt_file.write("\nJulian Day:\t\t\t\t\t"+str(julian_day))
		txt_file.write("\nP_Num for first transition:\t\t\t"+str(p_blip[0]))
		txt_file.write("\nEstimate of P_Num for first transition:\t\t"+str(p_blip_new[0]))
		txt_file.write("\nEstimated Packets/Sec:\t\t\t\t"+str(np.mean(slope(g_blip_new,p_blip_new))))
		txt_file.write("\nEstimated Packets/Sec(FPGA Blip):\t\t"+str(np.mean(slope(f_g_blip_new,f_p_blip_new))))
		txt_file.write("\nEstimated Sampling Freq.:\t\t\t"+str(np.mean(slope(g_blip_new,p_blip_new))*512))
		txt_file.write("\nEstimated Sampling Freq.(FPGA Blip):\t\t"+str(np.mean(slope(f_g_blip_new,f_p_blip_new))*512))
		txt_file.write("\n")
		G_BLIP.append(g_blip)
		P_BLIP.append(p_blip)
		F_G_BLIP.append(f_g_blip)
		F_P_BLIP.append(f_p_blip)
		stability.append(np.mean(slope(g_blip_new,p_blip_new))*512)
		stability_fpga.append(np.mean(slope(f_g_blip_new,f_p_blip_new))*512)
		SLOPE.append(s)

		if(j%2):
			g_blip			=	[]
			p_blip			=	[]
			f_g_blip 		=	[]
			f_p_blip 		=	[]

g_blip						=	double_arr_to_list(G_BLIP)
p_blip						=	double_arr_to_list(P_BLIP)
f_g_blip 					=	double_arr_to_list(F_G_BLIP)
f_p_blip 					=	double_arr_to_list(F_P_BLIP)
s							=	double_arr_to_list(SLOPE)

z 							=	np.polyfit(g_blip, p_blip, 1)
r 							= 	np.poly1d(z)
g_blip_new					= 	np.linspace(g_blip[0], g_blip[-1], len(g_blip))
p_blip_new					= 	r(g_blip_new)

z_s							=	np.polyfit(f_g_blip, f_p_blip, 1)
r_s 						= 	np.poly1d(z_s)
f_g_blip_new				= 	np.linspace(f_g_blip[0], f_p_blip[-1], len(f_g_blip))
f_p_blip_new				= 	r_s(f_g_blip_new)

txt_file.write("\t\t---For whole observation---")
txt_file.write("\nP_Num for first transition:\t\t\t"+str(p_blip[0]))
txt_file.write("\nEstimate of P_Num for first transition:\t\t"+str(p_blip_new[0]))
txt_file.write("\nEstimated Packets/Sec:\t\t\t\t"+str(np.mean(slope(g_blip_new,p_blip_new))))
txt_file.write("\nEstimated Packets/Sec(FPGA Blip):\t\t"+str(np.mean(slope(f_g_blip_new,f_p_blip_new))))
txt_file.write("\nEstimated Sampling Freq.:\t\t\t"+str(np.mean(slope(g_blip_new,p_blip_new))*512))
txt_file.write("\nEstimated Sampling Freq.(FPGA Blip):\t\t"+str(np.mean(slope(f_g_blip_new,f_p_blip_new))*512))

txt_file.close()

print("\t\t---For whole observation---")
print("\nP_Num for first transition:\t\t\t"+str(p_blip[0]))
print("\nEstimate of P_Num for first transition:\t\t"+str(p_blip_new[0]))
print("\nEstimated Packets/Sec:\t\t\t\t"+str(np.mean(slope(g_blip_new,p_blip_new))))
print("\nEstimated Packets/Sec(FPGA Blip):\t\t"+str(np.mean(slope(f_g_blip_new,f_p_blip_new))))
print("\nEstimated Sampling Freq.:\t\t\t"+str(np.mean(slope(g_blip_new,p_blip_new))*512))
print("\nEstimated Sampling Freq.(FPGA Blip):\t\t"+str(np.mean(slope(f_g_blip_new,f_p_blip_new))*512))

plt.figure()
plt.plot(g_blip,p_blip,"ro")
plt.plot(g_blip_new,p_blip_new)
plt.figure()
plt.plot(s)
plt.figure()
plt.plot(stability)
plt.plot(stability_fpga)
plt.show()
