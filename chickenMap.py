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
# 0) update coords for 2D vs 3D (get_3D_from_2D); --3D/--2D input args
#   - turn coord into class, add get_coord(). and have 3d coord class inherit, w/ get_3d()
# 1) argparse output file option: allow custom output file, but use get_next_filename() to prevent o/w
#   - prevent out_dir and anno_dir from being the same name (raise custom error?)
#   - input validation (after merging with default values?)
#   - pip install pathvalidate
# 3) add more error loggers
# 4) location-aware text drawing, like how a right-click menu flows up or down from cursor
# 5) function type hints
# 6) update code whitespace based on GPSG
# 7) add GUI (dropdown menus, sanitized text boxes) for options.json5?
# 8) change ruler to 80 and wrap appropriately (maybe)

# TO DO For someone that isn't me and knows Python UI development:
#   convert this to use a dedicated UI and keyboard/mouse input library instead of OpenCV?


__version__ = '2023.10.2'
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
import tkinter as tk #screen resolution
import types #for SimpleNamespace

import cv2
import openpyxl #Excel engine
import pytesseract #Tesseract-OCR wrapper


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


class AnnoTation(FilePath):
    def __init__(self, directory):
        super().__init__(directory)
        self.anno_text = ''
        self.typing = False
        self.enter_time = 0
        self.show_anno = False
        self.write_anno = False
        self.anno_pos = (0, 0)
        self.timestamp_time = ''

    def start_typing(self, x, y, timestamp_time):
        self.typing = True
        self.anno_text = ''
        self.enter_time = 0
        self.show_anno = True
        self.write_anno = False
        self.anno_pos = (x, y)
        self.timestamp_time = timestamp_time
        self.filename = f"{timestamp_time.replace(':', '-')}.jpg"
        self._prevent_filename_overwrite()

    def _prevent_filename_overwrite(self):
        """Gets next available filename (to avoid overwriting image at same timestamp)."""

        root, ext = os.path.splitext(self.filename) #get name and extension
        count = 0
        while os.path.exists(self.directory + self.filename):
            count += 1
            self.filename = f"{root}_{count}{ext}"


def get_next_filename(filename):
    """Gets next available filename (to avoid overwriting image at same timestamp).

    Args:
        filename (str): the proposed filename

    Returns:
        new_file (str): a filename that will not overwrite an existing file
    """

    new_file = filename
    root, ext = os.path.splitext(filename)
    count = 0
    while os.path.exists(new_file):
        count += 1
        new_file = f"{root}_{count}{ext}"

    return new_file


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


def set_up_spreadsheet(outfile_path, headers):
    """Sets up the output spreadsheet by adding bolded headers to columns.

    Args:
        outfile_path (str): the filepath to the Excel sheet
        headers (list): the bolded column headers to be written
    """

    with contextlib.closing(openpyxl.workbook.Workbook()) as wb:
        ws = wb.active
        ws.append(headers)
        for cell in ws['1:1']:
            cell.font = openpyxl.styles.Font(bold=True) #make headers bold
        wb.save(outfile_path)


def append_to_spreadsheet(outfile_path, data):
    """Appends data to spreadsheet located at outfile_path.

    Args:
        outfile_path (str): the filepath to the Excel sheet
        data (list): the data to be appended
    """

    with contextlib.closing(openpyxl.load_workbook(outfile_path)) as wb: #open existing workbook
        wb.active.append(data) #append data to sheet
        wb.save(outfile_path) #save workbook


def delete_last_coordinate(outfile_path):
    """Deletes most recent coordinate from Excel sheet.
        
    Args:
        outfile_path (str): the filepath to the Excel sheet
    """

    with contextlib.closing(openpyxl.load_workbook(outfile_path)) as wb:
        ws = wb.active
        last_row = ws.max_row
        ws.delete_rows(last_row)
        wb.save(outfile_path)


