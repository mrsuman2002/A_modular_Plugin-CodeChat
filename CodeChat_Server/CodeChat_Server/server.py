# .. Copyright (C) 2012-2020 Bryan A. Jones.
#
#   This file is part of the CodeChat system.
#
#   The CodeChat system is free software: you can redistribute it and/or
#   modify it under the terms of the GNU General Public License as
#   published by the Free Software Foundation, either version 3 of the
#   License, or (at your option) any later version.
#
#   The CodeChat system is distributed in the hope that it will be
#   useful, but WITHOUT ANY WARRANTY; without even the implied warranty
#   of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
#   General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with the CodeChat system.  If not, see
#   <http://www.gnu.org/licenses/>.
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
import time
from typing import Union
import webbrowser

# Third-party imports
# -------------------
from flask import (
    Flask,
    request,
    Response,
    make_response,
    render_template,
    send_file,
    abort,
)
from thrift.protocol import TJSONProtocol  # type: ignore
from thrift.server import TServer  # type: ignore
from thrift.transport import TTransport  # type: ignore
from thrift.transport import TSocket
from thrift.protocol import TBinaryProtocol
from werkzeug.serving import make_server


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
        self.render_manager: renderer.RenderManager

    # _`get_client`: Return the HTML for a web client.
    def get_client(self, codeChat_client_location: int) -> RenderClientReturn:
        print(
            "get_client({})".format(
                CodeChatClientLocation._VALUES_TO_NAMES[codeChat_client_location]
            )
        )
        id = self.render_manager.create_client()
        # Get the next ID.
        if id is None:
            ret = RenderClientReturn("", -1, "Duplicate id {}".format(id))
            print("  => {}".format(ret))
            return ret
        if id < 0:
            ret = RenderClientReturn("", -1, "Server is shutting down.")
            print("  => {}".format(ret))
            return ret

        # Return what's requested.
        url = "http://127.0.0.1:5000/client?id={}".format(id)
        if codeChat_client_location == CodeChatClientLocation.url:
            # Just return the URL.
            ret_str = url
        elif codeChat_client_location == CodeChatClientLocation.html:
            # Redirect to the webserver.
            ret_str = """
<!DOCTYPE html>
<html>
    <head>
    </head>
    <body style="margin: 0px; padding: 0px; overflow: hidden">
        <iframe src="{}" style="width: 100%; height: 100vh; border: none"></iframe>
    </body>
</html>""".format(
                url
            )
        elif codeChat_client_location == CodeChatClientLocation.browser:
            # Open in an external browser.
            webbrowser.open(url, 1)
            ret_str = ""
        else:
            ret = RenderClientReturn(
                "", -1, "Unknown command {}".format(codeChat_client_location)
            )
            print("  => {}".format(ret))
            return ret

        ret = RenderClientReturn(ret_str, id, "")
        print("  => {}".format(ret))
        return ret

    # Render the provided text to HTML, then enqueue it for the web view.
    def start_render(self, text: str, path: str, id: int, is_dirty: bool) -> str:
        print(
            "start_render(path={}, id={}, is_dirty={}, html=\n{}...)\n".format(
                path, id, is_dirty, text[:80]
            )
        )
        if self.render_manager.start_render(text, path, id, is_dirty):
            # Indicate success.
            print(" => (empty string)")
            return ""
        else:
            ret = "Unknown client id {}".format(id)
            print(" => {}".format(ret))
            return ret

    # Pass rendered results back to the web view.
    def get_result(self, id: int) -> GetResultReturn:
        print("get_result(id={})".format(id))
        q = self.render_manager.get_queue(id)
        if not q:
            ret = GetResultReturn(
                GetResultType.command, "error: unknown client id {}".format(id)
            )
            print("  => {}".format(ret))
            return ret
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
            # Request a `client deletion`_.
            self.render_manager.delete_client(id)
        print("  => {}".format(ret))
        return ret

    # _`Shut down an editor client`. The sequence is:
    #
    # #.    _`Client stop`: send a message to the web client, informing it of the shutdown. While the editor shouldn't make any more ``start_render`` or ``stop_client`` calls, doing so won't cause the server to misbehave.
    # #.    _`Client deletion`: when the web client receives the shutdown message, tell the renderer to delete its ClientState. Since the ClientState contains the queue with the shutdown message, it shouldn't be deleted until the message is sent.
    #
    # This method performs the first step; ``get_result`` performs the second.
    def stop_client(self, id: int) -> str:
        print("stop_client(id={})".format(id))
        q = self.render_manager.get_queue(id)
        if not q:
            ret = "unknown client {}.".format(id)
            print("  => {}".format(ret))
            return ret
        # Send the shutdown command to the client.
        q.put(GetResultReturn(GetResultType.command, "shutdown"))
        # Indicate success.
        print("  => (empty string)")
        return ""


