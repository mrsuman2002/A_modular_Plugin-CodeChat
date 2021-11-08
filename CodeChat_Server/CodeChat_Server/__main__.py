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
import asyncio
import os
from pathlib import Path
import sys
import subprocess
import threading
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
from .constants import LOCALHOST, THRIFT_PORT
from .gen_py.CodeChat_Services import EditorPlugin
from .gen_py.CodeChat_Services.ttypes import (
    CodeChatClientLocation,
)


# Utilities
# =========
def get_client() -> EditorPlugin.Client:
    socket = TSocket.TSocket(LOCALHOST, THRIFT_PORT)
    transport = TTransport.TBufferedTransport(socket)
    protocol = TBinaryProtocol.TBinaryProtocol(transport)
    client = EditorPlugin.Client(protocol)
    transport.open()
    return client


# Return the file's contents if it exists, or an empty string if not.
def file_text(path_to_file: Path) -> str:
    try:
        with open(path_to_file, encoding="utf-8", errors="backslashreplace") as f:
            return f.read()
    except Exception:
        return ""


# Watcher client
# ==============
# Provide a simple class to invoke a build when the file system watcher sends an event.
class WatcherClient:
    def __init__(
        self,
        directories: Sequence[Path],
        patterns: Sequence[str],
        ignore_patterns: Sequence[str],
    ):
        self.observer = Observer()
        self.thrift_client = get_client()

        # Request a client ID.
        try:
            ret = self.thrift_client.get_client(CodeChatClientLocation.browser)
        except ConnectionResetError as e:
            print(f"Unable to connect to the CodeChat Server: {e}.", file=sys.stderr)
            sys.exit(1)
        if ret.error:
            print(
                f"Error connecting to the CodeChat Server: {ret.error}.",
                file=sys.stderr,
            )
            sys.exit(1)
        assert ret.html == ""
        self.client_id = ret.id

        # See the `docs <https://watchdog.readthedocs.io/en/latest/api.html#watchdog.events.PatternMatchingEventHandler>`__. Rather than derive a separate class, just add a method to this instance.
        self.event_handler = PatternMatchingEventHandler(patterns, ignore_patterns)
        self.event_handler.on_any_event = self.on_any_event

        for pathname in set(directories):
            # See the `docs <https://watchdog.readthedocs.io/en/latest/api.html#watchdog.observers.api.BaseObserver.schedule>`__.
            self.observer.schedule(self.event_handler, pathname, recursive=True)
        self.observer.start()
        print(
            f"Watcher started, monitoring the path(s) {directories} containing patterns {patterns} but ignoring {ignore_patterns}.",
            file=sys.stderr,
        )

    # See the `docs <https://watchdog.readthedocs.io/en/latest/api.html#watchdog.events.FileSystemEventHandler.on_any_event>`__.
    def on_any_event(self, event: FileSystemEvent):
        if not event.is_directory:
            print(event, event.src_path, file=sys.stderr)
            src_path = Path(event.src_path).absolute()
            with open(src_path, encoding="utf-8", errors="backslashreplace") as f:
                try:
                    ret = self.thrift_client.start_render(
                        f.read(), str(src_path), self.client_id, False
                    )
                except TTransport.TTransportException as e:
                    print(
                        f"Unable to communicate with the CodeChat Server when requesting a render: {e}.",
                        file=sys.stderr,
                    )
                    self.running = False
                else:
                    if ret:
                        print(
                            f"Error requesting a render from the CodeChat Server: {ret}.",
                            file=sys.stderr,
                        )
                        self.running = False

    def run(self):
        self.running = True
        try:
            while self.running:
                sleep(1)
        except KeyboardInterrupt:
            pass
        self.shutdown()

    def shutdown(self):
        print("Watcher shutting down...", file=sys.stderr)
        try:
            ret = self.thrift_client.stop_client(self.client_id)
        except TTransport.TTransportException as e:
            print(
                f"Unable to communicate when the CodeChat Server when shutting down the CodeChat Client: {e}."
            )
        else:
            if ret:
                print(f"Error shutting down the CodeChat Client: {ret}.")
        self.observer.stop()
        self.observer.join()
        print("Watcher shut down.", file=sys.stderr)


# CLI interface
# =============
app = typer.Typer()


@app.command()
def start(
    coverage: bool = typer.Option(False, help="Run with code coverage enabled.")
) -> None:
    "Start the server."

    sys.exit(_start(coverage))