def arg_parsing():
    """Parses input arguments; separate from main() because it's long.

    Returns:
        parser.parse_args() (argparse.Namespace): object containing inputted command line arguments
    """

    parser = argparse.ArgumentParser(
        description='A coordinate displaying and writing program to track chicken behavior.')
    parser.add_argument('video_path', help='File path to the video')
    parser.add_argument('-od', '--out_dir', metavar='',
        help='Name of output folder for Excel files (default: sheets/)')
    parser.add_argument('-ad', '--anno_dir', metavar='',
        help='Name of output folder for annotated images (default: annotated_images/)')
    parser.add_argument('-e', '--exit_key', metavar='', help='Key to quit program (default: e)')
    parser.add_argument('-c', '--clear_key', metavar='',
        help='Key to remove coordinate from screen and Excel file (default: c)')
    parser.add_argument('-d', '--duration', metavar='',
        type=int, help='duration of coordinates on screen, in seconds (default: 5)')
    
    # Suppressed options: change in options.json5, except for --version
    parser.add_argument('-f', '--font', type=int, help=argparse.SUPPRESS)
    parser.add_argument('-fc', '--font_color', help=argparse.SUPPRESS)
    parser.add_argument('-fs', '--font_scale', type=int, help=argparse.SUPPRESS)
    parser.add_argument('-ft', '--font_thickness', type=int, help=argparse.SUPPRESS)
    parser.add_argument('--version', action='version',
        version=f"%(prog)s {__version__}", help=argparse.SUPPRESS)

    return parser.parse_args()


def write_args_to_file(args, filename):
    """Saves input arguments to file.

    Args:
        args (argparse.Namespace): arguments to be written to file
        filename (str): .json file for writing
    """

    arg_separator = '*' * 62 + '\n'
    info = [
        '\n\n/*\n', arg_separator, '"font_color" must be of the form [R,G,B], where R,G,B <= 255.\n',
        'You have 16.7 million options; here is the rainbow:\n', '\tred = [255, 0, 0]\n',
        '\torange = [255, 165, 0]\n', '\tyellow = [255, 255, 0]\n',
        '\tgreen (lime) = [0, 255, 0]\n', '\tblue = [0, 0, 255]\n', '\tindigo = [75, 0, 130]\n',
        '\tviolet = [128, 0, 128]\n', arg_separator, '\n', arg_separator,
        '"font" must be a number 0-7, or 16; feel free to try them out:\n',
        '\t0: normal size sans-serif font (default)\n', '\t1: small size sans-serif font\n',
        '\t2: normal size sans-serif font, complex\n', '\t3: normal size serif font\n',
        '\t4: normal size serif font, complex\n', '\t5: small size serif font\n',
        '\t6: hand-writing style font\n', '\t7: hand-writing style font, complex\n',
        '\t16: italic font\n', arg_separator, '*/\n'
    ]

    with open(filename, 'w') as f:
        json.dump(vars(args), f, indent=4)
        f.writelines(info)


