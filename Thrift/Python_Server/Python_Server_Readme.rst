Python Server Documentation!
=============================


To generate py files using thrift, firstly, you need to `Download <http://www.apache.org/dyn/closer.cgi?path=/thrift/0.11.0/thrift-0.11.0.exe>`_  a copy of thrift. Secondly, you need to create a thrift file called tutorial.thrift. Then you can generate .py code using following command:

``thrift --gen py tutorial.thrift``


After creating the python modules i.e gen-py. You need to build your python server to communicate with CodeChat Library, written in python programming language.

Supported Protocols, Transports and Servers.
-------------------------------------------------
The protocol layer provides serialization and deserialization. Thrift supports the following protocols :

* TBinaryProtocol
* TCompactProtocol
* TDenseProtocol
* TJSONProtocol
* TSimpleJSONProtocol
* TDebugProtocol

Tranport Layer
---------------
The transport layer is responsible for reading from and writing to the wire. Thrift supports the following:

* TSocket
* TFramedTransport
* TFileTransport
* TMemoryTransport
* TZlibTransport

Here, we have used TSocket transport layer and TBinaryProtocol to communicate with client. Also, we have imported module called
code_to_html_string that renders source code to webpage.

.. code-block:: Python
    :linenos:

    from CodeChat.CodeToRest import code_to_html_string
    from CodeChat.SourceClassifier import get_lexer


.. toctree::

    ppserver.bat
    PythonServer.py
