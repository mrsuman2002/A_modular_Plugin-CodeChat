*******************
The CodeChat client
*******************

Implementation sketch
=====================
Ideas:

- use http://getcontenttools.com/ for a nice HTML editor.

A sketch of the ``get_results`` callback:

.. code-block:: none

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


.. toctree::

    templates/CodeChat_client.html
    static/CodeChat_client.js
    static/CodeChat_client.css