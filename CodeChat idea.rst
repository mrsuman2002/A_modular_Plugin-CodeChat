Thrift
======
Draft of a `Thrift <https://thrift.apache.org/>`_ interface between the text editor extension and the CodeChat server, and between the web browser client and the CodeChat server:

- Extension service:

  - ``string html, int id = render_client()`` returns HTML that incorporates a JS client in the resulting HTML and an id for future render requests. The client loads in the result of a render. This can also be passed on to a web browser for rendering there.
  - ``string url, int id = render_client_url()`` returns a URL to a local webserver as above.
  - ``int id = render_client_browser()`` opens the HTML in a browser as above.
  - ``void start_render(string text, string file_path, int id)`` to render something.
  - ``void stop_render_client(int id)``
  - ``void sync_to(string text, uint text_index, uint global_y_coordinate_of_cursor)``
  - ``uint index, string text, enum result_type { sync, text, request_ownership } = get_results()`` returns:

    - The index for the next sync request made in the web view. Valid if result_type == sync.
    - Updated text for the editor. Valid if result_type == text.

  - ``void grant_ownswership(int id)``

- Web browser service. All methods raise an exception if the id isn't valid.

  - ``string result, enum result_type { render_string, output, status, highlight_find } get_results(int id)`` returns HTML/output/status from the latest render, or highlights the given result string. If this is status, the ``result`` is JSON-encoded to contain the status and also the source from which to load resources (file system path/web server URL).
  - ``void sync_to(string text, uint text_index, uint global_y_coordinate_of_cursor)``
  - ``void request_ownership(int id)`` returns when ownership is granted.

Edits may be made in the text editor or in the web view. To prevent users from modifying both at the same time, only one of these two places may have editing priviledges. The text editor begins with this priviledge; the web view must request and obtain it from the text editor before allowing edits. Privledges return to the text editor when the web view sends updated text. What if the text editor changes to another document while the web view is still editing? Probably pop up a modal dialog in the web page: save changes or discard changes.


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


Web browser client
==================
HTML consists of:

- JavaScript in ``<head>``, with a built-in id for queries. It should load in and start Thrift after page load, then call ``get_results``. See JavaScript_.
- Use https://nathancahill.github.io/Split.js/ for a nice splitter.
- use http://getcontenttools.com/ for a nice HTML editor.
- An `iframe <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/iframe>`_. Probably set the ``sandbox`` attribute to ``allow-scripts`` (or not) based on the Enable JS checkbox in the status bar. Set HTML via assigning to the ``htmlsrc`` attribute. Also set the origin of the page via the ``src`` attribute.
- A ``div`` containing output.
- A ``div`` containing status.


JavaScript
----------
A sketch of the ``get_results`` callback::

  if result_type == status:
    assign status to ``div``.
    Update ``src`` of ``iframe``.
  elif result_type == render:
    The HTML is always the last thing in a render. Therefore, the next
    received value starts a new render, so the output should be cleared
    the next time a result is received.
    b_clear_output = true.
    Save cursor, scroll, and highlight location.
    Update render iframe.
    Restore cursor, scroll, and highlight location.
  elif result_type == output:
    if b_clear_output
      clear output div.
      status = building.
      b_clear_output = false.
    Append output to output div.
  elif result_type == highlight_find:
    Call highlightFind.
  else:
    Report error to console.
  Call get_results.

Use the ``_jsPreviewSync`` in ``preview_sync.py`` for some of the JavaScript code. Currently, ``window_onClick`` returns the index of the beginning of the selection. It would be nice to also return the index of the end of the selection. In addition, it should return the value produced by calling ``selectionAnchorCoords``. Finally, this function should call the Thrift ``sync_to`` function with this data.
