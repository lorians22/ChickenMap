"""A coordinate mapping program made initially for chicken research"""

# Date: 07/13/23

# requirements: pip install -r requirements.txt
# py chickenMap.py <path_to_video>
#         ^You can drag a video file from Explorer/Finder into this window and press Enter.
# ex. py chickenMap.py test.mp4

# TODO:
# 1) argparse output file option: allow custom output file, but use get_next_filename() to prevent o/w
#   - prevent out_dir and anno_dir from being the same name (raise error)
#   - input validation (after merging with default values?)
#   - pip install pathvalidate
# 2) convert string concats to join() where possible for efficiency
# 3) convert globals to class(es): Font, Dir, MouseCallback
# 4) draw annotation on video instead of flipping back to cmd


__version__ = '2023.9.2'
__author__ = 'Logan Orians'


import argparse
import os
import time
import platform
import pytesseract #Tesseract-OCR wrapper
import cv2
import openpyxl #Excel engine
import json
#import re
#import tkinter as tk

#root = tk.Tk()
#screen_width = root.winfo_screenwidth()
#screen_height = root.winfo_screenheight()
#root.destroy()

#print(f"Screen resolution: {screen_width}x{screen_height}")



# Global variables
frame = None #get_timestamp() needs video frame when mouse is clicked
coords = () #need to get coords from mouse_callback, but mouse_callback doesn't "return"
outfile_path = ''
anno_dir = ''
coord_start_time = 0
font = None
font_color = None
font_scale = None
font_thickness = None


def mouse_callback(event, x, y, *_):
    """
    Runs when mouse input is received on the video window. Gets coordinate from mouse input and
    video timestamp via OCR
    """

    global coords
    global coord_start_time

    if event == cv2.EVENT_LBUTTONDOWN: #left mouse click
        coord_start_time = time.time()
        coords = (x, y)
        timestamp_date, timestamp_time = get_timestamp()
        data = [timestamp_date, timestamp_time, f'({x}, {y})'] #use f-string to format coordinate
        wb = openpyxl.load_workbook(outfile_path) #open existing workbook
        wb.active.append(data) #append data to sheet
        wb.save(outfile_path) #save workbook
        wb.close() #close file

        #Print timestamp and coordinates in case .xlsx gets corrupted
        print(timestamp_date)
        print(timestamp_time)
        print(str(coords)+'\n')


    elif event == cv2.EVENT_RBUTTONDOWN: #right mouse click
        _, timestamp_time = get_timestamp()
        annotation = input('Enter annotation: ')
        cv2.putText(frame, annotation, (x, y), font, font_scale, font_color, font_thickness)
        filename = anno_dir+timestamp_time.replace(':', '-')+'.jpg'
        anno_filename = get_next_filename(filename) #makes sure not to overwrite image
        cv2.imwrite(anno_filename, frame)


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
        new_file = '{}_{}{}'.format(root, count, ext)

    return new_file


def get_timestamp():
    """Gets burnt-in timestamp via OCR (not video timestamp from OpenCV)
    

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
    """Makes sure input argument is a directory
    
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


def delete_last_coordinate(outfile_path):
    """Deletes most recent coordinate from Excel sheet
        
    Args:
        outfile_path (str): the filepath to the Excel sheet
    """

    wb = openpyxl.load_workbook(outfile_path)
    ws = wb.active
    last_row = ws.max_row
    ws.delete_rows(last_row)
    wb.save(outfile_path)
    wb.close()