def get_args_from_file(filename):
    """Gets default optional arguments from file.

    Args:
        filename

    Returns:
        argparse.Namespace: arguments from file
    """

    with open(filename, 'r') as f:
        json_data = ''
        for line in f:
            #json_data += line
            json_data = ''.join([json_data, line]) #GPSG 3.10
            if '}' in line: #end of JSON object
                break
        args_dict = json.loads(json_data)

    return argparse.Namespace(**args_dict)


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
    """ Sets up error logger with custom terminator to separate error entries.

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


def set_window_dimensions(cap):
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

    return window_width, window_height


def main():
    logger = set_up_logger() #set up main() error logger

    system_date_time = time.strftime('%Y-%m-%d_%H-%M-%S', time.localtime()) #ISO 8601
    ascii_allowlist = string.printable[:-5] #OpenCV can only print up to <space>

    #point pytesseract to tesseract executable
    if platform.system() == 'Windows':
        pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'


    #TODO: move variable assignments out of try-except
    try:
        # Merge default arguments with input, write to file
        options_file = 'options.txt' #JSON5-formatted file
        args = arg_parsing() #get arg Namespace object
        defaults = get_args_from_file(options_file)
        for key, val in vars(args).items():
            if val == None:
                setattr(args, key, getattr(defaults, key))
        write_args_to_file(args, options_file) #write updated args to file


        # Set up arguments for program use
        infile_path = args.video_path.strip() #strip trailing space for MacOS compatibility
        if args.exit_key == 'Esc' or args.exit_key == 'esc':
            exit_key = 27
        else:
            exit_key = ord(args.exit_key)
        clear_key = ord(args.clear_key)
        duration = args.duration #duration of coordinates and annotations on screen, in seconds
        font = types.SimpleNamespace(font=args.font, scale=args.font_scale,
            color=tuple(args.font_color), thickness=args.font_thickness)


        # Instantiate classes/Create NameSpaces
        coord = types.SimpleNamespace(xy=(), start_time=0)
        anno = AnnoTation(f"{args.anno_dir}/{system_date_time}")
        headers = ['Date', 'Time', 'Coordinates']
        sheet = SpreadSheet(args.out_dir, system_date_time, headers)
        #mcb_handler = MouseCallbackHandler(coord, anno, sheet)

        # Determine delay to play video at normal speed
        cap = cv2.VideoCapture(infile_path) #create Video Capture object
        fps = cap.get(cv2.CAP_PROP_FPS) #get fps of cap input
        if fps == 0:
            fps = 25 #set default if determination fails
        delay = int(1000 / fps) #calculate delay from fps, in ms


        # Set up video window
        window_width, window_height = set_window_dimensions(cap)
        window_name = 'Video'
        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL) #create named window to display cap
        cv2.resizeWindow(window_name, width=window_width, height=window_height)

        frame = None
        def mouse_input(event, x, y, flags, param):
            del flags, param # Unused.

            if not anno.typing: #if user *isn't* typing annotation
                if event == cv2.EVENT_LBUTTONDOWN: #left mouse click
                    coord.start_time = time.time()
                    coord.xy = (x, y)
                    timestamp_date, timestamp_time = get_timestamp(frame)

                    data = [timestamp_date, timestamp_time, f"({x}, {y})"] #format data
                    sheet.append_to_spreadsheet(data)

                    # Print timestamp and coordinates in case .xlsx gets corrupted
                    print(timestamp_date)
                    print(timestamp_time)
                    print(f"{str(coord.xy)}\n")

                elif event == cv2.EVENT_RBUTTONDOWN: #right mouse click
                    _, timestamp_time = get_timestamp(frame)
                    anno.start_typing(x, y, timestamp_time)

        cv2.setMouseCallback(window_name, mouse_input)

        frame = None
        def mouse_input(event, x, y, flags, param):
            del flags, param # Unused.

            if not anno.typing: #if user *isn't* typing annotation
                if event == cv2.EVENT_LBUTTONDOWN: #left mouse click
                    coord.start_time = time.time()
                    coord.xy = (x, y)
                    timestamp_date, timestamp_time = get_timestamp(frame)

                    data = [timestamp_date, timestamp_time, f"({x}, {y})"] #format data
                    sheet.append_to_spreadsheet(data)

                    # Print timestamp and coordinates in case .xlsx gets corrupted
                    print(timestamp_date)
                    print(timestamp_time)
                    print(f"{str(coord.xy)}\n")

                elif event == cv2.EVENT_RBUTTONDOWN: #right mouse click
                    _, timestamp_time = get_timestamp(frame)
                    anno.start_typing(x, y, timestamp_time)

        cv2.setMouseCallback(window_name, mouse_input)

        paused = False
        pause_key = ord('p')

        while cap.isOpened():
            ret, frame = cap.read() #get cap frame-by-frame
            if ret:
                
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
                    coord.xy = ()

                # Only allow deletion of [date, time, coord] when on screen
                if coord.xy:
                    if key_press == clear_key:
                        coord.xy = ()
                        sheet.delete_last_coordinate()
                    elif (time.time() - coord.start_time < duration): #on-screen coordinate timeout
                        cv2.putText(frame, str(coord.xy), coord.xy,
                            font.font, font.scale, font.color, font.thickness)

                # This while loop ensures that the video is paused while annotating
                while anno.typing:
                    frame_copy = frame.copy() #get copy of frame so backspace works

                    # Display frame with annotation
                    if anno.show_anno:
                        cv2.putText(frame_copy, anno.anno_text,
                            anno.anno_pos, font.font, font.scale,
                            font.color, font.thickness)
                        cv2.imshow(window_name, frame_copy)

                    key_press = cv2.waitKey(0) & 0xFF #get LSByte of keypress for cross-platform compatibility
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
                        elif chr(key_press) in ascii_allowlist: #printable ascii chars
                            anno.anno_text += chr(key_press)
                            anno.show_anno = True

                if anno.show_anno:
                    cv2.putText(frame, anno.anno_text,
                        anno.anno_pos, font.font,
                        font.scale, font.color, font.thickness)

            #this looks unnecessary but it's the only way for things to be clean
            if paused and (coord.xy or anno.show_anno):
                cv2.imshow(window_name, frame_copy) #show video frame
            else:
                cv2.imshow(window_name, frame) #show video frame

    except Exception as e:
        logger.error('\nError: %s\n', e, exc_info=True)
        print(f'\n***AN ERROR OCCURRED! PLEASE FOLLOW THE SUPPORT INSTRUCTIONS IN THE README.***')

    finally:
        if 'cap' in locals() or 'cap' in globals(): #if program initialized cap before error
            cap.release() #release video capture object
            cv2.destroyAllWindows() #close all OpenCV windows


if __name__ == "__main__":
    main()
