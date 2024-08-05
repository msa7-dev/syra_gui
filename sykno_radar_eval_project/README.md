# README
![](./radar_eval/gui/resources/pics/Logo_Sykno.svg "")

# __Radar Evaluation GUI__ 

### System requirements:
- Unix based OS
- 4 Core CPU (x86_64)


 Open the terminal and execute the following commands:
### Install Sykno Radar USB device rules (udev):
```sh
$ sudo ./install_eval_gui.sh
```

### Run Sykno Evaluation GUI:
```sh
$ ./radar_gui_starter.bin
```

### Python virtuel enviorment:
A virtuel enviorment is recommended for working with jupyter notebook. 

Follow this instructions to install and activate a new virtuel enviorment with all dependencies. 

```sh
$ python3 -m pip install virtualenv
$ python3 -m venv sykno_env
$ source ./sykno_env/bin/activate
$ python3 -m pip install -r ./radar_eval/setup/requirements.txt
```

### Jupyter notebook as evaluation and post-processing entry point:
Activate virtual environment and install all requirements (described above).

Then you can open the jupyter notebook:

```sh
$ jupyter notebook 
```
