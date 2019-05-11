from astropy.io import fits

#file_name	=	raw_input("file: ")
hdulist	=	fits.open("lambda_haslam408_dsds.fits")
#hdulist	=	fits.open("All_sky_map_34.5MHz_GBD.fits")
fopen	=	open("lambda_haslam408_dsds.txt",'w+')
#fopen	=	open("All_sky_map_34.5MHz_GBD.txt", 'w+')
fopen.seek(0)
data	=	hdulist[1].data.T
#h,l,k	=	data.shape
#print h,l,k
for i in range(len(data)):
	for j in range(len(data[0])):
		fopen.write(str(data[i][j])+"\t\t")
	fopen.write("\n")

#plt.imshow(data.T)#, cmap=plt.cm.viridis)
#plt.colorbar()
#plt.show()