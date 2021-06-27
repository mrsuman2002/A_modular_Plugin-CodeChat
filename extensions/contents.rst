.. Copyright (C) 2012-2020 Bryan A. Jones.

    This file is part of the CodeChat System.

    The CodeChat System is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

    The CodeChat System is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more details.

    You should have received a `copy of the GNU General Public License </docs/LICENSE>` along with the CodeChat System.  If not, see http://www.gnu.org/licenses/.

**************************************
CodeChat editor/IDE extensions/plugins
**************************************
This directory contains documentation for all supported text editor/IDE extensions/plugins.

.. toctree::
    :maxdepth: 2

    VSCode_Extension/contents


Developer documentation
=======================
The typical operation of a plugin/extension is:

Initial start-up
----------------
#.  Open an in-editor/in-IDE web browser if possible. Use this to report status and errors during the following steps. Otherwise, fall back to in-editor/IDE notifications.
#.  Use this reporter to tell the user that the CodeChat System is starting.
#.  Run the CodeChat Server. Show output from the server in a terminal window/text box; reveal this if it's hidden. Reasoning:

    -   Make any failures more obvious by showing the terminal window in which the server reports problems, or the subprocess reports a failed run of the binary.
    -   This output should be kept separate from the error notification location, since it would be easy for reported errors to be lost in the voluminous output produced by the server.

#.  Wait a timeout delay for the server to report that it's ready, or for the subprocess to exit.

    -   The server writes a `standard string <CODECHAT_READY>` to stdout to indicate it's ready, making it easy for extensions to determine when it's safe to attempt connection to the server.
    -   If the server is already running, the second server will detect that the ports are in use and exit immediately. This allows extensions to unconditionally run the server at start-up, keeping extension code simpler.

#.  Open a connection to the server. If the connection fails, stop here and report the error.
#.  Invoke ``get_client``; send the returned HTML/URL to the web browser.

Main loop
---------
At this point, the CodeChat System is up and running. Now, the system should:

-   Watch for IDE events, then send render requests to the server.
-   Respond to and report connection errors.
-   Respond to closing of the extension or the CodeChat Client web browser window.


Modules
=======
A typical plugin/extension has these modules:

-   A ``codechat_terminal``: terminal/subprocess hosting the CodeChat Server.
-   A ``thrift_connection``: Thrift network connection to the server, along with a ``thrift_client`` created from that connection.
-   A set of functions/methods to invoke `CodeChat editor/IDE services <editor_services>` along with a ``codechat_client_id`` used to communicate with the CodeChat Client.
-   A web browser (optional; can be an external browser instead) hosting the CodeChat Client.
-   A system to make render requests based on IDE activity (edits, switching windows, etc.)

The extension GUI should allow restarting the server, which should require closing/restarting the Thrift connection and the web browser's contents. Closing the extension should cause all resources to be freed, so that restarting it would then restart the entire system.


Logging
=======
To help track down bugs, each side of a network connection needs to provide logging:

-   The server logs all requests from the IDE, web server activity, and CodeChat Client activity.
-   The CodeChat Client emits ``console.log`` info.
-   Each extension should provide IDE-specific logging capabilities.