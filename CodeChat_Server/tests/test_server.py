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
import asyncio
import json
import socketserver
import subprocess
from time import sleep

# Third-party imports
# -------------------
import pytest
import requests
from thrift.transport.TTransport import TTransportException

# Local imports
# -------------
from CodeChat_Server.constants import HTTP_PORT
from CodeChat_Server.gen_py.CodeChat_Services.ttypes import (
    RenderClientReturn,
    CodeChatClientLocation,
)
from CodeChat_Server.renderer import _render_CodeChat, _render_markdown, _render_ReST
from CodeChat_Server.render_manager import (
    WEBSOCKET_PORT,
    GetResultType,
    GetResultReturn,
)
from conftest import SUBPROCESS_SERVER_ARGS
import websockets


# Constants
# =========
HTTP_ADDRESS = f"http://localhost:{HTTP_PORT}/"
WEBSOCKET_ADDRESS = f"ws://localhost:{WEBSOCKET_PORT}"


# Tests
# =====
#
#
# Editor plug-in
# --------------
def test_1():
    subprocess.run(SUBPROCESS_SERVER_ARGS + ["stop"], check=True)
    # Open a port, so that it's in use.
    with socketserver.TCPServer(
        ("localhost", HTTP_PORT), socketserver.BaseRequestHandler
    ):
        # Run the server.
        cp = subprocess.run(
            SUBPROCESS_SERVER_ARGS + ["serve"], capture_output=True, text=True
        )
        # Check that it reported the ports were in use.
        assert "Error: ports " in cp.stdout


# Test the plugin with invalid parameters.
def test_2(editor_plugin):
    unknown_client = "Unknown client id 0."
    assert editor_plugin.start_render("", "", 0, False) == unknown_client
    assert editor_plugin.stop_client(0) == unknown_client

    assert editor_plugin.get_client(3) == RenderClientReturn(
        "", -1, "Invalid location 3"
    )


# Test the plugin shutdown.
def test_3(editor_plugin):
    rcr = editor_plugin.get_client(CodeChatClientLocation.html)
    assert rcr.error == ""
    assert editor_plugin.stop_client(rcr.id) == ""
    # Wait for the server to finish shutting down.
    sleep(2)
    # Make sure the server no longer responds to pings to verify it shut down.
    with pytest.raises(TTransportException):
        editor_plugin.ping()


# CodeChat Client HTTP
# --------------------
# Make a request of a non-existent ID.
def test_4(run_server):
    # Test on a file that doesn't exist.
    r = requests.get(HTTP_ADDRESS + "client/1/a file that does not exist")
    assert r.status_code == 404


# CodeChat Client websocket
# -------------------------
async def atest_5():
    # Test an invalid id.
    async with websockets.connect(WEBSOCKET_ADDRESS) as ws:
        await ws.send("boom")
        r = await ws.recv()
        assert json.loads(r) == GetResultReturn(
            GetResultType.command, "error: unknown client <invalid id 'boom'>."
        )

    # Test an unknown client.
    async with websockets.connect(WEBSOCKET_ADDRESS) as ws:
        await ws.send("1")
        r = await ws.recv()
        assert json.loads(r) == GetResultReturn(
            GetResultType.command, "error: unknown client 1."
        )


def test_5(run_server):
    asyncio.run(atest_5())


# Renderer tests
# --------------
def test_7():
    # Make sure a zero-input case works.
    assert _render_markdown("", "") == ("", "")

    assert _render_markdown("*hello*", "") == ("<p><em>hello</em></p>", "")


def test_8():
    # Make sure the zero-input case works.
    _render_ReST("", "")

    # Check basic error reporting.
    rst, err = _render_ReST("*hello", "")
    assert "Inline emphasis start-string without end-string." in err

    rst, err = _render_ReST("*hello*", "")
    assert "<em>hello</em>" in rst


# Requires updated CodeChat for this test to pass.
def xtest_9():
    # Make sure the zero-input case works.
    _render_CodeChat("", "")

    # Check basic error reporting.
    rst, err = _render_CodeChat("hello", "file.weird_name")
    assert "ERROR: this file is not supported by CodeChat." in err

    rst, err = _render_CodeChat("// *hello*", "foo.c")
    assert "<em>hello</em>" in rst


def test_10():
    pass
