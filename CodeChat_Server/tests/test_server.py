# ****************************************************
# |docname| - Tests for `../CodeChat_Server/server.py`
# ****************************************************
# TODO: create a CodeChat client. Use it to test the server. Import the event to shut down the server when needed. Run the server in a different thread from the fixture; drop all the subprocess stuff.
#
# Imports
# =======
# These are listed in the order prescribed by `PEP 8`_.
#
# Standard library
# ----------------
import socketserver
import subprocess
import sys

# Third-party imports
# -------------------
import pytest

# Local imports
# -------------
from CodeChat_Server.server import is_port_in_use


# Fixtures
# ========
@pytest.fixture
def run_servers():
    p = subprocess.Popen(
        [sys.argv[0], "-m", "CodeChat_Server"], stdin=subprocess.PIPE, text=True
    )
    yield
    p.communicate("q\n")
    p.wait()


def test_1():
    # Pick a random, unused port to test. First, make sure it's actually unused.
    port = 6000
    assert is_port_in_use(port) is False

    # Open a port, so that it's in use.
    with socketserver.TCPServer(("localhost", port), socketserver.BaseRequestHandler):
        assert is_port_in_use(port) is True
