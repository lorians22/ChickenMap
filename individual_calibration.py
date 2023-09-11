#Author: Logan Orians
#Date: 08/19/23

### USAGE
# individual_calibration.py <path_to_images> <filetype>
# ex:  individual_calibration.py images/individual/NB2B jpg

#NOTES:
# NB2B seems to use 12/18 images for calibration
# NB3A seems to use 15/17 images for calibration
# goal was 10, so should be fine
# not sure why NB2B is so much worse than NB3A...reflections?

import sys
import cv2
import numpy as np
import glob
import pathlib

# Perform camera calibration
def indiv_calibration(filepath, filetype):
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

			# Display corners (can comment out)
			#cv2.drawChessboardCorners(image, chSize, corners2, ret)
			#cv2.imshow('img', image)
			#cv2.waitKey(1000) #display image for 1 second

	# Camera calibration
	ret, camMatrix, distCoeffs, rotVecs, transVecs = cv2.calibrateCamera(objectPoints, imagePoints, gray.shape[::-1], None, None)

	# Print results (can comment out)
	print('Camera Matrix:\n', camMatrix)
	print('Distortion Coefficients', distCoeffs)

	return camMatrix, distCoeffs, rotVecs, transVecs

# Visually check if calibrated chBoard is "flat" and has straight lines
def sanity_check(filepath, filetype, camMatrix, distCoeffs):
	image = cv2.imread(filepath+'/image00'+filetype) #read in test image
	undistImage = cv2.undistort(image, camMatrix, distCoeffs, None, camMatrix) #undistort image
	cv2.imshow('Undistorted Image', undistImage) #show image
	cv2.waitKey(0) #wait for keypress
	cv2.destroyAllWindows() #close image viewer

	return

# Write camera matrix and distortion coefficients if satisfied with sanity check
def write_results(filepath, camMatrix, distCoeffs):
	# Setup output file
	path = pathlib.PurePath(filepath)
	outFileMtx = path.name+'_camMatrix'
	outFileDst = path.name+'_distCoeffs'

	#write to .npy for easier import
	np.save(outFileMtx, camMatrix)
	np.save(outFileDst, distCoeffs)

if __name__ == '__main__':
	filepath = sys.argv[1] #path to images you want to use for calibration
	filetype = '.'+sys.argv[2] #filetype of images you want to use for calibration
	camMatrix, distCoeffs, rotVecs, transVecs = indiv_calibration(filepath, filetype)
	sanity_check(filepath, filetype, camMatrix, distCoeffs)
	write_results(filepath, camMatrix, distCoeffs)