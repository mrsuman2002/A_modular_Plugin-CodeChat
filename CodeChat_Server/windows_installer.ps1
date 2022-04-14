# Used to allow powershell to run scripts, may be rendered unnecessary in future if workaround is found
# https://docs.microsoft.com/en-us/powershell/module/microsoft.powershell.security/set-executionpolicy?view=powershell-7.2#syntax
# User will need to manually select yes to allow this action to run
set-executionpolicy remotesigned
# 
# 
# URGENT: Need to add python installer
# Could probably use if statement to check if python is installed. If not, then install
# https://lazyadmin.nl/powershell/download-file-powershell/
# Issues: Need to let user decide file storage location and allow access to said location
# 
# Below is the start of the if statement as explained above
# May be simpler to allow the user to install python manually if file allocation is excessively difficult
# https://adamtheautomator.com/powershell-if-else/#:~:text=1%20The%20if%20statement%20contains%20the%20first%20test,if%20all%20the%20prior%20conditions%20tested%20are%20false.
# 
# 
# Automatically moves Powershell to the user directory, works better when using powershell as an admin
cd $env:USERPROFILE

$pythonVersion = python --version
$pythonVersionReq = #whatever this needs to be
if([string]::IsNullOrEmpty($pythonVersion)){
    $response = Read-Host -Prompt "You do not have Python installed, would you like to install the required version ($pythonVersion) (y/n)?"
    if($response == "y"){
        # echo "Installing Python Version ($pythonVersionReq)"
        # install Python using Invoke-WebRequest?
        echo "Not Implemented yet, please install python version $pythonVersionReq or later"
    }
    [else{
        echo "Please install the required version of python: $pythonVersionReq"
        exit
    }]
}
[elseif ($pythonVersion != $pythonVersionReq){
    $response = Read-Host -Prompt "You have Python version ($pythonVersion) installed, would you like to install the required version ($pythonVersion) (y/n)?"
    if($response == "y"){
        # echo "Installing Python Version ($pythonVersionReq)"
        # install Python
        echo "Not Implemented yet, please install python version $pythonVersionReq or later"
    }
    [else{
        echo "Please install the required version of python: $pythonVersionReq"
        exit
    }]
}]


# 
# code sample::
# 
#   Get-Item py
#   $Answer = Read-Host -Prompt "You have Python version '$PyVers' Would you like to update your Python version?"

# Make sure pip, the Python installer, is up to date on Windows
echo "Upgrading pip..."
py -m pip install --upgrade pip
echo "Upgrade Sucessful"

echo "Creating codechat venv..."
Get-Item codechat
if([string]::IsNullOrEmpty($pythonVersion)){
    # Create a virtual enviroment named codechat
    py -m venv codechat
    echo "Virtual Enviroment Created Sucessfully"
}
[else{
    echo "codechat virtual enviroment already found skipping this step"
}]

echo "Activating Virutal enviroment"
# Activate the virtual enviroment
.\codechat\Scripts\activate
echo "Virtual Enviroment Activated"

# find CodeChat_Server.exe and tell user if just updating or installing
Get-Command CodeChat_Server

if([string]::IsNullOrEmpty($pythonVersion)){
    # Install the CodeChat Server
    echo "installing CodeChat_Server"
    py -m pip install --upgrade CodeChat_Server
    echo "codechat Server Sucessfully Installed"
}
[else{
    echo "CodeChat_Server found, running update"
    py -m pip install --upgrade CodeChat_Server
    echo "CodeChat_Server sucessfully updated"
}]


# `Set-Clipboard <https://docs.microsoft.com/en-us/powershell/module/microsoft.powershell.management/set-clipboard?view=powershell-7.2>`_: Copies path of CodeChat_Server to the clipboard for easy pasting and displays path in terminal
$pathToCodeChat = Get-Command CodeChat_Server | Select-Object -ExpandProperty Definition
Set-Clipboard $pathToCodeChat
echo "Here is your path to CodeChat (Also copied to your clipboard): $pathToCodeChat"


Read-Host -Prompt "Press Enter to exit"

