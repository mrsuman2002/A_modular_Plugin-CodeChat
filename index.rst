Welcome to template's documentation!
====================================
.. digraph:: mydiagram

   "\nCodehat Plugin for VS Code \n \n"[shape=rectangle]

   "\n\nThrift\n\n" [shape=circle]
   "\nCodehat Plugin for VS Code \n \n" -> "\n\nThrift\n\n" [ label="Consists"];

   "CodeChat\n Extension" [shape=circle]
   "\nCodehat Plugin for VS Code \n \n" -> "CodeChat\n Extension" [label="Consists"];

   "\n Python\n Server \n" [shape=circle]
   "\n\nThrift\n\n"  -> "\n Python\n Server \n" [label="Consists"];

   "\n Python\n Server \n"  -> "JavaScript\nClient" [label="Consists"];

   "JavaScript\nClient" [shape=circle]
   "\n\nThrift\n\n"  -> "JavaScript\nClient" [label="Consists"];
   "JavaScript\nClient" -> "CodeChat\n Extension" [label="Talks to"];

   "CodeChat\nLibrary" [shape=square]
   "CodeChat\nLibrary" -> "\n Python\n Server \n" [label="Consists"];

   "Webview" [shape=circle]
   "CodeChat\n Extension" -> "Webview" [label="Generates"];



.. This is a comment and I am using it to (for table of content)

Contents:

.. toctree::
    :maxdepth: 2

    Readme.rst
    CodeChat_Extension/index.rst
    Thrift/Thrift_Readme.rst
    conf.py



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
