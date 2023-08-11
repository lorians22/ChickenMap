
# Chicken Map

A 2D and 3D coordinate system for monitoring the location of chickens.


## Key knowledge

### Windows

To open a command prompt, press the Windows key or click the start menu, type *cmd*, and press enter.

### MacOS

To open a Terminal, press Cmd + space, type *terminal*, and press return/enter.
## Prerequisites

Python 3.x (tested with 3.8, 3.11). Download the latest [here](https://www.python.org/downloads/).

After installation, verify that pip is installed in a command prompt/Terminal:

```bash
  pip --version
```
## Installation

Download a [zip](https://github.com/lorians22/ChickenMap/archive/refs/heads/main.zip) of the code, then extract to a folder on the Desktop. Open a command prompt/Terminal, navigate to the folder, and install the requirements:

### Windows
```bash
  cd %USERPROFILE%\Desktop\ChickenMap-main
  pip install -r requirements.txt
```

### MacOS
```bash
  cd ~/Desktop/ChickenMap-main
  pip install -r requirements.txt
```
    
## Usage/Examples

### Windows

In a command prompt:

```bash
cd %USERPROFILE%\Desktop\ChickenMap-main
python chickenMap.py
(drag video file to command prompt window, press enter)
```
Click in the video window to produce a coordinate.

### MacOS

In a Terminal:

```bash
cd ~/Desktop/ChickenMap-main
python chickenMap.py
(drag video file to Terminal window, press enter)
```
Click in the video window to produce a coordinate.


### Example

```bash
python chickenMap.py
chickenStockVideo.mp4
```

## Compatibility

Tested with:
- 2015 Intel MacBook Pro running MacOS 12.6.3 and Windows 10 via Boot Camp
- 2020 M1 MacBook Air running MacOS 13
## Support

For support, email logan.orians@gmail.com.


## License

[GPLv3.0](https://choosealicense.com/licenses/gpl-3.0/)