# Instantiate this class, which will be used by both servers.
handler = CodeChatHandler()


# Servers
# =======
#
# Server for the CodeChat editor plugin
# -------------------------------------
def editor_plugin_server() -> None:
    transport = TSocket.TServerSocket(host="127.0.0.1", port=9090)
    tfactory = TTransport.TBufferedTransportFactory()
    pfactory = TBinaryProtocol.TBinaryProtocolFactory()
    processor = EditorPlugin.Processor(handler)

    # This server spawns a thread per connection.
    ## server = TServer.TThreadedServer(processor, transport, tfactory, pfactory)
    # Spawns up to 10 threads by default, then uses those. Mark these threads as daemon, so they will be terminated on program exit.
    server = TServer.TThreadPoolServer(
        processor, transport, tfactory, pfactory, daemon=True
    )
    # For simplicity, we can use:
    # server = TServer.TSimpleServer(processor, transport, tfactory, pfactory)
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
def client_html() -> str:
    return render_template("CodeChat_client.html")


# The endpoint for the CodeChat client service.
@client_app.route("/client", methods=["POST"])
def client_service() -> Response:
    itrans = TTransport.TMemoryBuffer(request.data)
    otrans = TTransport.TMemoryBuffer()
    iprot = client_server.inputProtocolFactory.getProtocol(itrans)
    oprot = client_server.outputProtocolFactory.getProtocol(otrans)
    client_server.processor.process(iprot, oprot)
    return make_response(otrans.getvalue())


# The endpoint for files requested by a specific client, including rendered source files.
@client_app.route("/client/<int:id>/<path:url_path>")
def client_data(id: int, url_path: str) -> Union[str, Response]:
    # See if we rendered this file.
    html = handler.render_manager.get_render_results(id, url_path)
    # If we have rendered HTML, return it.
    if html:
        assert isinstance(html, str)
        return html

    # If this render was a project, then ``html`` is None. In this case, the rendered HTML is already on disk at ``url_path``; however, don't allow Flask to cache this, since it changes with each edit.
    send_file_kwargs = dict(cache_timeout=0) if html is None else {}

    # Send a static file or a 404 if nothing was found.
    try:
        # TODO SECURITY: if a web app, need to limit the base directory to wherever projects are placed on disk.
        return send_file(url_path, **send_file_kwargs)  # type: ignore
    except (FileNotFoundError, PermissionError):
        abort(404)


# Main code
# =========
# Run both servers. This does not (usually) return.
def run_servers() -> None:
    # Both servers block when run, so place them in a thread. Mark the Thrift server as a daemon, so it will be killed when the program shuts down.
    editor_plugin_thread = threading.Thread(target=editor_plugin_server, daemon=True)
    editor_plugin_thread.start()

    # Taken from https://stackoverflow.com/a/45017691.
    flask_server_thread = threading.Thread(target=client_app.run, daemon=True)
    flask_server_thread.start()

    # Start the render loop in another thread.
    render_manager = renderer.RenderManager()
    handler.render_manager = render_manager
    render_manager_thread = threading.Thread(target=render_manager.run)
    render_manager_thread.start()

    # Run the servers in threads until a user-requested shutdown occurs.
    try:
        while True:
            time.sleep(100)
    except KeyboardInterrupt:
        pass

    print("Shutting down...")
    # This will prevent future editor or web requests from being serviced.
    render_manager.shutdown()
    # When this is done, the Flask server and editor plugin sever can be shut down, since they're idle. Since they're daemons, they'll be shut down by exiting main.
    render_manager_thread.join()
