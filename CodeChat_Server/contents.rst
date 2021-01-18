.. Copyright (C) 2012-2020 Bryan A. Jones.

    This file is part of the CodeChat system.

    The CodeChat system is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

    The CodeChat system is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more details.

    You should have received a `copy of the GNU General Public License <LICENSE>` along with the CodeChat system.  If not, see http://www.gnu.org/licenses/.

*******************
The CodeChat server
*******************
The CodeChat server receives requests from CodeChat plugins/extensions running in text editors/IDEs to render a file, performs the render, then displays it in the CodeChat client. It also responds to user input from the CodeChat client by processing this request then sending the results back to the plugin/extension.


Installation
============
To install the CodeChat server:

#.  `Install a recent version of Python <https://www.python.org/downloads/>`_.
#.  From a terminal or command line, execute ``python -m pip install -U CodeChat_Server`` or ``python3 -m pip install -U CodeChat_Server``, depending on your OS.
#.  Determine the location of the ``CodeChat_Server`` by entering ``where CodeChat_Server`` (Linux/OS X) or ``which CodeChat_Server`` (Windows) at the terminal/command line.
#.  Enter this path into your text editor/IDE's CodeChat configuration as the CodeChat server path.


Use
===
Install a `CodeChat plugin or extension <../VSCode_Extension/contents>` to use the CodeChat system.


Server architecture
===================
TODO.


Contents
========
.. toctree::
    :maxdepth: 2

    README
    CodeChat_Server/__init__.py
    setup.py
    pre_commit_check.py
    ci_utils/ci_utils.py
    mypy.ini
    .flake8
    pyproject.toml
