#Author: Logan Orians
#Date: 08/28/23

import sys
import cv2
import numpy as np
import glob
import pathlib
from matplotlib import pyplot as plt

#NOTES:
#Calibration hit on 5/7 image pairs. Not bad, but it does seem to lag a bit after the first image,
#so I removed the two offending images. Those images had the checkerboard very far away,
#but it should've just skipped past if it didn't detect the corners. Oh well

# Read camera matrices and distortion coefficients from individual calibration
def load_camera_params():
	camMatrixLeft = np.load('inputs/NB2B_camMatrix.npy')
	distCoeffsLeft = np.load('inputs/NB2B_distCoeffs.npy')

	camMatrixRight = np.load('inputs/NB3A_camMatrix.npy')
	distCoeffsRight = np.load('inputs/NB3A_distCoeffs.npy')

	return camMatrixLeft, distCoeffsLeft, camMatrixRight, distCoeffsRight


# Perform stereo calibration
def stereo_cal(filepathLeft, filepathRight, filetype):
	#termination criteria for subpixel precision calculation
	criteria = cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001

	chSize = (8, 5) #size of checkerboard (inside vertices, not squares)
	chSqSize = 90 #size of checkerboard square in mm

	# Init points arrays
	objectPoints = []
	imagePointsLeft = []
	imagePointsRight = []

	# Setup 3D object points
	objP = np.zeros((np.prod(chSize), 3), dtype=np.float32)
	objP[:, :2] = np.mgrid[0:chSize[0], 0:chSize[1]].T.reshape(-1, 2)
	objP *= chSqSize #adjust for size of square on chBoard

	# Get calibration images
	imagesLeft = sorted(glob.glob(filepathLeft+'/*'+filetype))
	imagesRight = sorted(glob.glob(filepathRight+'/*'+filetype))
	imagePairs = zip(imagesLeft, imagesRight) #convert to iterable for for loop

	for imageFileLeft, imageFileRight in imagePairs:
		grayLeft = cv2.imread(imageFileLeft, cv2.IMREAD_GRAYSCALE) #read left image, convert to grayscale
		grayRight = cv2.imread(imageFileRight, cv2.IMREAD_GRAYSCALE) #read right image, convert to grayscale

		retLeft, cornersLeft = cv2.findChessboardCorners(grayLeft, chSize, None) #find left image's corners
		retRight, cornersRight = cv2.findChessboardCorners(grayRight, chSize, None) #find right image's corners

		# Add to points arrays
		if retLeft and retRight:
			objectPoints.append(objP)
			cornersLeft = cv2.cornerSubPix(grayLeft, cornersLeft, (11,11), (-1,-1), criteria) #increase subpixel precision
			cornersRight = cv2.cornerSubPix(grayRight, cornersRight, (11,11), (-1,-1), criteria) #increase subpixel precision
			imagePointsLeft.append(cornersLeft)
			imagePointsRight.append(cornersRight)

			'''
			# Display corners
			cv2.drawChessboardCorners(grayLeft, chSize, cornersLeft, retLeft)
			cv2.imshow('img', grayLeft)
			cv2.waitKey(1000) #display image for 1 second
			'''

	# Camera calibration
	ret, camMatrixLeftStereo, distCoeffsLeftStereo, camMatrixRightStereo, distCoeffsRightStereo, R, T, _, _ = cv2.stereoCalibrate(objectPoints, imagePointsLeft, imagePointsRight, camMatrixLeft, distCoeffsLeft, camMatrixRight, distCoeffsRight, grayLeft.shape[::-1])

	return camMatrixLeftStereo, distCoeffsLeftStereo, camMatrixRightStereo, distCoeffsRightStereo, R, T, grayLeft


# Write outputs of stereo calibration to files
def write_results(filepathLeft, filepathRight, camMatrixLeft, distCoeffsLeft, camMatrixRight, distCoeffsRight):
	# Setup output files
	pathLeft = pathlib.PurePath(filepathLeft)
	parentDirLeft = pathLeft.parts[-2]
	outFileMtxLeft = 'outputs/'+parentDirLeft+pathLeft.name+'_camMatrixStereoLeft'
	outFileDstLeft = 'outputs/'+parentDirLeft+pathLeft.name+'_distCoeffsStereoLeft'

	pathRight = pathlib.PurePath(filepathRight)
	parentDirRight = pathRight.parts[-2]
	outFileMtxRight = 'outputs/'+parentDirRight+pathRight.name+'_camMatrixStereoRight'
	outFileDstRight = 'outputs/'+parentDirRight+pathRight.name+'_distCoeffsStereoRight'

	#write to .npy for easier import
	np.save(outFileMtxLeft, camMatrixLeft)
	np.save(outFileDstLeft, distCoeffsLeft)
	np.save(outFileMtxRight, camMatrixRight)
	np.save(outFileDstRight, distCoeffsRight)

	return

