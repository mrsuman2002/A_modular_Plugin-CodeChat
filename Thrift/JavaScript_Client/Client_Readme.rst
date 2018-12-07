JavaScript Client
==================

After generating the JavaScript modules i.e gen-nodejs. You need to create javaScript client to communicate with python server(that contains CodeChat Library) so that it can be used in javaScript extension of VSCode.

Here, we have used TSocket transport layer and TBinaryProtocol to communicate with python server. Connection is made on localhost and port 9090. Also, we have defined javaScript client under function called Cilentfunc so that we can call whole client in extension.

.. code-block:: JavaScript

    function myfunc(webview)

Export function is used to export Clientfunc to extension.

.. code-block:: JavaScript

    exports.myfunc=myfunc

.. toctree::

    Client.js



