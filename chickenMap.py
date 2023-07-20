# Author: Logan Orians
# Date: 07/13/23

# requirements: pip install opencv-python
# MacOS (tested with 2020 M1 MBA running MacOS 12): in Terminal, type python3 chickenMap.py (type "python3 c" and press tab to autofill)
# Windows 10 (tested with 2015 MBP running BootCamp): type chickenMap.py in cmd

#TODO:
#1) change coordinate system to AxB grid instead of video resolution (need more info from E+G)
#2) ensure file type compatibility between openCV and chicken videos (.mp4?)
#3) Clear coordinate by clicking near it (x, y +/- a? text size?)
#4) Draw rectangles for annotating (can openCV distinguish between mouse click and drag?)
#4a) If frame is annotated, probably important, so save frame with annotation to disk?
#5) Update instructions (navigating to path)


import cv2


# "Global" variables
coordsList = [] #list of x,y,coordinate tuples


#openCV function for mouse input
def mouse_callback(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN: #left mouse click
        coords = f"({x}, {y})"
        coordsList.append((x, y, coords)) #append tuple to list
    return


def main():
    inString = 'Copy and paste the file path (drag the video from File Explorer here) and press Enter: '
    infilepath = input(inString).strip() #strip trailing space for MacOS compatibility

    video = cv2.VideoCapture(infilepath) #create VideoCapture object

    fps = video.get(cv2.CAP_PROP_FPS) #get fps of video input
    if fps == 0:
        fps = 30
    delay = int(1000 / fps) #calculate delay from fps, in ms

    exitKey = 'q' #key to press to exit video program
    clearKey = 'c' #key to clear previous coordinate on screen
    
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
            elif len(coordsList) > 0 and keyPress == ord(clearKey):
                coordsList.pop()

        else:
            break

    video.release() #release VC object
    cv2.destroyAllWindows() #close video frames

    return


if __name__ == "__main__":
    main()
