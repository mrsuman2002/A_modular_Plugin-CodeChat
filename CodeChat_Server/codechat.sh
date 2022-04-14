#!/bin/bash
# install CodeChat

# Run (without the pound or dollar signs):

# wget https://raw.githubusercontent.com/JoeKenn1118/CodeChat_system/master/CodeChat_Server/codechat.sh
# bash codechat.sh

if ! hash python3; then
    echo "Python 3 is not installed"
    exit 1
fi


# todo: check python version
python3 -c 'import sys; print(sys.version_info[:])'

# install / upgrade pip
python3 -m pip install --user --upgrade pip

# create virtual environment (no harm doing this multiple times)
python3 -m venv codechat


if [[ -d codechat ]]; then
    echo "CodeChat already installed"
else
    python3 -m pip install --upgrade CodeChat_Server
fi

# echo server directory to user
which CodeChat_Server


