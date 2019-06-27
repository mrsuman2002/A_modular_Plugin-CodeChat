# *****************************************
# |docname| - The CodeChat rendering server
# *****************************************

import glob
import sys
sys.path.append('./gen-py')
#sys.path.insert(0, glob.glob('../../lib/py/build/lib*')[0])
from tutorial import CodechatSyc
from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol
from thrift.server import TServer
from CodeChat.CodeToRest import code_to_html_string
from CodeChat.SourceClassifier import get_lexer
import threading
from threading import Thread
from flask_cors import CORS
from queue import Queue


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
            <body>          
              <iframe src="http://127.0.0.1:5000/skeleton/1" width="100%" height=1000px>Website</iframe>
            </body>
          </html>"""
        results_dict[1]=Queue()
        return html

    def get_result(self,hello):

      print("get result is called")
      return results_dict[1].get() 
        


    def start_render(self, text, path,id):       
        print(path)
        print("Start render works")
        id=1
        lexer = get_lexer(filename=path, code=text)
        html = code_to_html_string(text, lexer=lexer)
        html = html.replace('background-color: #eeeeee', '')
        results_dict[id].put(html)
        print("Html has been added to the queue")



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
      <body>
        <div id="output">Edit the Document !!!</div>

        <script src="../static/thrift.js"></script>
        <script src="../static/gen-js/CodechatSyc.js"></script>
        <script >
          (function() {
            var transport = new Thrift.TXHRTransport("../");
            var protocol  = new Thrift.TJSONProtocol(transport);
            var client    = new CodechatSycClient(protocol);
            var nameElement = document.getElementById("name_in");
            var outputElement = document.getElementById("output");
            function do_get_result() {
              client.get_result("render", function(result) {
                outputElement.innerHTML = result;
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

    







