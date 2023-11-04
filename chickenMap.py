#!/usr/bin/python3

#TODO: follow google style guide docstrings (incorporate Usage)
"""A coordinate mapping program made initially for chicken research"""

'''
Copyright 2023, Logan Orians in affiliation with Purdue University:
    Dr. Marisa Erasmus and Gideon Ajibola.

Approved for private use by students and employees of Purdue University only.
No implied support or warranty.
'''

# Date: 07/13/23

# requirements: pip install -r requirements.txt
# py chickenMap.py <path_to_video>
#         ^You can drag a video file from Explorer/Finder into this window and press Enter.
# ex. py chickenMap.py test.mp4

# TODO:
# 0) --2d/--3d input args
# 1) .bat/sh files for click running
# 2) shift-left click to add a note to the spreadsheet - use flags in mouse_callback
# 3) add more error loggers
# 4) location-aware text drawing, like how a right-click menu flows up or down from cursor
# 5) update code whitespace based on GPSG
# 6) change ruler to 80 and wrap appropriately (maybe)


__version__ = '2023.10.4'
__author__ = 'Logan Orians'


import argparse
import contextlib
import json
import logging
import os
import platform
#import re
import string
import time
import tkinter as tk
import types
from typing import Any, TypeVar

import cv2
import openpyxl
import pytesseract

import options_gui


class FilePath:
    def __init__(self, directory):
        self.directory = self._make_proper_path(directory)
        self.filename = ''

    @staticmethod
    def _make_proper_path(directory):
        #lstrip() and rstrip()? needs testing
        if not directory.endswith('/') and not directory.endswith('\\'): directory += '/'
        if not os.path.exists(directory): os.makedirs(directory)

        return directory

    def __str__(self):
        return f"{self.directory}{self.filename}"


class SpreadSheet(FilePath):
    def __init__(self, directory, filename, headers):
        super().__init__(directory)
        self.filename = f"{filename}.xlsx"
        self._set_up_spreadsheet(headers)

    def _set_up_spreadsheet(self, headers):
        """Sets up the output spreadsheet by adding bolded headers to columns.

        Args:
            headers (list): the bolded column headers to be written
        """

        with contextlib.closing(openpyxl.workbook.Workbook()) as wb:
            ws = wb.active
            ws.append(headers)
            for cell in ws['1:1']:
                cell.font = openpyxl.styles.Font(bold=True) #make headers bold
            wb.save(str(self))

    def append_to_spreadsheet(self, data):
        """Appends input data to spreadsheet.

        Args:
            data (list): the data to be appended
        """

        with contextlib.closing(openpyxl.load_workbook(str(self))) as wb: #open existing workbook
            wb.active.append(data) #append data to sheet
            wb.save(str(self)) #save workbook

    def delete_last_coordinate(self):
        """Deletes most recent coordinate from Excel sheet."""

        with contextlib.closing(openpyxl.load_workbook(str(self))) as wb:
            ws = wb.active
            last_row = ws.max_row
            ws.delete_rows(last_row)
            wb.save(str(self))


class AnnotationManager(FilePath):
    def __init__(self, directory):
        super().__init__(directory)
        self.anno_pos = (0, 0)
        self.anno_text = ''
        self.enter_time = 0
        self.filename = ''
        self.frame = None
        self.show_anno = False
        self.timestamp_time = ''
        self.typing = False
        self.write_anno = False

    def start_typing(self, x, y, timestamp_time):
        self.anno_pos = (x, y)
        self.anno_text = ''
        self.enter_time = 0
        self.filename = f"{timestamp_time.replace(':', '-')}.jpg"
        self._prevent_filename_overwrite()
        self.show_anno = True
        self.timestamp_time = timestamp_time
        self.typing = True
        self.write_anno = False

    def _prevent_filename_overwrite(self):
        """Gets next available filename (to avoid overwriting image at same timestamp)."""

        root, ext = os.path.splitext(self.filename) #get name and extension
        num = 0
        while os.path.exists(self.directory + self.filename):
            num += 1
            self.filename = f"{root}_{num}{ext}"


class CoordinateManager():
    def __init__(self, three_d=False):
        self._coord = ()
        self.start_time = 0
        self._three_d = three_d

    @property
    def coord(self):
        return self._coord
    
    @coord.setter
    def coord(self, x_and_y):
        if self._three_d:
            self._coord = self._get_3d_from_2d(*x_and_y)
        else:
            self._coord = x_and_y

    @staticmethod
    def _get_3d_from_2d(x, y):
        return (x, y)


def mouse_input(event, x, y, flags, param):
    del flags # Unused.

    coord, anno, sheet = param

    if not anno.typing: #if user *isn't* typing annotation
        if event == cv2.EVENT_LBUTTONDOWN: #left mouse click
            coord.start_time = time.time()
            coord.coord = (x, y)
            timestamp_date, timestamp_time = get_timestamp(anno.frame)

            data = [timestamp_date, timestamp_time, f"({x}, {y})"] #format data
            sheet.append_to_spreadsheet(data)

            # Print timestamp and coordinates in case .xlsx gets corrupted
            print(timestamp_date)
            print(timestamp_time)
            print(f"{str(coord.coord)}\n")

        elif event == cv2.EVENT_RBUTTONDOWN: #right mouse click
            _, timestamp_time = get_timestamp(anno.frame)
            anno.start_typing(x, y, timestamp_time)


