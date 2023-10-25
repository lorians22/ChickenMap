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
# py options_gui.py


__version__ = '2023.10.2'
__author__ = 'Logan Orians'


#TODO
# 0) integrate with chickenMap.py
# 1) put Default, Save, Close buttons in one line, evenly spaced (add frame?)
# 2) add labels to break things up: Output Folders, Keys, Font Options


import ast
import json
import string
import tkinter as tk
from tkinter import ttk
from tkinter import colorchooser
from typing import Any, TypeVar

import cv2
import numpy as np
from PIL import Image
from PIL import ImageTk


# Custom Types for Type Checking (mypy)
TRoot = TypeVar('TRoot', bound=tk.Tk)
TCanvas = TypeVar('TCanvas', bound=tk.Canvas)
TLabel = TypeVar('TLabel', bound=ttk.Label)
TStringVar = TypeVar('TStringVar', bound=tk.StringVar)


def write_args_to_file(args: dict[str, Any], filename: str) -> None:
    """Saves input arguments to file.

    Args:
        args: arguments to be written to file
        filename: .json file for writing
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


def add_error(name: str, message: str, err_msgs: dict[str, str], label_err: TLabel) -> None:
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


def pick_color(font_vars: list[TStringVar], canvas: TCanvas) -> None:
    """Callback function to choose a color and update the cv2 font preview.

    Args:
        font_vars: user entries from GUI for font style, color, scale, thickness
        canvas: canvas to hold cv2 font preview image
    """

    color = colorchooser.askcolor(title='Pick a color')
    if color != (None, None):
        font_vars[3].set(str(color[0]))
        update_font_preview(font_vars, canvas)


def set_defaults(default_vars: list[TStringVar], canvas: TCanvas) -> None:
    """Callback function to populate input fields with default values.

    Args:
        default_vars: user entries from GUI
        canvas: canvas to hold cv2 font preview image
    """

    default_vars[0].set('sheets/') #spreadsheets directory
    default_vars[1].set('annotated_images/') #annotations directory
    default_vars[2].set('q') #exit key
    default_vars[3].set('c') #clear key
    default_vars[4].set('5') #duration
    default_vars[5].set('1') #font scale
    default_vars[6].set('2') #font thickness
    default_vars[7].set('FONT_HERSHEY_SIMPLEX') #font
    default_vars[8].set('(0, 255, 0)') #font color tuple, green
    
    update_font_preview(default_vars[5:], canvas)


def save_options(root: TRoot, option_vars: list[TStringVar], label_ack: TLabel, err_msgs: dict[str, str]) -> None:
    """Formats user entries for writing to file.

    Args:
        root: main Tk widget
        option_vars: user entries from GUI
        label_ack: GUI label for a successful save/file write
        err_msgs: current and previous error messages
    """

    if err_msgs: return #if invalid input, don't submit

    # Rename options for output
    args = {} # type: dict[str, Any]
    args['out_dir'] = option_vars[0].get()
    args['anno_dir'] = option_vars[1].get()
    args['exit_key'] = option_vars[2].get()
    args['clear_key'] = option_vars[3].get()
    args['duration'] = float(option_vars[4].get())
    args['font'] = convert_font_name_to_int(option_vars[7].get())
    args['font_color'] = ast.literal_eval(option_vars[8].get())
    args['font_scale'] = float(option_vars[5].get())
    args['font_thickness'] = int(option_vars[6].get())
    
    write_args_to_file(args, 'options.txt')
    label_ack.config(text='Options saved!')
    root.after(2500, lambda: clear_label(label_ack)) #clear after 2.5 seconds


def update_font_preview(font_vars: list[TStringVar], canvas: TCanvas) -> None:
    """Updates the cv2 font preview when a font option is modified.

    Args:
        font_vars: user entries from GUI for font style, color, scale, thickness
        canvas: canvas to hold cv2 font preview image
    """

    # Construct preview
    image = np.zeros((100, 445, 3), dtype=np.uint8)
    image.fill(255)

    scale = float(font_vars[0].get())
    thickness = int(font_vars[1].get())

    color_rgb = ast.literal_eval(font_vars[3].get())
    color_bgr = tuple(reversed(color_rgb))

    font = convert_font_name_to_int(font_vars[2].get())
    text = '(456, 789)'
    cv2.putText(image, text, (5, 80), font, scale, color_bgr, thickness)

    img = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    img = Image.fromarray(img)
    img = ImageTk.PhotoImage(image=img)
    canvas.create_image(0, 0, anchor=tk.NW, image=img)
    #fake attribute to prevent GC; it's a callback function, so can't prevent GC
    canvas.image = img # type: ignore[attr-defined]


def validate_thickness(var: TStringVar, option_vars: list[TStringVar], err_msgs: dict[str, str], label_err: TLabel, canvas: TCanvas) -> None:
    """Callback function to validate thickness input and add error if invalid.

    Args:
        var: thickness input
        option_vars: user entries from GUI
        err_msgs: current and previous error messages
        label_err: GUI label for error messages
        canvas: canvas to hold cv2 font preview image
    """

    try:
        if int(var.get()) <= 0:
            raise ValueError
        clear_error('Font Thickness', err_msgs, label_err)
        if not err_msgs:
            update_font_preview(option_vars[5:], canvas)
    except ValueError:
        add_error('Font Thickness',
            'Please enter a positive integer for Font Thickness.',
            err_msgs, label_err)


def validate_duration(var: TStringVar, option_vars: list[TStringVar], err_msgs: dict[str, str], label_err: TLabel) -> None:
    """Callback function to validate duration input and add error if invalid.

    Args:
        var: duration input
        option_vars: user entries from GUI
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
            'Please enter a value between 1 and 60 for Duration',
            err_msgs, label_err)


