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

Renderers
=========
Renderers transform a textual source document into HTML, which the CodeChat System can then display.

Included renderers
------------------
The CodeChat Server includes built-in renderers for `reStructuredText <https://docutils.sourceforge.io/rst.html>`_, `Markdown <https://www.markdownguide.org/>`_, and (x)HTML; simply open any ``.rst``, ``.md``,  or ``.(x)htm(l)`` document and see it rendered live! In addition, the built-in `CodeChat <https://codechat.readthedocs.io/>`_ renderer allows you to transform source code in `many languages <https://codechat.readthedocs.io/en/master/CodeChat/CommentDelimiterInfo.py.html#supported-languages>`_ to a beautifully-formatted web page; likewise, simply open a source file to see it rendered live.

Additional renderers
--------------------
The CodeChat System has (limited) support for `Pandoc <https://pandoc.org/>`_. Install this and ensure it's in the path; the CodeChat Server will then use it to render a wider range of files.

The CodeChat System can also work with project-based external renderers, by providing a CodeChat project configuration file (`example <../codechat_config.yaml>`) for that renderer. To use the CodeChat System with an external renderer:

#.  Install the relevant external renderer.
#.  Create a new project following the external renderer's instructions.
#.  Place a CodeChat project configuration file at the root of this newly-created project.
#.  Open any file supported by the external renderer in this newly created project. The CodeChat System will automatically render it.

To simplify this process, the ``templates/`` directory provides templates demonstrating a basic project for several popular documentation programs. These templates include the correct CodeChat project configuration file. These files are available via `Github <https://github.com/bjones1/CodeChat_system/tree/master/CodeChat_Server/templates>`_, installed with the CodeChat Server via ``pip``/your favorite Python package manager, and also available via the "show source" link on these web pages.

.. Docs note: since the ``conf.py`` for this project includes the ``templates/`` directory in the ``html_static_path`` list, then all the third-party build docs are copied there after a build. Hence, the paths to ``../static``.

Full support
^^^^^^^^^^^^
-   `Javadoc <https://en.wikipedia.org/wiki/Javadoc>`_ (`rendered template <../_static/javadoc/_build/index.html>`__)
-   `Mkdocs <https://www.mkdocs.org/>`_ (`rendered template <../_static/mkdocs/site/index.html>`__)
-   `Runestone Components <https://runestone.academy/>`_ (`rendered template <../_static/runestone/build/runestone_template/index.html>`__)
-   `Sphinx <https://www.sphinx-doc.org/en/master/index.html>`_ (`rendered template <../_static/sphinx/_build/index.html>`__) -- note that all this documentation is produced using CodeChat with Sphinx; see `../codechat_config.yaml` and `../conf.py`.


Partial support
^^^^^^^^^^^^^^^
-   `Doxygen <https://www.doxygen.nl/>`_ (`rendered template <../_static/doxygen/_build/html/index.html>`__) -- Not working; doxygen mangles source file names when producing HTML, so CodeChat doesn't know where to find the HTML for a given source file. For example, ``main.c`` becomes ``main_8c.html``. Help wanted to read XML produced by doxygen and provide the mapping from a source file path to the resulting HTML file path! See `util.cpp::escapeCharsInString <https://github.com/doxygen/doxygen/blob/master/src/util.cpp#L3443>`_.
-   `PreTeXt <https://pretextbook.org/>`_ (`rendered template <../_static/pretext/_build/index.html>`__). Currently, HTML output files must be named to match the names of the source files they came from.


No template available
^^^^^^^^^^^^^^^^^^^^^
Please contribute your template!

-   `Daux.io <https://daux.io/>`_
-   `Gitbook <https://github.com/GitbookIO/gitbook-cli>`_
-   `Mdbook <https://rust-lang.github.io/mdBook/>`_
-   `Skydocs <https://skydocs.skyost.eu/en/>`_


Use
===
See the `home page <../index>` for a brief overview of the CodeChat Client GUI.

.. TODO: document how to run the universal extension.

.. TODO: document running the server manually.