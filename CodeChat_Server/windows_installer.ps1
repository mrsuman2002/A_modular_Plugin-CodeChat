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
# code sample::
# 
#   $pythonVersion = python --version
#   if([string]::IsNullOrEmpty($pythonVersion))
#   This is where you put the function to download python. If already installed, the if statement will be skipped and the programmed will continue uninterrupted
# 
# code sample::
# 
#   Get-Item py
#   $Answer = Read-Host -Prompt "You have Python version '$PyVers' Would you like to update your Python version?"

# Make sure pip, the Python installer, is up to date on Windows
py -m pip install --upgrade pip

# Create a virtual enviroment named codechat
py -m venv codechat

# Activate the virtual enviroment
.\codechat\Scripts\activate

# Install the CodeChat Server
py -m pip install --upgrade CodeChat_Server

# Copies path of CodeChat_Server to the clipboard for easy pasting and displays path in terminal
#https://docs.microsoft.com/en-us/powershell/module/microsoft.powershell.management/set-clipboard?view=powershell-7.2
$pathToCodeChat = Get-Command CodeChat_Server | Select-Object -ExpandProperty Definition
Set-Clipboard $pathToCodeChat
echo "Here is your path to CodeChat (Also copied to your clipboard): $pathToCodeChat"


Read-Host -Prompt "Press Enter to exit"

