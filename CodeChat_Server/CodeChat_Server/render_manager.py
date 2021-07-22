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
# **************************************************
# |docname| - Render manager for the CodeChat Server
# **************************************************
# The render manager takes rendering requests send from the Thrift interface of the CodeChat Server, renders them, then sends the results to the associated CodeChat Client.
#
# Imports
# =======
# Library imports
# ---------------
from . import LOCALHOST
import asyncio
from enum import Enum
import json
from pathlib import Path
import sys
import threading
from typing import (
    Any,
    cast,
    Callable,
    Coroutine,
    Dict,
    Optional,
    Union,
)
import urllib.parse

# Third-party imports
# -------------------
import websockets

# Local imports
# -------------
from .renderer import render_file


# RenderManager / render thread
# ==============================
# Constants
# =========
# The port used by a websocket connection between the CodeChat Server and the CodeChat Client.
WEBSOCKET_PORT = 5001


# .. _GetResultType Py:
#
# These must match the `constants in the client <GetResultType JS>`.
class GetResultType(Enum):
    # A URL indicating that new rendered content is available.
    url = 0
    # A build output message.
    build = 1
    # Errors from the build.
    errors = 2
    # A command, such as ``shutdown```.
    command = 3


# Utilities
# =========
def GetResultReturn(get_result_type: GetResultType, text: str):
    return {"get_result_type": get_result_type.value, "text": text}


# Convert a path to a URI component: make it absolute and use forward (POSIX) slashes. If the provided ``file_path`` is falsey, just return it.
def path_to_uri(file_path: str):
    return Path(file_path).resolve().as_posix() if file_path else file_path


# Store data for about each client.
class ClientState:
    def __init__(self):
        # A queue of messages for the client.
        self.q = asyncio.Queue()

        # The remaining data in this class should only be accessed by rendering thread.
        #
        # The most recent HTML and editor text after rendering the specified file_path.
        self._html = None
        self._editor_text = None
        self._file_path = None

        # A flag to indicate if this has been placed in the renderer's job queue.
        self._in_job_q = False
        # A flag to indicate that this client has work to perform.
        self._needs_processing = True

        # A bucket to hold text and the associated file to render.
        self._to_render_editor_text = None
        self._to_render_file_path = None
        self._to_render_is_dirty = None

        # A bucket to hold a sync request.
        #
        # The index into either the editor text or HTML converted to text.
        self._to_sync_index = None
        self._to_sync_from_editor = None
        # The HTML converted to text.
        self._html_as_text = None

        # Shutdown is tricky; see `this discussion <shut down an editor client>`_.
        #
        # A flag to request the worker to delete this client.
        self._is_deleting = False


# The render manager sets this event when it is ready.
render_manager_ready_event = threading.Event()


# Use the contents of the provided ClientState to perform a render.
async def render_client_state(cs: ClientState) -> None:
    # Provide a coroutine used by converters to write build results.
    def co_build(_str: str) -> Coroutine[Any, Any, None]:
        return cs.q.put(
            GetResultReturn(
                GetResultType.build,
                _str,
            )
        )

    is_converted, rendered_file_path, html, err_string = await render_file(
        cs._to_render_editor_text,
        cs._to_render_file_path,
        co_build,
        cs._to_render_is_dirty,
    )

    if not is_converted:
        return

    cs._file_path = rendered_file_path
    cs._html = html
    cs._editor_text = cs._to_render_editor_text

    # Send any errors. An empty error string will clear any errors from a previous build, and should still be sent.
    await cs.q.put(GetResultReturn(GetResultType.errors, err_string))

    # Sending the HTML signals the end of this build.
    #
    # For Windows, make the path contain forward slashes.
    uri = path_to_uri(cs._file_path)
    # Encode this, for Windows paths which contain a colon (or unusual Linux paths).
    await cs.q.put(GetResultReturn(GetResultType.url, urllib.parse.quote(uri)))


