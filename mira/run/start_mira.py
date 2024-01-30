#! /usr/bin/python3

import subprocess

command = "python3.10"
args = ["sykno_cli", "mira-gui"]

result = subprocess.run([command] + args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)


# Output results
print("Return Code:", result.returncode)
print("Output:", result.stdout)
print("Error:", result.stderr)