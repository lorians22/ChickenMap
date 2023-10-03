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
# 0) update coords for 2D vs 3D (get_3D_from_2D); --3D input arg
# 1) argparse output file option: allow custom output file, but use get_next_filename() to prevent o/w
#   - prevent out_dir and anno_dir from being the same name (raise custom error)
#   - input validation (after merging with default values?)
#   - pip install pathvalidate
# 2) convert string concats to join() where possible for efficiency
# 3) add error logger to except (Logger class?)
#   - add try-except to arg_parsing()
# 4) location-aware text drawing, like how a right-click menu flows up or down from cursor
# 5) function type hints
# 6) update code whitespace based on GPSG
# 7) add GUI (dropdown menus, sanitized text boxes) for options.json5?
# 8) change ruler to 80 and wrap appropriately
# 9) look into GPSG decorators
# 10) convert to f-strings where possible

# TO DO For someone that isn't me and knows Python UI development:
#   convert this to use a dedicated UI and keyboard/mouse input library instead of OpenCV?


__version__ = '2023.10.1'
__author__ = 'Logan Orians'


import argparse
import os
import time
import platform
import string
import json
import logging
import types #for SimpleNamespace
import tkinter as tk #screen resolution
import pytesseract #Tesseract-OCR wrapper
import cv2
import openpyxl #Excel engine
#import re


class AnnotationManager:
    def __init__(self):
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


class MouseCallbackHandler:
    def __init__(self, outfile_path):
        self.coord = types.SimpleNamespace(coords=(), coord_start_time=0)
        self.anno_manager = AnnotationManager()
        self.outfile_path = outfile_path
        self.frame = None

    def mouse_input(self, event, x, y, flags, param):
        del flags, param

        if not self.anno_manager.typing: #if user *isn't* typing annotation
            if event == cv2.EVENT_LBUTTONDOWN: #left mouse click
                self.coord.coord_start_time = time.time()
                self.coord.coords = (x, y)
                timestamp_date, timestamp_time = get_timestamp(self.frame)

                #convert to function
                data = [timestamp_date, timestamp_time, f'({x}, {y})'] #format data
                append_to_spreadsheet(self.outfile_path, data)

                #Print timestamp and coordinates in case .xlsx gets corrupted
                print(timestamp_date)
                print(timestamp_time)
                print(str(self.coord.coords)+'\n')

            elif event == cv2.EVENT_RBUTTONDOWN: #right mouse click
                _, timestamp_time = get_timestamp(self.frame)
                self.anno_manager.start_typing(x, y, timestamp_time)


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
        new_file = f'{root}_{count}{ext}'

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

    wb = openpyxl.workbook.Workbook()
    ws = wb.active
    ws.append(headers)
    for cell in ws['1:1']:
        cell.font = openpyxl.styles.Font(bold=True) #make headers bold
    wb.save(outfile_path)
    wb.close()


def append_to_spreadsheet(outfile_path, data):
    """Appends data to spreadsheet located at outfile_path.

    Args:
        outfile_path (str): the filepath to the Excel sheet
        data (list): the data to be appended
    """

    wb = openpyxl.load_workbook(outfile_path) #open existing workbook
    wb.active.append(data) #append data to sheet
    wb.save(outfile_path) #save workbook
    wb.close() #close file


def delete_last_coordinate(outfile_path):
    """Deletes most recent coordinate from Excel sheet.
        
    Args:
        outfile_path (str): the filepath to the Excel sheet
    """

    wb = openpyxl.load_workbook(outfile_path)
    ws = wb.active
    last_row = ws.max_row
    ws.delete_rows(last_row)
    wb.save(outfile_path)
    wb.close()


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
        version=f'%(prog)s {__version__}', help=argparse.SUPPRESS)

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

    with open(filename, 'w') as FILE:
        json.dump(vars(args), FILE, indent=4)
        FILE.writelines(info)


def get_args_from_file(filename):
    """Gets default optional arguments from file.

    Args:
        filename

    Returns:
        argparse.Namespace: arguments from file
    """

    with open(filename, 'r') as FILE:
        json_data = ''
        for line in FILE:
            json_data += line
            if '}' in line: #end of JSON object
                break
        args_dict = json.loads(json_data)

    return argparse.Namespace(**args_dict)