class RenderManager:
    # Provide a way to perform thread-safe access of methods in this class.
    def __getattr__(self, name: str) -> Callable:
        if name.startswith("threadsafe_"):
            # Strip off ``threadsafe`` and look for the function.
            internal_func = self.__getattr__(name[11:])

            # Invoke it as an async if needed.
            async def async_wrap(*args, **kwargs):
                return internal_func(*args, **kwargs)

            # See if we need to wrap this in an async.
            async_func = (
                internal_func
                if asyncio.iscoroutinefunction(internal_func)
                else async_wrap
            )

            # Wrap the async func in a threadsafe call.
            def threadsafe_async(*args, **kwargs):
                future = asyncio.run_coroutine_threadsafe(
                    async_func(*args, **kwargs), self._loop
                )
                return future.result()

            return threadsafe_async

        # Not found. Let Python raise the exception for us.
        return self.__getattribute__(name)

    # Determine if the provided id exists and is not being deleted. Return the ClientState for the id if so; otherwise, return False.
    def get_client_state(self, id: int) -> Union[bool, ClientState]:
        cs = self._client_state_dict.get(id)
        # Signal an error if this client doesn't exist or is being deleted; otherwise, return it.
        return cs if cs and not cs._is_deleting else False

    # Add the provided client to the job queue.
    def _enqueue(self, id: int) -> None:
        # Add to the job queue unless it's already there.
        cs = self._client_state_dict[id]
        cs._needs_processing = True
        if not cs._in_job_q:
            self._job_q.put_nowait(id)
            cs._in_job_q = True

    # Create a new client. Returns the client id on success or False on failure. The client may optionally provide an id for a new client.
    def create_client(self, id: Optional[int] = None) -> int:
        if self._is_shutdown:
            return -1
        if id is None:
            self._last_id += 1
            id = self._last_id
        if id in self._client_state_dict:
            # Indicate failure if this id exists.
            return False
        self._client_state_dict[id] = ClientState()
        return id

    def delete_client(self, id: int) -> bool:
        cs = self.get_client_state(id)
        if cs:
            cs = cast(ClientState, cs)
            # Tell the worker to delete this.
            self._enqueue(id)
            cs._is_deleting = True
            return True
        else:
            return False

    # Place the item in the render queue; must be called from another (non-render) thread. Returns True on success, or False if the provided id doesn't exist.
    def start_render(
        self, editor_text: str, file_path: str, id: int, is_dirty: bool
    ) -> bool:
        cs = self.get_client_state(id)
        if not cs:
            # Signal an error for an invalid client id.
            return False
        assert isinstance(cs, ClientState)

        # Add to the job queue.
        self._enqueue(id)

        # Update the job parameters.
        cs._to_render_editor_text = editor_text
        cs._to_render_file_path = file_path
        cs._to_render_is_dirty = is_dirty

        # Indicate success
        return True

    # Get a client's queue.
    def get_queue(self, id: int) -> Optional[asyncio.Queue]:
        cs = self.get_client_state(id)
        return cast(ClientState, cs).q if cs else None

    # Return the results of rendering the provided URL:
    #
    # - If the URL matches with the latest render, return the resulting HTML for a non-project render. Return ``None`` for a project render, indicating that the render was stored to disk and the URL is a path to the rendered file.
    # - If there's no match to the URL or the ID doesn't exist, return False. Note that the "HTML" can be None, meaning
    def get_render_results(self, id: int, url_path: str) -> Union[None, str, bool]:
        cs = self.get_client_state(id)
        return (
            cast(ClientState, cs)._html
            if cs and path_to_uri(cast(ClientState, cs)._file_path) == url_path
            else False
        )

    # Communicate with a CodeChat Client via a websocket.
    async def websocket_handler(
        self, websocket: websockets.WebSocketServerProtocol, path: str
    ):
        # First, read this client's ID.
        try:
            data = await websocket.recv()
        except websockets.exceptions.WebSocketException:
            # Give up if there's a websocket error.
            return

        # Find the queue for this client.
        try:
            id = json.loads(data)
        except json.decoder.JSONDecodeError:
            id = f"<invalid id {repr(data)}>"
        q = self.get_queue(id)
        if not q:
            try:
                await websocket.send(
                    json.dumps(
                        GetResultReturn(
                            GetResultType.command, f"error: unknown client {id}."
                        )
                    )
                )
            except websockets.exceptions.WebSocketException:
                # Ignore any errors here, since we're closing the socket anyway.
                pass
            return

        # Send messages until shutdown.
        while not self._is_shutdown:
            ret = await q.get()
            try:
                await websocket.send(json.dumps(ret))
            except websockets.exceptions.WebSocketException:
                # An error occurred -- close the websocket. The client will open another, so we can try again.
                return

            # Delete the client if this was a shutdown command.
            if (ret["get_result_type"] == GetResultType.command.value) and (
                ret["text"] == "shutdown"
            ):
                # Check that the queue is empty
                if not q.empty():
                    print(
                        "CodeChat warning: client id {} shut down with pending commands.".format(
                            id
                        ),
                        file=sys.stderr,
                    )
                # Request a client deletion.
                assert self.delete_client(id)

    # Shut down a CodeChat Client.
    async def shutdown_client(self, id: int) -> bool:
        q = self.get_queue(id)
        # Fail if the ID is unknown.
        if not q:
            return False
        # Send the shutdown command to the client.
        await q.put(GetResultReturn(GetResultType.command, "shutdown"))
        # In case the client is dead, shut down after a delay.
        asyncio.create_task(self._delete_client_later(id))
        # Indicate success.
        return True

    # Delete a CodeChat Client after a delay.
    async def _delete_client_later(self, id: int):
        await asyncio.sleep(1)
        if self.delete_client(id):
            print(f"Client {id} not responding -- deleted it.", file=sys.stderr)

    # Shut down the render manager, called from another thread.
    def threadsafe_shutdown(self):
        # We can't wait for a result, since this causes the asyncio event loop to exit, but the result must be retrieved from a Future running within the event loop. Therefore, call without waiting.
        self._loop.call_soon_threadsafe(asyncio.create_task, self.shutdown())

    # Shut down the render manager.
    async def shutdown(self):
        print("Render manager shutting down...", file=sys.stderr)
        self._is_shutdown = True
        # Stop each client. This will tell the web client to shut down and also delete the render client.
        for id in self._client_state_dict.keys():
            await self.shutdown_client(id)
        # A special case: there are no clients currently. Then, the code above did nothing, so shut the workers down now.
        if len(self._client_state_dict) == 0:
            for i in range(self._num_workers):
                await self._job_q.put(None)
        # Shut down the websocket.
        self.websocket_server.close()
        await self.websocket_server.wait_closed()

    # Start the render manager. This typically never returns.
    def run(self, *args, debug: bool = True) -> None:
        # The default Windows event loop doesn't support asyncio subprocesses.
        is_win = sys.platform.startswith("win")
        if is_win:
            asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

        asyncio.run(self._run(*args), debug=debug)
        print("Render manager is shut down.", file=sys.stderr)

    # Run the rendering thread with the given number of workers.
    async def _run(self, num_workers: int = 1) -> None:
        self._num_workers = num_workers
        # Create a queue of jobs for the renderer to process. This must be created from within the main loop to avoid ``got Future <Future pending> attached to a different loop`` errors.
        self._job_q: asyncio.Queue = asyncio.Queue()
        # Keep a dict of id: ClientState for each client.
        self._client_state_dict: Dict[int, ClientState] = {}
        # The next ID will be 0. Use the lock below to establish ownership before writing this.
        self._last_id = -1
        self._loop = asyncio.get_running_loop()
        self._is_shutdown = False

        self.websocket_server = await websockets.serve(
            self.websocket_handler, LOCALHOST, WEBSOCKET_PORT
        )
        # _`CODECHAT_READY`: let the user know that the server is now ready -- this is the last piece of it to start.
        print("The CodeChat Server is ready.\nCODECHAT_READY", file=sys.stderr)
        render_manager_ready_event.set()
        # Flush this since extension and test code waits for it before connecting to the server/running the rest of a test.
        sys.stdout.flush()
        await asyncio.gather(*[self._worker(i) for i in range(num_workers)])

    # Process items in the render queue.
    async def _worker(self, worker_index: int) -> None:
        while True:
            # Get an item to process.
            id = await self._job_q.get()
            # Check for shutdown.
            if id is None:
                print(f"Render worker {worker_index} is shut down.", file=sys.stderr)
                break
            cs = self._client_state_dict[id]
            assert cs._in_job_q
            # Every item in the queue should have some work to do.
            assert cs._needs_processing
            # Indicate that the current jobs in this ClientState will all be completed.
            cs._needs_processing = False

            # If the client should be deleted, ignore all other requests.
            if cs._is_deleting:
                del self._client_state_dict[id]
                # If there are no more clients, shut down.
                if len(self._client_state_dict) == 0:
                    self.shutdown()
            else:
                # Sync first.
                # TODO: sync.

                # Render next.
                await render_client_state(cs)

                # If this client received more work to do while working on the current job, add it back to the queue -- it can't safely be added to the queue while in the job is in process. Otherwise, we would potentially allow two workers to render the same job in parallel, which would confuse the renderer.
                if cs._needs_processing:
                    self._job_q.put_nowait(id)
                else:
                    cs._in_job_q = False
