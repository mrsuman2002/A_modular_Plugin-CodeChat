# ****************************************************
# |docname| - Tests for `../CodeChat_Server/server.py`
# ****************************************************
#
# Imports
# =======
# These are listed in the order prescribed by `PEP 8`_.
#
# Standard library
# ----------------
import socketserver

# Third-party imports
# -------------------
# None.
#
# Local imports
# -------------
from CodeChat_Server.server import is_port_in_use


def test_1():
    # Pick a random, unused port to test. First, make sure it's actually unused.
    port = 6000
    assert is_port_in_use(port) is False

    # Open a port, so that it's in use.
    with socketserver.TCPServer(("localhost", port), socketserver.BaseRequestHandler):
        assert is_port_in_use(port) is True
