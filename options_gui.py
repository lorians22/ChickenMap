#!/usr/bin/python3

#Date: 10/13/2023

__version__ = '2023.10.2'
__author__ = 'Logan Orians'


#TODO
# 0) integrate with chickenMap.py - no file writing
# 1) add and update docstrings
# 2) convert label_err to class to cut down on function parameter mess?
# 3) ensure accuracy of fontscale (doesn't look accurate)
# 4) convert combobox to radio buttons? would remove a validation function

# Note: in Python3.7, dicts are insertion-ordered -> need Python 3.7+


import ast
import json
import string
import tkinter as tk
from tkinter import ttk
from tkinter import colorchooser

import cv2
import numpy as np
from PIL import Image
from PIL import ImageTk


def center_window(root, width, height):
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x = (screen_width - width) // 2
    y = (screen_height - height) // 2
    root.geometry(f'{width}x{height}+{x}+{y}')


def write_args_to_file(args, filename):
    """Saves input arguments to file.

    Args:
        args (dict): arguments to be written to file
        filename (str): .json file for writing
    """

    try:
        with open(filename, 'w') as f:
            json.dump(args, f, indent=4)
    except OSError:
        raise


def clear_error(name, error_messages, label_err):
    if name in error_messages: del error_messages[name]
    update_error_label(error_messages, label_err)


def add_error(name, message, error_messages, label_err):
    error_messages[name] = message
    update_error_label(error_messages, label_err)


def update_error_label(error_messages, label_err):
    if error_messages:
        # Get most recently inserted error message, Python 3.7+
        latest_error = error_messages[next(reversed(error_messages))]
        label_err.config(text=f'{latest_error}')
    else: label_err.config(text='')


def pick_color(font_vars, canvas):
    color = colorchooser.askcolor(title='Pick a color')
    if color != (None, None):
        font_vars[4].config(background=color[1]) #update color widget
        font_vars[3].set(color[0])
        update_font_preview(font_vars[:4], canvas)


def set_defaults(default_vars, canvas):
    default_vars[0].set('sheets/') #spreadsheets directory
    default_vars[1].set('annotated_images/') #annotations directory
    default_vars[2].set('q') #exit key
    default_vars[3].set('c') #clear key
    default_vars[4].set(5) #duration
    default_vars[5].set(1) #font scale
    default_vars[6].set(2) #font thickness
    default_vars[7].set(0) #font
    default_vars[8].set('(0, 255, 0)') #font color tuple, green
    default_vars[9].config(background='#00FF00') #font color widget, green
    
    update_font_preview(default_vars[5:9], canvas)


def submit_options(root, option_vars, label_ack, error_messages):
    #if invalid input, don't submit
    if error_messages: return

    # Rename options for output
    args = {}
    args['out_dir'] = option_vars[0].get()
    args['anno_dir'] = option_vars[1].get()
    args['exit_key'] = option_vars[2].get()
    args['clear_key'] = option_vars[3].get()
    args['duration'] = float(option_vars[4].get())
    args['font'] = int(option_vars[7].get())
    args['font_color'] = ast.literal_eval(option_vars[8].get())
    args['font_scale'] = float(option_vars[5].get())
    args['font_thickness'] = int(option_vars[6].get())
    
    write_args_to_file(args, 'options1.txt')
    label_ack.config(text='Options saved!')
    root.after(2500, lambda:clear_label(label_ack)) #clear after 2.5 seconds


def update_font_preview(font_vars, canvas):
    # Construct preview
    image = np.zeros((200, 400, 3), dtype=np.uint8)
    image.fill(255)

    scale = float(font_vars[0].get())
    thickness = int(font_vars[1].get())

    color_rgb = ast.literal_eval(font_vars[3].get())
    color_bgr = tuple(reversed(color_rgb))

    font = int(font_vars[2].get())
    text = '(12345, 67890)'
    cv2.putText(image, text, (10, 100), font, scale, color_bgr, thickness)

    img = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    img = Image.fromarray(img)
    img = ImageTk.PhotoImage(image=img)
    canvas.create_image(0, 0, anchor=tk.NW, image=img)
    canvas.image = img


def validate_int(var, name, option_vars, error_messages, label_err, canvas):
    try:
        entry = int(var.get()) #raises ValueError if cannot cast
        if entry <= 0:
            raise ValueError
        clear_error(name, error_messages, label_err)
        if not error_messages:
            update_font_preview(option_vars[5:9], canvas)
    except ValueError:
        add_error(name, f'Please enter a positive integer for {name}.', error_messages, label_err)


