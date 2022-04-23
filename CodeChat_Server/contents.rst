.. Copyright (C) 2012-2022 Bryan A. Jones.

    This file is part of the CodeChat System.

    The CodeChat System is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

    The CodeChat System is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more details.

    You should have received a `copy of the GNU General Public License <LICENSE>` along with the CodeChat System.  If not, see http://www.gnu.org/licenses/.

*******************
The CodeChat Server
*******************
The CodeChat Server receives requests from CodeChat plugins/extensions running in text editors/IDEs to render a file, performs the render, then displays it in the CodeChat Client. It also responds to user input from the CodeChat Client by processing this request then sending the results back to the plugin/extension.


User documentation
==================
.. toctree::
    :maxdepth: 2

    README
    install
    cli
    security


Developer docs
==============
See also the `developer docs <developer>`.

.. toctree::
    :hidden:

    developer