def validate_scale(var: TStringVar, option_vars: list[TStringVar], err_msgs: dict[str, str], label_err: TLabel, canvas: TCanvas) -> None:
    """Callback function to validate scale input and add error if invalid.

    Args:
        var: scale input
        option_vars: user entries from GUI
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
            update_font_preview(option_vars[5:], canvas) #update preview
    except ValueError:
        add_error('Font Scale',
            'Please enter a value between 0 and 2.5 for Scale.',
            err_msgs, label_err)


def validate_key(var: TStringVar, name: str, option_vars: list[TStringVar], err_msgs: dict[str, str], label_err: TLabel, approved_keys) -> None:
    """Callback function to validate key input and add error if invalid.

    Args:
        var: key input
        name: key name (exit, clear)
        option_vars: user entries from GUI
        err_msgs: current and previous error messages
        label_err: GUI label for error messages
        approved_keys: valid key choices
    """

    entry = var.get()

    try:
        #TODO: combine and DeMorgan's?
        if len(entry) == 1 and entry in approved_keys:
            pass
        elif entry.lower() == 'esc':
            pass
        else:
            raise ValueError
        clear_error(name, err_msgs, label_err)
    except ValueError:
        add_error(name, 'Please enter one character a-z or 0-9, or type Esc.',
            err_msgs, label_err)


def validate_dir(var: TStringVar, name: str, option_vars: list[TStringVar], err_msgs: dict[str, str], label_err: TLabel) -> None:
    """Callback function to validate directory input and add error if invalid.

    Args:
        var: directory input
        name: directory name (sheets, anno)
        option_vars: user entries from GUI
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
        add_error(name, f'{name} cannot be empty or contain < > : " | ? *',
            err_msgs, label_err)


def clear_label(label: TLabel) -> None:
    """Clears passed-in label. Callback function for root.after().

    Args:
        label: label to be cleared
    """

    label.config(text='')


def close_window(root: TRoot) -> None:
    """Closes GUI and exits program.

    Args:
        root: toplevel Tk widget
    """

    root.destroy()


