#!/bin/bash
# install CodeChat

# Run (without the pound or dollar signs):
# $ chmod 700 install.sh
# to make this script executable on your system
# then run:
# $ bash install.sh

# https://stackoverflow.com/questions/6141581/detect-python-version-in-shell-script

# check for python
if ! hash python; then
    echo "Python is not installed"
    exit 1
fi

# todo: if no python, echo commands to install

# todo: check python version

# install / upgrade pip
python3 -m pip install --user --upgrade pip

# create virtual environment (no harm doing this multiple times)
python3 -m venv codechat

# activate virtual environment
source codechat/bin/activate
# . codechat/bin/activate  (alternate command?)

# check to see if CodeChat is already installed
# todo: check version number

if [[ -d codechat ]]; then
    echo "CodeChat already installed"
else
    python3 -m pip install --upgrade CodeChat_Server
fi

# echo server directory to user
which CodeChat_Server
