# Author: Logan Orians
# Date: 07/13/23

# requirements: pip install -r requirements.txt
# python chickenMap.py <path_to_video>          You can drag a video file from Explorer/Finder into this window and press Enter
# ex. python chickenMap.py test.mp4

# Notes: It's probably bad practice to have a 'time' variable when I'm importing the time package. But it works, so I don't mind.


# TODO:
# show coordinate on screen for ~5 seconds

import sys
import os
import cv2
import pytesseract
import platform
import time
from datetime import datetime
import openpyxl
#import re


#point pytesseract to tesseract executable
if platform.system() == 'Windows':
    pytesseract.pytesseract.tesseract_cmd = r'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'


# Global variables
frame = None #get_timestamp() needs video frame when mouse is clicked
coords = () #need to get coords from mouse_callback, but mouse_callback doesn't "return"
outfilepath = ''


# Runs when mouse input is received on the video window. Gets coordinate from mouse input and video timestamp via OCR
def mouse_callback(event, x, y, flags, param):
    global coords

    if event == cv2.EVENT_LBUTTONDOWN: #left mouse click
        coords = (x, y)
        date, time = get_timestamp()
        write_excel_file(date, time, x, y)

        #Print timestamp and coordinates in case .xlsx gets corrupted
        print(date) 
        print(time)
        print(str(coords))
        print() #print newline to separate


    elif event == cv2.EVENT_RBUTTONDOWN: #right mouse click
        _, time = get_timestamp()
        annotation = input('Enter annotation: ')
        cv2.putText(frame, annotation, (x, y), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 0), 2)
        
        #create output directory if it doesn't exist
        annoDir = 'annotated_images/'
        if not os.path.exists(annoDir):
            os.makedirs(annoDir)

        filename = annoDir+time.replace(':', '-')+'.jpg'
        annofilename = get_next_filename(filename) #makes sure not to overwrite image
        cv2.imwrite(annofilename, frame)

    return


# Gets next available filename (to avoid overwriting image at same timestamp with multiple views of same video)
def get_next_filename(filename):
    newFile = filename
    root, ext = os.path.splitext(filename)
    count = 0
    while os.path.exists(newFile):
        count += 1
        newFile = '{}_{}{}'.format(root, count, ext)
    return newFile



# Gets burnt-in timestamp via OCR (not video timestamp from OpenCV)
def get_timestamp():
    tsArea = frame[30:100, 20:645] #bounding box of timestamp in pixels, [y:y+h, x:x+w]
    tsGray = cv2.cvtColor(tsArea, cv2.COLOR_BGR2GRAY) #convert timestampArea to grayscale
    _, tsThresh = cv2.threshold(tsGray, 127, 255, cv2.THRESH_BINARY) #binary threshold for better recognition
    timestamp = pytesseract.image_to_string(tsThresh, config='--psm 7') #convert text in image to string
    #rePattern = r'(\d{2}/\d{2}/\d{4}) (\d{2}:\d{2}:\d{2})' #regex group pattern
    #if re.match(rePattern, timestamp): #could use regex to verify but this has been accurate so far

    return timestamp.strip().split(' ') #date, time


# Sets up Excel file and adds bolded headers
def setup_excel_file():
    headers = ['Date', 'Time', 'Coordinates']
    wb = openpyxl.workbook.Workbook()
    ws = wb.active
    ws.append(headers)
    for cell in ws['1:1']:
        cell.font = openpyxl.styles.Font(bold=True) #make headers bold
    wb.save(outfilepath)
    wb.close()

    return


# Writes timestamp and coordinates to .xlsx
def write_excel_file(date, time, x, y):
    data = [date, time, f'({x}, {y})'] #use f-string to format coordinate
    wb = openpyxl.load_workbook(outfilepath) #open existing workbook
    wb.active.append(data) #append data to sheet
    wb.save(outfilepath) #save workbook
    wb.close() #close file

    return


# Clears last coordinate saved to Excel file
def delete_last_coordinate():
    wb = openpyxl.load_workbook(outfilepath)
    ws = wb.active
    lastRow = ws.max_row
    ws.delete_rows(lastRow)
    wb.save(outfilepath)
    wb.close()

    return


def main():
    global frame
    global coords
    global outfilepath

    infilepath = sys.argv[1].strip() #strip trailing space for MacOS compatibility

    # Setup output directory and file
    outputDir = 'output'
    if not os.path.exists(outputDir):
        os.makedirs(outputDir)
    systemDateTime = time.strftime('%Y-%m-%d_%H-%M-%S', time.localtime()) #ISO 8601 system date/time
    outfilepath = outputDir+'/'+systemDateTime+'.xlsx'
    setup_excel_file()
    
    cap = cv2.VideoCapture(infilepath) #create Video Capture object
    fps = cap.get(cv2.CAP_PROP_FPS) #get fps of cap input
    #print(fps)
    if fps == 0:
        fps = 25 #set default if determination fails
    delay = int(1000 / fps) #calculate delay from fps, in ms

    exitKey = 'q' #key to press to exit video program
    clearKey = 'c' #key to clear previous coordinate on screen
    
    cv2.namedWindow('Video') #create named window to display cap
    cv2.setMouseCallback('Video', mouse_callback) #mouse callback function

    while (video.isOpened()):
        ret, frame = video.read() #get video frame-by-frame
        if ret:
            keyPress = cv2.waitKey(delay) & 0xFF #get keyPress
            if keyPress == ord(exitKey): #quit program
                break

            if coords: #only allow removal of [date, time, coord] when on screen
                if keyPress == ord(clearKey):
                    coords = ()
                    delete_last_coordinate()
                else:
                    cv2.putText(frame, str(coords), coords, cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            cv2.imshow('Video', frame) #show video frame
        else:
            break

    cap.release() #release video capture object
    cv2.destroyAllWindows() #close all OpenCV windows

    return


if __name__ == "__main__":
    main()