# Load your stereo images
img1 = cv2.imread('images/floor/NB2B/image05.jpg')
img2 = cv2.imread('images/floor/NB3A/image05.jpg')

def stereo_rectify(camMatrixLeft, distCoeffsLeft, camMatrixRight, distCoeffsRight, R, T, gray):
	# Stereo rectification transforms computation
	rotLeft, rotRight, poseLeft, poseRight, disp2depth, _, _ = cv2.stereoRectify(camMatrixLeft, distCoeffsLeft, camMatrixRight, distCoeffsRight, gray.shape[::-1], R, T)

	# Undistortion and rectification transformation map computation
	mapLeftX, mapLeftY = cv2.initUndistortRectifyMap(camMatrixLeft, distCoeffsLeft, R, poseLeft, gray.shape[::-1], cv2.CV_32FC1)
	mapRightX, mapRightY = cv2.initUndistortRectifyMap(camMatrixRight, distCoeffsRight, R, poseRight, gray.shape[::-1], cv2.CV_32FC1)

	# Stereo images rectification
	img1Rect = cv2.remap(img1, mapLeftX, mapLeftY, cv2.INTER_LINEAR)
	img2Rect = cv2.remap(img2, mapRightX, mapRightY, cv2.INTER_LINEAR)

	# Disparity computation
	stereo = cv2.StereoSGBM_create(minDisparity=0, numDisparities=16, blockSize=5)
	disparity = stereo.compute(img1Rect, img2Rect)
	
	# Visualization
	num_lines = 10  # Number of epipolar lines to draw
	line_color = (0, 0, 255)  # Red color for lines

	# Define some points on the left image
	points_left = [(100, 200), (150, 250), (200, 300), (250, 350)]

	for point in points_left:
	    x, y = point
	    cv2.circle(img1Rect, (x, y), 5, line_color, -1)
	    lines = cv2.computeCorrespondEpilines(np.array([[x, y]]).reshape(-1, 1, 2), 1, rotRight, T)
	    lines = lines.reshape(-1, 3)
	    for line in lines:
	        a, b, c = line
	        x0, y0, x1, y1 = 0, int(-c / b), img2Rect.shape[1], int(-(c + a * img2Rect.shape[1]) / b)
	        cv2.line(img2Rect, (x0, y0), (x1, y1), line_color, 2)

	# Display the rectified images with epipolar lines
	cv2.imshow("Rectified Left Image with Epipolar Lines", img1Rect)
	cv2.imshow("Rectified Right Image", img2Rect)
	cv2.waitKey(0)
	cv2.destroyAllWindows()
	'''
	disparityScaled = cv2.normalize(disparity, dst=None, alpha=0, beta=511, norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_8U)
	#cv2.imshow("Rectified Left Image", img1Rect)
	#cv2.imshow("Rectified Right Image", img2Rect)
	cv2.applyColorMap(disparityScaled, cv2.COLORMAP_JET)
	cv2.imshow("Disparity Map", disparityScaled)
	cv2.waitKey(0)
	cv2.destroyAllWindows()
	fig, ax = plt.subplots(ncols=3, nrows=1)
	ax[0].imshow(img1Rect)
	ax[1].imshow(img2Rect)
	ax[2].imshow(disparityScaled)
	plt.show()
	'''

	# Return array of 3D points
	return cv2.reprojectImageTo3D(disparity, disp2depth)


if __name__ == '__main__':
	filepathLeft = sys.argv[1] #NB2B, floor or aviary
	filepathRight = sys.argv[2] #NB3A, floor or aviary
	filetype = sys.argv[3]
	camMatrixLeft, distCoeffsLeft, camMatrixRight, distCoeffsRight = load_camera_params() #get params from indiv_cal
	camMatrixLeftStereo, distCoeffsLeftStereo, camMatrixRightStereo, distCoeffsRightStereo, R, T, gray = stereo_cal(filepathLeft, filepathRight, filetype) #perform stereo calibration
	write_results(filepathLeft, filepathRight, camMatrixLeftStereo, distCoeffsLeftStereo, camMatrixRightStereo, distCoeffsRightStereo) #write new mtxs and coeffs to file
	points3D = stereo_rectify(camMatrixLeftStereo, distCoeffsLeftStereo, camMatrixRightStereo, distCoeffsRightStereo, R, T, gray)