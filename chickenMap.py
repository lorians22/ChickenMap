# Author: Logan Orians
# Date: 07/13/23

# requirements: pip install opencv-python
# MacOS (tested with 2020 M1 MBA running MacOS 12): in Terminal, type python3 chickenMap.py (type "python3 c" and press tab to autofill)
# Windows 10 (tested with 2015 MBP running BootCamp): type chickenMap.py in cmd

#Possible TODO:
#1) change coordinate system to AxB grid instead of cap resolution (need more info from E+G)
#2) Clear coordinate by clicking near it (x, y +/- a? text size?)
#3) Draw rectangles for annotating (can openCV distinguish between mouse click and drag?)
#3a) If frame is annotated, probably important, so save frame with annotation to disk?


import sys
import cv2
import pytesseract
import platform
#import re
from openpyxl import load_workbook
import pandas as pd
from datetime import datetime
import os

#point pytesseract to executable
if platform.system() == 'Windows':
    pytesseract.pytesseract.tesseract_cmd = r'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'


# Global variables
frame = None
coords = ()
systemDateTime = datetime.now().strftime('%d-%m-%Y_%H-%M-%S') #get system date time on startup


# Runs when mouse input is received on the video window. Gets coordinate from mouse input and video timestamp via OCR
def draw_coords(event, x, y, flags, param):
    global coords

    if event == cv2.EVENT_LBUTTONDOWN: #left mouse click
        coords = (x, y)
        tsArea = frame[30:100, 20:645] #bounding box of timestamp in pixels, [y:y+h, x:x+w]
        tsGray = cv2.cvtColor(tsArea, cv2.COLOR_BGR2GRAY) #convert timestampArea to grayscale
        _, tsThresh = cv2.threshold(tsGray, 127, 255, cv2.THRESH_BINARY) #binary threshold for better recognition

        timestamp = pytesseract.image_to_string(tsThresh, config='--psm 7') #convert text in image to string
        #rePattern = r'(\d{2}/\d{2}/\d{4}) (\d{2}:\d{2}:\d{2})' #regex pattern
        #if re.match(rePattern, timestamp):
        print(timestamp)
        print(str(coords)+'\n')
        write_coords_and_timestamp(timestamp, x, y)
    return

# Writes timestamp and coordinates to modern Excel file
def write_coords_and_timestamp(timestamp, x, y):
    outfilepath = 'output/'+systemDateTime+'.xlsx' #setup output file
    data = [{'Timestamp': timestamp, 'Coordinates': (x,y)}]
    df = pd.DataFrame(data)
    try:
        with pd.ExcelWriter(outfilepath, engine='openpyxl', mode='A') as writer:
            writer.book = load_workbook(outfilepath)
            df.to_excel(writer, sheet_name='Sheet1', index=False, header=False, startrow=writer.sheets['Sheet1'].max_row)
            writer.save()
    except:
        #If the file doesn't exist, create one (should only run the first time)
        df.to_excel(outfilepath, sheet_name='Sheet1', index=False)


def main():
    global frame
    global coords

    #inString = 'Copy and paste the file path (drag the cap from File Explorer here) and press Enter: '
    #infilepath = input(inString).strip() #strip trailing space for MacOS compatibility
    infilepath = sys.argv[1].strip()

    # Setup output directory
    outputDir = 'output'
    if not os.path.exists(outputDir):
        os.makedirs(outputDir)
    
    cap = cv2.VideoCapture(infilepath) #create Video Capture object

    fps = cap.get(cv2.CAP_PROP_FPS) #get fps of cap input
    if fps == 0:
        fps = 30
    delay = int(1000 / fps) #calculate delay from fps, in ms

    exitKey = 'q' #key to press to exit cap program
    clearKey = 'c' #key to clear previous coordinate on screen
    
    cv2.namedWindow('Video') #create named window to display cap
    cv2.setMouseCallback('Video', draw_coords) #mouse callback function

    while (cap.isOpened()):
        ret, frame = cap.read() #get cap frame-by-frame
        if ret:
            if coords:
                cv2.putText(frame, str(coords), coords, cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            cv2.imshow('Video', frame)

            keyPress = cv2.waitKey(delay) & 0xFF #get keyPress
            if keyPress == ord(exitKey):
                break

            if keyPress == ord(clearKey):
                coords = ()

        else:
            break

    cap.release() #release VC object
    cv2.destroyAllWindows() #close cap frames

    return


if __name__ == "__main__":
    main()
