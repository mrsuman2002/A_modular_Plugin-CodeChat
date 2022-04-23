***********************
Developer documentation
***********************

Release procedures
==================
Each extension has a unique publish procedure. See each extension/plugin's developer docs.

-   `Visual studio code <VSCode/developer>`
-   `IntelliJ <IntelliJ/developer>`


Typical operation
=================
The typical operation of a plugin/extension is:

Initial start-up
----------------
#.  Open an in-editor/in-IDE web browser if possible. Use this to report status and errors during the following steps. Otherwise, fall back to in-editor/IDE notifications.
#.  Use this reporter to tell the user that the CodeChat System is starting.
#.  Run the CodeChat Server with the ``start`` subcommand and wait for it to finish. If the return was 0, the server is running. Otherwise, a non-zero return value indicates an error; stop here, reporting stdout and stderr to the user.
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