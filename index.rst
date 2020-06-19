CodeChat
========
CodeChat integrates the capabilities of `CodeChat renderer <https://codechat.readthedocs.io/>`_ into popular text editors [#]_. To support multiple editors, this program offloads most of the processing to the CodeChat server and display to the CodeChat client, making the editor plugin code shorter and easier to port. The basic architecture:

.. digraph:: architecture

    bgcolor = transparent;
    compound = true;
    node [shape = box];
    subgraph cluster_text_editor {
        label = "Text editor/IDE";
        source_code [label = <source<br />code>, style = dashed];
        CodeChat_plugin [label = <CodeChat<br />plugin>];
    }

    subgraph cluster_server {
        label = <CodeChat<br />server>;
        render_engine [label = <Renderers>];
    }

    subgraph cluster_client {
        label = "CodeChat client";
        rendered_code [label = "rendered code", style = dashed];
        JavaScript;
    }

    CodeChat_plugin -> render_engine [label = "Thrift", dir = both, lhead = cluster_server];
    render_engine -> JavaScript [label = "Thrift", dir = both, lhead = cluster_client, ltail = cluster_server];

This approach bridges the services CodeChat provides, which are defined in Python, to the variety of programming languages which various text editors require. To accomplish these goals, this project:

#.  Develops a `CodeChat server <CodeChat_Server/contents>` to provide the needed services;
#.  Provides a `CodeChat client <CodeChat_Server/CodeChat_Server/CodeChat_Client/contents>`, hosted in a web browser, to display the rendered source code and provide for user input;
#.  Introduces a `plugin for Visual Studio Code <VSCode_Extension/contents>`, a free and popular cross-platform text editor; and
#.  Employs `Apache Thrift <https://thrift.apache.org>`_ to define `CodeChat services <CodeChat_Services/contents>`, which allows the CodeChat server to communicate with plugins developed in a `variety of languages <https://thrift.apache.org/docs/Languages>`_.

Contents:

.. toctree::
    :maxdepth: 2

    CodeChat_Server/contents
    CodeChat_Server/CodeChat_Server/CodeChat_Client/contents
    VSCode_Extension/contents
    CodeChat_Services/contents
    docs/CHANGELOG
    conf.py
    run_sphinx.bat
    .gitignore


To do
=====
-   Lots of testing.
-   Make the opacity a class, then apply that in JS.
-   Scan for percentages in the web client and update the progress bar.
-   Wait 300 ms before a render.
-   Only render saved documents for projects.
-   Handle syntax error line number click from the web client.
-   Provide way to do a rebuild all.
-   Find a way not to overload/abuse the ClientState._file_name.
-   Add the license to all new files.
-   Add in sync.
-   Monitor iframe location changes and try to sync by loading another file.
-   Offer an option for VSCode to render in an external browser.
-   Package.
-   Allow user-define JSON of mapping from extensions to renderers.
-   Provide a nicer style for docutils renders.
-   Support all the pandoc renderes.
-   Support rust projects?
-   Improve docs
-   Create a new repo for the CodeChat renderer? Or make it a subproject of this repo?
-   Support at least one more editor.
-   More things.


Indices and tables
==================
* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`


License
=======
Copyright (C) 2012-2020 Bryan A. Jones.

This file is part of the CodeChat plugin.

The CodeChat plugin is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

The CodeChat plugin is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more details.

You should have received a `copy of the GNU General Public License <docs/LICENSE>` along with the CodeChat plugin.  If not, see http://www.gnu.org/licenses/.


Footnotes
=========
.. [#] At this time, only the Visual Studio Code editor is supported.