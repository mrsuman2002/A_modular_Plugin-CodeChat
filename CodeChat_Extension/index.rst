Visual Studio Extension  Documentation!
=================================================

..  You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

This is the README for extension "CodeChat". After writing up a brief description, we recommend including the following sections.

Requirements:
-------------
*   Installation of `npm <https://nodejs.org/en/>`_.
*   Installation of `python <https://www.python.org/downloads/>`_.
*   Installation of the extension manifest: `package.json <https://docs.npmjs.com/files/package.json>`_. can  be done by using following command:

    ``npm install``

The structure of an extension:
------------------------------
Here under extension, we have command extension.sayHello so that it runs in extension development host. Also, we have created webview panel so that we can render source code to webview in webviewpanel.

.. code-block:: JavaScript

    const panel = vscode.window.createWebviewPanel('CodeChat', "CodeChat", vscode.ViewColumn.One, { });

We have used Clientfunc to call JavaScriptClient in extension.

.. code-block:: JavaScript
    :linenos:

    var tools = require('../Thrift/JavaScript_Client/Client');
    tools.Clientfunc(panel.webview);

Running your extension
----------------------
* Open a CodeChat_Extention folder from VSCode, Press F5 or click start debugging under debug (Note: If you open A modular_Plugin-CodeChat Folder you might see vscode error saying  "module not found" ).
* A new instance of VS Code will start in a special mode (Extension Development Host) which is Codechat extension.
* Open the project(any source code),Now you press ctrl+shift+p and run the extension. You will be able to see the webview of your active window.
* Enjoy your descriptive mode of your source code.







Contents:

..  toctree::
    :maxdepth: 2

    extension.js
    CodeChat_Extension_Readme.rst
    CHANGELOG


