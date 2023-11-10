#!/usr/bin/python3

"""A GUI with font preview for entering options for chickenMap.py"""

'''
Copyright 2023, Logan Orians in affiliation with Purdue University:
    Dr. Marisa Erasmus and Gideon Ajibola.

Approved for private use by students and employees of Purdue University only.
No implied support or warranty.
'''

# Date: 10/13/2023

# requirements: pip3 install -r requirements.txt
# Windows: py options_gui.py
# MacOS: python3 options_gui.py


__version__ = '2023.10.3'
__author__ = 'Logan Orians'


#TODO on unpaid time:
# 1) convert to class (might be cleaner/shorter)
# 2) "When catching operating system errors,
#    prefer the explicit exception hierarchy introduced in Python 3.3
#    over introspection of errno values."


import ast
import json
import platform
import string
import tkinter as tk
from tkinter import colorchooser
from tkinter import filedialog
from tkinter import font
from tkinter import ttk
from typing import Any, TypeVar

import cv2
import numpy as np
from PIL import Image
from PIL import ImageTk


# Custom Types for Type Checking (mypy)
TRoot = TypeVar('TRoot', bound=tk.Tk)
TCanvas = TypeVar('TCanvas', bound=tk.Canvas)
TLabel = TypeVar('TLabel', bound=ttk.Label)
TOptionmenu = TypeVar('TOptionmenu', bound=ttk.OptionMenu)
TStringVar = TypeVar('TStringVar', bound=tk.StringVar)
TBooleanVar = TypeVar('TBooleanVar', bound=tk.BooleanVar)


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


def write_args_to_file(args: dict[str, Any], filename: str) -> None:
    """Saves input arguments to file.

    Args:
        args: arguments to be written to file
        filename: .txt file for writing
    """

    try:
        with open(filename, 'w') as f:
            json.dump(args, f, indent=4)
    except OSError: #file permissions, etc.
        raise


def clear_error(name: str, err_msgs: dict[str, str], label_err: TLabel) -> None:
    """Clears current error from label_err.

    Args:
        name: name of entry with current error
        err_msgs: current and previous error messages
        label_err: GUI label for error messages
    """

    if name in err_msgs: del err_msgs[name]
    update_error_label(err_msgs, label_err)


def clear_label(label: TLabel) -> None:
    """Clears passed-in label. Callback function for root.after().

    Args:
        label: label to be cleared
    """

    label.config(text='')


def toggle_menu_state(check_var: TBooleanVar, menu: TOptionmenu,
                      menu_var: TStringVar) -> None:
    """Enables or resets menu based on checkbox.

    Args:
        check_var: checkbox variable
        menu: drop-down menu widget
        menu_var: variable holding current menu option
    """

    if check_var.get(): menu.config(state='normal')
    else:
        menu.config(state='disabled')
        menu_var.set('Select Chicken Location')


def add_error(name: str, message: str, err_msgs: dict[str, str],
              label_err: TLabel) -> None:
    """Adds error message to label_err.

    Args:
        name: name of entry with current error
        message: individualized error message
        err_msgs: current and previous error messages
        label_err: GUI label for error messages
    """

    err_msgs[name] = message
    update_error_label(err_msgs, label_err)


def update_error_label(err_msgs: dict[str, str], label_err: TLabel) -> None:
    """Updates error on GUI.

    Args:
        err_msgs: current and previous error messages
        label_err: GUI label for error messages
    """

    if err_msgs:
        # Get most recently inserted error message, Python 3.7+
        latest_error = err_msgs[next(reversed(err_msgs))]
        label_err.config(text=latest_error)
    else: label_err.config(text='')


