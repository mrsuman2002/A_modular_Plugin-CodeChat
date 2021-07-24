*********
Templates
*********
The ``templates/`` directory provide templates demonstrating a basic setup for several popular documentation programs. The templates include the correct CodeChat configuration file.

-   :ref:`CodeChat_root` -- all this documentation is produced using CodeChat; see `../codechat_config.yaml` and `../conf.py`.
-   `Doxygen <../../CodeChat_Server/templates/doxygen/_build/html/index.html>`_ -- Not working; doxygen mangles source file names when producing HTML, so CodeChat doesn't know where to find the HTML for a given source file. For example, ``main.c`` becomes ``main_8c.html``. Help wanted to read XML produced by doxygen and provide the mapping from source file name to resulting HTML file name!
-   `Javadoc <../../CodeChat_Server/templates/javadoc/_build/index.html>`_
-   `Mkdocs  <../../CodeChat_Server/templates/mkdocs/site/index.html>`_
-   `Sphinx <../../CodeChat_Server/templates/sphinx/_build/index.html>`_
