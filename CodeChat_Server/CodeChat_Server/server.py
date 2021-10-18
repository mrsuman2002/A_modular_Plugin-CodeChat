# .. Copyright (C) 2012-2020 Bryan A. Jones.
#
#   This file is part of the CodeChat System.
#
#   The CodeChat System is free software: you can redistribute it and/or
#   modify it under the terms of the GNU General Public License as
#   published by the Free Software Foundation, either version 3 of the
#   License, or (at your option) any later version.
#
#   The CodeChat System is distributed in the hope that it will be
#   useful, but WITHOUT ANY WARRANTY; without even the implied warranty
#   of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
#   General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with the CodeChat System.  If not, see
#   <http://www.gnu.org/licenses/>.
#
# *******************************
# |docname| - The CodeChat Server
# *******************************
# The CodeChat Server receives requests from the editor/IDE, renders these, then displays them in the CodeChat Client; likewise, it listens for CodeChat Client requests, processes them, and forwards the results to the editor/IDE.
#
#
# Imports
# =======
# These are listed in the order prescribed by `PEP 8
# <http://www.python.org/dev/peps/pep-0008/#imports>`_.
#
# Standard library
# ----------------
import logging
import signal
import socket
import sys
from textwrap import dedent
import threading
import webbrowser

# Third-party imports
# -------------------
from flask import (
    Flask,
    Response,
    make_response,
    render_template,
    send_file,
    abort,
)
from thrift.server import TServer
from thrift.transport import TTransport
from thrift.transport import TSocket
from thrift.protocol import TBinaryProtocol


# Local application imports
# -------------------------
from . import __version__
from . import render_manager
from .constants import HTTP_PORT, LOCALHOST, THRIFT_PORT, WEBSOCKET_PORT
from .gen_py.CodeChat_Services import EditorPlugin
from .gen_py.CodeChat_Services.ttypes import (
    RenderClientReturn,
    CodeChatClientLocation,
)

# Constants
# =========
UNKNOWN_CLIENT = "Unknown client id {}."

logger = logging.getLogger(__name__)