def convert_font_name_to_int(font_name: str) -> int:
    """Maps the font_name to an integer for main program use.

    Args:
        font_name: name of cv2 font

    Returns:
        font_map[font_name]: integer mapped from cv2 font_name
    """

    font_map = {
        'FONT_HERSHEY_SIMPLEX': 0,
        'FONT_HERSHEY_PLAIN': 1,
        'FONT_HERSHEY_DUPLEX': 2,
        'FONT_HERSHEY_COMPLEX': 3,
        'FONT_HERSHEY_TRIPLEX': 4,
        'FONT_HERSHEY_COMPLEX_SMALL': 5,
        'FONT_HERSHEY_SCRIPT_SIMPLEX': 6,
        'FONT_HERSHEY_SCRIPT_COMPLEX': 7,
    }

    return font_map[font_name]


def pick_file(file_var: TStringVar) -> None:
    """Callback function to choose an input video file.

    Args:
        file_var: var to store user entry for video file
    """

    file_var.set(str(filedialog.askopenfilename()))


def pick_color(font_vars: list[TStringVar], canvas: TCanvas,
               sys_theme: str) -> None:
    """Callback function to choose a color and update the cv2 font preview.

    Args:
        font_vars: user entries from GUI for font style, color, scale, thickness
        canvas: canvas to hold cv2 font preview image
    """

    color = colorchooser.askcolor(title='Pick a color')
    if color != (None, None):
        font_vars[1].set(str(color[0]))
        update_font_preview(font_vars, canvas, sys_theme)


def set_defaults(default_vars: list[Any], canvas: TCanvas,
                 sys_theme: str) -> None:
    """Callback function to populate input fields with default values.

    Args:
        default_vars: user entries from GUI
        canvas: canvas to hold cv2 font preview image
    """

    default_vars[0].set('test.mp4') #input video file
    default_vars[1].set(False)
    default_vars[2].set('Select Chicken Location')
    default_vars[3].set('sheets/') #spreadsheets directory
    default_vars[4].set('annotated_images/') #annotations directory
    default_vars[5].set('q') #exit key
    default_vars[6].set('c') #clear key
    default_vars[7].set('p') #pause key
    default_vars[8].set('5.0') #duration
    default_vars[9].set('FONT_HERSHEY_SIMPLEX') #font
    default_vars[10].set('(0, 255, 0)') #font color tuple, green
    default_vars[11].set('1.0') #font scale
    default_vars[12].set('2') #font thickness
    
    update_font_preview(default_vars[9:], canvas, sys_theme)


def save_options(root: TRoot, option_vars: list[Any],
                 label_ack: TLabel, err_msgs: dict[str, str]) -> None:
    """Formats user entries for writing to file.

    Args:
        root: main Tk widget
        option_vars: user entries from GUI
        label_ack: GUI label for a successful save/file write
        err_msgs: current and previous error messages
    """

    if err_msgs: return #if invalid input, don't submit

    # Rename options for output
    args = {} # type: dict[str, str | float | int | bool | tuple[int, int, int]]
    args['video_path'] = option_vars[0].get()
    if option_vars[1].get():
        args['three_d'] = option_vars[2].get()
    else: args['three_d'] = False
    args['out_dir'] = option_vars[3].get()
    args['anno_dir'] = option_vars[4].get()
    args['exit_key'] = option_vars[5].get()
    args['clear_key'] = option_vars[6].get()
    args['pause_key'] = option_vars[7].get()
    args['duration'] = float(option_vars[8].get())
    args['font'] = convert_font_name_to_int(option_vars[9].get())
    args['font_color'] = ast.literal_eval(option_vars[10].get())
    args['font_scale'] = float(option_vars[11].get())
    args['font_thickness'] = int(option_vars[12].get())
    
    write_args_to_file(args, 'options.json')
    label_ack.config(text='Saved!')
    root.after(2500, lambda: clear_label(label_ack)) #clear after 2.5 seconds


