#!/bin/bash
sudo taskset -c 1 nice -n -20 poetry run python3.10 -B sykno_cli mira-gui
