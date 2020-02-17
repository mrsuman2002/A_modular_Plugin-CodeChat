.. Copyright (C) 2012-2020 Bryan A. Jones.

    This file is part of the CodeChat plugin.

    The CodeChat plugin is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

    The CodeChat plugin is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more details.

    You should have received a `copy of the GNU General Public License <LICENSE>` along with the CodeChat plugin.  If not, see http://www.gnu.org/licenses/.

*******************
The CodeChat server
*******************
TODO: introduction.


Installation
============
TODO: Create a setup.py file. Should reference CodeChat, flask, thrift.


Server architecture
===================
- Calls to render are put in a queue. Another thread pops an entry from the queue and renders it. The result is placed in a dict of {id: results queue} or discarded if there's no entry.

- The webserver url is https://127.0.0.1:fixedport/id/path. It should reject all non-local traffic. Looks like I can check the client_address for this. It looks like overriding translate_path in SimpleHTTPRequestHandler would work. Having this return None for a directory would also prevent list directory from being shown.

- To determine if the render should be a single document or a Sphinx project, the server loks for a file named ``CodeChat-config.json`` in the directory of the file to render and in all parent directories. To allow comments using a ``#`` and relaxed syntax, read this using ``ast.literal_eval``. The format is::

    {
        'ProjectPath': 'path to root of the project, relative to the '
          'directory this file is located in',
        'OutputPath' : 'path relative to the project path',
        'SourcePath' : 'path relative to the project path',
        'CommandLine' : 'command used to involke a build. Used with'
          '.format(ProjectPath, OutputPath, SourcePath).',
        # Optional. The same format as in a Sphinx ``conf.py``.
        'CodeChat_lexer_for_glob': {,
            'glob1' : 'lexer_alias1`,
        }
    }

Contents
========
.. toctree::

    CodeChat_Server/server.py
    CodeChat_Server/renderer.py
    CodeChat_Server/__main__.py
    CodeChat_Server/__init__.py
    run_server.bat
    CodeChat_Server/sphinx_template/conf.py
    CodeChat_Server/sphinx_template/index