def update_font_preview(font_vars: list[TStringVar], canvas: TCanvas,
                        sys_theme: str) -> None:
    """Updates the cv2 font preview when a font option is modified.

    Args:
        font_vars: user entries from GUI for font style, color, scale, thickness
        canvas: canvas to hold cv2 font preview image
        sys_theme: light mode or dark mode
    """

    # Construct preview
    image = np.zeros((100, 500, 3), dtype=np.uint8)
    if sys_theme == 'dark': image.fill(68) #dark gray
    else: image.fill(225) #light gray

    scale = float(font_vars[2].get())
    thickness = int(font_vars[3].get())

    color_rgb = ast.literal_eval(font_vars[1].get())
    color_bgr = tuple(reversed(color_rgb))

    font = convert_font_name_to_int(font_vars[0].get())
    text = '(42, 7) Test'
    cv2.putText(image, text, (5, 80), font, scale, color_bgr, thickness)

    img = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    img = Image.fromarray(img)
    img = ImageTk.PhotoImage(image=img)
    canvas.create_image(0, 0, anchor=tk.NW, image=img)
    #fake attribute to prevent GC; it's a callback function, so can't prevent GC
    canvas.image = img # type: ignore[attr-defined]


def validate_duration(var: TStringVar, err_msgs: dict[str, str],
                      label_err: TLabel) -> None:
    """Callback function to validate duration input and add error if invalid.

    Args:
        var: duration input
        err_msgs: current and previous error messages
        label_err: GUI label for error messages
    """

    try:
        entry = float(var.get())
        if entry < 1 or entry > 60:
            raise ValueError
        clear_error('Duration', err_msgs, label_err)
    except ValueError:
        add_error('Duration',
                  'Please enter a value between 1 and 60 for Duration.',
                  err_msgs, label_err)


def validate_scale(var: TStringVar, font_vars: list[TStringVar],
                   err_msgs: dict[str, str], label_err: TLabel, canvas: TCanvas,
                   sys_theme: str) -> None:
    """Callback function to validate scale input and add error if invalid.

    Args:
        var: scale input
        font_vars: user entries from GUI for font style, color, scale, thickness
        err_msgs: current and previous error messages
        label_err: GUI label for error messages
        canvas: canvas to hold cv2 font preview image
    """

    try:
        entry = float(var.get()) #raises ValueError if cannot cast
        if entry <= 0 or entry > 2.5:
            raise ValueError
        clear_error('Font Scale', err_msgs, label_err)
        if not err_msgs:
            update_font_preview(font_vars, canvas, sys_theme) #update preview
    except ValueError:
        add_error('Font Scale',
                  'Please enter a value between 0 and 2.5 for Scale.',
                  err_msgs, label_err)


def validate_thickness(var: TStringVar, font_vars: list[TStringVar],
                       err_msgs: dict[str, str], label_err: TLabel,
                       canvas: TCanvas, sys_theme: str) -> None:
    """Callback function to validate thickness input and add error if invalid.

    Args:
        var: thickness input
        font_vars: user entries from GUI for font style, color, scale, thickness
        err_msgs: current and previous error messages
        label_err: GUI label for error messages
        canvas: canvas to hold cv2 font preview image
    """

    try:
        if int(var.get()) <= 0:
            raise ValueError
        clear_error('Font Thickness', err_msgs, label_err)
        if not err_msgs:
            update_font_preview(font_vars, canvas, sys_theme)
    except ValueError:
        add_error('Font Thickness',
                  'Please enter a positive integer for Font Thickness.',
                  err_msgs, label_err)


def validate_keys(err_msgs: dict[str, str], label_err: TLabel,
                  approved_keys: str, key_vars: list[TStringVar]) -> None:
    """Callback wrapper func to check all key inputs for invalid/repeated keys.

    Args:
        err_msgs: current and previous error messages
        label_err: GUI label for error messages
        approved_keys: valid key choices
        key_vars: all key vars - Exit, Clear, Pause
    """

    # Generate all current key values
    key_var_vals = [key_var.get() for key_var in key_vars]

    validate_key(key_var_vals[0], 'Exit Key', err_msgs, label_err,
                 approved_keys, key_var_vals[1:])
    validate_key(key_var_vals[1], 'Clear Key', err_msgs, label_err,
                 approved_keys, key_var_vals[::2])
    validate_key(key_var_vals[2], 'Pause Key', err_msgs, label_err,
                 approved_keys, key_var_vals[:2])


