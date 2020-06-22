.. Copyright (C) 2012-2020 Bryan A. Jones.

    This file is part of the CodeChat system.

    The CodeChat system is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

    The CodeChat system is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more details.

    You should have received a `copy of the GNU General Public License </docs/LICENSE>` along with the CodeChat system.  If not, see http://www.gnu.org/licenses/.

*****************************************
The Visual Studio Code CodeChat extension
*****************************************
This extension provide hosts CodeChat's capabilities within the Visual Studio Code editor.


Installation
============
First, `install the CodeChat extension for Visual Studio Code <https://code.visualstudio.com/docs/introvideos/extend>`_. Then, `install the CodeChat server <../CodeChat_Server/contents>`, which performs all the back-end work and is required for the extension to work. Optionally, install additional external renderers such as Pandoc, Doxygen, etc.


Use
===
#.  `Start  the CodeChat Server <../CodeChat_Server/contents>`_.
#.  Open a file that CodeChat can render (`most source files <https://codechat.readthedocs.io/en/master/CodeChat/CommentDelimiterInfo.py.html#supported-languages>`_, along with .rst, .md, .html files).
#.  Open the `Visual Studio Code command palette <https://code.visualstudio.com/docs/getstarted/userinterface#_command-palette>`_ by pressing ``Ctrl+Shift+P``. Type ``CodeChat``, then press enter to run the extension. After a moment, the rendered file should load.

If you would like to build documentation for an entire project instead of a single file, create a `project configuration file <../codechat_config.json>` then place it in the root directory of your project.

See the `CodeChat tutorial <https://codechat.readthedocs.io/en/master/docs/tutorial.html>`_ for step-by-step instructions on authoring literate programming documents.


From source
===========
To install from source:

*   Install `npm <https://nodejs.org/en/>`_.
*   Install this extension's manifest (`package.json <https://code.visualstudio.com/api/references/extension-manifest>`_): from this directory, open a command prompt/terminal then execute::

        npm install
        npm install -g typescript
        npm build

Debugging the extension
-----------------------
*   Open this folder from VSCode, then press F5 or click start debugging under the Debug menu.
*   A new instance of VSCode will start in a special mode (Extension Development Host) which contains the CodeChat extension.
*   Open any source code, then press Ctrl+Shift+P and type "CodeChat" to run the CodeChat extension. You will be able to see the rendered version of your active window.


Notes
=====
*   The NPM Thrift 0.13.0 release is `broken <https://github.com/apache/thrift/pull/1947>`_. Don't install it.
*   You can also reload (``Ctrl+R`` or ``Cmd+R`` on Mac) the VS Code window with your extension to load your changes.
*   You can open the full set of our API when you open the file ``node_modules/vscode/vscode.d.ts``.

Tests
-----
TODO: tests are missing.

*   Open the debug viewlet (``Ctrl+Shift+D`` or ``Cmd+Shift+D`` on Mac) and from the launch configuration dropdown pick ``Launch Tests``.
*   Press ``F5`` to run the tests in a new window with your extension loaded.
*   See the output of the test result in the debug console.
*   Make changes to ``test/extension.test.js`` or create new test files inside the ``test`` folder.

    *   By convention, the test runner will only consider files matching the name pattern ``**.test.js``.
    *   You can create folders inside the ``test`` folder to structure your tests any way you want.


Contents
========
.. toctree::

    src/extension.ts
    README