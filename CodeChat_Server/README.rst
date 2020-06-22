.. Copyright (C) 2012-2020 Bryan A. Jones.

    This file is part of the CodeChat system.

    The CodeChat system is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

    The CodeChat system is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more details.

    You should have received a `copy of the GNU General Public License </docs/LICENSE>` along with the CodeChat system.  If not, see http://www.gnu.org/licenses/.

The CodeChat System
===================
The CodeChat system provides a powerful literate programming authoring system to a variety of text editors and IDEs. Specifically, it provides a GUI to automatically render source code and/or markup documents to HTML, displaying the HTML document produced by the rendering process next to the source. For example:

.. figure:: docs/CodeChat_screenshot_annotated.png

    This screenshot shows the Visual Studio Code editor with the CodeChat extension.

In ❶, the left panel shows a the Visual Studio Code text editor with Python source code. CodeChat renders this source code to ❷, the right panel, which shows the resulting HTML document. Finally, ❸ displays output from the build process. A splitter between ❷ and ❸ allows the user to adjust the build output size or hide it entirely. Below ❸, a status bar displays the build status and a count of errors and warnings produced by the build.

In addition to native support for Markdown and reStructuredText, the CodeChat system supports almost any external renderer via user-provided JSON configuration files. For example, CodeChat can:

-   invoke `Pandoc <https://pandoc.org/>`_ to render a wide variety of markup formats;
-   use `Sphinx <https://www.sphinx-doc.org/>`_ to build project documentation;
-   call `Runestone <https://runestone.academy/>`_ to create interactive textbooks;
-   employ `Doxygen <https://www.doxygen.nl/>`_ to generate documentation from source code;

... and many more. See the `CodeChat server documentation <https://CodeChat_system.readthedocs.io/en/master/docs/CodeChat_Server/contents.html>`_ to get started.