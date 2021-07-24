.. Copyright (C) 2012-2020 Bryan A. Jones.

    This file is part of the CodeChat System.

    The CodeChat System is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

    The CodeChat System is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more details.

    You should have received a `copy of the GNU General Public License </docs/LICENSE>` along with the CodeChat System.  If not, see http://www.gnu.org/licenses/.

**********
Change Log
**********
-   `Github master <https://github.com/bjones1/CodeChat_system.git>`_:

    -   Upgraded to Thrift v. 14.2.
    -   Added the file change watcher client.
    -   Added the CLI render client.
    -   Added a Sphinx template.
    -   Add code coverage support.
    -   Changed Markdown support to a more standard subset.
    -   Corrected command-line parsing in CodeChat project files.
    -   Added a number of CLI subcommands.
    -   Added the ping service.
    -   Replaced the shutdown service with auto-shutdown.

-   0.0.22, 16-Jun-2021:

    -   Enforce a light theme.
    -   Print server version on startup.
    -   Improved docs.

-   0.0.21, 11-Jun-2021:

    -   Use YAML for ``codechat_config.yaml`` instead of pseudo-JSON.
    -   Allow the ``codechat_config`` file ``args`` to be a string or a sequence of strings.
    -   Wait until the server has started before connecting to it.
    -   Remove a broken and useless feature: if the server is stopped, a keystroke closes the terminal window. (The GUI already provides a working and well-understood method to do this.)
    -   Add logging to better track down bugs. Fixed problem where some log data wasn't showing in VS Code.
    -   Fix startup bug -- skipped initial render in some cases.

-   0.0.20, 23-Feb-2021:

    -   The CodeChat Server now displays stderr in the VSCode terminal and runs correctly.
    -   Better CodeChat Server handling of signals and exceptions.

-   0.0.19, 17-Feb-2021:

    -   Run the CodeChat Server in a VSCode terminal.
    -   Allow the user to specify a command to run the server, not just a path to an executable.

-   0.0.18, 8-Feb-2021:

    -   Add missing dependency to the server.
    -   Reduce server start-up time.
    -   Update install docs for the VSCode extension; need to use a light theme.

-   0.0.17, 20-Jan-2021:

    -   Correctly size splitter on startup.
    -   Correct shut-down sequence.
    -   Show errors if the plugin/server connection is lost.

-   0.0.16, 18-Jan-2021:

    -   Correctly return an error message when no renderer is found (another fixed case).
    -   Display percentage in the progress bar when available.
    -   Prevent CodeChat from dying when a laptop goes to sleep then wakes back up.
    -   Automatically start the CodeChat Server when the VSCode extension is run.
    -   Correctly return an error message when no renderer is found.
    -   Update the status bar on the first build.

-   0.0.15, 4-Dec-2020:

    -   Provide a more helpful CodeChat Client message at startup.
    -   Correctly handle browsing away from the produced docs.
    -   Continue operation in the CodeChat Client after an error occurs.
    -   Fix CodeChat renderer error messages so they'll be counted in the CodeChat Client's tally of errors.
    -   Fix error message processing to support Windows drive letters.
    -   Don't claim focus when revealing the CodeChat panel.
    -   Fix hang on shutdown.

-   0.0.14, 18-Aug-2020:

    -   Additional shutdown fixes.
    -   Server instructs web client to never cache HTML files.
    -   Improved VSClient error reporting.

-   0.0.13, 11-Aug-2020:

    -   Improved VSClient error handling.
    -   CodeChat Server can now shut down gracefully.

-   0.0.12, 29-Jul-2020:

    -   Change method used to load the CodeChat Client to work with VSCode 1.47.

-   0.0.11, 28-Jul-2020:

    -   Add type hints.
    -   Make VSCode client more robust after a shutdown/restart.
    -   Add note that VSCode 1.47, where the webview doesn't work at all, isn't supported.

-   0.0.10, 1-Jul-2020:

    -   Enable running the server via ``CodeChat_Server`` from the terminal/command line.

-   0.0.9, 29-Jun-2020:

    -   Correctly shut down/restart VSCode client.
    -   Return a 404 on a permission error.
    -   Correct subprocess decoding approach.

-   0.0.8, 24-Jun-2020:

    -   Horizontal scroll bars now appear when necessary.
    -   Newlines correctly display in the web client's build messages panel.
    -   Shutdown sequence corrected.
    -   Avoid missed renders.
    -   Allow multiple editor clients.
    -   Improve error handling.
    -   Nicer stylesheets for single-file renders of CodeChat and reST.

-   0.0.7, 22-Jun-2020:

    -   Documentation improvements.

-   0.0.5, 20-Jun-2020:

    -   First fully functioning public release.
