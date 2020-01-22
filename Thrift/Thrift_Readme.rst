`Apache Thrift <https://thrift.apache.org/>`_.: Scalable Cross-Language Services Implementation

===================================================================================================

The Apache Thrift software framework is used for scalable cross-language services development. It combines a software stack with a code generation engine to build services that work efficiently and seamlessly between Java, Python, C++ PHP, Erlang, Ruby, Perl, Haskell, C#, Cocoa, JavaScript, Node.js, Smalltalk, OCaml and Delphi and other languages.

Some of the requirements to be met while using appache thrift:

* Install `python <https://www.python.org/downloads/>`_.
* Install `npm <https://nodejs.org/en/>`_.
* Install thrift packages

  ``npm install thrift``

Note: If you are installing from command prompt, you must run command prompt as an administrator.


To generate py files and node:js files using thrift, firstly, you need to `Download <http://www.apache.org/dyn/closer.cgi?path=/thrift/0.11.0/thrift-0.11.0.exe>`_  a copy of thrift. Secondly, you need to create a thrift file called tutorial.thrift. Then you can generate .py and js:node code using following commands:

``thrift --gen py tutorial.thrift``

``thrift --gen js:node tutorial.thrift``

We are trying to keep same files together so we will be generating nodejs files(gen-nodejs) inside the JavaScript_Client folder which is under CodeChat_Extension and gen-py in Python_Server

.. toctree::

    Python_Server/Python_Server_Readme
    ../CodeChat_Extension/JavaScript_Client/index

