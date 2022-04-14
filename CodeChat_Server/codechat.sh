#!/bin/bash
# install CodeChat

# Run (without the pound or dollar signs):
# $ chmod 700 install.sh
# to make this script executable on your system
# then run:
# $ bash install.sh


# todo: if no python, echo commands to install

# todo: check python version

# install / upgrade pip
python3 -m pip install --user --upgrade pip

# create virtual environment (no harm doing this multiple times)
python3 -m venv codechat

# activate virtual environment



if [[ -d codechat ]]; then
    echo "CodeChat already installed"
else
    python3 -m pip install --upgrade CodeChat_Server
fi

# echo server directory to user
which CodeChat_Server