def validate_key(val: str, name: str, err_msgs: dict[str, str],
                 label_err: TLabel, approved_keys: str,
                 other_key_vals: list[str]) -> None:
    """Validates key input and adds error if invalid.

    Args:
        val: key input value
        name: key name (exit, clear, pause)
        err_msgs: current and previous error messages
        label_err: GUI label for error messages
        approved_keys: valid key choices
        other_key_vals: values of other keys; prevent user from using same key
    """

    try:
        if val in other_key_vals:
            raise ValueError('Please do not reuse the same key.')
        if not(len(val) == 1 and val in approved_keys) and val.lower() != 'esc':
            raise ValueError(f'For {name}, enter one key a-z/0-9, or type Esc.')
        clear_error(name, err_msgs, label_err)
    except ValueError as e:
        add_error(name, str(e), err_msgs, label_err)


def validate_dir(var: TStringVar, name: str, err_msgs: dict[str, str],
                 label_err: TLabel) -> None:
    """Callback function to validate directory input and add error if invalid.

    Args:
        var: directory input
        name: directory name (sheets, anno)
        err_msgs: current and previous error messages
        label_err: GUI label for error messages
    """

    invalid_chars = ('<', '>', ':', '"', '|', '?', '*')
    entry = var.get()

    try:
        if any(inv_char in entry for inv_char in invalid_chars) or entry == '':
            raise ValueError
        clear_error(name, err_msgs, label_err)
    except ValueError:
        add_error(name, f'{name} cannot contain < > : " | ? *', err_msgs,
                  label_err)


def close_window(root: TRoot) -> None:
    """Closes GUI and exits program.

    Args:
        root: toplevel Tk widget
    """

    root.destroy()


def get_windows_theme() -> str:
    """Determines the Windows personalization theme via the Registry.

    Returns:
        'light' | 'dark': theme value
    """

    try:
        import winreg
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            R'Software\Microsoft\Windows\CurrentVersion\Themes\Personalize')
        theme = winreg.QueryValueEx(key, "AppsUseLightTheme")
        winreg.CloseKey(key)

        if theme[0] == 1: return 'light'
        else: return 'dark'
    except ImportError as e:
        print(f'Import Error: {e}\nThis should not happen. Contact author.')
        return 'light'
    except Exception as e:
        print(f'{e}\nContact author.')
        return 'light'


def get_macos_theme() -> str:
    """Determines the MacOS system theme via an OSAscipt.

    Returns:
        'light' | 'dark': theme value
    """

    try:
        import subprocess
        cmd = (
            'tell application "System Events" to '
            'tell appearance preferences to return dark mode')
        res = subprocess.run(['osascript', '-e', cmd],
                             capture_output=True, text=True)
        if res.stdout.strip() == 'true': return 'dark'
        else: return 'light'
    except subprocess.CalledProcessError as e:
        print(f'Non-zero exit status: {e.returncode}\nContact author.')
        return 'light'
    except FileNotFoundError as e:
        print(f'OSAscript command not found: {e}\nContact author.')
        return 'light'
    except Exception as e:
        print(f'Error: {e}\nContact author.')
        return 'light'