def setup_spreadsheet(outfile_path, headers):
    """Sets up the output spreadsheet by adding bolded headers to columns

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


def arg_parsing():
    """Parses input arguments. Because it's long, separate function encapsulates it from main()

    Returns:
        parser.parse_args (argparse.Namespace): object containing inputted command line arguments
    """

    parser = argparse.ArgumentParser(description='A coordinate displaying and writing program to \
        track chicken behavior.')
    parser.add_argument('video_path', help='File path to the video')
    parser.add_argument('-od', '--out_dir', metavar='',
        help='Name of output folder for Excel files')
    parser.add_argument('-ad', '--anno_dir', metavar='',
        help='Name of output folder for annotated images')
    parser.add_argument('-e', '--exit_key', metavar='', help='Key to quit program')
    parser.add_argument('-c', '--clear_key', metavar='',
        help='Key to remove coordinate from screen and Excel file')
    parser.add_argument('-d', '--duration', metavar='',
        type=int, help='duration of coordinates on screen, in seconds')
    parser.add_argument('--version', action='version',
        version='%(prog)s {version}'.format(version=__version__))
    # Suppressed options: change in options.json5
    parser.add_argument('-f', '--font', type=int, help=argparse.SUPPRESS)
    parser.add_argument('-fc', '--font_color', help=argparse.SUPPRESS)
    parser.add_argument('-fs', '--font_scale', type=int, help=argparse.SUPPRESS)
    parser.add_argument('-ft', '--font_thickness', type=int, help=argparse.SUPPRESS)

    return parser.parse_args()


def write_args_to_file(args, filename, info = []):
    """Saves input arguments to file

    Args:
        args (argparse.Namespace): arguments to be written to file
        filename (str): .json file for writing
        info (list) [optional]: helpful information to append to file
    """

    with open(filename, 'w') as FILE:
        json.dump(vars(args), FILE, indent=4)
        FILE.writelines(info)


def get_args_from_file(filename):
    """Gets arguments from file

    Args:
        filename

    Returns:
        argparse.Namespace: arguments from file
    """

    try:
        with open(filename, 'r') as FILE:
            json_data = ''
            for line in FILE:
                json_data += line
                if '}' in line: #end of JSON object
                    break
            args_dict = json.loads(json_data)
        return argparse.Namespace(**args_dict)
    except FileNotFoundError:
        return None


def main():
    global frame
    global coords
    global outfile_path
    global anno_dir
    global font
    global font_color
    global font_scale
    global font_thickness


    #point pytesseract to tesseract executable
    if platform.system() == 'Windows':
        pytesseract.pytesseract.tesseract_cmd = r'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'


    # Merge default arguments with input
    args = arg_parsing() #get arg Namespace object
    defaults = get_args_from_file('options.json5')
    for key, val in vars(args).items():
        if val == None:
            setattr(args, key, getattr(defaults, key))


    # Update arguments in options.json5 and add the info at the bottom
    info = [
        '\n\n/*', '/////////////////////////////////////////////////////////////',
        '"font_color" must be of the form [R,G,B], where R,G,B <= 255.',
        'You have 16.7 million options; here is the rainbow:',
        '\tred = [255, 0, 0]', '\torange = [255, 165, 0]', '\tyellow = [255, 255, 0]',
        '\tgreen (lime) = [0, 255, 0]', '\tblue = [0, 0, 255]', '\tindigo = [75, 0, 130]',
        '\tviolet = [128, 0, 128]',
        '/////////////////////////////////////////////////////////////',
        '', '/////////////////////////////////////////////////////////////',
        '"font" must be a number 0-7; feel free to try them out:',
        '\t0: cv2.FONT_HERSHEY_SIMPLEX (default)', '\t1: cv2.FONT_HERSHEY_PLAIN',
        '\t2: cv2.FONT_HERSHEY_DUPLEX', '\t3: cv2.FONT_HERSHEY_COMPLEX', '\t4: cv2.FONT_HERSHEY_TRIPLEX',
        '\t5: cv2.FONT_HERSHEY_COMPLEX_SMALL', '\t6: cv2.FONT_HERSHEY_SCRIPT_SIMPLEX',
        '\t7: cv2.FONT_HERSHEY_SCRIPT_COMPLEX',
        '/////////////////////////////////////////////////////////////', '*/'
        ]
    write_args_to_file(args, 'options.json5', [item + '\n' for item in info]) #write updated args to file

    # Setup arguments
    infile_path = args.video_path.strip() #strip trailing space for MacOS compatibility
    if args.exit_key == 'Esc' or args.exit_key == 'esc':
        exit_key = 27
    else:
        exit_key = ord(args.exit_key)
    clear_key = ord(args.clear_key)
    duration = args.duration #duration of coordinates on screen, in seconds
    out_dir = get_set_proper_dir(args.out_dir)
    anno_dir = get_set_proper_dir(args.anno_dir)
    font = args.font
    font_color = tuple(args.font_color)
    font_scale = args.font_scale
    font_thickness = args.font_thickness


    # Setup spreadsheet file
    system_date_time = time.strftime('%Y-%m-%d_%H-%M-%S', time.localtime()) #ISO 8601
    outfile_path = out_dir+system_date_time+'.xlsx'
    headers = ['Date', 'Time', 'Coordinates']
    setup_spreadsheet(outfile_path, headers)


    # Determine delay to play video at normal speed
    cap = cv2.VideoCapture(infile_path) #create Video Capture object
    fps = cap.get(cv2.CAP_PROP_FPS) #get fps of cap input
    if fps == 0:
        fps = 25 #set default if determination fails
    delay = int(1000 / fps) #calculate delay from fps, in ms


    # Setup video window
    cv2.namedWindow('Video', cv2.WINDOW_NORMAL) #create named window to display cap
    cv2.resizeWindow('Video', 1344, 760)
    cv2.setMouseCallback('Video', mouse_callback) #mouse callback function


    while cap.isOpened():
        ret, frame = cap.read() #get cap frame-by-frame
        if ret:
            key_press = cv2.waitKey(delay) & 0xFF #get key_press
            if key_press == exit_key: #quit program
                break

            if coords: #only allow deletion of [date, time, coord] when on screen
                if key_press == clear_key:
                    coords = ()
                    delete_last_coordinate(outfile_path)

                elif time.time() - coord_start_time < duration: #on-screen coordinate timeout
                    cv2.putText(frame, str(coords), coords, font, font_scale, font_color,
                        font_thickness)

            cv2.imshow('Video', frame) #show video frame
        else:
            break

    cap.release() #release video capture object
    cv2.destroyAllWindows() #close all OpenCV windows


if __name__ == "__main__":
    main()
