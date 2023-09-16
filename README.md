
# Chicken Map

A 2D and 3D coordinate system for monitoring the location of chickens.


## Key knowledge

### Windows

To open a command prompt, press the Windows key or click the Start Menu, type *cmd*, and press enter.

### MacOS

To open a Terminal, press Cmd + space, type *terminal*, and press return/enter.

## Prerequisites

Python 3.x (tested with 3.8, 3.11). Download the latest [here](https://www.python.org/downloads/).

After installation, verify that pip is installed in a command prompt/Terminal:

```bash
  pip --version
```

Tesseract 5.x. (tested with 5.3.1). Download the latest [here for Windows](https://digi.bib.uni-mannheim.de/tesseract/tesseract-ocr-w64-setup-5.3.1.20230401.exe).

## Installation

Download a [zip](https://github.com/lorians22/ChickenMap/archive/refs/heads/main.zip) of the code, then extract. Open a command prompt/Terminal, navigate to the folder, and install the requirements:

### Windows
```bash
  cd %USERPROFILE%\Downloads\ChickenMap-main
  pip install -r requirements.txt
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
python chickenMap.py <path_to_video>
```
Make sure to separate `python chickenMap.py` and the video file by a space. You can drag a video file into the command prompt window and press enter to run the program. Click in the video window to produce a coordinate.

### MacOS

In a Terminal:

```bash
cd ~/Downloads/ChickenMap-main
python chickenMap.py <path_to_video>
```
Make sure to separate `python chickenMap.py` and the video file by a space. You can drag a video file into the Terminal window and press enter to run the program. Click in the video window to produce a coordinate.

### Example

```bash
python chickenMap.py test.mp4
```

## Compatibility

Tested with:
- 2015 Intel MacBook Pro running MacOS 12.6.3 and Windows 10 via Boot Camp
- 2020 M1 MacBook Air running MacOS 13
- AM4 PC running Windows 10 22H2 (build 19045)

## Support

For support, email me at logan.orians@gmail.com or message me on [Discord](https://discord.com/users/l_orians).

## License

Approved for private use by students and employees of Purdue University. No implied support or warranty. Looking to become open source (under GPLv3.0) or source-available if permissable by Purdue University.
