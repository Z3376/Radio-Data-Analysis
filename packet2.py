import os
import matplotlib.pyplot as plt
import numpy as np
def packet_num(file_name):
	size			=	os.path.getsize(file_name)
	i				=	26
	total_packets	=	size/32
	gps				=	[]
	p_num 			=	[]
	g_blip 			=	[]
	p_blip 			=	[]
	d_blip			=	[]
	blip			=	[]
	flag			=	0

	with open(file_name,"rb") as file:
		while(i < size):
			file.read(26)
			gps.append(int(str(file.read(2)).encode('hex'),16))
			p_num.append(int(str(file.read(4)).encode('hex'),16))
			i		+=	32

	#print gps[:],p_num[:]

	for i in range(total_packets-1):
		if((gps[i+1]-gps[i]) == 1 and p_num[i+1]-p_num[i] == 1):
			g_blip.append(gps[i+1])
			p_blip.append(p_num[i+1])

	f				=	[0 for i in range(len(p_blip))]
	s				=	slope(g_blip,p_blip)
	#t				=	[0 for i in range(len(s))]
	for i in range(len(p_blip)):
		f[i]		=	p_blip[i]/g_blip[i]
	
	#for i in range(len(s)):
	#	t[i]		=	s[i]-np.mean(s)

	blip.append(0)
	for i in range(len(s)-2):
		if(s[i]!= int(np.mean(s))):
			blip.append(i+1)

	for i in range(len(blip)-1):
		d_blip.append(blip[i+1]-blip[i])


	for i in range(len(d_blip)-1):
		if (d_blip[i] != d_blip[i+1]):
			flag	=	1

	if (flag == 0):
		sf_l		=	(round(np.mean(s))+1/float(d_blip[0]))*512
		sf_u		=	(round(np.mean(s))+int(len(s)/d_blip[0])/float(int(len(s)/d_blip[0])*d_blip[0]-1))*512

		if (len(s)==(int(len(s)/d_blip[0])+1)*d_blip[0]-1):
			sf_u		=	(round(np.mean(s))+(int(len(s)/d_blip[0])+1)/float((int(len(s)/d_blip[0])+1)*d_blip[0]-1))*512

		print "Sampling frequency is stable between", sf_l, "Hz and", sf_u, "Hz"

	else:
		print "Sampling frequency is unstable"

	#print int(len(s)/d_blip[0]), float(int(len(s)/d_blip[0])*d_blip[0]-1)
	
	#p_est = []
	#p_est.append(p_blip[0])
	#for i in range(1,len(g_blip)):
	#	p_est.append((p_blip[i]-p_blip[i-1])/(g_blip[i]-g_blip[i-1]))

	#print g_blip[:], "\n", p_blip[:], "\n", s, "\n", f, "\n", t, "\n", np.mean(s)

	z = np.polyfit(g_blip, p_blip, 1)
	r = np.poly1d(z)
	g_blip_new = np.linspace(g_blip[0], g_blip[-1], 31)
	p_blip_new = r(g_blip_new)

	print p_blip[0], p_blip_new[0], np.mean(slope(g_blip_new,p_blip_new))

	plt.figure(1)
	plt.plot(g_blip, p_blip, 'ro')
	plt.plot(g_blip_new,p_blip_new)
	#plt.figure(2)
	#plt.plot(s)
	#plt.plot(s,'ro')
	#plt.xlabel('GPS')
	#plt.ylabel('Packets/Second')
	#plt.xlim(0,35)
	#plt.figure(3)
	#plt.plot(f,'o')
	#plt.plot(g_blip_new,f_new)
	#plt.figure(4)
	#plt.plot(t,'o')
	#plt.figure(5)
	#plt.plot(p_est,'o')
	#plt.figure(6)
	#plt.plot(d_p, 'ro')
	#plt.figure(7)
	#plt.plot(d_blip, 'ro')
	plt.show()

def slope(a,b):
	s				=	[0 for i in range(len(a)-1)]
	for i in range(len(a)-1):
		s[i]		=	float(b[i+1]-b[i])/(a[i+1]-a[i])
	return s

if __name__ == '__main__':
	packet_num(raw_input('File_name: ')+'.hdr')
	#packet_num('ch01_moon_obs_20161118_011507_000.hdr')
	#packet_num('ch00_DRIFT_49_20161019_205446_001.hdr')




