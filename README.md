# Chicken Map

A 2D and 3D coordinate system for monitoring the location of chickens.

## Key knowledge

### Windows

To open a command prompt, press the Windows key or click the Start Menu, type *cmd*, and press enter.

### MacOS

To open a Terminal, press Cmd + space, type *terminal*, and press return/enter.

## Prerequisites

* Python 3.x (tested with 3.8, 3.11). Download the latest [here](https://www.python.org/downloads/). When installing, make sure to check the *Add python.exe to PATH* box, then click *Install Now*.  ![](C:\Users\st33l\ChickenMap\pythonPath.png)After installation, verify that Python and pip are installed in a command prompt/Terminal. If both respond with a version number, you're good to go:
  
  ```bash
  py --version
  pip3 --version
  ```



* Tesseract 5.x. (tested with 5.3.1). Download the latest [here for Windows](https://digi.bib.uni-mannheim.de/tesseract/tesseract-ocr-w64-setup-5.3.1.20230401.exe) and install.

## Installation

Download a [zip](https://github.com/lorians22/ChickenMap/archive/refs/heads/main.zip) of the code, then extract. Open a command prompt/Terminal, navigate to the folder, and install the requirements:

### Windows

```bash
  cd %USERPROFILE%\Downloads\ChickenMap-main
  pip3 install -r requirements.txt
```

### MacOS

```bash
  cd ~/Downloads/ChickenMap-main
  pip install -r requirements.txt
```

## Usage/Examples

### Windows

In a command prompt:

```bash
cd %USERPROFILE%\Downloads\ChickenMap-main
py chickenMap.py <path_to_video>
```

Make sure to separate `python3 chickenMap.py` and the video file by a space. You can drag a video file into the command prompt window and press enter to run the program. Click in the video window to produce a coordinate.

### MacOS

In a Terminal:

```bash
cd ~/Downloads/ChickenMap-main
python chickenMap.py <path_to_video>
```

Make sure to separate `python chickenMap.py` and the video file by a space. You can drag a video file into the Terminal window and press enter to run the program. Click in the video window to produce a coordinate.

### Example

```bash
py chickenMap.py test.mp4
```

Left-click anywhere to produce a coordinate at your cursor. Coordinates are saved along with their video timestamps in an Excel file in the output/ directory. Press 'c' while a coordinate is on-screen to clear it from the screen and remove it from the Excel sheet.

Right-click to annotate at your cursor: Go back to the Command Prompt/Terminal window, type your annotation, and hit enter, then click the Python/video window to go back to the chicken video. Click the window border, as clicking inside the video will produce a coordinate. Annotated images are saved in the annotated_images/ directory.

Press 'q' to quit the program.

## Compatibility

Tested with:

- 2015 Intel MacBook Pro running MacOS 12.6.3 and Windows 10 via Boot Camp
- 2020 M1 MacBook Air running MacOS 13
- AM4 PC running Windows 10 22H2 (build 19045)

## Support

For support, email me at logan.orians@gmail.com or message me on [Discord](https://discord.com/users/l_orians).

## License

Approved for private use by students and employees of Purdue University. No implied support or warranty. Looking to become open source (under GPLv3.0) or source-available if permissable by Purdue University.
