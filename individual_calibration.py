#Author: Logan Orians
#Date: 08/19/23

import sys
import cv2
import numpy as np
import glob

def main():

	filepath = str(sys.argv[1]) #path to images you want to use for calibration
	filetype = '.jpg' #filetype of images you want to use for calibration

	#termination criteria for subpixel precision calculation
	criteria = cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001

	chSize = (8, 5) #size of checkerboard
	objectPoints = [] #init 3D points
	imagePoints = [] #init 2D points

	# Process checkerboard points
	objP = np.zeros((chSize[0] * chSize[1], 3), np.float32)
	objP[:, :2] = np.mgrid[0:chSize[0], 0:chSize[1]].T.reshape(-1, 2)

	# Import calibration images
	images = glob.glob(filepath+'/*'+filetype)

	for imageFile in images:
		image = cv2.imread(imageFile) #read image
		gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) #convert to grayscale

		ret, corners = cv2.findChessboardCorners(gray, chSize, None) #find corners

		# Add to points arrays
		if ret:
			objectPoints.append(objP)
			corners2 = cv2.cornerSubPix(gray, corners, (11,11), (-1,-1), criteria) #increase subpixel precision
			imagePoints.append(corners2)

	# Camera calibration
	ret, camMatrix, distCoeffs, rotVecs, transVecs = cv2.calibrateCamera(objectPoints, imagePoints, gray.shape[::-1], None, None)

	# Print results
	print('Camera Matrix:\n', camMatrix)
	print('Distortion Coefficients', distCoeffs)

	# Setup output file
	cameraModel = filepath.rsplit('/', 1)[-1] #determine output file name
	outFile = cameraModel+'.txt' #set output file name
	FILE = open(outFile, 'w') #clear file
	FILE = open(outFile, 'a') #open file for appending

	# Write results to output file
	camMatrix.tofile(FILE, sep=' ') #write camera matrix to file
	FILE.write('\n') #separate by newline
	distCoeffs.tofile(FILE, sep=' ') #write distortion coefficients to file
	FILE.close() #close file

	# Sanity check: make sure things look okay (straight lines) by undistorting image
	image = cv2.imread(filepath+'/image00.jpg') #hardcode straight-on image
	undistImage = cv2.undistort(image, camMatrix, distCoeffs, None, camMatrix) #undistort image
	cv2.imshow('Undistorted Image', undistImage) #show image
	cv2.waitKey(0) #wait for keypress
	cv2.destroyAllWindows() #close image viewer

if __name__ == '__main__':
	main()