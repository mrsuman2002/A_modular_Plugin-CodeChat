# *****************************************
# |docname| - The CodeChat rendering server
# *****************************************

import glob
import sys
import io
import threading
from threading import Thread
from flask_cors import CORS
from queue import Queue
sys.path.append('./gen-py')
#sys.path.insert(0, glob.glob('../../lib/py/build/lib*')[0])
from tutorial import CodechatSyc
from tutorial.ttypes import get_result_type, get_result_return
from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol
from thrift.server import TServer
from CodeChat.CodeToRest import code_to_html_string
from CodeChat.SourceClassifier import get_lexer

class CodechatHandler:
    def __init__(self):
        self.log = {}

    def render_client(self):
        print("render_client works")
        html= """<!DOCTYPE html>
          <html lang="en">
            <head>
                <link rel="icon" href="data:,">
              <meta charset="utf-8">
              <title>Hello Thrift</title>
            </head>
            <body style="color:red;"  >          
              <iframe src="http://127.0.0.1:5000/skeleton/1" width="100%"  height="1000px" color="white">Website</iframe>
            </body>
          </html>"""
        results_dict[1]=Queue()
        return html

    def get_result(self,id):
      print("get result is called")
      get_result_return_object = get_result_return() 
      get_result_return_object.gr_type=get_result_type.html
      get_result_return_object.text,get_result_return_object.gr_type =results_dict[1].get()
      print("Python struct output: ",get_result_return_object)
      return get_result_return_object



    def start_render(self, text, path, id):       
        print(path)
        print("Start render works")
        id=1
        # Use StringIO to pass CodeChat compilation information back to

        # the UI.

        errStream = io.StringIO()

        try:

            htmlString = code_to_html_string(text, errStream, filename=path)

        except KeyError:

            # Although the file extension may be in the list of supported

            # extensions, CodeChat may not support the lexer chosen by Pygments.

            # For example, a ``.v`` file may be Verilog (supported by CodeChat)

            # or Coq (not supported). In this case, provide an error messsage

            errStream.write('Error: this file is not supported by CodeChat.')

            htmlString = ''

        errString = errStream.getvalue()

        errStream.close()
        results_dict[id].put((htmlString, get_result_type.html))
        results_dict[id].put((errString, get_result_type.build))

        print("HTML and type add in a queue")




    def stop_render_client(self, id):
        return


def service2():
    handler = CodechatHandler()
    processor = CodechatSyc.Processor(handler) 
    transport = TSocket.TServerSocket(host='127.0.0.1', port=9090)
    tfactory = TTransport.TBufferedTransportFactory()
    pfactory = TBinaryProtocol.TBinaryProtocolFactory()

    server = TServer.TSimpleServer(processor, transport, tfactory, pfactory)

    # You could do one of these for a multithreaded server
    ## server = TServer.TThreadedServer(
    ##     processor, transport, tfactory, pfactory)
    ## server = TServer.TThreadPoolServer(
    ##     processor, transport, tfactory, pfactory)
    print('Starting the server...')
    server.serve()
    print('done.')


import sys
sys.path.append('gen-py')
from flask import Flask, request, make_response
from thrift.protocol import TJSONProtocol
from thrift.server import TServer
from thrift.transport import TTransport
from tutorial import CodechatSyc


handler = CodechatHandler()
processor = CodechatSyc.Processor(handler)
protocol = TJSONProtocol.TJSONProtocolFactory()
server = TServer.TServer(processor, None, None, None, protocol, protocol)

app = Flask(__name__)
@app.route('/', methods=['POST'])
def service1():
    itrans = TTransport.TMemoryBuffer(request.data)
    otrans = TTransport.TMemoryBuffer()
    iprot = server.inputProtocolFactory.getProtocol(itrans)
    oprot = server.outputProtocolFactory.getProtocol(otrans)
    server.processor.process(iprot, oprot)
    return make_response(otrans.getvalue())

@app.route('/skeleton/<int:unique_id>')
def skeleton(unique_id):
  html="""<!DOCTYPE html>
    <html lang="en">
      <head>
          <link rel="icon" href="data:,">
        <meta charset="utf-8">
        <title>Hello Thrift</title>

      </head>
      <body >
        <iframe id="output" width="100%"  height="1000px" color="white" >Edit the Document !!!</iframe>
        <div id="build" style="margin: 10px; border: 1px solid #4CAF50;">
        This is for build msg!!!
        </div>
        <div id="status" style="margin: 10px; padding 10px; border: 1px solid #4CAF50;">
        This is  for Status!!!
        </div>

        <script src="../static/thrift.js"></script>
        <script src="../static/gen-js/CodechatSyc.js"></script>
        <script src="../static/gen-js/tutorial_types.js"></script>
        <script >

          (function() {
            var transport = new Thrift.TXHRTransport("../");
            var protocol  = new Thrift.TJSONProtocol(transport);
            var client    = new CodechatSycClient(protocol);
            var nameElement = document.getElementById("name_in");
            var outputElement = document.getElementById("output");
            var outputElement2 = document.getElementById("build");
            function do_get_result() {
              client.get_result(1, function(result) {
                if (result.gr_type==get_result_type.html){
                var result2=result.text;
                //var result3 = result2.fontcolor("red");
                outputElement.srcdoc = result2;
               

                }
                else{
                var result2=result.text;
                //var result3 = result2.fontcolor("blue");
                outputElement.srcdoc = result2;
                }

                do_get_result();
              });
            };
            do_get_result();
          })();

        </script>
      </body>
    </html>"""
  return html


results_dict={}
if __name__ == '__main__':
    t1 = threading.Thread(target=service2)
    t1.start()
    print("HTTP server running")
    app.run()

    







