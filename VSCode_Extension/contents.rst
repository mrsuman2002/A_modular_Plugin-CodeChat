.. Copyright (C) 2012-2020 Bryan A. Jones.

    This file is part of the CodeChat system.

    The CodeChat system is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

    The CodeChat system is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more details.

    You should have received a `copy of the GNU General Public License </docs/LICENSE>` along with the CodeChat system.  If not, see http://www.gnu.org/licenses/.

*****************************************
The Visual Studio Code CodeChat extension
*****************************************
This extension provides CodeChat's capabilities within the Visual Studio Code editor, as illustrated in `the CodeChat system for Visual Studio Code <README>` page.


Installation
============
First, install `Visual Studio Code <https://code.visualstudio.com/>`_ then install the `CodeChat extension for Visual Studio code <https://marketplace.visualstudio.com/items?itemName=CodeChat.codechat>`_. Next:

#.  `Install the CodeChat Server <../CodeChat_Server/contents>`, which performs all the back-end work and is required for the extension to work. Optionally, install additional external renderers such as Pandoc, Doxygen, etc.
#.  `Switch to a light theme <https://code.visualstudio.com/docs/getstarted/themes>`_ -- unfortunately, Visual Studio's dark theme isn't supported by the CodeChat system.


.. _use CodeChat:

Use
===
#.  Open a file that CodeChat can render (`most source files <https://codechat.readthedocs.io/en/master/CodeChat/CommentDelimiterInfo.py.html#supported-languages>`_, along with ``.rst``, ``.md``, and ``.html`` files).
#.  Open the `Visual Studio Code command palette <https://code.visualstudio.com/docs/getstarted/userinterface#_command-palette>`_ by pressing ``Ctrl+Shift+P``. Type ``CodeChat``, then press enter to run the extension. After a moment, the rendered file should load. If it doesn't:

    #.  Determine the location of the ``CodeChat_Server`` by entering ``which CodeChat_Server`` (Linux/OS X) or ``where CodeChat_Server`` (Windows) at the terminal/command line.
    #.  Open the Visual Studio Code settings for CodeChat by navigating to ``File`` > ``Preferences`` > ``Settings`` then typing ``CodeChat`` in the search box. Enter this path for the ``Code Chat.Code Chat Server: Command``. **Important**: in Windows, replace ``\`` in the location you determined with either ``\\`` or ``/``.
    #.  Run the extension again (``Ctrl+Shift+P`` then select CodeChat).

At any time, run the CodeChat extension again (``Ctrl+Shift+P``, then ``CodeChat``) to show the CodeChat panel, re-start the CodeChat server if it's not running, then reconnect with the server. Close the CodeChat panel then run the extension for a more complete reset.

The CodeChat Server runs in an `integrated terminal <https://code.visualstudio.com/docs/editor/integrated-terminal>`_. You may hide this window (the X button at the top right of the pane) if you wish. To stop the server, either press any key in the terminal or click the trash can icon near the top right of the pane; re-run the CodeChat extension to restart it.

See the `CodeChat tutorial <https://codechat.readthedocs.io/en/master/docs/tutorial.html>`_ for step-by-step instructions on authoring literate programming documents using Sphinx. For other documentation systems, create a `project configuration file <../codechat_config.json>` then place it in the root directory of your project.


From source
===========
To install from source:

*   Install `npm <https://nodejs.org/en/>`_.
*   Install this extension's manifest (`package.json <https://code.visualstudio.com/api/references/extension-manifest>`_): from this directory, open a command prompt/terminal then execute::

        npm install
        npm build

Debugging the extension
-----------------------
*   Open this folder from VSCode, then press F5 or click start debugging under the Debug menu.
*   A new instance of VSCode will start in a special mode (Extension Development Host) which contains the CodeChat extension.
*   Open any source code, then press Ctrl+Shift+P and type "CodeChat" to run the CodeChat extension. You will be able to see the rendered version of your active window.


Notes
=====
*   The NPM Thrift 0.13.0 release is `broken <https://github.com/apache/thrift/pull/1947>`_. Don't install it.

Tests
-----
TODO: tests are missing.


Contents
========
.. toctree::
    :maxdepth: 2

    src/extension.ts
    README