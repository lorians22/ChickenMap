# Chicken Map

A 2D ~~and 3D coordinate system~~ for monitoring the location of chickens.

## Table of Contents

[Key Knowledge](#key-knowledge)

    [Windows](#windows)

    [MacOS](#macos)

[Prerequisites](#prerequisites)

    [Windows](#windows-1)

    [MacOS](#macos-1)

    [Both](#both)

[Installation](#installation)

     [Windows](#windows-2)

    [MacOS](#macos-2)

[How to Use](#how-to-use)

[Usage](#usage)

     [Windows](#windows-3)

    [MacOS](#macos-3)

    [Examples](#examples)

[Compatibility](#compatibility)

[Privacy](#privacy)

[Support](#support)

[Development Tools Used](#development-tools-used)

[License](#license)

## Key knowledge

### Windows

To open a command prompt, press the Windows key or click the Start Menu, type *cmd*, and press enter. To paste into a command prompt, right-click.

### MacOS

To open a Terminal, press Cmd + space, type *terminal*, and press return/enter. To paste into a Terminal, right-click.

## Prerequisites

### Windows

Tesseract 5.x. (tested with 5.3.1). Download the latest [here for Windows](https://digi.bib.uni-mannheim.de/tesseract/tesseract-ocr-w64-setup-5.3.1.20230401.exe) and install.

### MacOS

Tesseract 5.x (tested with 5.3.2). First, install homebrew:

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

and then install Tesseract:

```bash
brew install tesseract -y
```

### Both

Python 3.x (tested with 3.8, 3.11). Download the latest for your system [here](https://www.python.org/downloads/). When installing, make sure to check the *Add python.exe to PATH* box, then click *Install Now*.

* At the end, you have the option to *Disable path length limit*. While not necessary for this program, it's a good idea to click that option.

* After installation, verify that Python and pip are installed in a command prompt/Terminal:
  
  ```bash
  py --version
  pip3 --version
  ```

        If both respond with a version number, you're good to go

## Installation

Download a [zip](https://github.com/lorians22/ChickenMap/archive/refs/heads/main.zip) of the code, then extract to a folder on the Desktop. Open a command prompt/Terminal, navigate to the folder, and install the requirements:

### Windows

```bash
  cd %USERPROFILE%\Downloads\ChickenMap-main\ChickenMap-main
  pip3 install -r requirements.txt
```

### MacOS

```bash
  cd ~/Desktop/ChickenMap-main
  pip install -r requirements.txt
```

## How To Use

- Press `q` to quit the program. Clicking the X (Windows) or red dot (MacOS) will just replace the video with another window.

- Left-click anywhere to produce a coordinate at your cursor.
  
  - Coordinates are saved along with their video timestamps (from the top-left corner of the video) in an Excel file in the `sheets/` directory. You can find this .xlsx file in the `ChickenMap-main/` folder. Filenames are based on your system's date and time when the program started.
  
  - Coordinates remain on screen for 5 seconds after click. Press `c` while a coordinate is on-screen to clear it from the screen and remove it from the Excel sheet. Once the coordinate is off-screen, the coordinate cannot be cleared from the Excel sheet.
  
  - Coordinates and timestamps are printed to the Command Prompt/Terminal window as a backup and are not removed when `c` is pressed.

- Right-click to annotate at your cursor.
  
  - The video will freeze/pause. Go back to the Command Prompt/Terminal window, type your annotation, and hit enter. The annotation will not appear on screen. The video will resume. To return to the chicken video, click the Python/video window border or taskbar icon to go back to the chicken video. It is important to click on the window border or taskbar icon, as clicking inside the video will produce a coordinate. If you accidentally click the screen and a coordinate appears, press 'c' to clear the coordinate.
  
  - Annotated images are saved in the `annotated_images/` directory. You can find these .jpg files in the `ChickenMap-main/` folder. Filenames are based on the timestamp in the top-left corner of the video; annotations at the same timestamp are given a `_#` suffix to prevent overwriting.

## Usage

See [Examples](#examples) for platform-specific instructions (what you should actually type into the command line). VIDEO_PATH is a required argument; arguments encapsulated by brackets are optional, meaning they do not have to be entered.

```bash
py chickenMap.py VIDEO_PATH [out_dir] [anno_dir] [exit_key] \
    [clear_key] [duration]
```

You can view command-line options by typing:

```bash
py chickenMap.py -h
```

| Short Argument | Long Argument | Description                                                    | Default           |
| -------------- | ------------- | -------------------------------------------------------------- | ----------------- |
| -od            | --out_dir     | Name of output folder for Excel files                          | sheets/           |
| -ad            | --anno_dir    | Name of output folder for annotated_images                     | annotated_images/ |
| -e             | --exit_key    | Key to quit program (a-z, 0-9)                                 | q                 |
| -c             | --clear_key   | Key to remove coordinate from screen and Excel file (a-z, 0-9) | c                 |
| -d             | --duration    | Duration of coordinates on screen, in seconds                  | 5                 |

Full options are available in the `options.json5` file. You can open this file with Notepad (Windows) or TextEdit (MacOS), or your favorite text editor, if you have one. Make sure to save the file after you change options. Any option not entered at the command line will default to the one stored in this file. Here, you can also edit font, font color, font scale, and font thickness. See the comments in the file for limitations.

For example, you can change all the settings you want in `options.json5` and just type `py chickenMap.py VIDEO_PATH` into the command line, and the program will use the settings you entered into `options.json5`. This should be more user-friendly.

### Windows

In a new command prompt:

```bash
cd %USERPROFILE%\Downloads\ChickenMap-main\ChickenMap-main
py chickenMap.py VIDEO_PATH
```

`VIDEO_PATH` should not be typed out; it should be the filename of the video you want to play. You can drag a video file from File Explorer into the command prompt window and press enter to run the program; this makes it easy if your video is stored on an external hard drive. Just make sure to add a space after `py chickenMap.py` before dragging a video file into the window.

### MacOS

In a new Terminal:

```bash
cd ~/Downloads/ChickenMap-main
python chickenMap.py VIDEO_PATH
```

`VIDEO_PATH` should not be typed out; it should be the filename of the video you want to play. You can drag a video file from Finder into the Terminal window and press enter to run the program; this makes it easy if your video is stored on an external hard drive. Just make sure to add a space after `python chickenMap.py` before dragging a video file into the window.

### Examples

Basic:

```bash
py chickenMap.py test.mp4
```

Kitchen-sink example - set the exit key to Esc, output directory to `shts/`, annotated images folder to `anno_im/`, and duration of on-screen coordinates to 2 seconds:

```bash
py chickenMap.py test.mp4 -e Esc -od shts -ad anno_im -d 2
```

## Compatibility

Tested with:

- Devices and Platforms
  
  - MacOS
    
    - 2015 MacBook Pro (Intel) running MacOS 12.6.3
    
    - 2020 MacBook Air (M1) running MacOS 13
  
  - Windows
    
    - 2015 MacBook Pro (Intel) running Windows 10 Home via Boot Camp
    
    - AM4 PC running Windows 10 Pro 22H2 (build 19045)
    
    - Samsung laptop running Windows 11 Home 22H2 (build 22621)
  
  - *Linux probably works since MacOS works, but I offer no detailed instructions for it (you can figure it out).*

- Software
  
  - Tesseract-OCR 5.12, 5.11
  
  - Python 3.11, 3.9
    
    - OpenCV-Python 4.8.0.74
    
    - Python-tesseract 0.3.10
    
    - Pillow 10.0.0
    
    - openpyxl 3.1.2

## Privacy

This program does not store or transmit any user data to an external source and can run without connection to the Internet. Your OS/platform (Windows, MacOS) is determined at runtime to point `pytesseract` to the Tesseract-OCR executable on Windows, and it is not stored after the program exits. Program errors and platform info are stored in `error_log.txt` and are not transmitted by this program; if you have errors, see [Support](#support).

## Support

For support, email me at logan.orians@gmail.com or message me on [Discord](https://discord.com/users/l_orians). Please attach `error_log.txt` to your message and describe what you were doing when the error occurred.

## Development Tools Used

- [MarkText](https://www.marktext.cc/) for README editing

- [Sublime Text 4](https://www.sublimetext.com/), [Notepad++](https://notepad-plus-plus.org/) and [VSCode](https://code.visualstudio.com/) for text editing and programming

# 


## License

Approved for private use by students and employees of Purdue University only. No implied support or warranty. Copyright 2023, Logan Orians in affiliation with Purdue University: Dr. Marisa Erasmus and Gideon Ajibola.
