#!/bin/bash

# Installs CodeChat

# To download this script and automatically run it, run in a terminal (without the # or $ signs):
# $ wget https://raw.githubusercontent.com/JoeKenn1118/CodeChat_system/master/CodeChat_Server/codechat.sh && bash codechat.sh

# check for Python 3
if ! hash python3; then
    echo "Python 3 is not installed"
    exit 1
fi

# check python version
python3 -c 'import sys'

if ! python3 -c 'import sys; assert sys.version_info >= (3,7)' 2> /dev/null; then
    echo "Upgrade Python to version 3.7 or above"
    exit 1
fi

# install / upgrade pip
python3 -m pip install --user --upgrade pip

# create virtual environment
python3 -m venv codechat

# check if codechat already installed
if [[ -d codechat ]]; then
    echo "CodeChat already installed"
    exit 1
else
    codechat/bin/python3 -m pip install --upgrade CodeChat_Server
fi

# echo server directory to user
echo "CodeChat installation complete!"
echo "Install directory:"
which CodeChat_Server