def get_timestamp(frame):
    """Gets burnt-in timestamp via OCR (not video timestamp from OpenCV).
    

    Returns:
        timestamp_date (str): date from timestamp, DD/MM/YYYY
        timestamp_time (str): time from timestamp, HH:MM:SS
    """

    timestamp_area = frame[30:100, 26:634] #bounding box of timestamp in pixels, [y:y+h, x:x+w]
    timestamp_gray = cv2.cvtColor(timestamp_area, cv2.COLOR_BGR2GRAY) #convert to grayscale
    #binary threshold for better recognition
    _, timestamp_thresh = cv2.threshold(timestamp_gray, 187, 255, cv2.THRESH_BINARY)
    #cv2.imshow('thresh', timestamp_thresh)
    #convert text in image to string
    timestamp = pytesseract.image_to_string(timestamp_thresh, config='--psm 7')
    timestamp_date, timestamp_time = timestamp.strip().split(' ') #remove space, split after date

    # regex in case it messes up. but it seems to be okay without it
    #rePattern = r'(\d{2}/\d{2}/\d{4}) (\d{2}:\d{2}:\d{2})' #regex group pattern
    #patternMatch = re.search(rePattern, timestamp)
    #timestamp_date = patternMatch.group(0)
    #timestamp_time = patternMatch.group(1)

    return timestamp_date, timestamp_time


def get_set_proper_dir(argument):
    """Makes sure input argument is a directory.
    
    Args:
        argument (str): the input argument directory

    Returns:
        argument (str): the corrected directory
    """

    if not argument.endswith('/') and not argument.endswith('\\'):
        argument += '/'
    if not os.path.exists(argument):
        os.makedirs(argument)

    return argument


def arg_parsing():
    """Parses input arguments; separate from main() because it's long.

    Returns:
        parser.parse_args() (argparse.Namespace): object containing inputted command line arguments
    """

    parser = argparse.ArgumentParser(
        description='A program that displays and saves coordinates for tracking chicken behavior.')
    parser.add_argument('-o', '--options', action='store_true',
        help='Opens the GUI for setting program options.')
    parser.add_argument('--version', action='version',
        version=f"%(prog)s {__version__}", help=argparse.SUPPRESS)

    return parser.parse_args()


def get_args_from_file(filename: str) -> dict[str, Any]:
    """Gets program options from file.

    Args:
        filename: name of file that contains options

    Returns:
        args: arguments from file
    """

    try:
        with open(filename, 'r') as f:
            args = json.load(f)
        return args
    except OSError as e:
        print(f'Error accessing file; please contact author: {e}')
        raise
    except json.JSONDecodeError as e:
        print(f'Error decoding JSON, please contact author: {e}')
        raise


# TODO: get more info?
def get_system_info():
    """Gets system info, formatted into lines, for the error log file.

    Returns:
        info (str): multi-line string containing system info
    """

    uname = platform.uname()
    info = (
        f"\nOS: {uname.system}\n"
        f"Release: {uname.release}\n"
        f"Version: {uname.version}\n"
        f"Processor: {uname.processor}\n"
        f"Python: {platform.python_version()}"
    )

    return info


def set_up_logger():
    """Sets up error logger with custom terminator to separate error entries.

    Returns:
        logger (logging.Logger): an instance of a logger object
    """

    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    file_handler = logging.FileHandler('error_log.txt')
    file_handler.terminator = f"\n\n{'=' * 80}\n\n"
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger


def get_window_and_video_dims(cap):
    """Gets screen resolution and returns suitable window dimensions.

    Args:
        cap (cv2.VideoCapture obj): video captured by OpenCV

    Returns:
        window_width (int): suitable window width, in pixels
        window_height (int): suitable window height, in pixels
    """

    # Get screen resolution
    root = tk.Tk()
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    root.destroy()

    video_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    video_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    aspect_ratio = video_width / video_height
    window_width = int(min(screen_width - 150, video_width)) #account for taskbar, etc.
    window_height = int(window_width / aspect_ratio)

    return window_width, window_height, video_width, video_height