# Service provider
# ================
# This class implements the EditorPlugin service.
class CodeChatHandler:
    def __init__(self):
        self.render_manager: render_manager.RenderManager

    # _`get_client`: Return the HTML for a web client.
    def get_client(self, codeChat_client_location: int) -> RenderClientReturn:
        try:
            location_name = CodeChatClientLocation._VALUES_TO_NAMES[
                codeChat_client_location
            ]
        except KeyError:
            location_name = "invalid location"
        logger.info("get_client({})".format(location_name))
        id = self.render_manager.threadsafe_create_client()
        # Get the next ID.
        if id is None:
            ret = RenderClientReturn("", -1, "Duplicate id {}".format(id))
            logger.info("  => {}".format(ret))
            return ret
        if id < 0:
            ret = RenderClientReturn("", -1, "Server is shutting down.")
            logger.info("  => {}".format(ret))
            return ret

        # Return what's requested.
        url = "http://{}:{}/client?id={}".format(LOCALHOST, HTTP_PORT, id)
        if codeChat_client_location == CodeChatClientLocation.url:
            # Just return the URL.
            ret_str = url
        elif codeChat_client_location == CodeChatClientLocation.html:
            # Redirect to the webserver.
            ret_str = dedent(
                f"""\
                <!DOCTYPE html>
                <html>
                    <head>
                    </head>
                    <body style="margin: 0px; padding: 0px; overflow: hidden">
                        <iframe src="{url}" style="width: 100%; height: 100vh; border: none"></iframe>
                    </body>
                </html>"""
            )
        elif codeChat_client_location == CodeChatClientLocation.browser:
            # Open in an external browser.
            webbrowser.open(url, new=1, autoraise=True)
            ret_str = ""
        else:
            ret = RenderClientReturn(
                "", -1, "Invalid location {}".format(codeChat_client_location)
            )
            logger.info("  => {}".format(ret))
            return ret

        ret = RenderClientReturn(ret_str, id, "")
        logger.info("  => {}".format(ret))
        return ret

    # Indicate the server is alive.
    def ping(self) -> str:
        logger.info("ping()\n")
        if shutdown_event.is_set():
            # Indicate an error by returning a non-emptry string.
            return "Shutting down."
        return ""

    # Render the provided text to HTML, then enqueue it for the web view.
    def start_render(self, text: str, path: str, id: int, is_dirty: bool) -> str:
        logger.info(
            "start_render(path={}, id={}, is_dirty={}, html=\n{}...)\n".format(
                path, id, is_dirty, text[:80]
            )
        )
        if self.render_manager.threadsafe_start_render(text, path, id, is_dirty):
            # Indicate success.
            logger.info(" => (empty string)")
            return ""
        else:
            # If the client specified an non-existant ID, create it.
            if id < 0:
                if self.render_manager.threadsafe_create_client(id) != id:
                    ret = f"Duplicate id {id}."
                    logger.info(f" => {ret}")
                    return ret
                else:
                    # Since we just created this id, start the CodeChat Client in an external browser.
                    webbrowser.open(
                        "http://{}:{}/client?id={}".format(LOCALHOST, HTTP_PORT, id),
                        new=1,
                        autoraise=True,
                    )
                    # Try the render again.
                    if self.render_manager.threadsafe_start_render(
                        text, path, id, is_dirty
                    ):
                        # Indicate success.
                        logger.info(" => (empty string)")
                        return ""

            # Indicate an error.
            ret = UNKNOWN_CLIENT.format(id)
            logger.info(" => {}".format(ret))
            return ret

    # _`Shut down an editor client`. The sequence is complex. Here's a web of links which step throughs the process.
    #
    # _`Delete step 1.` `--> <Delete step 2.>` The editor/IDE invokes stop_client, which delegates to the render manager thread.
    def stop_client(self, id: int) -> str:
        logger.info("stop_client(id={})".format(id))
        ok = self.render_manager.threadsafe_shutdown_client(id)
        if not ok:
            ret = UNKNOWN_CLIENT.format(id)
            logger.info("  => {}".format(ret))
            return ret
        # Indicate success.
        logger.info("  => (empty string)")
        return ""


# Instantiate this class, which will be used by both servers.
handler = CodeChatHandler()


# Servers
# =======
#
# Server for the CodeChat editor plugin
# -------------------------------------
def editor_plugin_server() -> None:
    transport = TSocket.TServerSocket(host=LOCALHOST, port=THRIFT_PORT)
    tfactory = TTransport.TBufferedTransportFactory()
    pfactory = TBinaryProtocol.TBinaryProtocolFactory()
    processor = EditorPlugin.Processor(handler)

    # Spawns up to 10 threads by default, then uses those. Mark these threads as daemon, so they will be terminated on program exit.
    server = TServer.TThreadPoolServer(
        processor, transport, tfactory, pfactory, daemon=True
    )
    # Other options for the server:
    #
    # This server spawns a thread per connection.
    ## server = TServer.TThreadedServer(processor, transport, tfactory, pfactory)  # noqa: E266
    # A simpler server:
    ## server = TServer.TSimpleServer(processor, transport, tfactory, pfactory)  # noqa: E266

    try:
        server.serve()
    except Exception:
        # Shut down the server instead of allowing it to keep running in a broken state.
        shutdown_event.set()
        raise


# Server for the CodeChat Client
# ------------------------------
client_app = Flask(
    __name__,
    # Serve CodeChat Client files statically.
    static_url_path="/static",
    static_folder="CodeChat_Client/static",
    # Serve the CodeChat Client HTML as a template.
    template_folder="CodeChat_Client/templates",
)


# The endpoint to get the HTML for the CodeChat Client.
@client_app.route("/client")
def client_html() -> str:
    return render_template("CodeChat_client.html", WEBSOCKET_PORT=WEBSOCKET_PORT)


