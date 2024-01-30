# README

## _Forschungspraktikum - Sykno - Paatsch_ 
#### _Implementation and Optimization of a Real-Time Interface_
---

# General CLI for Sykno Projects

## Project Files:
### Main Functional Python Scripts:
```
$ ./cli_Sykno.py
$ ./xRad_Qt/xRad_qt_Sykno.py
$ ./xRad_GUI/xRad_gui_Sykno.py
$ ./py_scripts_Sykno/filter_Sykno.py
$ ./py_scripts_Sykno/xRad_serial_Sykno.py
$ ./py_scripts_Sykno/frame_analyzer_Sykno.py
$ ./py_scripts_Sykno/logic_analyzer_Sykno.py
$ ./py_scripts_Sykno/xRad_rx_convert_Sykno.py
```
### Bash Scripts - Linux
```
$ ./bash_scripts_Sykno/esp_adc_capture.sh
$ ./bash_scripts_Sykno/usb_adc_caputre.sh
$ ./bash_scripts_Sykno/launch_automation_analyzer.sh
```
### Power Shell Scripts - Windows
``` 
$ ./shell_scripts_Sykno/esp_adc_capture.ps1
$ ./shell_scripts_Sykno/usb_adc_capture.ps1
$ ./launch_automation_analyzer.ps1
```
### Further Information
```
$ README.md
$ python3 ./cli_Sykno --help
```

---
## Dependencies:
All python packages and modules are handled in the _pyproject.toml_ file, with _poetry_ a virtuel enviroment can be installed localy. For further information install have a look at:

 - [github poetry](https://github.com/python-poetry/poetry/)
- [pyproject.toml structure](https://github.com/python-poetry/poetry/blob/master/pyproject.toml)

First install _poetry_ to manage virtuel enviroment:
```sh
$ pip install poetry 
```
Then install and open the _poetry_ shell in root directory of the project:
```sh
$ poetry install
$ poetry shell
```

---
## Code Usage
Start _poetry_ shell to get all necessary dependencies:
- Hint: start this command from /projectRoot/
```sh
$ poetry shell
```

Plot USB xRad data in realtime: 
```sh
# Get serial data (Ch0 & Ch1) from XRad1.01 and plot real time
$ python3 ./cli_Sykno plot-xrad rt

# Optional arguments for real time plot
$ python3 ./cli_Sykno plot-xrad rt --com_port"/dev/ttyACM0" --rt_samples=100 --duration_time=5 --baud=115200 --debug=True
```
Plot USB xRad data with a number of n samples:
```sh
# Get serial data (Ch0 & Ch1 from xRad and plot n samples
$ python3 ./cli_Sykno plot-xrad no_rt 

# Optional arguments for n samples plot
$ python3 ./cli_Sykno plot-xrad no_rt --com_port="/dev/ttyACM0" --n_samples=10000 --baud=115200 --debug=True
```

Get raw serial xRad data and save it to a CSV file:
- Hint: start this command from /projectRoot/py_scripts/
```sh
# Capture serial input to a csv file
$ python3 ../cli_Sykno xrad-csv

# Optional arguments for serial to csv capturing
$ python3 ../cli_Sykno xrad-csv --com_port="/dev/ttyACM0" --baud=115200 --n_samples=100000 --filename="Measurement_XY" --path="./Measurements" --duration=5[sec] --debug=False
```

Start a measurement with the Saleae logic analyzer: 
- Hint: start this command from /projectRoot/py_scripts/
```sh
# Starts a saleae logic analyzer session 
$ python3 ../cli_Sykno logic-analyzer

# Optional arguments for logic analyzer session
$ python3 ../cli_Sykno logic-analyzer --path="./Measurements" --name="Measurement_XY" --duration=5[sec] --timestamp=True --duts=1-2 --debug=False
```

Analyze the frames of the two measurements (Logic Analyzer & xRad Serial Capture):
- Hint: start this command from /projectRoot/py_scripts/
```sh
# Starts frame analyzer which compares two captured files
$ python3 ../cli_Sykno frame-analyzer 

# Optional arguments for frame analyzer
$ python3 ../cli_Sykno frame-analyzer --path_frame1="../Measurements/Saleae_Capture_CSV_Files/" --path_frame2="../Measurements/xRad_ser_Capture_PKL_Files/" --filename1="Measurement_Logic_Analyzer" --filename2="Measurement_xRad_serial" --output_path="../Measurement"
```

Measure the serial output speed:
```sh
# Starts a measurement to get the sampling rate of the serial input
$ python3 ./cli_Sykno serial-meas

# Optional arguments for serial measurement 
$ python3 ./cli_Sykno serial-meas --com_port="/dev/ttyACM0" --baud=115200 --debug=False
```

Start xRad Qt for video producing:
- Hint: start this command from /projectRoot/xRad_Qt/
```sh
# Starts the Qt window to produce videos 
$ python3 ../cli_Sykno xrad-qt

# Optional arguments for Qt window 
$ python3 ../cli_Sykno xrad-qt --file1="./data/folder_XY/filename_XY" --file2="./data/folder_XY/filename_XY" --freq_ax=60
```

Start xRad GUI to visualize raw value plot, spectrum, elipse:
- Hint: start this command from /projectRoot/xRad_GUI/
- Start Plot with F12 and Close it with ESC
```sh
# Starts the xRad GUI
$ python3 ../cli_Sykno xrad-gui

# Optional arguments for xRad GUI 
# ! Hint: to use a CSV file as input use this argument: --input="file" 
$ python3 ../cli_Sykno xrad-gui --input="serial" --file1="../Measurements/xRad_Data/Measurement_XY_CH0" --file2="../Measurements/xRad_Data/Measurement_XY_CH1" --freq_ax=60 --update=5 --filename="Measurement_GUI" --com_port="/dev/ttyACM0"
```

Start mira Rx Tx
- Hint: start this command from /projectRoot/ 
```sh
# Start the mira Rx Tx
$ python3 ./cli_sykno mira-rx-tx
```

Get more information about the usage of the Sykno CLI:
```sh
# Get more information about optional arguments
$ python3 cli_Sykno.py --help
$ python3 cli_Sykno.py <command> --help
```



