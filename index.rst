Welcome to template's documentation!
====================================
.. digraph:: mydiagram

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


.. This is a comment and I am using it to (for table of content)

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
