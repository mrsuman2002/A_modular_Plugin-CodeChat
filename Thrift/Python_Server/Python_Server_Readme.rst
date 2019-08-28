Python Server Documentation!
=============================
In this directory, we need to install ppackages. To install packages run the following command from the current location

C:\Users\suman\Desktop\MSU_Spring_2018\Research\A_modular_Plugin-CodeChat\Thrift\Python_Server>pip install Codechat

``pip install -U flask-cors``

``pip install thrift``

``pip install CodeChat``


If you are getting errors like ImportError: No module named queue then check your python version using ``python -v``. If it is version 2 then try to install python 3 and pip 3.

If the system is not taking version 3 as a defeault then try running command as
``pip3 install -U flask-cors``

``pip3 install thrift``

``pip3 install CodeChat``

or 

``python3 PythonServer.py``


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

Coechathandler class was created and different functions like 

 render_client() returns address(</skeleton/<int:unique_id>) that has HTML that incorporates a JS client in the resulting HTML and an id for future render requests. The client loads in the result of a render. This can also be passed on to a web browser for rendering there. It also initialize the queue to the unique id.

 start_render(string text, string file_path, int id) to render the source code. It also puts the rendered HTML to the dictionary and assigns it to un key.
 
 get_result(string text) to gets the html that was assigned to unique id.


The webpage communicates to the python flask server using TJSONProtocol and writes the rendered source code to the specific address </skeleton/<int:unique_id>, which later on called in a iframe to load webpage from that specific.

Here idea is not to serve actual html to the webpage but to call address that contains rendered text(html) 

In the browser get_result function is called to get the html that was assigned tot the unique_id(key) from the dictionary.

.. code-block:: Python
    :linenos:

    from CodeChat.CodeToRest import code_to_html_string
    from CodeChat.SourceClassifier import get_lexer


.. toctree::

    ppserver.bat
    PythonServer.py
