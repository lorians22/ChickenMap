#!/usr/bin/python3

#Date: 10/13/2023

__version__ = '2023.10.1'
__author__ = 'Logan Orians'


#TODO
# 0) integrate with chickenMap.py - no file writing
# 1) add cv2 font preview (is this possible?)
# 3) add and update docstrings


import json
import string #ascii
import tkinter as tk
from tkinter import ttk #newer widgets
from tkinter import colorchooser #colorpicker

from PIL import ImageColor #rgb hex conversion


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


def pick_color(widget):
    color = colorchooser.askcolor(title='Pick a color')
    if color: widget.config(background=color[1])


def set_defaults(default_vars, widget):
    default_vars[0].set('sheets/') #spreadsheets directory
    default_vars[1].set('annotated_images/') #annotations directory
    default_vars[2].set('q') #exit key
    default_vars[3].set('c') #clear key
    default_vars[4].set(5) #duration
    default_vars[5].set(2) #font scale
    default_vars[6].set(2) #font thickness
    default_vars[7].set(0) #font
    widget.config(background='#00FF00') #font color (green)


def submit_options(root, entries, drop_down, label_ack, label_err, color_widget,
    font_options):

    label_err.config(text='') #clear error label

    # Rename options
    args = dict()
    args['out_dir'] = entries[0].get() #sheets directory
    args['anno_dir'] = entries[1].get() #annotated images directory
    args['exit_key'] = entries[2].get() #exit key
    args['clear_key'] = entries[3].get() #clear key
    args['duration'] = int(entries[4].get()) #duration
    args['font'] = int(drop_down.get()) #font

    rgb_hex = str(color_widget['background']) #get #RRGGBB from color_label
    args['font_color'] = ImageColor.getrgb(rgb_hex) #convert to (R, G, B)
    args['font_scale'] = int(entries[5].get()) #font scale
    args['font_thickness'] = int(entries[6].get()) #font thickness
    
    write_args_to_file(args, 'options1.txt')
    label_ack.config(text='Options saved!')
    root.after(2500, lambda:clear_label(label_ack)) #clear after 2.5 seconds


def validate_int(var, name, option_vals, label_err):
    # Clear error and options value
    option_vals[name] = 0
    label_err.config(text='')

    entry = var.get()

    try:
        entry = int(entry)
        if entry <= 0:
            raise ValueError
        option_vals[name] = entry
    except ValueError:
        label_err.config(text=f'Please enter a positive integer for {name}.')


def validate_key(var, name, option_vals, label_err, approved_keys):
    # Clear error and options value
    option_vals[name] = 0
    label_err.config(text='')

    entry = var.get()

    try:
        #TODO: DeMorgan's this?
        if len(entry) == 1 and entry in approved_keys:
            option_vals[name] = entry
        elif entry.lower() == 'esc':
            option_vals[name] = 'Esc'
        else:
            raise ValueError
    except ValueError:
        label_err.config(text='Please enter one character a-z or 0-9, or type Esc.')


def validate_dir(var, name, option_vals, label_err):
    # Clear error and options value
    option_vals[name] = 0
    label_err.config(text='')

    invalid_chars = ('<', '>', ':', '"', '|', '?', '*')
    entry = var.get()

    try:
        if any(inv_char in entry for inv_char in invalid_chars) or entry == '':
            raise ValueError
        option_vals[name] = entry
    except ValueError:
        label_err.config(text='Directory cannot contain < > : " | ? *')


