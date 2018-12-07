Welcome to CodeChat Plugin Documentation!
==========================================

The CodeChat plugin transforms source code into a web page, allowing software developers to view their source code as a beautiful and descriptive document by adding headings, formatting, hyperlinks, images, and diagrams. However, this plugin requires use of a little-known text editor, Enki. To broaden its impact, this project presents the creation of a modular plug-in architecture for CodeChat, enabling its use with a Visual Studio Code.


.. digraph:: mydiagram

    bgcolor="transparent"

    CodeChat_plugin [label="\nCodehat Plugin for VS Code \n \n",shape=rectangle]

    Thrift [label="\n\nThrift\n\n", shape=circle]
    CodeChat_plugin -> Thrift [ label="Consists"];

    CodeChat_Extention [label="CodeChat\n Extension", shape=circle]
    CodeChat_plugin -> CodeChat_Extention [label="Consists"];

    PythonServer [label ="\n Python\n Server \n", shape=circle]
    Thrift  -> PythonServer  [label="Consists"];

    JavaScriptClient [label ="JavaScript\nClient", shape=circle]
    PythonServer   -> JavaScriptClient [label="Consists"];

    Thrift -> JavaScriptClient [label="Consists"];
    JavaScriptClient -> CodeChat_Extention [label="Talks to"];

    CodeChatLibrary [label= "CodeChat\nLibrary", shape=square]
    CodeChatLibrary -> PythonServer  [label="Consists"];

    Webview [label="Webview", shape=circle]
    CodeChat_Extention -> Webview [label="Generates"];

This approach bridges the services CodeChat provides, which are provided in the Python programming language, to the variety of programming languages which various text editors require. To accomplish this, this project (1) employs Apache Thrift, which provides scalable cross-language service development; (2) develops a CodeChat server to provide the needed services; and (3) creates a JavaScript plugin client for Visual Studio Code, a free and popular crossplatform text editor.

Contents:

.. toctree::
    :maxdepth: 2

    Readme.rst
    CodeChat_Extension/index.rst
    Thrift/Thrift_Readme.rst
    conf.py
    .gitignore





Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
