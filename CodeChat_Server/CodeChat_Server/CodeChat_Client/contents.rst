.. Copyright (C) 2012-2022 Bryan A. Jones.

    This file is part of the CodeChat System.

    The CodeChat System is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

    The CodeChat System is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more details.

    You should have received a `copy of the GNU General Public License <LICENSE>` along with the CodeChat System.  If not, see http://www.gnu.org/licenses/.

*******************
The CodeChat Client
*******************
One major goal of the CodeChat System is to provide as much functionality outside the IDE/editor host as possible. The CodeChat Client therefore uses JavaScript as a platform-neutral method of doing most of the work of displaying the rendered results and enabling the user to interact with those results. Specifically, the client:

-   Provides panes to display rendered output, errors, and build status.
-   Parses warnings/errors and provide (currently useless) links to them.
-   Provides a simple build status progress bar.


Sync notes
===========
Use the ``_jsPreviewSync`` in ``preview_sync.py`` for some of the JavaScript code. Currently, ``window_onClick`` returns the index of the beginning of the selection. It would be nice to also return the index of the end of the selection. In addition, it should return the value produced by calling ``selectionAnchorCoords``. Finally, this function should call the Thrift ``sync_to`` function with this data.


Contents
========
.. toctree::
    :maxdepth: 2

    templates/CodeChat_client.html
    templates/insecure.html
    static/CodeChat_client.js
    static/CodeChat_client.css
    static/ReconnectingWebsocket.js