The CodeChat System
===================
The CodeChat system integrates the capabilities of the `CodeChat renderer <https://codechat.readthedocs.io/>`_ into popular text editors [#]_. To support multiple editors, this program offloads most of the processing to the CodeChat server and display to the CodeChat client, making the editor plugin/extension code shorter and easier to port. The basic architecture:

.. digraph:: architecture

    bgcolor = transparent;
    compound = true;
    node [shape = box];
    subgraph cluster_text_editor {
        label = <Text editor/IDE>;
        source_code [label = <Source<br />code>, style = dashed];
        CodeChat_plugin [label = <CodeChat<br />plugin>];
    }

    subgraph cluster_server {
        label = <CodeChat server>;
        thrift_server [label = <Thrift<br />server>];
        web_server [label = <Web <br />server>];
        renderers [label = <Built-in<br />Renderers>];
    }

    external_renderers [label = <External <br />renderers>];

    subgraph cluster_client {
        label = "CodeChat client";
        rendered_code [label = <Rendered code>, style = dashed];
        JavaScript;
    }

    CodeChat_plugin -> thrift_server [label = <Thrift>, dir = both, lhead = cluster_server];
    thrift_server -> JavaScript [label = <websocket>, dir = both, lhead = cluster_client, ltail = cluster_server];
    web_server -> JavaScript [label = <HTTP>, dir = both, lhead = cluster_client, ltail = cluster_server];
    renderers -> external_renderers [label = <subprocess>, ltail = cluster_server, dir = both];

This approach bridges the services CodeChat provides, which are defined in Python, to the variety of programming languages which various text editors require. To accomplish these goals, this project:

#.  Develops a `CodeChat server <CodeChat_Server/contents>` to provide the needed services;
#.  Provides a `CodeChat client <CodeChat_Server/CodeChat_Server/CodeChat_Client/contents>`, hosted in a web browser, to display the rendered source code and provide for user input;
#.  Introduces a `plugin for Visual Studio Code <VSCode_Extension/contents>`, a free and popular cross-platform text editor; and
#.  Employs `Apache Thrift <https://thrift.apache.org>`_ to define `CodeChat services <CodeChat_Services/contents>`, which allows the CodeChat server to communicate with plugins developed in a `variety of languages <https://thrift.apache.org/docs/Languages>`_.

Contents
--------

.. toctree::
    :maxdepth: 2

    README
    CodeChat_Server/contents
    CodeChat_Server/CodeChat_Server/CodeChat_Client/contents
    VSCode_Extension/contents
    CodeChat_Services/contents
    docs/CHANGELOG
    conf.py
    run_sphinx.bat
    .gitignore


Contributors
============
The following developers provided valuable help in creating the CodeChat system.

-   `Bryan A. Jones <https://github.com/bjones1/>`_
-   `Suman Adhikari <https://github.com/mrsuman2002>`_
-   Christian Bush
-   Jack Betbeze


To do
=====
-   Lots of testing.
-   Handle syntax error line number click from the web client.
-   Provide way to do a rebuild all.
-   Find a way not to overload/abuse the ClientState._file_name.
-   Add in sync.
-   Monitor iframe location changes and try to sync by loading another file.
-   Offer an option for VSCode to render in an external browser.
-   Allow user-defined JSON of mapping from extensions to renderers.
-   Provide a nicer style for docutils renders.
-   Support all the pandoc renderers.
-   Improve docs
-   Support at least one more editor.
-   Save and restore scroll position on a per-file basis.
-   Separate the render manager code from the renderer code.
-   Provide a verbose/non-verbose logging option.

Ideas:

-   At the core of the design is a wrapped StringIO class that allows reads/writes from/to (dest, str) [e.g. (build_output, "...rendered x as JavaScript...")]. Opening this stream for reading returns an object that does blocking reads and remembers its location in the stream. It also offers a close_open method that, given an existing stream to close and a new stream to open, switches the blocking read being performed from the old to the new stream. StringIO also implements universal newlines
-   The editor requests a render. The render manager either finds an existing render or creates a new render. For new renders, the render is enqueued. The render manager close_opens the web client's current render stream, replacing it with the new, resulting render stream; as a result, the web client then beings to read from this stream.
-   The render manager worker eventually dequeues the render then starts writing to it. The renderer writes output, then errors, then html.
-   The web client blocks on read until data is ready, then returns as much data as it can for each read.


Search
======
* :ref:`search`


License
=======
Copyright (C) 2012-2020 Bryan A. Jones.

This file is part of the CodeChat system.

The CodeChat system is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

The CodeChat system is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more details.

You should have received a `copy of the GNU General Public License <docs/LICENSE>` along with the CodeChat system.  If not, see http://www.gnu.org/licenses/.


Footnotes
=========
.. [#] At this time, only the Visual Studio Code editor is supported.