# *****************************************
# |docname| - The CodeChat rendering server
# *****************************************

import glob
import sys
sys.path.append('../gen-py')
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

    def ping(self):
        print('ping()')
        print('suman')
    def render(self,text,path):
        #print(text)
        print(path)
        print("it works")
        lexer = get_lexer(filename=path, code=text)
        html = code_to_html_string(text, lexer=lexer)
        html = html.replace('background-color: #eeeeee', '')
        print(html)
        with open('out.html', 'w', encoding='utf-8') as f:
            f.write(html)
        return html



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





