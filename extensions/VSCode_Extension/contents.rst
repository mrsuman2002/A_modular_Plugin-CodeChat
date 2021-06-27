.. Copyright (C) 2012-2020 Bryan A. Jones.

    This file is part of the CodeChat System.

    The CodeChat System is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

    The CodeChat System is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more details.

    You should have received a `copy of the GNU General Public License </docs/LICENSE>` along with the CodeChat System.  If not, see http://www.gnu.org/licenses/.

*****************************************
The Visual Studio Code CodeChat extension
*****************************************
This extension provides CodeChat's capabilities within the Visual Studio Code editor, as illustrated in `the CodeChat System for Visual Studio Code <README>` page.


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

    README
    install
    src/extension.ts
