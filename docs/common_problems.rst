***************
Common problems
***************
If the problem you've encountered isn't listed here, please `open an issue <https://github.com/bjones1/CodeChat_system/issues/new>`_.

Before consulting the errors below:

#.  Update the CodeChat extension/plugin.

#.  Update the CodeChat Server. See the sentence at the end of the `installation instructions <install CodeChat Server>` for your platform.

Updating one **does not** update the other. Both must be using the same version to work correctly.

**Contents**

.. contents::
    :local:

Error communicating with the CodeChat Server
============================================
First, look first at the output in the terminal window.

Server not found
----------------
::

    > Executing the CodeChat Server: C:\Users\xxxx\Documents\git\venv\Scripts\python.exe -m CodeChat_Server <

    Press any key to stop the server.

    > While running the CodeChat Server: Error - cannot find the file C:\Users\bjones\Documents\git\venv\Scripts\pythonx.exe <

    This terminal will be reused by the CodeChat Server; to restart the server, re-run the CodeChat extension.


This error could be caused if:

#.  The CodeChat Server isn't installed. See the `installation instructions <install CodeChat Server>`.

#.  The location of the CodeChat Server provided to the CodeChat IDE/plugin is incorrect. See `instructions for Visual Studio Code <use CodeChat>`.

Another approach: manually run the CodeChat Server from a terminal/command prompt, then restart the CodeChat extension/plugin. If this works, then the two suggestions above should enable you to run the server automatically, instead of manually.

Server exited
-------------
::

    > CodeChat Server exited with signal SIGTERM. <

    This terminal will be reused by the CodeChat Server; to restart the server, re-run the CodeChat extension.

The server exited. Re-run it by restarting the CodeChat extension/plugin.This is usually caused by pressing any key while in the terminal window.