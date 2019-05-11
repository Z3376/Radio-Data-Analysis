#!/usr/bin/python
import os
import sys

if(len(sys.argv)==2):
	file_name	=	sys.argv[1]
else:
	file_name	=	raw_input("File: ")
	
i		=	0
size 	=	os.path.getsize(file_name+".mbr")

with open(file_name+".mbr","rb") as mbr:
	with open(file_name+".hdr","wb") as hdr:
		while (i	!=	size):
			hdr.write(mbr.read(32))
			i	+=	1056
			mbr.read(1024)

print "\nFile Name:		", file_name+".mbr"
print "MBR File Size:		", float(size)/(1024*1024*1024), "GB"
print "HDR File Size:		", float(os.path.getsize(file_name+".hdr"))/1024/1024, "MB"
print "Packets Received:	", float(os.path.getsize(file_name+".hdr"))/32
