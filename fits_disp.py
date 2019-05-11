from astropy.io import fits
import numpy as np
import matplotlib.pyplot as plt
#hdulist	=	fits.open(raw_input("File: "))
hdulist		=	fits.open("All_sky_map_34.5MHz_GBD.fits")
#hdulist	=	fits.open("lambda_haslam408_dsds.fits")
data		=	hdulist[0].data.T
#(h,k,l)	=	data.shape
#np_d	=	np.zeros((len(data),len(data[0])), dtype='float64')

#for i in range(len(data)):
#	for j in range(len(data[0])):
#		np_d[i][j]=data[i][j]
#for i in range(len(data[0][0])):
plt.imshow(data[0:-1][0:-1][0], cmap=plt.cm.viridis)
plt.colorbar()
plt.show()
