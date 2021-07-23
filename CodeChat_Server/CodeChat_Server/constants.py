# *********************
# |docname| - Constants
# *********************
#
# The port used for an HTTP connection from the CodeChat Client to the CodeChat Server.
HTTP_PORT = 5000
# .. _CodeChat service port:
#
# The port used for the Thrift connection between text editor/IDE extensions/plugins and the CodeChat Server. All editor/IDE plugins must use this port to access CodeChat services.
THRIFT_PORT = 9090

# The port used by a websocket connection between the CodeChat Server and the CodeChat Client.
WEBSOCKET_PORT = 5001

# The network address used by all servers in the CodeChat Server.
LOCALHOST = "127.0.0.1"
