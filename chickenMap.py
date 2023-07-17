import cv2

#/Users/kim/Downloads/SampleVideo_1280x720_1mb.mp4

infilepath = input('Copy and paste (right click) the file path: ')

video = cv2.VideoCapture(infilepath) #create VideoCapture object
fps = video.get(cv2.CAP_PROP_FPS)
delay = int(1000 // fps) #get delay from fps in ms, cast to int
#delay = 1 #delay between frames in ms. 1 ms for performance, maybe
exitKey = 'q' #key to press to exit program
global frame

def mouse_callback(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        print('mouse pressed')
        coordinates = f"({x}, {y})"
        cv2.putText(frame, coordinates, (x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        cv2.imshow("Video", frame)

cv2.namedWindow('Video') #create named window to display video
cv2.setMouseCallback("Video", mouse_callback) #mouse callback function

while (video.isOpened()):
    ret, frame = video.read() #get video frame-by-frame
    if ret:
        cv2.imshow('Frame', frame)
        if cv2.waitKey(1) & 0xFF == ord(exitKey):
            break
    else:
        break

video.release() #release VC object
cv2.destroyAllWindows() #close video frames
