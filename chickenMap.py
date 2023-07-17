#Author: Logan Orians
#Date: 07/13/23

#requirements: pip install opencv-python
#does not seem to function properly on MacOS (tested with 2021 M1 MBA running MacOS 12)
#does work on Windows 10 (tested 2015 MBP running BootCamp)
#to run: chickenMap.py in cmd

#TODO:
#1) change coordinate system to AxB grid instead of video resolution (need more info from E+G)
#2) ensure file type compatibility between openCV and chicken videos (.mp4?)
#3) Clear coordinate by clicking near it (x, y +/- a? text size?)

import cv2

coordsList = [] #"global" list of x,y,coordinate tuples

#openCV function for mouse input
def mouse_callback(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN: #left mouse click
        coords = f"({x}, {y})"
        coordsList.append((x, y, coords)) #append tuple to list
    return

def main():
    infilepath = input('Copy and paste the file path (drag the video from File Explorer into here): ')

    video = cv2.VideoCapture(infilepath) #create VideoCapture object

    fps = video.get(cv2.CAP_PROP_FPS) #get fps of video input
    delay = int(1000 / fps) #calculate delay from fps, in ms

    exitKey = 'q' #key to press to exit video program
    clearLey = 'c' #key to clear previous coordinate on screen
    
    cv2.namedWindow('Video') #create named window to display video
    cv2.setMouseCallback("Video", mouse_callback) #mouse callback function

    while (video.isOpened()):
        ret, frame = video.read() #get video frame-by-frame
        if ret:
            for coord in coordsList:
                x, y, coords = coord #unpack each (x,y,coords)
                cv2.putText(frame, coords, (x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            cv2.imshow('Video', frame)

            keyPress = cv2.waitKey(delay) & 0xFF #get keyPress
            if keyPress == ord(exitKey):
                break

            #clear previous coordinate
            elif len(coordsList) > 0 and keyPress == ord('c'):
                coordsList.pop()

        else:
            break

    video.release() #release VC object
    cv2.destroyAllWindows() #close video frames

if __name__ == "__main__":
    main()
