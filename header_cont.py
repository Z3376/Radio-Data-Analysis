import os

def get_header(file_name):
	
	for j in range(999):
		
		j_d		=	j/10
		d		=	1

		while(j_d):
			j_d	=	j_d/10
			d	+=	1

		s		=	('_'+'0'*(3-d))+str(j)
		
		if (not(os.path.isfile(file_name+s+".mbr"))):
			break

		i		=	0
		size	=	os.path.getsize(file_name+s+".mbr")

		with open(file_name+s+".mbr","rb") as mbr:
			with open(file_name+s+".hdr","wb") as hdr:
				while (i != size):
					hdr.write(mbr.read(32))
					i	+=	1056
					mbr.seek(i)
	
		print "\nFile Name:		", file_name+s+".mbr"
		print "MBR File Size:		", float(size)/(1024*1024*1024), "GB"
		print "HDR File Size:		", float(os.path.getsize(file_name+s+".hdr"))/1024/1024, "MB"
		print "Packets Received:	", float(os.path.getsize(file_name+s+".hdr"))/32

		with open(file_name+s+".mbr","rb") as mbr:
			with open(file_name+"_full.hdr","wb") as hdr:
				while (i != size):
					hdr.append(mbr.read(32))
					i	+=	1056
					mbr.seek(i)

if __name__ == '__main__':
	get_header(raw_input("File: "))