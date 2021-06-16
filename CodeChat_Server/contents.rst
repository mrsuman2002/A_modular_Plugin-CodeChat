.. Copyright (C) 2012-2020 Bryan A. Jones.

    This file is part of the CodeChat system.

    The CodeChat system is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

    The CodeChat system is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more details.

    You should have received a `copy of the GNU General Public License <LICENSE>` along with the CodeChat system.  If not, see http://www.gnu.org/licenses/.

*******************
The CodeChat Server
*******************
The CodeChat Server receives requests from CodeChat plugins/extensions running in text editors/IDEs to render a file, performs the render, then displays it in the CodeChat Client. It also responds to user input from the CodeChat Client by processing this request then sending the results back to the plugin/extension.


.. _install CodeChat Server:

Installation
============
To install the CodeChat Server:

Windows
-------
#.  Install Python. There are two options:

    #.  Install it from the `Windows Store <https://www.microsoft.com/store/productId/9P7QFQMJRFP7>`_.
    #.  Install Python from the web; check the "Add Python 3.x to PATH" box during the installation by following `these instructions <https://datatofish.com/add-python-to-windows-path/>`_.

#.  Open a `Command Prompt <https://www.howtogeek.com/235101/10-ways-to-open-the-command-prompt-in-windows-10/>`_.

#.  Make sure pip, the Python installer, is `up to date on Windows <https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/#windows>`_. At the command prompt, type ``py -m pip install --upgrade pip``.

#.  `Create a virtual environment <https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/#creating-a-virtual-environment>`_ named *codechat* by typing ``py -m venv codechat``. This keeps the installation of the CodeChat System from interfering with other installed Python programs and vice versa.

#.  `Activate this virtual environment <https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/#activating-a-virtual-environment>`_ by typing ``.\codechat\Scripts\activate``.

#.  Install the CodeChat Server by typing ``py -m pip install --upgrade CodeChat_Server``.

#.  Determine the location of the installed CodeChat Server by typing ``where CodeChat_Server``. You'll need to enter this path when setting up the CodeChat plugin/extension in your IDE.

#.  Install the `CodeChat extension/plugin <../extensions/contents>`_ for your IDE or text editor.

To update the CodeChat Server, repeat steps 2, 5, and 6.

Linux
-----
#.  `Open a terminal <https://www.howtogeek.com/howto/22283/four-ways-to-get-instant-access-to-a-terminal-in-linux/>`__.

#.  Make sure pip, the Python installer, is `up to date <https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/#linux-and-macos>`_. At the terminal, type ``python3 -m pip install --user --upgrade pip``.

#.  `Create a virtual environment`_ named *codechat* by typing ``python3 -m venv codechat``. This keeps the installation of the CodeChat System from interfering with other installed Python programs and vice versa.

#.  `Activate this virtual environment`_ by typing ``source codechat/bin/activate``.

#.  Install the CodeChat Server by typing ``python3 -m pip install --upgrade CodeChat_Server``.

#.  Determine the location of the installed CodeChat Server by typing ``which CodeChat_Server``. You'll need to enter this path when setting up the CodeChat plugin/extension in your IDE.

#.  Install the `CodeChat extension/plugin <../extensions/contents>`_ for your IDE or text editor.

To update the CodeChat Server, repeat steps 1, 4, and 5.

Mac
---
#.  `Open a terminal <https://support.apple.com/guide/terminal/open-or-quit-terminal-apd5265185d-f365-44cb-8b09-71a064a42125/mac>`__.

#.  `Install modern Python <https://opensource.com/article/19/5/python-3-default-mac>`_.

#.  Make sure pip, the Python installer, is `up to date`_. At the terminal, type ``python3 -m pip install --user --upgrade pip``.

#.  `Create a virtual environment`_ named *codechat* by typing ``python3 -m venv codechat``. This keeps the installation of the CodeChat System from interfering with other installed Python programs and vice versa.

#.  `Activate this virtual environment`_ by typing ``source codechat/bin/activate``.

#.  Install the CodeChat Server by typing ``python3 -m pip install --upgrade CodeChat_Server``.

#.  Determine the location of the installed CodeChat Server by typing ``which CodeChat_Server``. You'll need to enter this path when setting up the CodeChat plugin/extension in your IDE.

#.  Install the `CodeChat extension/plugin <../extensions/contents>`_ for your IDE or text editor.

To update the CodeChat Server, repeat steps 1, 5, and 6.


Use
===
Install a `CodeChat plugin or extension <../extensions/contents>` to use the CodeChat system (the final step of the installation steps above).


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
    tests/contents
