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
from time import sleep
import socketserver
import threading

# Third-party imports
# -------------------
import pytest

# Local imports
# -------------
from CodeChat_Server.server import run_servers, HTTP_PORT, shutdown_event


# Fixtures
# ========
@pytest.fixture
def run_servers_fixture(capsys):
    t = threading.Thread(target=run_servers, name="run_servers")
    t.start()
    # Wait for the server to start.
    out = ""
    while "Ready.\n" not in out:
        sleep(0.1)
        _out, err = capsys.readouterr()
        # Accumulate the characters -- prints may get chopped in pieces by thread switching. (Or the may not -- is print an atomic operation?)
        out += _out
    yield
    shutdown_event.set()
    t.join()


def test_1(capsys):
    # Open a port, so that it's in use.
    with socketserver.TCPServer(
        ("localhost", HTTP_PORT), socketserver.BaseRequestHandler
    ):
        # Run the server.
        assert run_servers() == 1
        # Check that it reported the ports were in use.
        out, err = capsys.readouterr()
        assert out.startswith("Error: ports ")


# For now, just test out the fixture.
def test_2(run_servers_fixture):
    pass
