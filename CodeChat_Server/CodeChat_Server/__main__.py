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
# ***********************************
# |docname| - Run the CodeChat Server
# ***********************************
# This parses command-line parameters then invokes the requested CodeChat System functionality.
#
# Imports
# =======
# These are listed in the order prescribed by `PEP 8
# <http://www.python.org/dev/peps/pep-0008/#imports>`_.
#
# Standard library
# ----------------
import os
from pathlib import Path
import subprocess
from time import sleep
from typing import List, Sequence

# Third-party imports
# -------------------
import psutil
from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol
import typer
from watchdog.observers import Observer
from watchdog.events import FileSystemEvent, PatternMatchingEventHandler

# Local application imports
# -------------------------
from . import THRIFT_PORT
from .gen_py.CodeChat_Services import EditorPlugin
from .gen_py.CodeChat_Services.ttypes import (
    CodeChatClientLocation,
)


# CLI interface
# =============
app = typer.Typer()


@app.command()
def start():
    "Start the server."

    print("Starting the server -- searching for an already-running instance...")

    # Try pinging the server to see if it's up.
    try:
        client = get_client()
        assert client.ping() == ""
        print("A running CodeChat Server instance was found.")
        return 0
    except Exception:
        print("No running CodeChat Server instances found.")

    # The server isn't up or has crashed. Stop any existing instances in case it crashed.
    stop()

    # Start the server, now that any hung instances are terminated.
    p = subprocess.Popen(
        ["CodeChat_Server", "serve"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
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
            print("The server failed to start.")
            return 1
        sleep(0.1)
    print("done.")
    return 0


@app.command()
def stop():
    "Stop the server."

    print("Stopping all CodeChat Server instances...")
    # Look for the server. TODO: should I avoid hard-coding this?
    server_name = "CodeChat_Server"
    # This code was copied from the `psutil docs <https://psutil.readthedocs.io/en/latest/#find-process-by-name>`_ then lightly modified.
    for p in psutil.process_iter(["cmdline", "exe", "name", "pid"]):
        if (
            server_name == p.info["name"]
            or p.info["exe"]
            and os.path.basename(p.info["exe"]) == server_name
            or p.info["cmdline"]
            # On Windows, sometimes the process cmdline contains ``C:\...\venv\Scripts\CodeChat_Server-script.py``. So, we need to search inside each of the cmdline strings.
            and any([server_name in x for x in p.info["cmdline"]])
        ) and (
            # Don't kill the current process (its parent is often a Python launcher).
            p.pid != os.getpid()
            and p.pid != os.getppid()
        ):
            print(
                f"Killing server process {p.pid} named {p.info['name']}   with command line {p.info['cmdline']}."
            )
            # Killing the parent of a CodeChat Server process will kill the child; ignore the exception in this case.
            try:
                p.kill()
            except psutil.NoSuchProcess:
                pass

    return 0


@app.command()
def serve():
    "Run the server in the current terminal/console."

    # This file takes a long time to load and run. Print a status message as it starts.
    print("Loading...")
    from .server import run_servers

    return run_servers()


@app.command()
def build(path_to_build: List[Path]):
    "Build the specified CodeChat project(s)."
    # TODO
    print(f"Building {path_to_build}...")


@app.command()
def render(path_to_build: Path, id: int):
    "Render the specified CodeChat project in a web browser."
    # TODO
    print(f"Rendering {path_to_build} using ID {id}.")


@app.command()
def watch(
    paths: List[Path] = typer.Option(
        [Path(".")], help="Directory(s) to watch for changes."
    ),
    patterns: List[str] = typer.Option(
        ["*"], help="Patterns of files to watch in the provided directory(s)."
    ),
    ignore_patterns: List[str] = typer.Option(
        [], help="Patterns of files to ignore in the provided directory(s)."
    ),
):
    "Watch the specified directories; perform a render when a matching file is changed."

    start()

    print(f"Watching {paths} for {patterns}, ignoring {ignore_patterns}.")


if __name__ == "__main__":
    app()


# Utilities
# =========
def get_client():
    transport = TSocket.TSocket("localhost", THRIFT_PORT)
    transport = TTransport.TBufferedTransport(transport)
    protocol = TBinaryProtocol.TBinaryProtocol(transport)
    client = EditorPlugin.Client(protocol)
    transport.open()
    return client


# Watcher client
# ==============
# Provide a simple class to invoke a build when the file system watcher sends an event.
class WatcherClient:
    def __init__(
        self,
        directories: Sequence[str],
        patterns: Sequence[str],
        ignore_patterns: Sequence[str],
    ):
        self.observer = Observer()
        self.thrift_client = get_client()

        # Request a client ID.
        ret = self.thrift_client.get_client(CodeChatClientLocation.browser)
        assert ret.error == ""
        assert ret.html == ""
        self.client_id = ret.id

        # See the `docs <https://watchdog.readthedocs.io/en/latest/api.html#watchdog.events.PatternMatchingEventHandler>`__. Rather than derive a separate class, just add a method to this instance.
        self.event_handler = PatternMatchingEventHandler(patterns, ignore_patterns)
        self.event_handler.on_any_event = self.on_any_event

        for pathname in set(directories):
            # See the `docs <https://watchdog.readthedocs.io/en/latest/api.html#watchdog.observers.api.BaseObserver.schedule>`__.
            self.observer.schedule(self.event_handler, pathname, recursive=True)
        self.observer.start()
        print("Watcher started.")

    # See the `docs <https://watchdog.readthedocs.io/en/latest/api.html#watchdog.events.FileSystemEventHandler.on_any_event>`__.
    def on_any_event(self, event: FileSystemEvent):
        if not event.is_directory:
            print(event, event.src_path)
            src_path = Path(event.src_path).absolute()
            with open(src_path, encoding="utf-8", errors="backslashreplace") as f:
                # TODO: check the return value, then do what on failure?
                self.thrift_client.start_render(
                    f.read(), str(src_path), self.client_id, False
                )

    def shutdown(self):
        if self.observer:
            print("Watcher shutting down...")
            self.thrift_client.stop_client(self.client_id)
            self.observer.stop()
            self.observer.join()
            print("Watcher shut down.")
