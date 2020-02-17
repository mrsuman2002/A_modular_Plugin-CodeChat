*****************************************
The Visual Studio Code CodeChat extension
*****************************************
This extension provide hosts CodeChat's capabilities within the Visual Studio Code editor.

Installation
============
(Eventually) this can be installed from the Visual Studio Code Marketplace. To install from source:

*   Install `npm <https://nodejs.org/en/>`_.
*   Install this extension's manifest (`package.json <https://code.visualstudio.com/api/references/extension-manifest>`_): from this directory, open a command prompt/terminal then execute::

        npm install
        npm install -g typescript
        npm build

Running the extension
=====================
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