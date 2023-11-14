# Chicken Map

A 2D coordinate mapping program for monitoring the location of chickens.

Version 2023.11.1

## Table of Contents

- [Key Knowledge](#key-knowledge)
  
  - [Windows](#windows)
  
  - [MacOS](#macos)

- [Prerequisites](#prerequisites)
  
  - [Windows](#windows-1)
  
  - [MacOS](#macos-1)

- [Installation](#installation)
  
  - [Windows](#windows-2)
  
  - [MacOS](#macos-2)

- [How to Use](#how-to-use)
  
  - [Instructions](#instructions)

- [Usage](#usage)
  
  - [Windows](#windows-3)
  
  - [MacOS](#macos-3)

- [Compatibility](#compatibility)

- [Privacy](#privacy)

- [Development](#development)
  
  - [Third-Party Resources](#third-party-resources)
  
  - [Tools Used](#tools-used)
  
  - [Style and Formatting](#style-and-formatting)
  
  - [Decisions](#decisions-nerd-questions)

- [Support](#support)

    [MacOS](#macos-2)

[How to Use](#how-to-use)

[Usage](#usage)

    [Windows](#windows-3)

    [MacOS](#macos-3)

    [Examples](#examples)

[Compatibility](#compatibility)

[Privacy](#privacy)

[Support](#support)

[Development](#development)

    [Style and Formatting](#style-and-formatting)

    [Decisions](#decisions-nerd-questions)

    [Tools Used](#tools-used)

[License](#license)

## Key knowledge

### Windows

- To open a command prompt, press the Windows key or click the Start Menu, type *cmd*, and press enter.

- To execute a command, type the command and press Enter.

- To paste into a command prompt, right-click.

- To re-run a previous command, navigate between them using the up and down arrow keys, then press Enter.

- If you have any issues with commands not being recognized after installing Python, Tesseract, or packages using `pip3`, close all command prompt windows and open a new one.

### MacOS

- To open a Terminal, press Cmd + space, type *terminal*, and press Return/Enter.

- To execute a command, type the command and press Return/Enter.

- To paste into a Terminal, right-click.

- To re-run a previous command, navigate between them using the up and down arrow keys, then press Enter.

- If you have any issues with commands not being recognized after installing Python, Tesseract, or packages using `pip3`, close all Terminals and open a new one.

## Prerequisites

### Windows

- Tesseract 5.x. (tested with 5.3.1). Download the latest [here for Windows](https://digi.bib.uni-mannheim.de/tesseract/tesseract-ocr-w64-setup-5.3.1.20230401.exe) and install.

- Python 3.7+ (tested with 3.8, 3.11, 3.12). Download the latest for your system [here](https://www.python.org/downloads/) and install. If you have Python installed already and want to see if your currently installed version is sufficient (i.e., >=3.7), type `py --version` in a command prompt.
  
  - On Windows, when installing, make sure to check the *Add python.exe to PATH* box, then click *Install Now*. At the end, you'll have the option to *Disable path length limit*. While not necessary for this program, it's a good idea to click that option.
  
  - After installation, if another command prompt window pops up and the characters to the left are `>>>`, close out of that command prompt. Then, verify that Python3 and pip3 are installed in a normal command prompt, which starts with `C:\`. If both respond with a version number, you're good to go:
    
    ```bash
    py --version
    pip3 --version
    ```

### MacOS

- Tesseract 5.x (tested with 5.3.2).
  
  - First, install [Homebrew](https://brew.sh/) by typing the below command into Terminal. If you already have Homebrew installed, typing `which brew` will show you the install location, and you can skip to the next step:
    
    ```bash
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    ```
  
  - Then install Tesseract:
    
    ```bash
    brew install tesseract
    ```

- Python 3.7+ (tested with 3.8, 3.11, 3.12). Download the latest for your system [here](https://www.python.org/downloads/).
  
  - After installation, verify that Python3 and pip3 are installed in a Terminal. If both respond with a version number, you're good to go:
    
    ```bash
    python3 --version
    pip3 --version
    ```

## Installation

[Download a zip](https://github.com/lorians22/ChickenMap/archive/refs/heads/main.zip) of this code, then extract. Required Python libraries for this program:

- NumPy

- OpenCV-Python

- openpyxl

- Python-tesseract

- Pillow

- sv-ttk

These can be installed by double-clicking the `REQS_WIN.cmd` file on Windows or `REQS_MAC.command` on MacOS. MacOS users will likely be prompted with a security pop-up due to the system [Gatekeeper](https://support.apple.com/en-us/HT202491#openanyway). Bypass this by  navigating to [Privacy and Security in System Preferences](x-apple.systempreferences:com.apple.preference.security?Privacy), and clicking Open Anyway next to *REQS_MAC.command* in the Security pane.

### Windows

```bash
  cd %USERPROFILE%\Downloads\ChickenMap-main\ChickenMap-main
  pip3 install -r requirements.txt
```

### MacOS

```bash
  cd ~/Downloads/ChickenMap-main
  pip3 install -r requirements.txt
```

## How To Use

Command line usage can be found under [Usage](#usage). To test things out, if you don't already have a command prompt/Terminal open and navigated to the ChickenMap folder, do so:

    Windows: `cd %USERPROFILE%\Downloads\ChickenMap-main\ChickenMap-main`

    MacOS: `cd ~/Downloads/ChickenMap-main`

Then, run the program with the test video:

    Windows: `py chickenMap.py`

    MacOS: `python3 chickenMap.py`

### Instructions

- Press `q` to quit the program. Clicking the X in the corner (on Windows) will just replace the video with another window.

- Press `p` to pause the video. Press `p` again to resume. The video is automatically paused while annotating but will resume once `Enter` is pressed, unless you pressed `p` beforehand.

- Left-click anywhere to produce a coordinate at your cursor.
  
  - Coordinates are saved along with their video timestamps (from the top-left corner of the video) in an Excel file in the `sheets/` directory. You can find this .xlsx file in the `ChickenMap-main/` folder. Filenames are based on your system's date and time when the program started.
  
  - Coordinates remain on screen for 5 seconds after click by default. Press `c` while a coordinate is on-screen to clear it from the screen and remove it from the Excel sheet. Once the coordinate is off-screen, the coordinate cannot be cleared from the Excel sheet.
  
  - Coordinates and timestamps are printed to the Command Prompt/Terminal window as a backup and are not removed when `c` is pressed.

- Right-click to annotate at your cursor.
  
  - The video will freeze/pause. Each key you press will show up on screen, at the location you right-clicked.
    
    - Press `Enter` to save the annotated image and resume the video.
    
    - Press `Esc` to cancel annotating. If the video was not manually paused before, the video will resume.
    
    - Press `Backspace` just as you would normally to remove letters from the annotation.
    
    - Annotations will stay on screen for 5 seconds by default.
  
  - Annotated images are saved as `.jpg`s in the `annotated_images/<timestamp>` directory, where `<timestamp>` is the system date/time when you ran the program. Filenames are based on the timestamp in the top-left corner of the video; annotations at the same timestamp are given a `_#` suffix to prevent overwriting.

## Usage

```bash
chickenMap.py [-h] [-o]
```

You can set program options with a GUI with:

```bash
chickenMap.py -o
```

Please do not edit the `options.json` file.

### Windows

In a new command prompt:

```bash
cd %USERPROFILE%\Downloads\ChickenMap-main\ChickenMap-main
py chickenMap.py
```

### MacOS

In a new Terminal:

```bash
cd ~/Downloads/ChickenMap-main
python3 chickenMap.py
```

## Compatibility

Tested with:

- Devices and Platforms
  
  - Windows
    
    - AM4 PC running Windows 10 Pro 22H2 (build 19045)
    
    - Samsung laptop running Windows 11 Home 22H2 (build 22621)
    
    - 2015 MacBook Pro (Intel) running Windows 10 Home via Boot Camp
  
  - MacOS
    
    - 2020 MacBook Air (M1) running MacOS 13
    
    - 2015 MacBook Pro (Intel) running MacOS 12.6.3
    
    - AM4 PC running MacOS 12.6 via OpenCore
  
  - *Linux probably works since MacOS works, but I offer no detailed instructions for it (you run Linux — you can figure it out).*

- Software
  
  - Tesseract-OCR 5.12, 5.11
  
  - Python 3.12, 3.11, 3.9
    
    - OpenCV-Python 4.8.0.74
    
    - Python-tesseract 0.3.10
    
    - Pillow 10.0.0
    
    - openpyxl 3.1.2

## Privacy

This program does not store or transmit any user data to an external source and can run without connection to the Internet. Your OS/platform (Windows, MacOS) is determined at runtime to point `pytesseract` to the Tesseract-OCR executable on Windows, and it is not stored after the program exits. Program errors and platform info (OS version, Python version, processor name) are stored in `error_log.txt` and are not transmitted by this program; if you have errors, see [Support](#support).

## Development

### Third-Party Resources

- [NumPy](https://pypi.org/project/numpy/)

- [OpenCV-Python](https://pypi.org/project/opencv-python/)

- [openpyxl](https://pypi.org/project/openpyxl/)

- [Python-tesseract](https://pypi.org/project/pytesseract/)

- [Pillow](https://pypi.org/project/Pillow/)

- [Azure theme by rdbende](https://github.com/rdbende/Azure-ttk-theme)

### Tools Used

- [Sublime Text 4](https://www.sublimetext.com/), [Notepad++](https://notepad-plus-plus.org/) and [VSCode](https://code.visualstudio.com/) for text editing and programming

- [MarkText](https://www.marktext.cc/) for README editing

### Style and Formatting

This code attempts to follow [PEP 484](https://peps.python.org/pep-0484/) and [PEP 604](https://peps.python.org/pep-0604/) for type hints and [PEP 8](https://peps.python.org/pep-0008/) and the [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html) for style and formatting, with programmer's freedom on any conflicting elements. Line width is set to 100 characters (not 80) because it's 2023 and we have high-resolution and ultrawide monitors.

### Decisions (Nerd Questions)

**Q:** Why did you change the mouse callback function for OpenCV so much?

**A:** *Stop stalking my commits*        All the tutorials suck and just have you use a global variable if you need to get something like `x` and `y` from the callback (you can't grab the return value of a callback function). Nothing explicitly wrong with globals, I just like to avoid them when I can so I don't risk interfering with something unexpected. You can set the callback function to a class method, define it in main() as a nested function, or actually read the documentation and notice that the `param` argument might as well be nearly purpose-built for this, and yet no one uses it. Just pass in an *object* for `param` and set a value in the callback and bam, problem solved.

**Q:** Why did you make *x* a `SimpleNamespace` instead of a `dict`?

**A:** I really like the dot notation for accessing object attributes and often find myself trying to use it on dicts. If I don't need to do anything fancy with key-value pairs, why not make it easier on myself? Plus it looks cleaner, in my opinion.

**Q:** Why didn't you use a modern UI library or toolkit?

**A:** I didn't have experience with modern UIs in Python, but I had experience with tkinter/Tcl/Tk and OpenCV. OpenCV and tkinter were able to do what I needed. Feel free to rewrite using [PyQt5](https://pypi.org/project/PyQt5/), [DearPyGUI](https://pypi.org/project/dearpygui/), [PySimpleGUI](https://pypi.org/project/PySimpleGUI/), or other modern cross-platform framework and fork/pull request. Not sure what else exists for OpenCV, but go nuts.

**Q:** Why did you use a [third-party theme](https://github.com/rdbende/Azure-ttk-theme) for the GUI instead of just the built-in ones?

**A:** Honestly, I didn't want to spend the time to make a dark version of the default theme for Windows (and yes, a dark mode was totally necessary). MacOS's default `aqua` theme handled it automatically without me telling it to, but Windows would have just taken too long to get right (unless I'm missing something obvious). It's only a few lines of code to determine the system theme, so adding a theme where I can just tell it "light" or "dark" was far less of a headache. And the theme looks better, in my opinion.

## Support

For support, email me at [logan.orians@gmail.com](mailto:logan.orians@gmail.com) with "chicken map" in the subject line, or message me on [Discord](https://discord.com/users/l_orians) and I will get back to you as soon as possible. Please attach `error_log.txt` to your message (and copy+paste/screenshot+attach any errors present in Command Prompt/Terminal) and describe what you were doing when the error occurred.

## License

Approved for private use by students and employees of Purdue University only. No implied support or warranty. Copyright 2023, Logan Orians in affiliation with Purdue University: Dr. Marisa Erasmus and Gideon Ajibola.
