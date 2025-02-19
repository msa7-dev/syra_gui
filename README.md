# README
![](./radar_eval/gui/resources/pics/Logo_Sykno.svg "")

# __MiRa Evaluation GUI__ 


## System setup

### Prerequrement:
```sh
$ python3 -m pip install click loguru
```

### Install dependencies:
```sh
$ sudo python3 sykno_cli setup
```
### Build cython module:
```sh
$ python3 sykno_cli build
```

### Python virtual enviorment:
```sh
$ python3 -m venv sykno_env
$ source ./sykno_env/bin/activate
$ sudo python3 -m pip install -r ./radar_eval/setup/requirements.txt
```

### Start MiRa eval GUI:
```sh
$ sudo python3 sykno_cli start-gui
```

### Build MiRa eval GUI as one-file executable via nuitka
To be executed in the virtual enviorment:
```sh
$  nuitka3 --standalone --onefile --enable-plugin=pyqt5 --output-dir=./compiled ./radar_gui_starter.py
```