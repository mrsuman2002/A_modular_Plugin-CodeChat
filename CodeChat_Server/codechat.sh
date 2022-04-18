#!/bin/bash
# installs CodeChat

# Run (without the pound or dollar signs):

# wget https://raw.githubusercontent.com/JoeKenn1118/CodeChat_system/master/CodeChat_Server/codechat.sh && bash codechat.sh


# check for Python 3
if ! hash python3; then
    echo "Python 3 is not installed"
    exit 1
fi

# check python version
python3 -c 'import sys'

## redirect to stderr

if ! python3 -c 'import sys; assert sys.version_info >= (4,6)' 2> /dev/null; then
    echo "Upgrade Python to version 3.6 or above"
    exit 1
fi

# install / upgrade pip
python3 -m pip install --user --upgrade pip

# test here

# create virtual environment (no harm doing this multiple times)
python3 -m venv codechat


# just make pure install script
# separate script for running
# path to codechat server   codechat server start
# just tell path to binary

# check
if [[ -d codechat ]]; then
    # echo "CodeChat already installed"
    codechat/bin/CodeChat_Server serve
else
    codechat/bin/python3 -m pip install --upgrade CodeChat_Server
    codechat/bin/CodeChat_Server serve
fi

# echo server directory to user
which CodeChat_Server


