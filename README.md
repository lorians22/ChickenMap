
# ChickenMap - Individual Calibration

Program to perform individual camera calibration. This code is not needed (only the outputs) to run the main ChickenMap program, so it was omitted.


## Compatibility

Tested with AM4 PC running Windows 10 22H2.
## Requirements

Run to install pre-requisite packages:
```bash
pip install -r requirements.txt
```
## Usage/Examples
In a command prompt:

```bash
python individual_calibration.py <path_to_images> <filetype>
```
```bash
python individual_calibration.py images/individual/NB2B jpg
```

Results (camera matrix and distortion coefficients) are written to <filepath_basename>.txt (i.e., a filepath of images/individual/NB2B has results written to NB2B.txt).
## Support

For support, email me at logan.orians@gmail.com or message me on [Discord](https://discord.com/users/l_orians).


## License

[GPLv3.0](https://choosealicense.com/licenses/gpl-3.0/)

