# .. Copyright (C) 2012-2020 Bryan A. Jones.
#
#    This file is part of the CodeChat plugin.
#
#    The CodeChat plugin is free software: you can redistribute it and/or
#    modify it under the terms of the GNU General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    The CodeChat plugin is distributed in the hope that it will be
#    useful, but WITHOUT ANY WARRANTY; without even the implied warranty
#    of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
#    General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with the CodeChat plugin.  If not, see
#    <http://www.gnu.org/licenses/>.
#
# *******************************
# |docname| - The CodeChat server
# *******************************
# TODO:
#
# - Try out `Quart <https://gitlab.com/pgjones/quart>`_.
#
# Imports
# =======
# These are listed in the order prescribed by `PEP 8
# <http://www.python.org/dev/peps/pep-0008/#imports>`_.
#
# Standard library
# ----------------
import threading
import webbrowser

# Third-party imports
# -------------------
from flask import Flask, request, make_response, render_template, send_file, abort
from thrift.protocol import TJSONProtocol
from thrift.server import TServer
from thrift.transport import TTransport
from thrift.transport import TSocket
from thrift.protocol import TBinaryProtocol

# Local application imports
# -------------------------
from . import renderer
from .gen_py.CodeChat_Services import EditorPlugin, CodeChatClient
from .gen_py.CodeChat_Services.ttypes import (
    GetResultType,
    GetResultReturn,
    RenderClientReturn,
    CodeChatClientLocation,
)


# Service provider
# ================
# This class implements both the EditorPlugin and CodeChat client services.
class CodeChatHandler:
    def __init__(self):
        print("__init__()")

    # _`get_client`: Return the HTML for a web client.
    def get_client(self, codeChat_client_location):
        print("get_client({})".format(codeChat_client_location))
        id = self.render_manager.create_client()
        # Get the next ID.
        if id is None:
            return RenderClientReturn("", -1, "Duplicate id {}".format(id))

        # Return what's requested.
        url = "http://127.0.0.1:5000/client?id={}".format(id)
        if codeChat_client_location == CodeChatClientLocation.url:
            # Just return the URL.
            ret = url
        elif codeChat_client_location == CodeChatClientLocation.html:
            # Redirect to the webserver.
            ret = """
<!DOCTYPE html>
<html>
    <head>
        <script>window.location = "{}";</script>
    </head>
    <body></body>
</html>""".format(
                url
            )
        elif codeChat_client_location == CodeChatClientLocation.browser:
            # Open in an external browser.
            webbrowser.open(url, 1)
            ret = ""
        else:
            return RenderClientReturn(
                "", -1, "Unknown command {}".format(codeChat_client_location)
            )

        return RenderClientReturn(ret, id, "")

    # Render the provided text to HTML, then enqueue it for the web view.
    def start_render(self, text, path, id):
        print("start_render(\n{}\n, {}, {})".format(text[:80], path, id))
        if self.render_manager.start_render(text, path, id):
            # Indicate success.
            return ""
        else:
            return "Unknown client id {}".format(id)

    # Pass rendered results back to the web view.
    def get_result(self, id):
        print("get_result({})".format(id))
        q = self.render_manager.get_queue(id)
        if not q:
            return GetResultReturn(GetResultType.command, "error: unknown id")
        ret = q.get()
        # Delete the client if this was a shutdown command.
        if (ret.get_result_type == GetResultType.command) and (ret.text == "shutdown"):
            # Check that the queue is empty
            if not q.empty():
                print(
                    "CodeChat warning: client id {} shut down with pending commands.".format(
                        id
                    )
                )
            self.render_manager.delete_client(id)
        print(ret)
        return ret

    # Shut down a client.
    def stop_client(self, id):
        print("stop_client({})".format(id))
        q = self.render_manager.get_queue(id)
        if not q:
            return "unknown client {}.".format(id)
        # Send the shutdown command to the client.
        q.put(GetResultReturn(GetResultType.command, "shutdown"))
        # Indicate success.
        return ""


# Instantiate this class, which will be used by both servers.
handler = CodeChatHandler()


# Servers
# =======
#
# Server for the CodeChat editor plugin
# -------------------------------------
def editor_plugin_server():
    transport = TSocket.TServerSocket(host="127.0.0.1", port=9090)
    tfactory = TTransport.TBufferedTransportFactory()
    pfactory = TBinaryProtocol.TBinaryProtocolFactory()
    processor = EditorPlugin.Processor(handler)

    # You could do one of these for a multithreaded server
    ## server = TServer.TThreadedServer(
    ##     processor, transport, tfactory, pfactory)
    ## server = TServer.TThreadPoolServer(
    ##     processor, transport, tfactory, pfactory)
    server = TServer.TSimpleServer(processor, transport, tfactory, pfactory)
    print("Starting the plugin server...")
    server.serve()


# Server for the CodeChat client
# ------------------------------
# Create these once, globally.
client_processor = CodeChatClient.Processor(handler)
client_protocol = TJSONProtocol.TJSONProtocolFactory()
client_server = TServer.TServer(
    client_processor, None, None, None, client_protocol, client_protocol
)

client_app = Flask(
    __name__,
    # Serve CodeChat client files statically.
    static_url_path="/static",
    static_folder="CodeChat_Client/static",
    # Serve the CodeChat client HTML as a template.
    template_folder="CodeChat_Client/templates",
)

# The endpoint to get the HTML for the CodeChat client.
@client_app.route("/client")
def client_html():
    return render_template("CodeChat_client.html")


# The endpoint for the CodeChat client service.
@client_app.route("/client", methods=["POST"])
def client_service():
    itrans = TTransport.TMemoryBuffer(request.data)
    otrans = TTransport.TMemoryBuffer()
    iprot = client_server.inputProtocolFactory.getProtocol(itrans)
    oprot = client_server.outputProtocolFactory.getProtocol(otrans)
    client_server.processor.process(iprot, oprot)
    return make_response(otrans.getvalue())


# The endpoint for files requested by a specific client, including rendered source files.
@client_app.route("/client/<int:id>/<path:url_path>")
def client_data(id, url_path):
    # See if we rendered this file by comparing the ``url_path`` with the stored file path.
    file_path, html = handler.render_manager.get_render_results(id)
    send_file_kwargs = {}
    if renderer.path_to_uri(file_path) == url_path:
        # Yes, so return the rendered version.
        if html is None:
            # If it's a project, then ``html`` is None. In this case, the rendered HTML is already on disk at ``url_path``; however, don't allow Flask to cache this, since it changes with each edit.
            send_file_kwargs = dict(cache_timeout=0)
        else:
            return html

    # No, so assume it's a static file (such an as image).
    # TODO: check for a renderable file.
    try:
        # TODO SECURITY: if a web app, need to limit the base directory. This is a security hole.
        return send_file(url_path, **send_file_kwargs)
    except FileNotFoundError:
        abort(404)


# Run both servers. This does not (usually) return.
def run_servers():
    # Both servers block when run, so place them in a thread.
    editor_plugin_thread = threading.Thread(target=editor_plugin_server)
    editor_plugin_thread.start()

    # While we can also pass ``kwargs=dict(debug=True)``, this doesn't work since Flask isn't running in the main thread.
    client_thread = threading.Thread(target=client_app.run)
    client_thread.start()

    # Start the render loop in the main thread.
    render_manager = renderer.RenderManager()
    handler.render_manager = render_manager
    # TODO: Remove ``debug=True`` for production code.
    render_manager.run(debug=True)

    # Wait forever...
    editor_plugin_thread.join()
    client_thread.join()