def main():
    # Set up GUI window
    root = tk.Tk()
    root.title('Options')
    frame = ttk.Frame(root)
    frame.grid(row=0, column=0, padx=10, pady=10)
    # Set up font preview
    canvas = tk.Canvas(root, width=450, height=100)
    canvas.grid(row=10, column=0)


    # List of acceptable keys for exit/clear/etc. key selection
    approved_keys = string.ascii_lowercase + string.digits + r",./;'[]\-=`*-+"


    # Input labels
    label_sheet = ttk.Label(frame, text='Spreadsheet folder:')
    label_sheet.grid(row=0, column=0, sticky='W')

    label_anno = ttk.Label(frame, text='Annotated images folder:')
    label_anno.grid(row=label_sheet.grid_info()['row']+1,
        column=0, sticky='W')

    label_exit_key = ttk.Label(frame, text='Exit key:')
    label_exit_key.grid(row=label_anno.grid_info()['row']+1,
        column=0, sticky='W')

    label_clear_key = ttk.Label(frame, text='Clear key:')
    label_clear_key.grid(row=label_exit_key.grid_info()['row']+1,
        column=0, sticky='W')

    label_duration = ttk.Label(frame, text='Coordinate duration:')
    label_duration.grid(row=label_clear_key.grid_info()['row']+1,
        column=0, sticky='W')

    label_font = ttk.Label(frame, text='Font:')
    label_font.grid(row=label_duration.grid_info()['row']+1,
        column=0, sticky='W')

    label_font_color = ttk.Label(frame, text='Font Color:')
    label_font_color.grid(row=label_font.grid_info()['row']+1,
        column=0, sticky='W')

    label_font_scale = ttk.Label(frame, text='Font Scale:')
    label_font_scale.grid(row=label_font_color.grid_info()['row']+1,
        column=0, sticky='W')

    label_font_thickness = ttk.Label(frame, text='Font Thickness:')
    label_font_thickness.grid(row=label_font_scale.grid_info()['row']+1,
        column=0, sticky='W')


    # Input fields
    option_vars = [] #entry field vars
    err_msgs = {} #dict for keeping track of on-GUI error messages

    sheet_var = tk.StringVar(value='sheets/')
    entry_sheet = ttk.Entry(frame, textvariable=sheet_var)
    entry_sheet.grid(row=label_sheet.grid_info()['row'], column=1)
    sheet_var.trace_add('write', lambda *args: validate_dir(
        sheet_var, 'Spreadsheet Directory', option_vars, err_msgs,
        label_err))
    option_vars.append(sheet_var)

    anno_var = tk.StringVar(value='annotated_images/')
    entry_anno = ttk.Entry(frame, textvariable=anno_var)
    entry_anno.grid(row=label_anno.grid_info()['row'], column=1)
    anno_var.trace_add('write', lambda *args: validate_dir(
        anno_var, 'Annotation Directory', option_vars, err_msgs,
        label_err))
    option_vars.append(anno_var)

    exit_key_var = tk.StringVar(value='q')
    entry_exit_key = ttk.Entry(frame, textvariable=exit_key_var)
    entry_exit_key.grid(row=label_exit_key.grid_info()['row'], column=1)
    exit_key_var.trace_add('write', lambda *args: validate_key(
        exit_key_var, 'Exit Key', option_vars, err_msgs, label_err,
        approved_keys))
    option_vars.append(exit_key_var)

    clear_key_var = tk.StringVar(value='c')
    entry_clear_key = ttk.Entry(frame, textvariable=clear_key_var)
    entry_clear_key.grid(row=label_clear_key.grid_info()['row'], column=1)
    clear_key_var.trace_add('write', lambda *args: validate_key(
        clear_key_var, 'Clear Key', option_vars, err_msgs, label_err,
        approved_keys))
    option_vars.append(clear_key_var)

    duration_var = tk.StringVar(value=5)
    spinbox_duration = ttk.Spinbox(frame, from_=1, to=60, increment=1,
        textvariable=duration_var)
    spinbox_duration.grid(row=label_duration.grid_info()['row'], column=1)
    duration_var.trace_add('write', lambda *args: validate_duration(
        duration_var, option_vars, err_msgs, label_err))
    option_vars.append(duration_var)

    font_scale_var = tk.StringVar(value=1)
    spinbox_font_scale = ttk.Spinbox(frame, from_=0.1, to=2.5, increment=0.1,
        textvariable=font_scale_var)
    spinbox_font_scale.grid(row=label_font_scale.grid_info()['row'], column=1)
    font_scale_var.trace_add('write', lambda *args: validate_scale(
        font_scale_var, option_vars, err_msgs, label_err, canvas))
    option_vars.append(font_scale_var)

    font_thickness_var = tk.StringVar(value=2)
    spinbox_font_thickness = ttk.Spinbox(frame, from_=1, to=5, increment=1,
        textvariable=font_thickness_var)
    spinbox_font_thickness.grid(row=label_font_thickness.grid_info()['row'],
        column=1)
    font_thickness_var.trace_add('write', lambda *args: validate_thickness(
        font_thickness_var, option_vars, err_msgs, label_err, canvas))
    option_vars.append(font_thickness_var)

    # Drop-down menu
    font_options = (
        'FONT_HERSHEY_SIMPLEX',
        'FONT_HERSHEY_PLAIN',
        'FONT_HERSHEY_DUPLEX',
        'FONT_HERSHEY_COMPLEX',
        'FONT_HERSHEY_TRIPLEX',
        'FONT_HERSHEY_COMPLEX_SMALL',
        'FONT_HERSHEY_SCRIPT_SIMPLEX',
        'FONT_HERSHEY_SCRIPT_COMPLEX',
    )
    font_var = tk.StringVar(value=font_options[0])
    font_menu = ttk.OptionMenu(frame, font_var, font_options[0], *font_options,
        command=lambda *args: update_font_preview(option_vars[5:], canvas))
    font_menu.config(width=31)
    font_menu.grid(row=label_font.grid_info()['row'], column=1)
    option_vars.append(font_var)

    # Color picker
    color_tuple_var = tk.StringVar(value=(0, 255, 0))
    option_vars.append(color_tuple_var)
    color_button = ttk.Button(frame, text='Pick Font Color',
        command=lambda: pick_color(option_vars[5:], canvas))
    color_button.grid(row=label_font_color.grid_info()['row'], column=1)


    # Reset to Defaults Button
    default_button = ttk.Button(frame, text='Defaults',
        command=lambda: set_defaults(option_vars, canvas))
    default_button.grid(row=label_font_thickness.grid_info()['row']+2, column=0)

    # Save Options Button
    save_button = ttk.Button(frame, text='Save',
        command=lambda: save_options(root, option_vars, label_ack,
            err_msgs))
    save_button.grid(row=default_button.grid_info()['row']+1, column=0)

    # Close Program Button
    close_button = ttk.Button(frame, text='Close',
        command=lambda: close_window(root))
    close_button.grid(row=save_button.grid_info()['row'], column=1)


    # Acknowledgement Label
    label_ack = ttk.Label(frame, foreground='green')
    label_ack.grid(row=save_button.grid_info()['row']+1, column=0)

    # Error Label
    label_err = ttk.Label(frame, foreground='red')
    label_err.grid(row=label_font_thickness.grid_info()['row']+1, columnspan=3)


    # Initialize font preview
    update_font_preview(option_vars[5:], canvas)


    root.mainloop()

if __name__ == "__main__":
    main()
