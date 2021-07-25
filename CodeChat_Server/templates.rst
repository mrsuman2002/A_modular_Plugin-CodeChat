*********
Templates
*********
The ``templates/`` directory provide templates demonstrating a basic setup for several popular documentation programs. The templates include the correct CodeChat configuration file. These files are available via `Github <https://github.com/bjones1/CodeChat_system/tree/master/CodeChat_Server/templates>`_ and are also installed with the CodeChat Server via ``pip``/your favorite Python package manager; they're also available via the "show source" link on these web pages.

-   `CodeChat with Sphinx <../_static/sphinx/_build/index.html>`_ -- note that all this documentation is produced using CodeChat; see `../codechat_config.yaml` and `../conf.py`.
-   `Javadoc <../_static/javadoc/_build/index.html>`_
-   `Pretext <../_static/pretext/_build/index.html>`_
-   `Mkdocs <../_static/mkdocs/site/index.html>`_
-   `Runestone <../_static/runestone/build/runestone_template/index.html>`_


Partial support
---------------
-   `Doxygen <../_static/doxygen/_build/html/index.html>`_ -- Not working; doxygen mangles source file names when producing HTML, so CodeChat doesn't know where to find the HTML for a given source file. For example, ``main.c`` becomes ``main_8c.html``. Help wanted to read XML produced by doxygen and provide the mapping from source file name to resulting HTML file name! See `util.cpp::escapeCharsInString <https://github.com/doxygen/doxygen/blob/master/src/util.cpp#L3443>`_.
