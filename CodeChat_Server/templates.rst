*********
Templates
*********
The ``templates/`` directory provides templates demonstrating a basic setup for several popular documentation programs. The templates include the correct CodeChat project configuration file. These files are available via `Github <https://github.com/bjones1/CodeChat_system/tree/master/CodeChat_Server/templates>`_ and are also installed with the CodeChat Server via ``pip``/your favorite Python package manager; they're also available via the "show source" link on these web pages.

.. Docs note: since the ``conf.py`` for this project includes the ``templates/`` directory in the ``html_static_path`` list, then all the third-party build docs are copied there after a build. Hence, the paths to ``../static``.

-   `CodeChat with Sphinx <../_static/sphinx/_build/index.html>`_ -- note that all this documentation is produced using CodeChat; see `../codechat_config.yaml` and `../conf.py`.
-   `Javadoc <../_static/javadoc/_build/index.html>`_
-   `Mkdocs <../_static/mkdocs/site/index.html>`_
-   `Runestone <../_static/runestone/build/runestone_template/index.html>`_


Partial support
---------------
-   `Doxygen <../_static/doxygen/_build/html/index.html>`_ -- Not working; doxygen mangles source file names when producing HTML, so CodeChat doesn't know where to find the HTML for a given source file. For example, ``main.c`` becomes ``main_8c.html``. Help wanted to read XML produced by doxygen and provide the mapping from a source file path to the resulting HTML file path! See `util.cpp::escapeCharsInString <https://github.com/doxygen/doxygen/blob/master/src/util.cpp#L3443>`_.
-   `PreTeXt <../_static/pretext/_build/index.html>`_. Currently, HTML output files must be named to match the names of the source files they came from.