# Typer's default arguments don't work when called directly from Python. This avoid provides a function which returns a value (0 for success, a non-zero value for failure), instead of calling ``sys.exit()``. The following CLI functions follow this pattern as well.
def _start(coverage=False) -> int:
    print(
        "Starting the server -- searching for an already-running instance...",
        file=sys.stderr,
    )

    # Try pinging the server to see if it's up.
    try:
        client = get_client()
        assert client.ping() == ""
        print("A running CodeChat Server instance was found.", file=sys.stderr)
        return 0
    except Exception:
        print("No running CodeChat Server instances found.", file=sys.stderr)

    # The server isn't up or has crashed. Stop any existing instances in case it crashed.
    ret = _stop()
    if ret:
        return ret

    # Start the server, now that any hung instances are terminated.
    cov_args = ["-m", "coverage", "run"] if coverage else []
    p = subprocess.Popen(
        [sys.executable, *cov_args, "-m", "CodeChat_Server", "serve"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    # Terminate the server after 5 seconds if it doesn't start.
    server_starting = True

    def timeout():
        sleep(10)
        if server_starting:
            p.terminate()
            print(
                "The server failed to start before the timeout expired.",
                file=sys.stderr,
            )

    # Make this a daemon thread, so it will exit when the main thread finishes.
    timeout_thread = threading.Thread(target=timeout, daemon=True)
    timeout_thread.start()

    # Wait for the server to start.
    print("Waiting for the server to start...", file=sys.stderr)
    out = ""
    line = ""
    while "CODECHAT_READY\n" not in line:
        # To make mypy happy.
        assert p.stderr is not None
        p.stderr.flush()
        line = p.stderr.readline()
        out += line
        print(line, end="")
        if p.poll() is not None:
            # The server shut down. Print the output collected to help the user understand what went wrong.
            #
            # Make mypy happy.
            assert p.stdout is not None
            print(p.stdout.read())
            print(p.stderr.read())
            print("The server exited unexpectedly.", file=sys.stderr)
            return 1
        sleep(0.001)
    # Indicate the server started to the timeout thread, so the timeout won't kill the server now that it's started.
    server_starting = False
    return 0


@app.command()
def stop() -> None:
    "Stop the server."
    sys.exit(_stop())


def _stop() -> int:
    print("Stopping all CodeChat Server instances...", file=sys.stderr)
    # Look for the server. TODO: should I avoid hard-coding this?
    server_name = "CodeChat_Server"
    ret = 0
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
            # If we have the command line, then "serve" must be in it.
            and (not p.info["cmdline"] or "serve" in p.info["cmdline"])
        ):
            print(
                f"Killing server process {p.pid} named {p.info['name']} with command line {p.info['cmdline']}.",
                file=sys.stderr,
            )
            # Killing the parent of a CodeChat Server process will kill the child; ignore the exception in this case.
            try:
                p.kill()
            except psutil.NoSuchProcess:
                # Report an error, but continue trying to kill other processes first.
                ret = 1

    return ret


@app.command()
def serve() -> None:
    "Run the server in the current terminal/console."

    # This file takes a long time to load and run. Print a status message as it starts.
    print("Loading...", file=sys.stderr)
    from .server import run_servers

    sys.exit(run_servers())


@app.command()
def build(path_to_build: List[Path]) -> None:
    "Build the specified CodeChat project(s)."

    from .renderer import render_file

    async def aprint(_str):
        print(_str, end="")

    # Build each path provided.
    for ptb in path_to_build:
        ptb = ptb.resolve()
        print(f"Building {ptb}...", file=sys.stderr)
        (
            was_performed,
            rendered_project_path,
            rendered_file_path,
            html,
            err_string,
        ) = asyncio.run(render_file(file_text(ptb), str(ptb), None, aprint, False))
        assert was_performed
        # Print all errors produced by the render.
        print(err_string, file=sys.stderr)
        # Dump the HTML produced.
        if html is None:
            print(
                f"The rendered result is stored in {rendered_file_path}.",
                file=sys.stderr,
            )
        else:
            if ptb.is_file():
                print(html)
            else:
                print(
                    f"Error: file {ptb} not found, and no containing project to render was found.",
                    file=sys.stderr,
                )
                sys.exit(1)


@app.command()
def render(path_to_build: Path, id: int) -> None:
    "Render the specified CodeChat project in a web browser."

    print(f"Rendering {path_to_build} using ID {id}.", file=sys.stderr)
    ret = _start()
    if ret:
        sys.exit(ret)

    # Ensure the ID is negative.
    id = -abs(id) - 1

    # Request a render.
    path_to_build = path_to_build.resolve()
    thrift_client = get_client()
    thrift_client.start_render(file_text(path_to_build), str(path_to_build), id, False)


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
) -> None:
    "Watch the specified directories; perform a render when a matching file is changed."

    ret = _start()
    if ret:
        sys.exit(ret)

    wc = WatcherClient(paths, patterns, ignore_patterns)
    wc.run()


if __name__ == "__main__":
    app()
