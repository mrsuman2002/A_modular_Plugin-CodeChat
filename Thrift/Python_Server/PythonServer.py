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


class CodechatHandler:
    def __init__(self):
        self.log = {}

    
        
    def render_client(self):
        print("render_client works")
        with open('../../CodeChat_Extension/JavaScript_Client/gen-js/CodechatSyc.js') as f:
            thrift_js = f.read()
        html= """<!DOCTYPE html>
        <html lang="en">
        <head>
        <title>RenderClient</title>

        </head>
        <body>
        <p id="demo"> Render client is working </p>
        <iframe id="render"></iframe>
        <div id="message"></div>
        <script> 
        document.getElementById("demo").innerHTML = "Hello world";
                    %s
                    
                    var transport = thrift.TBufferedTransport;
                    var protocol = thrift.TBinaryProtocol;
                    var connection = thrift.createConnection("localhost", 9090, {
                    transport : transport,
                    protocol : protocol
                    });
                    connection.on('error', function(err) {
                    assert(false, err);
                    });
                    var client = thrift.createClient(CodechatSyc, connection);

                    client.get_result(      
                        function(err, response) {
                            window.getElementById("render").srcdoc = response;
                connection.end();
                });
                
                
        </script>

        </body>
        </html>
        """ % thrift_js

        with open('tmp.html', 'w', encoding='utf-8') as f:
            f.write(html)

        return "See the file!"

    def get_result(self):
        return "get_results worked"
        


    def start_render(self, text, path,id):
        return



    def stop_render_client(self, id):
        return



if __name__ == '__main__':
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