def main():
    
    args = arg_parsing()
    if args.options:
        options_gui.main() #run GUI

    logger = set_up_logger() #set up bad error logger

    system_date_time = time.strftime('%Y-%m-%d_%H-%M-%S', time.localtime()) #ISO 8601
    ascii_allowlist = string.printable[:-5] #OpenCV can only print up to <space>

    #point pytesseract to tesseract executable
    if platform.system() == 'Windows':
        pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
    
    options_file = 'options.json'
    prog_options = types.SimpleNamespace(**get_args_from_file(options_file))

    # Set up arguments for program use
    infile_path = prog_options.video_path.strip() #strip trailing space for MacOS
    if prog_options.exit_key.lower() == 'esc':
        exit_key = 27
    else:
        exit_key = ord(prog_options.exit_key)
    clear_key = ord(prog_options.clear_key)
    pause_key = ord(prog_options.pause_key)
    duration = prog_options.duration #duration of coords and annos on screen, in seconds
    font = types.SimpleNamespace(font=prog_options.font, scale=prog_options.font_scale,
        color=tuple(prog_options.font_color), thickness=prog_options.font_thickness)

    # Instantiate classes
    #coord = types.SimpleNamespace(xy=(), start_time=0)
    coord = CoordinateManager()
    anno = AnnotationManager(f"{prog_options.anno_dir}/{system_date_time}")
    headers = ['Date', 'Time', 'Coordinates']
    sheet = SpreadSheet(prog_options.out_dir, system_date_time, headers)

    # Determine delay to play video at normal speed
    cap = cv2.VideoCapture(infile_path) #create Video Capture object
    fps = cap.get(cv2.CAP_PROP_FPS) #get fps of cap input
    if fps == 0:
        fps = 25 #set default if determination fails
    delay = int(1000 / fps) #calculate delay from fps, in ms

    # Set up video window
    w_width, w_height, v_width, v_height = get_window_and_video_dims(cap)
    window_name = 'Video'
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL) #create named window to display cap
    cv2.resizeWindow(window_name, width=w_width, height=w_height)

    paused = False
    callback_params = (coord, anno, sheet)
    cv2.setMouseCallback(window_name, mouse_input, param=callback_params)


    try:
        while cap.isOpened():
            if not paused:
                ret, anno.frame = cap.read() #get cap frame-by-frame
                if not ret: break
                
                # Get LSByte of keypress for cross-platform compatibility
                key_press = cv2.waitKey(delay) & 0xFF
                if not anno.typing:
                    if key_press == exit_key: #quit program
                        break
                    if anno.write_anno:
                        anno.write_anno = False
                        cv2.imwrite(str(anno), frame_copy)
                    if time.time() - anno.enter_time > duration:
                        anno.show_anno = False
                        anno.anno_text = ''

            # Prevent coords from popping back up after annotation is entered
            if anno.typing:
                coord.coord = ()

            # Only allow deletion of [date, time, coord] when on screen
            if coord.coord:
                frame_copy = anno.frame.copy() #clearing looks better
                if key_press == clear_key:
                    coord.coord = ()
                    sheet.delete_last_coordinate()
                elif (time.time() - coord.start_time < duration): #on-screen coordinate timeout
                    if paused:
                        cv2.putText(frame_copy, str(coord.coord), coord.coord[:2],
                            font.font, font.scale, font.color, font.thickness)
                    else:
                        cv2.putText(anno.frame, str(coord.coord), coord.coord[:2],
                            font.font, font.scale, font.color, font.thickness)

            # This while loop ensures that the video is paused while annotating
            while anno.typing:
                frame_copy = anno.frame.copy() #get copy of frame so backspace works

                if anno.show_anno:
                    cv2.putText(frame_copy, anno.anno_text,
                        anno.anno_pos, font.font, font.scale,
                        font.color, font.thickness)
                    cv2.imshow(window_name, frame_copy)

                key_press = cv2.waitKey(0) & 0xFF #LSByte for cross-plat compat
                if key_press != 255:
                    if key_press == 13: #Enter
                        anno.typing = False
                        anno.write_anno = True
                        anno.enter_time = time.time()
                    elif key_press == 27: #Esc
                        anno.typing = False
                        anno.show_anno = False
                        anno.anno_text = ''
                    elif key_press == 8: #Backspace
                        if anno.anno_text: #DON'T COMBINE INTO ^ELIF
                            anno.anno_text = anno.anno_text[:-1]
                    elif chr(key_press) in ascii_allowlist: #printable ascii
                        anno.anno_text += chr(key_press)
                        anno.show_anno = True

            if anno.show_anno:
                if paused:
                    cv2.putText(frame_copy, anno.anno_text,
                        anno.anno_pos, font.font,
                        font.scale, font.color, font.thickness)
                else:
                    cv2.putText(anno.frame, anno.anno_text,
                        anno.anno_pos, font.font,
                        font.scale, font.color, font.thickness)

            if not(paused and (coord.coord or anno.show_anno)):
                cv2.imshow(window_name, anno.frame) #show video frame

    except Exception as e:
        logger.error('\nError: %s\n', e, exc_info=True)
        print(f'\n***AN ERROR OCCURRED! PLEASE FOLLOW THE SUPPORT INSTRUCTIONS IN THE README.***')

    finally:
        if 'cap' in locals() or 'cap' in globals(): #if program initialized cap before error
            cap.release() #release video capture object
            cv2.destroyAllWindows() #close all OpenCV windows


if __name__ == "__main__":
    main()