# TODO
def get_system_info():
    """Gets JSON-serialized system info for the error log file.

    Returns:
        info (str): multi-line string containing system info
    """

    uname = platform.uname()
    info = (
        f'\nOS: {uname.system}\n'
        f'Release: {uname.release}\n'
        f'Version: {uname.version}\n'
        f'Processor: {uname.processor}\n'
        f'Python: {platform.python_version()}'
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
    file_handler.terminator = f'\n\n{"=" * 80}\n\n'
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
        options_file = 'options.json5'
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
        out_dir = get_set_proper_dir(args.out_dir) #create sheets folder
        anno_dir = get_set_proper_dir(args.anno_dir) #create annotated_images folder
        anno_dir = get_set_proper_dir(anno_dir+system_date_time+'/') #create a_i subfolder
        font_ns = types.SimpleNamespace(font=args.font, scale=args.font_scale,
            color=tuple(args.font_color), thickness=args.font_thickness)


        # Set up spreadsheet file
        outfile_path = out_dir+system_date_time+'.xlsx'
        headers = ['Date', 'Time', 'Coordinates']
        set_up_spreadsheet(outfile_path, headers)


        # Initialize MouseCallbackHandler object
        mcb_handler = MouseCallbackHandler(outfile_path)


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
        cv2.setMouseCallback(window_name, mcb_handler.mouse_input)


        while cap.isOpened():
            ret, frame = cap.read() #get cap frame-by-frame
            if ret:
                # Pass frame to mcb_handler
                mcb_handler.frame = frame
                
                # Get LSByte of keypress for cross-platform compatibility
                key_press = cv2.waitKey(delay) & 0xFF
                if not mcb_handler.anno_manager.typing:
                    if key_press == exit_key: #quit program
                        break
                    if mcb_handler.anno_manager.write_anno:
                        mcb_handler.anno_manager.write_anno = False
                        filename = anno_dir+mcb_handler.anno_manager.timestamp_time.replace(':', '-')+'.jpg'
                        anno_filename = get_next_filename(filename) #makes sure not to overwrite image
                        cv2.imwrite(anno_filename, frame_copy)
                    if time.time() - mcb_handler.anno_manager.enter_time > duration:
                        mcb_handler.anno_manager.show_anno = False
                        mcb_handler.anno_manager.anno_text = ''

                # Prevent coords from popping back up after annotation is entered
                if mcb_handler.anno_manager.typing:
                    mcb_handler.coord.coords = ()

                # Only allow deletion of [date, time, coord] when on screen
                if mcb_handler.coord.coords:
                    if key_press == clear_key:
                        mcb_handler.coord.coords = ()
                        delete_last_coordinate(outfile_path)
                    elif (time.time() - mcb_handler.coord.coord_start_time < duration): #on-screen coordinate timeout
                        cv2.putText(frame, str(mcb_handler.coord.coords), mcb_handler.coord.coords,
                            font_ns.font, font_ns.scale, font_ns.color, font_ns.thickness)

                # This while loop ensures that the video is paused while annotating
                while mcb_handler.anno_manager.typing:
                    frame_copy = frame.copy() #get copy of frame so backspace works

                    # Display frame with annotation
                    if mcb_handler.anno_manager.show_anno:
                        cv2.putText(frame_copy, mcb_handler.anno_manager.anno_text,
                            mcb_handler.anno_manager.anno_pos, font_ns.font, font_ns.scale,
                            font_ns.color, font_ns.thickness)
                        cv2.imshow(window_name, frame_copy)

                    key_press = cv2.waitKey(0) & 0xFF #get LSByte of keypress for cross-platform compatibility
                    if key_press != 255:
                        if key_press == 13: #Enter
                            mcb_handler.anno_manager.typing = False
                            mcb_handler.anno_manager.write_anno = True
                            mcb_handler.anno_manager.enter_time = time.time()
                        elif key_press == 27: #Esc
                            mcb_handler.anno_manager.typing = False
                            mcb_handler.anno_manager.show_anno = False
                            mcb_handler.anno_manager.anno_text = ''
                        elif key_press == 8: #Backspace
                            if mcb_handler.anno_manager.anno_text: #DON'T COMBINE INTO ^ELIF
                                mcb_handler.anno_manager.anno_text = mcb_handler.anno_manager.anno_text[:-1]
                        elif chr(key_press) in ascii_allowlist: #printable ascii chars
                            mcb_handler.anno_manager.anno_text += chr(key_press)
                            mcb_handler.anno_manager.show_anno = True

                if mcb_handler.anno_manager.show_anno:
                    cv2.putText(frame, mcb_handler.anno_manager.anno_text,
                        mcb_handler.anno_manager.anno_pos, font_ns.font,
                        font_ns.scale, font_ns.color, font_ns.thickness)

                cv2.imshow(window_name, frame) #show video frame
            else:
                break

    except Exception as e:
        logger.error(f"\nError: {e}\n{get_system_info()}\n", exc_info=True)
        print('\n***AN ERROR OCCURRED! PLEASE FOLLOW THE SUPPORT INSTRUCTIONS IN THE README.***')

    finally:
        if 'cap' in locals() or 'cap' in globals(): #if program initialized cap before error
            cap.release() #release video capture object
            cv2.destroyAllWindows() #close all OpenCV windows


if __name__ == "__main__":
    main()
