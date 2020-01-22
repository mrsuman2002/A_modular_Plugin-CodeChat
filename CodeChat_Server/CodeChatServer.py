# .. Copyright (C) 2012-2020 Bryan A. Jones.
#
#    This file is part of CodeChat.
#
#    CodeChat is free software: you can redistribute it and/or modify it under
#    the terms of the GNU General Public License as published by the Free
#    Software Foundation, either version 3 of the License, or (at your option)
#    any later version.
#
#    CodeChat is distributed in the hope that it will be useful, but WITHOUT ANY
#    WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
#    FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
#    details.
#
#    You should have received a copy of the GNU General Public License along
#    with CodeChat.  If not, see <http://www.gnu.org/licenses/>.
#
# *****************************************
# |docname| - The CodeChat rendering server
# *****************************************
# TODO:
#
# - Document the code.
#
# Imports
# =======
# These are listed in the order prescribed by `PEP 8
# <http://www.python.org/dev/peps/pep-0008/#imports>`_.
#
# Standard library
# ----------------
import sys
import io
import threading
from queue import Queue
import re

# Third-party imports
# -------------------
from flask import Flask, request, make_response
from flask_cors import cross_origin
from thrift.protocol import TJSONProtocol
from thrift.server import TServer
from thrift.transport import TTransport
from thrift.transport import TSocket
from thrift.protocol import TBinaryProtocol
from CodeChat.CodeToRest import code_to_html_string

# Local application imports
# -------------------------
sys.path.append('gen-py')
from CodeChat_Services import Editor_Extension, Web_Sync
from CodeChat_Services.ttypes import Get_Result_Type, Get_Result_Return


# Service provider
# ================
# This class implements both the Editor_Extension and Web_Sync services.
class CodeChatHandler:
    def __init__(self):
        self.results_dict = {}

    # Return the HTML for a web client.
    def render_client(self):
        # TODO: Generate a unique ID and return it.
        id = 1
        self.results_dict[id] = Queue()

        # Return the HTML for the client.
        html = file_contents("CodeChat_client.html")
        
        # Manually replace references to script files with the scripts themselves. This means the server doesn't need to serve these files, whose names might conflict with files requsted by the rendered contents.
        def script_replacer(match_object):
            return "<script>{}</script>".format(
                file_contents(match_object.group(1))
            )
        html = re.sub(
            # Lookf for a script tag.
            '<script src="'
            # Capture the src name...
            '('
                # Look for a path, which for simplicity we define as anything that's not a quote (").
                r'[^"]+'
            # ...as group one.
            ')'
            # Include the end of the script tag in this re.
            '"></script>', script_replacer, html
        )
        # Manually replace the unique id in the HTML. TODO: use a unique ID.
        html = html.replace(
            "<script>run_client(unique_id);</script>", 
            "<script>run_client({});</script>".format(id)
        )
        return html

    # Render the provided text to HTML, then enqueue it for the web view.
    def start_render(self, text, path, id):
        # Use StringIO to pass CodeChat compilation information back to
        # the UI.
        errStream = io.StringIO()

        # Render the source code.
        try:
            htmlString = code_to_html_string(text, errStream, filename=path)
        except KeyError:
            # Although the file extension may be in the list of supported
            # extensions, CodeChat may not support the lexer chosen by Pygments.
            # For example, a ``.v`` file may be Verilog (supported by CodeChat)
            # or Coq (not supported). In this case, provide an error messsage
            errStream.write('Error: this file is not supported by CodeChat.')
            htmlString = ''

        # Save any errors.
        errString = errStream.getvalue()
        errStream.close()

        # Enqueue the results.
        self.results_dict[id].put(Get_Result_Return(Get_Result_Type.build, errString))
        self.results_dict[id].put(Get_Result_Return(Get_Result_Type.html, htmlString))

    # Pass rendered results back to the web view.
    def get_result(self, id):
        return self.results_dict[id].get()

    # TODO
    def stop_render_client(self, id):
        return


# Instantiate this class, which will be used by both servers.
handler = CodeChatHandler()


# Utility function to return the contents of a given file.
def file_contents(file_path):
    with open(file_path, encoding="utf-8") as f:
        return f.read()


# Servers
# =======
# Server for the CodeChat editor extension service.
def editor_extension_service():
    transport = TSocket.TServerSocket(host='127.0.0.1', port=9090)
    tfactory = TTransport.TBufferedTransportFactory()
    pfactory = TBinaryProtocol.TBinaryProtocolFactory()
    processor = Editor_Extension.Processor(handler)

    # You could do one of these for a multithreaded server
    ## server = TServer.TThreadedServer(
    ##     processor, transport, tfactory, pfactory)
    ## server = TServer.TThreadPoolServer(
    ##     processor, transport, tfactory, pfactory)
    server = TServer.TSimpleServer(processor, transport, tfactory, pfactory)
    print('Starting the server...')
    server.serve()


# Server for the CodeChat webview service
app = Flask(__name__)
@app.route('/', methods=['POST'])
# Allows the XHR requests from the webview to suceed.
# See max ages at https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Access-Control-Max-Age.
@cross_origin(max_age=100000)
def web_sync_service():
    processor = Web_Sync.Processor(handler)
    protocol = TJSONProtocol.TJSONProtocolFactory()
    server = TServer.TServer(processor, None, None, None, protocol, protocol)
    itrans = TTransport.TMemoryBuffer(request.data)
    otrans = TTransport.TMemoryBuffer()
    iprot = server.inputProtocolFactory.getProtocol(itrans)
    oprot = server.outputProtocolFactory.getProtocol(otrans)
    server.processor.process(iprot, oprot)
    return make_response(otrans.getvalue())


# Main
# ====
# Run both servers.
if __name__ == '__main__':
    t = threading.Thread(target=editor_extension_service)
    t.start()
    app.run()