def validate_float(var, name, option_vars, error_messages, label_err, canvas=None):
    try:
        entry = float(var.get()) #raises ValueError if cannot cast
        if entry <= 0:
            raise ValueError
        clear_error(name, error_messages, label_err)
        if canvas and not error_messages: #only update if all params are available
            update_font_preview(option_vars[5:9], canvas) #update preview with font_vars and canvas
    except ValueError:
        add_error(name, f'Please enter a positive value for {name} (decimals are okay).', error_messages, label_err)


def validate_key(var, name, option_vars, error_messages, label_err, approved_keys):
    entry = var.get()

    try:
        #TODO: combine and DeMorgan's?
        if len(entry) == 1 and entry in approved_keys:
            pass
        elif entry.lower() == 'esc':
            pass
        else:
            raise ValueError
        clear_error(name, error_messages, label_err)
    except ValueError:
        add_error(name, 'Please enter one character a-z or 0-9, or type Esc.', error_messages, label_err)


def validate_dir(var, name, option_vars, error_messages, label_err):
    invalid_chars = ('<', '>', ':', '"', '|', '?', '*')
    entry = var.get()

    try:
        if any(inv_char in entry for inv_char in invalid_chars) or entry == '':
            raise ValueError
        clear_error(name, error_messages, label_err)
    except ValueError:
        add_error(name, 'Directory cannot contain < > : " | ? *', error_messages, label_err)


def validate_dropdown(var, name, option_vars, error_messages, label_err, font_options):
    drop_down = var.get()

    try:
        if drop_down not in font_options:
            raise ValueError
        clear_error(name, error_messages, label_err)
    except ValueError:
        add_error(name, 'Please select an item from the drop-down menu.', error_messages, label_err)


def clear_label(label):
    """Clears passed-in label. Callback function for root.after().

    Args:
        label (ttk.Label): label to be cleared
    """

    label.config(text='')


def close_window(root):
    """Closes GUI and exits program.

    Args:
        root (tk.Tk): main Tk widget window
    """

    root.destroy()