def main():
    # Set up GUI window
    root = tk.Tk()
    root.title('ChickenMap Options')

    # Set up GUI theme
    root.tk.call('source', 'tcl_theme/azure.tcl')
    if platform.system() == 'Windows':
        sys_theme = get_windows_theme()
    elif platform.system() == 'Darwin':
        sys_theme = get_macos_theme()
    else:
        sys_theme = 'light'
    root.tk.call('set_theme', sys_theme)

    frame = ttk.Frame(root)
    frame.grid(row=0, column=0, padx=6, pady=6)

    bold_font = font.Font(weight='bold', size=11)
    width = 32


    # List of acceptable keys for exit/clear/etc. key selection
    approved_keys = string.ascii_lowercase + string.digits + r",./;'[]\-=`*-+"


    # Input fields
    option_vars = [] #entry field vars list
    err_msgs = {} #dict for keeping track of on-GUI error messages

    saved_args = get_args_from_file('options.json')

    label_video = ttk.Label(frame, text='Input video file:')
    label_video.grid(row=0, column=0, sticky='w', pady=2)
    video_var = tk.StringVar(value=saved_args['video_path'])
    option_vars.append(video_var)
    video_entry = ttk.Entry(frame, textvariable=video_var, state='readonly',
                            width=width)
    video_entry.grid(row=label_video.grid_info()['row'], column=1, pady=3)
    video_button = ttk.Button(frame, text='Browse', width=7,
                              command=lambda: pick_file(video_var))
    video_button.grid(row=video_entry.grid_info()['row']+1, column=1, pady=3)

    var_3d = tk.BooleanVar()
    option_vars.append(var_3d)
    checkbox_3d = ttk.Checkbutton(frame, text='3D?', variable=var_3d,
                                  command=lambda *args: toggle_menu_state(
                                      var_3d, menu_3d, var_location_3d))
    checkbox_3d.grid(row=video_button.grid_info()['row']+1, column=0,
                     padx=(200,0), pady=2)
    var_location_3d = tk.StringVar()
    option_vars.append(var_location_3d)
    options_3d = ['Select Chicken Location', 'Floor', 'Aviary']
    menu_3d = ttk.OptionMenu(frame, var_location_3d, options_3d[0], *options_3d)
    menu_3d.config(width=29, state='disabled')
    menu_3d.grid(row=checkbox_3d.grid_info()['row'], column=1, pady=3)

    label_out_folders = ttk.Label(frame, text='Output Folders', font=bold_font)
    label_out_folders.grid(row=checkbox_3d.grid_info()['row']+1, column=0,
                           sticky='w')

    label_sheet = ttk.Label(frame, text='Spreadsheet folder:')
    label_sheet.grid(row=label_out_folders.grid_info()['row']+1, column=0,
                     sticky='w', padx=(20, 0), pady=2)
    sheet_var = tk.StringVar(value=saved_args['out_dir'])
    entry_sheet = ttk.Entry(frame, textvariable=sheet_var, width=width)
    entry_sheet.grid(row=label_sheet.grid_info()['row'], column=1, pady=3)
    sheet_var.trace_add('write',
                        lambda *args: validate_dir(
                            sheet_var, 'Spreadsheet Directory', err_msgs,
                            label_err))
    option_vars.append(sheet_var)

    label_anno = ttk.Label(frame, text='Annotated images folder:')
    label_anno.grid(row=label_sheet.grid_info()['row']+1, column=0,
                    sticky='w', padx=(20, 0), pady=2)
    anno_var = tk.StringVar(value=saved_args['anno_dir'])
    entry_anno = ttk.Entry(frame, textvariable=anno_var, width=width)
    entry_anno.grid(row=label_anno.grid_info()['row'], column=1, pady=3)
    anno_var.trace_add('write',
                       lambda *args: validate_dir(
                           anno_var, 'Annotation Directory', err_msgs,
                           label_err))
    option_vars.append(anno_var)

    label_keys = ttk.Label(frame, text='Program Keys & Options', font=bold_font)
    label_keys.grid(row=label_anno.grid_info()['row']+1, column=0,
                    sticky='w')

    label_exit_key = ttk.Label(frame, text='Exit key:')
    label_exit_key.grid(row=label_keys.grid_info()['row']+1, column=0,
                        sticky='w', padx=(20, 0), pady=2)
    exit_key_var = tk.StringVar(value=saved_args['exit_key'])
    entry_exit_key = ttk.Entry(frame, textvariable=exit_key_var, width=width)
    entry_exit_key.grid(row=label_exit_key.grid_info()['row'],
                        column=1, pady=3)
    exit_key_var.trace_add('write',
                           lambda *args: validate_keys(
                               err_msgs, label_err, approved_keys, key_vars))
    option_vars.append(exit_key_var)

    label_clear_key = ttk.Label(frame, text='Clear key:')
    label_clear_key.grid(row=label_exit_key.grid_info()['row']+1, column=0,
                         sticky='w', padx=(20, 0), pady=2)
    clear_key_var = tk.StringVar(value=saved_args['clear_key'])
    entry_clear_key = ttk.Entry(frame, textvariable=clear_key_var, width=width)
    entry_clear_key.grid(row=label_clear_key.grid_info()['row'],
                         column=1, pady=3)
    clear_key_var.trace_add('write',
                            lambda *args: validate_keys(
                                err_msgs, label_err, approved_keys, key_vars))
    option_vars.append(clear_key_var)

    label_pause_key = ttk.Label(frame, text='Pause key:')
    label_pause_key.grid(row=label_clear_key.grid_info()['row']+1, column=0,
                         sticky='w', padx=(20, 0), pady=2)
    pause_key_var = tk.StringVar(value=saved_args['pause_key'])
    entry_pause_key = ttk.Entry(frame, textvariable=pause_key_var, width=width)
    entry_pause_key.grid(row=label_pause_key.grid_info()['row'],
                         column=1, pady=3)
    pause_key_var.trace_add('write',
                            lambda *args: validate_keys(
                                err_msgs, label_err, approved_keys, key_vars))
    option_vars.append(pause_key_var)

    label_duration = ttk.Label(frame, text='Coordinate duration:')
    label_duration.grid(row=label_pause_key.grid_info()['row']+1, column=0,
                        sticky='w', padx=(20, 0), pady=2)
    duration_var = tk.StringVar(value=saved_args['duration'])
    spinbox_duration = ttk.Spinbox(frame, from_=1, to=60, increment=1,
                                   textvariable=duration_var, width=width)
    spinbox_duration.grid(row=label_duration.grid_info()['row'],
                          column=1, pady=3)
    duration_var.trace_add('write',
                           lambda *args: validate_duration(
                               duration_var, err_msgs, label_err))
    option_vars.append(duration_var)

    label_keys = ttk.Label(frame, text='Font Options', font=bold_font)
    label_keys.grid(row=label_duration.grid_info()['row']+1, column=0,
                    sticky='w')

    # Drop-down menu
    label_font = ttk.Label(frame, text='Font:')
    label_font.grid(row=label_keys.grid_info()['row']+1, column=0,
                    sticky='w', padx=(20, 0))
    font_options = (
        'FONT_HERSHEY_SIMPLEX',
        'FONT_HERSHEY_PLAIN',
        'FONT_HERSHEY_DUPLEX',
        'FONT_HERSHEY_COMPLEX',
        'FONT_HERSHEY_TRIPLEX',
        'FONT_HERSHEY_COMPLEX_SMALL',
        'FONT_HERSHEY_SCRIPT_SIMPLEX',
        'FONT_HERSHEY_SCRIPT_COMPLEX')
    font_value = font_options[saved_args['font']]
    font_var = tk.StringVar(value=font_value)
    font_menu = ttk.OptionMenu(frame, font_var, font_value, *font_options,
                               command=lambda *args: update_font_preview(
                                   font_vars, canvas, sys_theme))
    font_menu.config(width=29)
    font_menu.grid(row=label_font.grid_info()['row'], column=1, pady=3)
    option_vars.append(font_var)

    # Color picker
    label_font_color = ttk.Label(frame, text='Font Color:')
    label_font_color.grid(row=label_font.grid_info()['row']+1, column=0,
                          sticky='w', padx=(20, 0))
    color_var = tk.StringVar(value=saved_args['font_color'])
    option_vars.append(color_var)
    color_button = ttk.Button(frame, text='Pick Font Color', width=14,
                              command=lambda: pick_color(
                                  font_vars, canvas, sys_theme))
    color_button.grid(row=label_font_color.grid_info()['row'],
                      column=1, pady=3)

    label_font_scale = ttk.Label(frame, text='Font Scale:')
    label_font_scale.grid(row=label_font_color.grid_info()['row']+1, column=0,
                          sticky='w', padx=(20, 0))
    font_scale_var = tk.StringVar(value=saved_args['font_scale'])
    spinbox_font_scale = ttk.Spinbox(frame, from_=0.1, to=2.5, increment=0.1,
                                     textvariable=font_scale_var, width=width)
    spinbox_font_scale.grid(row=label_font_scale.grid_info()['row'],
                            column=1, pady=3)
    font_scale_var.trace_add('write',
                             lambda *args: validate_scale(
                                 font_scale_var, font_vars, err_msgs, label_err,
                                 canvas, sys_theme))
    option_vars.append(font_scale_var)

    label_font_thickness = ttk.Label(frame, text='Font Thickness:')
    label_font_thickness.grid(row=label_font_scale.grid_info()['row']+1,
                              column=0, sticky='w', padx=(20, 0))
    font_thickness_var = tk.StringVar(value=saved_args['font_thickness'])
    spinbox_font_thickness = ttk.Spinbox(frame, from_=1, to=5, increment=1,
                                         textvariable=font_thickness_var,
                                         width=width)
    spinbox_font_thickness.grid(row=label_font_thickness.grid_info()['row'],
                                column=1, pady=3)
    font_thickness_var.trace_add('write',
                                 lambda *args: validate_thickness(
                                     font_thickness_var, font_vars, err_msgs,
                                     label_err, canvas, sys_theme))
    option_vars.append(font_thickness_var)


    # Error Label
    label_err = ttk.Label(frame, foreground='red')
    label_err.grid(row=label_font_thickness.grid_info()['row']+1,
                   column=1, columnspan=2)


    # Create sliced option_vars lists (avoids find+replace shenanigans)
    font_vars = option_vars[9:]
    key_vars = option_vars[5:8]


    # Initialize font preview
    canvas = tk.Canvas(frame, width=500, height=100)
    canvas.grid(row=label_err.grid_info()['row']+1, columnspan=2)
    update_font_preview(font_vars, canvas, sys_theme)


    # BUTTONS
    # New frames setup
    default_frame = ttk.Frame(root)
    default_frame.grid(row=label_err.grid_info()['row']+1, sticky='w')
    save_close_frame = ttk.Frame(root)
    save_close_frame.grid(row=label_err.grid_info()['row']+1, sticky='E')

    # Reset to defaults button
    default_button = ttk.Button(default_frame, text='Defaults',
                                command=lambda: set_defaults(
                                    option_vars, canvas, sys_theme))
    default_button.grid(row=0, column=0, padx=6, pady=(0, 6))

    # Save options button
    save_button = ttk.Button(save_close_frame, text='Save',
                             command=lambda: save_options(
                                 root, option_vars, label_ack, err_msgs))
    save_button.grid(row=0, column=2, pady=(0, 6))

    # Close program button
    close_button = ttk.Button(save_close_frame, text='Close',
                              command=lambda: close_window(root))
    close_button.grid(row=0, column=3, padx=6, pady=(0, 6))


    # Acknowledgement Label
    label_ack = ttk.Label(save_close_frame, foreground='green')
    label_ack.grid(row=save_button.grid_info()['row'], column=0,
                   padx=6, pady=(0, 6))

    root.mainloop()

if __name__ == "__main__":
    main()
