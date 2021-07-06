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
from pathlib import Path
from time import sleep
import socketserver
import subprocess
import sys

# Third-party imports
# -------------------
import pytest
import requests
from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol

# Local imports
# -------------
from CodeChat_Server.__main__ import parse_args
from CodeChat_Server.server import HTTP_PORT, THRIFT_PORT
from CodeChat_Server.render_manager import (
    WEBSOCKET_PORT,
    GetResultType,
    GetResultReturn,
)
from CodeChat_Server.gen_py.CodeChat_Services import EditorPlugin
from CodeChat_Server.gen_py.CodeChat_Services.ttypes import RenderClientReturn
import websockets


# Constants
# =========
HTTP_ADDRESS = f"http://localhost:{HTTP_PORT}/"
WEBSOCKET_ADDRESS = f"ws://localhost:{WEBSOCKET_PORT}"


# Fixtures
# ========
SUBPROCESS_SERVER_ARGS = ([sys.executable, "-m", "CodeChat_Server"],)
SUBPROCESS_SERVER_KWARGS = dict(
    stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
)


@pytest.fixture
def editor_plugin():
    p = subprocess.Popen(*SUBPROCESS_SERVER_ARGS, **SUBPROCESS_SERVER_KWARGS)
    # Wait for the server to start.
    out = ""
    line = ""
    print("Waiting for the server to start...")
    while "CODECHAT_READY\n" not in line:
        p.stdout.flush()
        line = p.stdout.readline()
        out += line
        print(line, end="")
        if p.poll() is not None:
            # The server shut down.
            print(p.stdout.read())
            print(p.stderr.read())
            assert False
        sleep(0.1)
    print("done.\n")

    transport = TSocket.TSocket("localhost", THRIFT_PORT)
    transport = TTransport.TBufferedTransport(transport)
    protocol = TBinaryProtocol.TBinaryProtocol(transport)
    client = EditorPlugin.Client(protocol)
    transport.open()

    # Provide the subprocess.
    client.subprocess = p
    yield client

    # If tests already shut down the server, skip telling it to shut down.
    if p.poll() is None:
        client.shutdown_server()
        p.wait()
    print(p.stdout.read())
    print(p.stderr.read())
    transport.close()


# Tests
# =====
#
#
# Editor plug-in
# --------------
def test_1():
    # Open a port, so that it's in use.
    with socketserver.TCPServer(
        ("localhost", HTTP_PORT), socketserver.BaseRequestHandler
    ):
        # Run the server.
        cp = subprocess.run(*SUBPROCESS_SERVER_ARGS, **SUBPROCESS_SERVER_KWARGS)
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
    assert editor_plugin.shutdown_server() == ""
    editor_plugin.subprocess.wait()


# CodeChat Client HTTP
# --------------------
# Make a request of a non-existent ID.
def test_4(editor_plugin):
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


def test_5(editor_plugin):
    asyncio.run(atest_5())


# Command line parsing
# --------------------
def test_6():
    assert vars(parse_args([])) == dict(
        watch=[],
        patterns=["*"],
        ignore_patterns=[],
        build=[],
    )

    assert vars(parse_args(["--watch"])) == dict(
        watch=[str(Path(".").absolute())],
        patterns=["*"],
        ignore_patterns=[],
        build=[],
    )

    assert vars(parse_args(["--watch", "1"])) == dict(
        watch=["1"],
        patterns=["*"],
        ignore_patterns=[],
        build=[],
    )

    assert vars(parse_args(["--watch", "--watch", "1"])) == dict(
        watch=["1"],
        patterns=["*"],
        ignore_patterns=[],
        build=[],
    )

    assert vars(
        parse_args(
            [
                "--watch",
                "1",
                "--pattern",
                "*.txt",
                "*.rst",
                "--ignore-pattern",
                "*.html",
            ]
        )
    ) == dict(
        watch=["1"],
        patterns=["*.txt", "*.rst"],
        ignore_patterns=["*.html"],
        build=[],
    )

    assert vars(parse_args(["--build", "5"])) == dict(
        watch=[],
        patterns=["*"],
        ignore_patterns=[],
        build=["5"],
    )