# The endpoint for files requested by a specific client, including rendered source files. Note that ``int`` by default is `positive only <https://werkzeug.palletsprojects.com/en/2.0.x/routing/#werkzeug.routing.IntegerConverter>`_.
@client_app.route("/client/<int(signed=True):id>/<path:url_path>")
def client_data(id: int, url_path: str) -> Union[str, Response]:
    # On Windows, the path begins with a drive letter; otherwise, the path begins with a ``/``, which gets absorbed into the ``/`` before the ``url_path`` component of the URL. Restore it.
    if not render_manager.is_win:
        url_path = "/" + url_path
    # See if we rendered this file.
    html = handler.render_manager.threadsafe_get_render_results(id, url_path)

    # If we have rendered HTML, return it.
    if type(html) == str:
        assert isinstance(html, str)
        response = make_response(html)
    else:
        # The file is on disk. Send it or a 404 if nothing was found.
        try:
            # Don't allow Flask to cache files on disk, since they may change with each edit.
            response = make_response(send_file(url_path, cache_timeout=0))  # type: ignore
        except (FileNotFoundError, PermissionError):
            abort(404)

    # Don't allow the browser to cache files. See the `Flask docs <https://flask.palletsprojects.com/en/1.1.x/api/#flask.Request.cache_control>`_ and `MDN docs <https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Cache-Control#Directives>`_.
    response.cache_control.no_store = True
    return response


# Main code
# =========
# When this event is ``set``, ``run_servers`` will shut down the servers and return.
shutdown_event = threading.Event()


# Handle signals by setting the shutdown event.
def signal_handler(signum, frame):
    shutdown_event.set()


# Handle exceptions in the same way.
def excepthook(type, value, traceback):
    shutdown_event.set()
    sys.__excepthook__(type, value, traceback)


# Run both servers. This does not (usually) return.
def run_servers() -> int:

    print(f"The CodeChat Server, v.{__version__}\n")
    logging.basicConfig(level=logging.INFO)

    # See if the required ports are in use, probably by another instance of this server.
    if (
        is_port_in_use(HTTP_PORT)
        or is_port_in_use(WEBSOCKET_PORT)
        or is_port_in_use(THRIFT_PORT)
    ):
        print(
            f"Error: ports {HTTP_PORT}, {WEBSOCKET_PORT}, and/or {THRIFT_PORT} are already in use.\n"
            "Hopefully, this means that the CodeChat Server is already running in another process.\n"
            "Exiting.\n"
        )
        return 1

    # Shut down if any unhandled exception occurs.
    sys.excepthook = excepthook

    # Both servers block when run, so place them in a thread. Mark the servers as a daemon, so they will be killed when the program shuts down.
    editor_plugin_thread = threading.Thread(
        target=editor_plugin_server, name="Editor plugin server", daemon=True
    )
    editor_plugin_thread.start()

    def flask_launcher(*args, **kwargs):
        try:
            client_app.run(*args, **kwargs)
        except Exception:
            # Shut down the server instead of allowing it to keep running in a broken state.
            shutdown_event.set()
            raise

    # Taken from https://stackoverflow.com/a/45017691.
    flask_server_thread = threading.Thread(
        target=flask_launcher, kwargs=dict(port=HTTP_PORT), name="Flask", daemon=True
    )
    flask_server_thread.start()

    # Start the render loop in another thread.
    handler.render_manager = render_manager.RenderManager(shutdown_event)
    render_manager_thread = threading.Thread(
        target=handler.render_manager.run, name="asyncio"
    )
    render_manager_thread.start()

    # On a signal, shut down gracefully.
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)

    # Run the servers in threads until a user-requested shutdown occurs.
    while True:
        # Ctrl+C is ignored while waiting, so use a 1 second poll.
        if shutdown_event.wait(1):
            # If the event is received, exit the loop in order to shut down. First, clear the event so the next invocation of this function will work correctly.
            shutdown_event.clear()
            break

    logger.info("Shutting down...")
    # This will prevent future editor or web requests from being serviced.
    handler.render_manager.threadsafe_shutdown()
    # When this is done, the Flask server and editor plugin sever can be shut down, since they're idle. Since they're daemons, they'll be shut down by exiting main.
    render_manager_thread.join()
    return 0


# Inspired by Stack Overflow. The original post used ``connect_ex``, which is very slow (~2 seconds).
def is_port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind((LOCALHOST, port))
        except OSError:
            return True
        return False