def main():
    # Set up GUI Window
    root = tk.Tk()
    root.title('Options')
    frame = ttk.Frame(root)
    frame.grid(row=0, column=0, padx=10, pady=10)

    #window_width = 500
    #window_height = 400
    #center_window(root, window_width, window_height)

    # Set Up Font Preview
    canvas = tk.Canvas(root, width=400, height=200)
    canvas.grid(row=10, column=0)


    lower_ascii = string.ascii_lowercase
    digits_ascii = string.digits
    other_ascii = r",./;'[]\-=`*-+"
    approved_keys = lower_ascii + digits_ascii + other_ascii


    # Input labels
    label_sheet = ttk.Label(frame, text='Spreadsheet output folder:')
    label_sheet.grid(row=0, column=0, sticky='W')

    label_anno = ttk.Label(frame, text='Annotated images folder:')
    label_anno.grid(row=1, column=0, sticky='W')

    label_exit_key = ttk.Label(frame, text='Exit key:')
    label_exit_key.grid(row=2, column=0, sticky='W')

    label_clear_key = ttk.Label(frame, text='Clear key:')
    label_clear_key.grid(row=3, column=0, sticky='W')

    label_duration = ttk.Label(frame, text='Coordinate/Annotation duration:')
    label_duration.grid(row=4, column=0, sticky='W')

    label_font = ttk.Label(frame, text='Font:')
    label_font.grid(row=5, column=0, sticky='W')

    label_font_color = ttk.Label(frame, text='Font Color:')
    label_font_color.grid(row=6, column=0, sticky='W')

    label_font_scale = ttk.Label(frame, text='Font Scale:')
    label_font_scale.grid(row=7, column=0, sticky='W')

    label_font_thickness = ttk.Label(frame, text='Font Thickness:')
    label_font_thickness.grid(row=8, column=0, sticky='W')


    # Input fields
    option_vars = [] #entry field vars. [8] is color tuple, [9] is color widget
    error_messages = {} #dict for keeping track of on-GUI errors

    sheet_var = tk.StringVar()
    sheet_var.set('sheets/')
    entry_sheet = ttk.Entry(frame, textvariable=sheet_var)
    entry_sheet.grid(row=0, column=1)
    sheet_var.trace_add('write', lambda *args: validate_dir(
        sheet_var, 'Spreadsheet Directory', option_vars, error_messages, label_err))
    option_vars.append(sheet_var)

    anno_var = tk.StringVar()
    anno_var.set('annotated_images/')
    entry_anno = ttk.Entry(frame, textvariable=anno_var)
    entry_anno.grid(row=1, column=1)
    anno_var.trace_add('write', lambda *args: validate_dir(
        anno_var, 'Annotation Directory', option_vars, error_messages, label_err))
    option_vars.append(anno_var)

    exit_key_var = tk.StringVar()
    exit_key_var.set('q')
    entry_exit_key = ttk.Entry(frame, textvariable=exit_key_var)
    entry_exit_key.grid(row=2, column=1)
    exit_key_var.trace_add('write', lambda *args: validate_key(
        exit_key_var, 'Exit Key', option_vars, error_messages, label_err, approved_keys))
    option_vars.append(exit_key_var)

    clear_key_var = tk.StringVar()
    clear_key_var.set('c')
    #final_args['Clear Key'] = clear_key_var.get()
    entry_clear_key = ttk.Entry(frame, textvariable=clear_key_var)
    entry_clear_key.grid(row=3, column=1)
    clear_key_var.trace_add('write', lambda *args: validate_key(
        clear_key_var, 'Clear Key', option_vars, error_messages, label_err, approved_keys))
    option_vars.append(clear_key_var)

    duration_var = tk.StringVar()
    duration_var.set(5)
    entry_duration = ttk.Entry(frame, textvariable=duration_var)
    entry_duration.grid(row=4, column=1)
    duration_var.trace_add('write', lambda *args: validate_float(
        duration_var, 'Duration', option_vars, error_messages, label_err))
    option_vars.append(duration_var)

    font_scale_var = tk.StringVar()
    font_scale_var.set(1)
    entry_font_scale = ttk.Entry(frame, textvariable=font_scale_var)
    entry_font_scale.grid(row=7, column=1)
    font_scale_var.trace_add('write', lambda *args: validate_float(
        font_scale_var, 'Font Scale', option_vars, error_messages, label_err, canvas))
    option_vars.append(font_scale_var)

    font_thickness_var = tk.StringVar()
    font_thickness_var.set(2)
    entry_font_thickness = ttk.Entry(frame, textvariable=font_thickness_var)
    entry_font_thickness.grid(row=8, column=1)
    font_thickness_var.trace_add('write', lambda *args: validate_int(
        font_thickness_var, 'Font Thickness', option_vars, error_messages, label_err, canvas))
    option_vars.append(font_thickness_var)


    # Drop-down menu
    font_options = ['0', '1', '2', '3', '4', '5', '6', '7', '16']
    font_var = tk.StringVar()
    font_var.set(font_options[0])
    font_menu = ttk.Combobox(frame, textvariable=font_var, values=font_options)
    font_menu.grid(row=5, column=1)
    font_var.trace_add('write', lambda *args: validate_dropdown(
        font_var, 'Font', option_vars, error_messages, label_err, font_options))
    option_vars.append(font_var)


    # Color picker
    color_tuple_var = tk.StringVar()
    color_tuple_var.set('(0, 255, 0)')
    option_vars.append(color_tuple_var)
    rectangle_color = tk.Canvas(frame, width=25, height=25, bg='#00FF00')
    rectangle_color.grid(row=6, column=1, sticky='E')
    option_vars.append(rectangle_color)

    color_button = ttk.Button(frame, text='Pick Font Color',
        command=lambda: pick_color(option_vars[5:], canvas))
    color_button.grid(row=6, column=1)


    # Acknowledgement/Error labels
    label_ack = ttk.Label(frame, foreground='green')
    label_ack.grid(row=11, column=0, columnspan=3)

    label_err = ttk.Label(frame, foreground='red')
    label_err.grid(row=10, column=0, columnspan=3)


    # Reset to Defaults Button
    default_button = ttk.Button(frame, text='Defaults',
        command=lambda: set_defaults(option_vars, canvas))
    default_button.grid(row=9, column=0)

    # Submit Options Button
    submit_button = ttk.Button(frame, text='Submit',
        command=lambda: submit_options(root, option_vars, label_ack,
            error_messages))
    submit_button.grid(row=9, column=1)

    # Close Program Button
    close_button = ttk.Button(frame, text='Close',
        command=lambda: close_window(root))
    close_button.grid(row=9, column=2)


    update_font_preview(option_vars[5:9], canvas) #initialize font preview

    root.mainloop()

if __name__ == "__main__":
    main()
