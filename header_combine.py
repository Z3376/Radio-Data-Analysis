from os import path

def get_header(file_name):
	
	for j in range(999):
		
		j_d		=	j/10
		d		=	1

		while(j_d):
			j_d	=	j_d/10
			d	+=	1

		s		=	('_'+'0'*(3-d))+str(j)
		
		if (not(path.isfile(file_name+s+".hdr"))):
			break

		i		=	0
		size	=	path.getsize(file_name+s+".hdr")

		with open(file_name+s+".hdr","rb") as hdr:
			with open(file_name+"_full.hdr","a") as hdw:
				hdw.write(hdr.read())
					
	
		print "\nFile Name:		", file_name+"_full.hdr"
		print "Full HDR File Size:	", float(path.getsize(file_name+"_full.hdr"))/1024/1024, "MB"
		print "Packets Received:	", float(path.getsize(file_name+"_full.hdr"))/32

if __name__ == '__main__':
	get_header(raw_input("File: "))