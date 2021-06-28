********************
Installation and use
********************

.. contents:: Table of Contents
    :local:
    :depth: 2


To install the CodeChat System, install the CodeChat Server and a CodeChat extension or plugin, along with optional external renders you desire.

.. _install CodeChat Server:

CodeChat Server Installation
============================
To install the CodeChat Server:

Windows
-------
#.  Install Python. There are two options:

    #.  Install it from the `Windows Store <https://www.microsoft.com/store/productId/9P7QFQMJRFP7>`_.
    #.  Install Python from the web; check the "Add Python 3.x to PATH" box during the installation by following `these instructions <https://datatofish.com/add-python-to-windows-path/>`_.

#.  Open a `Command Prompt <https://www.howtogeek.com/235101/10-ways-to-open-the-command-prompt-in-windows-10/>`_.

#.  Make sure pip, the Python installer, is `up to date on Windows <https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/#windows>`_: at the command prompt, type ``py -m pip install --upgrade pip``.

#.  `Create a virtual environment <https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/#creating-a-virtual-environment>`_ named *codechat* by typing ``py -m venv codechat``. This keeps the installation of the CodeChat System from interfering with other installed Python programs and vice versa.

#.  `Activate this virtual environment <https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/#activating-a-virtual-environment>`_ by typing ``.\codechat\Scripts\activate``.

#.  Install the CodeChat Server by typing ``py -m pip install --upgrade CodeChat_Server``.

#.  Determine the location of the installed CodeChat Server by typing ``where CodeChat_Server``. You'll need to enter this path when setting up the CodeChat plugin/extension in your IDE.

#.  Install the `CodeChat extension/plugin <../extensions/contents>`_ for your IDE or text editor.

To update the CodeChat Server, repeat steps 2, 5, and 6.

Linux
-----
#.  `Open a terminal <https://www.howtogeek.com/howto/22283/four-ways-to-get-instant-access-to-a-terminal-in-linux/>`__.

#.  Make sure pip, the Python installer, is `up to date <https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/#linux-and-macos>`_: at the terminal, type ``python3 -m pip install --user --upgrade pip``.

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

#.  Make sure pip, the Python installer, is `up to date`_: at the terminal, type ``python3 -m pip install --user --upgrade pip``.

#.  `Create a virtual environment`_ named *codechat* by typing ``python3 -m venv codechat``. This keeps the installation of the CodeChat System from interfering with other installed Python programs and vice versa.

#.  `Activate this virtual environment`_ by typing ``source codechat/bin/activate``.

#.  Install the CodeChat Server by typing ``python3 -m pip install --upgrade CodeChat_Server``.

#.  Determine the location of the installed CodeChat Server by typing ``which CodeChat_Server``. You'll need to enter this path when setting up the CodeChat plugin/extension in your IDE.

#.  Install the `CodeChat extension/plugin <../extensions/contents>`_ for your IDE or text editor.

To update the CodeChat Server, repeat steps 1, 5, and 6.


CodeChat extension/plugin installation
======================================
Install a `CodeChat plugin or extension <../extensions/contents>` to use the CodeChat System (the final step of the installation steps above).

Optional installs
-----------------
Optionally, install additional external renderers such as:

-   `Daux.io <https://daux.io/>`_
-   `Doxygen <https://www.doxygen.nl/>`_
-   `Gitbook <https://github.com/GitbookIO/gitbook-cli>`_
-   `Javadoc <https://en.wikipedia.org/wiki/Javadoc>`_
-   `Mdbook <https://rust-lang.github.io/mdBook/>`_
-   `Mkdocs <https://www.mkdocs.org/>`_
-   `Pandoc <https://pandoc.org/>`_
-   `Runestone Components <https://runestone.academy/>`_
-   `Skydocs <https://skydocs.skyost.eu/en/>`_
-   `Sphinx <https://www.sphinx-doc.org/en/master/>`_ (CodeChat `template <templates/sphinx/index.html>`_)

CodeChat Server configuration file
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The linked templates above include the correct CodeChat Server configuration file along with the files needed by that external renderer to create a basic project. The `configuration file for this project <../codechat_config.yaml>` documents the format of this file and provides a working example.


Use
===

CodeChat Client
---------------
See the `home page <../index>` for a brief overview of the CodeChat Client GUI.

Included renderers
------------------
The CodeChat Server includes built-in renderers for `reStructuredText <https://docutils.sourceforge.io/rst.html>`_, `Markdown <https://www.markdownguide.org/>`_, and (x)HTML; simply open any ``.rst``, ``.md``,  or ``.(x)htm(l)`` document and see it rendered live! In addition, the built-in `CodeChat <https://codechat.readthedocs.io/>`_ renderer allows you to transform source code in `many languages <https://codechat.readthedocs.io/en/master/CodeChat/CommentDelimiterInfo.py.html#supported-languages>`_ to a beautifully-formatted web page.

External renderers
------------------
To use an external renderer, such as those listed `above <optional installs>`_, provide a `CodeChat Server configuration file`_.

.. TODO: Provide example files for the renderers above, plus a script to build all docs (run Sphinx, run builders on all templates, copy the output files to a single HTML location). I need a way to upload these to readthedocs -- perhaps a github branch that is force-pushed with each docs build, then rtd pulls from? Dropbox? Some other way to push the built HTML?

.. TODO: document how to run the universal extension.

.. TODO: document running the server manually.