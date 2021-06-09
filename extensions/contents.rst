.. Copyright (C) 2012-2020 Bryan A. Jones.

    This file is part of the CodeChat system.

    The CodeChat system is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

    The CodeChat system is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more details.

    You should have received a `copy of the GNU General Public License </docs/LICENSE>` along with the CodeChat system.  If not, see http://www.gnu.org/licenses/.

**************************************
CodeChat editor/IDE extensions/plugins
**************************************
This directory contains text editor/IDE extensions/plugins.

.. toctree::
    :maxdepth: 2

    VSCode_Extension/contents

Sequence of events
==================
The typical operation of a plugin/extension is:

Initial start-up
----------------
#.  Open an in-editor/in-IDE web browser if possible. Use this to report errors during the following steps. Otherwise, fall back to in-editor/IDE notifications.
#.  Use this to tell the user that the CodeChat system is starting.
#.  Run the CodeChat server. Show output from the server in a terminal window/text box; reveal this if it's hidden. Reasoning:

    -   Make any failures more obvious by showing the terminal window in which the server reports problems, or the subprocess reports a failed run of the binary.
    -   This output should be kept separate from the error notification location, since it would be easy for reported errors to be lost in the voluminous output produced by the server.

#.  Wait a timeout delay for the server to report that it's ready, or for the subprocess to exit. (If the server is already running, the second server will detect that the ports are in use and exit immediately.)
#.  Open a connection to the server. If the connection fails, stop here and report the error.
#.  Invoke ``get_client``; send the returned HTML/URL to the web browser.

Main loop
---------
At this point, the CodeChat system is up and running. Now, the system should:

-   Watch for IDE events, then send render requests to the server.
-   Respond to and report connection errors.
-   Continue to monitor the server, preferably in a webserver window.
-   Respond to closing of the extension or web browser window.


Modules
=======
A typical plugin/extension has these modules:

-   A terminal/subprocess for the server.
-   A Thrift network connection to the server.
-   A system to make render requests based on IDE activity (edits, switching windows, etc.)
-   A web browser (optional; can be an external browser instead) hosting the CodeChat client.

The extension GUI should allow restarting the server, which should require closing/restarting the Thrift connection and the web browser's contents. Closing the extension should cause all resources to be freed, so that restarting it would then restart the entire system.

Logging
=======
To help track down bugs, each side of a network connection needs to provide logging:

-   The server logs all requests from the IDE, web server activity, and CodeChat client activity.
-   The CodeChat client emits ``console.log`` info.
-   Each extension should provide IDE-specific logging capabilities.