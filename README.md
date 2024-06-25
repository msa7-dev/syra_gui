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

### Python virtuel enviorment:
```sh
$ python3 -m venv sykno_env
$ source ./sykno_env/bin/activate
$ sudo python3 -m pip install -r ./requirements.txt
```

### Start Radar Eval GUI:
```sh
$ python3 sykno_cli radar-gui
```

### Build Radar Eval GUI as one-file-executable via nuitka
```sh
$  nuitka3 --standalone --onefile --enable-plugin=pyqt5 --output-dir=./mira_build ./mira_installer.py
```