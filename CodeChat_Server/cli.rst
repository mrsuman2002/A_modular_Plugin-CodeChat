**************************
The command-line interface
**************************
The CodeChat Server provides a series of subcommands:


``CodeChat_Server start``
=========================

Run this command to start the CodeChat Server; if the server is already running, no action is taken. This also checks to see if the server has crashed, stopping then starting it if necessary.


``CodeChat_Server stop``
========================
Run this command to stop the CodeChat Server.


``CodeChat_Server serve``
=========================
This command runs the server in the current terminal/command prompt, displaying logging info as the server runs. Press Ctrl-C to stop the server.


``CodeChat_Server build <PATH_TO_BUILD...>``
============================================
This command builds one or more files, then exits. CodeChat projects are saved to disk, then non-project files are sent to ``stdout``.


.. _CodeChat_Server-watch:

``CodeChat_Server watch --paths PATH --patterns PATTERNS --ignore-patterns IGNORE_PATTERNS``
==============================================================================================
Watch the specified path(s) for a changed file; only files which match the provided pattern and aren't in the list of ignored patterns are monitored. When a file changes, the CodeChat Server renders the changed file.

The mode allows easy use of the CodeChat System with almost any editor.


.. _CodeChat_Server-render:

``CodeChat_Server render <PATH_TO_BUILD> <ID>``
===============================================
Render the specified file to a web browser; each unique ID renders to a unique web browser window.

This mode allows any editor/IDE with the ability to execute a program to render a file.