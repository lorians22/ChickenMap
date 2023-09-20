# Chicken Map

A 2D and 3D coordinate system for monitoring the location of chickens.

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

## Usage/Examples

* Press `q` to quit the program. Clicking the X (Windows) or red dot (MacOS) will just replace the video with another window.

* Left-click anywhere to produce a coordinate at your cursor.
  
  * Coordinates are saved along with their video timestamps (from the top-left corner of the video) in an Excel file in the `sheets/` directory. You can find this .xlsx file in the `ChickenMap-main/` folder. Filenames are based on your system's date and time when the program started.
  
  * Coordinates remain on screen for 5 seconds after click. Press `c` while a coordinate is on-screen to clear it from the screen and remove it from the Excel sheet. Once the coordinate is off-screen, the coordinate cannot be cleared from the Excel sheet.
  
  * Coordinates and timestamps are printed to the Command Prompt/Terminal window as a backup and are not removed when `c` is pressed.

* Right-click to annotate at your cursor.
  
  * The video will freeze/pause. Go back to the Command Prompt/Terminal window, type your annotation, and hit enter. The annotation will not appear on screen. The video will resume. To return to the chicken video, click the Python/video window border or taskbar icon to go back to the chicken video. It is important to click on the window border or taskbar icon, as clicking inside the video will produce a coordinate. If you accidentally click the screen and a coordinate appears, press 'c' to clear the coordinate.
  
  * Annotated images are saved in the `annotated_images/` directory. You can find these .jpg files in the `ChickenMap-main/` folder. Filenames are based on the timestamp in the top-left corner of the video; annotations at the same timestamp are given a `_#` suffix to prevent overwriting.

### Windows

In a new command prompt:

```bash
cd %USERPROFILE%\Downloads\ChickenMap-main\ChickenMap-main
py chickenMap.py <path_to_video>
```

`<path_to_video>` should not be typed out; it should be the filename of the video you want to play. You can drag a video file from File Explorer into the command prompt window and press enter to run the program. Just make sure to add a space after `py chickenMap.py` before dragging a video file into the window.

### MacOS

In a new Terminal:

```bash
cd ~/Desktop/ChickenMap-main
python chickenMap.py
(drag video file to Terminal window, press enter)
```

`<path_to_video>` should not be typed out; it should be the filename of the video you want to play. You can drag a video file from Finder into the Terminal window and press enter to run the program. Just make sure to add a space after `python chickenMap.py` before dragging a video file into the window.

### Example

```bash
py chickenMap.py test.mp4
```

## Compatibility

Tested with:

- 2015 MacBook Pro (Intel) running MacOS 12.6.3 and Windows 10 via Boot Camp
- 2020 MacBook Air (M1) running MacOS 13
- AM4 PC running Windows 10 Pro 22H2 (build 19045)
- Samsung laptop running Windows 11 Home 22H2 (build 22621)

Linux probably works since MacOS works, but I offer no detailed instructions for it (you can figure it out).

## Support

For support, email me at logan.orians@gmail.com or message me on [Discord](https://discord.com/users/l_orians).


## License

Approved for private use by students and employees of Purdue University. No implied support or warranty. Looking to become open source (under GPLv3.0) or at least source-available if permissable by Purdue University.