def validate_dropdown(var, name, option_vals, label_err, font_options):
    option_vals[name] = 0
    label_err.config(text='')

    drop_down = var.get()

    try:
        if drop_down not in font_options:
            raise ValueError
        option_vals[name] = drop_down
    except ValueError:
        label_err.config(text='Please select an item from the drop-down menu.')

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
    root = tk.Tk()
    root.title('Options')


    window_width = 500
    window_height = 400
    #center_window(root, window_width, window_height)


    frame = ttk.Frame(root)
    frame.grid(row=0, column=0, padx=10, pady=10)


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
    entries = []
    defaults = []
    final_args = dict()

    sheet_var = tk.StringVar()
    sheet_var.set('sheets/')
    defaults.append(sheet_var)
    entry_sheet = ttk.Entry(frame, textvariable=sheet_var)
    entry_sheet.grid(row=0, column=1)
    sheet_var.trace_add('write', lambda *args:validate_dir(
        sheet_var, 'Spreadsheet Directory', final_args, label_err))
    entries.append(entry_sheet)

    anno_var = tk.StringVar()
    anno_var.set('annotated_images/')
    defaults.append(anno_var)
    entry_anno = ttk.Entry(frame, textvariable=anno_var)
    entry_anno.grid(row=1, column=1)
    anno_var.trace_add('write', lambda *args: validate_dir(
        anno_var, 'Annotation Directory', final_args, label_err))
    entries.append(entry_anno)

    exit_key_var = tk.StringVar()
    exit_key_var.set('q')
    defaults.append(exit_key_var)
    entry_exit_key = ttk.Entry(frame, textvariable=exit_key_var)
    entry_exit_key.grid(row=2, column=1)
    exit_key_var.trace_add('write', lambda *args: validate_key(
        exit_key_var, 'Exit Key', final_args, label_err, approved_keys))
    entries.append(entry_exit_key)

    clear_key_var = tk.StringVar()
    clear_key_var.set('c')
    defaults.append(clear_key_var)
    entry_clear_key = ttk.Entry(frame, textvariable=clear_key_var)
    entry_clear_key.grid(row=3, column=1)
    clear_key_var.trace_add('write', lambda *args: validate_key(
        clear_key_var, 'Exit Key', final_args, label_err, approved_keys))
    entries.append(entry_clear_key)

    duration_var = tk.StringVar()
    duration_var.set(5)
    defaults.append(duration_var)
    entry_duration = ttk.Entry(frame, textvariable=duration_var)
    entry_duration.grid(row=4, column=1)
    duration_var.trace_add('write', lambda *args: validate_int(
        duration_var, 'Duration', final_args, label_err))
    entries.append(entry_duration)

    font_scale_var = tk.StringVar()
    font_scale_var.set(2)
    defaults.append(font_scale_var)
    entry_font_scale = ttk.Entry(frame, textvariable=font_scale_var)
    entry_font_scale.grid(row=7, column=1)
    font_scale_var.trace_add('write', lambda *args: validate_int(
        font_scale_var, 'Duration', final_args, label_err))
    entries.append(entry_font_scale)

    font_thickness_var = tk.StringVar()
    font_thickness_var.set(2)
    defaults.append(font_thickness_var)
    entry_font_thickness = ttk.Entry(frame, textvariable=font_thickness_var)
    entry_font_thickness.grid(row=8, column=1)
    font_thickness_var.trace_add('write', lambda *args: validate_int(
        font_thickness_var, 'Duration', final_args, label_err))
    entries.append(entry_font_thickness)


    # Drop-down menu
    font_options = ['0', '1', '2', '3', '4', '5', '6', '7', '16']
    font_var = tk.StringVar()
    defaults.append(font_var)
    font_var.set(font_options[0])
    font_menu = ttk.Combobox(frame, textvariable=font_var,
        values=font_options)
    font_menu.grid(row=5, column=1)
    font_var.trace_add('write', lambda *args: validate_dropdown(
        font_var, 'Font', final_args, label_err, font_options))


    # Color picker
    rectangle_color = tk.Canvas(frame, width=25, height=25, bg='#00FF00')
    rectangle_color.grid(row=6, column=1, sticky='E')
    color_button = ttk.Button(frame, text='Pick Font Color',
        command=lambda: pick_color(rectangle_color))
    color_button.grid(row=6, column=1)


    # Acknowledgement/Error labels
    label_ack = ttk.Label(frame, foreground='green')
    label_ack.grid(row=11, column=0, columnspan=2)

    label_err = ttk.Label(frame, foreground='red')
    label_err.grid(row=10, column=0, columnspan=2)


    # Function buttons
    default_button = ttk.Button(frame, text='Defaults',
        command=lambda: set_defaults(defaults, rectangle_color))
    default_button.grid(row=9, column=0)

    submit_button = ttk.Button(frame, text='Submit',
        command=lambda: submit_options(root, entries, font_menu, label_ack,
            label_err, rectangle_color, font_options))
    submit_button.grid(row=9, column=1)

    close_button = ttk.Button(frame, text='Close',
        command=lambda: close_window(root))
    close_button.grid(row=9, column=2)


    root.mainloop()

if __name__ == "__main__":
    main()
