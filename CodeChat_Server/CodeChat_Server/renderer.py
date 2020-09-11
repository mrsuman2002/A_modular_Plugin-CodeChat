# .. Copyright (C) 2012-2020 Bryan A. Jones.
#
#   This file is part of the CodeChat system.
#
#   The CodeChat system is free software: you can redistribute it and/or
#   modify it under the terms of the GNU General Public License as
#   published by the Free Software Foundation, either version 3 of the
#   License, or (at your option) any later version.
#
#   The CodeChat system is distributed in the hope that it will be
#   useful, but WITHOUT ANY WARRANTY; without even the implied warranty
#   of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
#   General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with the CodeChat system.  If not, see
#   <http://www.gnu.org/licenses/>.
#
# *********************************************
# |docname| - Renderers for the CodeChat server
# *********************************************
# These functions convert from a text to HTML for a variety of formats.
#
# Imports
# =======
# Library imports
# ---------------
import ast
import asyncio
import codecs
from contextlib import contextmanager
import fnmatch
import io
from pathlib import Path
from queue import Queue
import sys
from tempfile import NamedTemporaryFile
from typing import Any, cast, Callable, Dict, Generator, List, Optional, Tuple, Union
import urllib.parse

# Third-party imports
# -------------------
import markdown  # type: ignore
import docutils.core
import docutils.writers.html4css1
from CodeChat.CodeToRest import code_to_rest_string, html_static_path  # type: ignore
from CodeChat.CommentDelimiterInfo import SUPPORTED_GLOBS  # type: ignore

# Local imports
# -------------
from .gen_py.CodeChat_Services.ttypes import (
    GetResultType,
    GetResultReturn,
)


# Utilities
# =========
# Convert a path to a URI component: make it absolute and use forward (POSIX) slashes. If the provided ``file_path`` is falsey, just return it.
def path_to_uri(file_path: str):
    return Path(file_path).resolve().as_posix() if file_path else file_path


# Renderers
# =========
#
# Markdown
# --------
# A handy Markdown extension.
class _StrikeThroughExtension(markdown.Extension):
    DEL_RE = r"(~~)(.*?)~~"

    def extendMarkdown(self, md, md_globals):
        # Create the del pattern
        delTag = markdown.inlinepatterns.SimpleTagPattern(self.DEL_RE, "del")
        # Insert del pattern into markdown parser
        md.inlinePatterns.add("del", delTag, ">not_strong")


# Convert Markdown to HTML
def _convertMarkdown(text: str, filePath: str) -> Tuple[str, str]:
    return (
        markdown.markdown(
            text,
            extensions=[
                "markdown.extensions.fenced_code",
                "markdown.extensions.nl2br",
                "markdown.extensions.tables",
                _StrikeThroughExtension(),
            ],
        ),
        "",
    )


# reStructuredText (reST)
# -----------------------
# Convert reStructuredText (reST) to HTML.
def _convertReST(
    text: str, filePath: str, use_codechat: bool = False
) -> Tuple[str, str]:

    errStream = io.StringIO()
    settingsDict = {
        # Make sure to use Unicode everywhere. This name comes from
        # ``docutils.core.publish_string`` version 0.12, lines 392 and following.
        "output_encoding": "unicode",
        # While ``unicode`` **should** work for ``input_encoding``, it doesn't if
        # there's an ``.. include`` directive, since this encoding gets passed to
        # ``docutils.io.FileInput.__init__``, in which line 236 of version 0.12
        # tries to pass the ``unicode`` encoding to ``open``, producing:
        #
        # .. code:: python3
        #    :number-lines:
        #
        #    File "...\python-3.4.4\lib\site-packages\docutils\io.py", line 236, in __init__
        #      self.source = open(source_path, mode, **kwargs)
        #    LookupError: unknown encoding: unicode
        #
        # So, use UTF-8 and encode the string first. Ugh.
        "input_encoding": "utf-8",
        # Don't stop processing, no matter what.
        "halt_level": 5,
        # Capture errors to a string and return it.
        "warning_stream": errStream,
        "stylesheet_dirs": html_static_path(),
        "stylesheet_path": ["docutils.css"]
        + (["CodeChat.css"] if use_codechat else []),
    }
    htmlString = docutils.core.publish_string(
        bytes(text, encoding="utf-8"),
        writer_name="html",
        settings_overrides=settingsDict,
    )
    errString = errStream.getvalue()
    errStream.close()
    return htmlString, errString


# CodeChat
# ========
# Convert source code to HTML.
def _convertCodeChat(text: str, filePath: str) -> Tuple[str, str]:
    try:
        rest_string = code_to_rest_string(text, filename=filePath)
    except KeyError:
        # Although the file extension may be in the list of supported
        # extensions, CodeChat may not support the lexer chosen by Pygments.
        # For example, a ``.v`` file may be Verilog (supported by CodeChat)
        # or Coq (not supported). In this case, provide an error message
        return "", "{}:ERROR: this file is not supported by CodeChat.".format(filePath)
    return _convertReST(rest_string, filePath, True)


# External tools/projects
# =======================
# Convert a file using an external program.
async def _convert_external(
    text: str,
    file_path: str,
    tool_or_project_path: List[Union[bool, str]],
    q: asyncio.Queue,
) -> Tuple[str, str]:
    # Split the provided tool path.
    uses_stdin, uses_stdout, *args_ = tool_or_project_path
    args = cast(List[str], args_)

    # Run from the directory containing the file.
    cwd = str(Path(file_path).parent)

    # Save the text in a temporary file for use with the external tool.
    with _optional_temp_file(not uses_stdin) as input_file, _optional_temp_file(
        not uses_stdout
    ) as output_file:
        if input_file:
            # Write the text to the input file then close it, so that it can be opened on all platforms by the external tool. See `NamedTemporaryFile <https://docs.python.org/3/library/tempfile.html#tempfile.NamedTemporaryFile>`_.
            input_file.write(text)
            input_file.close()

        if output_file:
            # Close the output file for the same reason.
            output_file.close()

        # Do replacements on the args.
        args = [
            s.format(
                input_file=input_file and input_file.name,
                output_file=output_file and output_file.name,
            )
            for s in args
        ]

        stdout, stderr = await _run_subprocess(
            args, cwd, None if input_file else text, bool(output_file), q
        )

        # Gather the output from the file if necessary.
        if output_file:
            with open(output_file.name, "r", encoding="utf-8") as f:
                stdout = f.read()

    return stdout, stderr


# Return False if source_file is newer than output_file; otherwise, return string with an error message.
def _checkModificationTime(
    source_file: Path, base_html_file: Path, html_ext: str
) -> Tuple[str, str]:

    # Look for the resulting HTML.
    possible_html_file = base_html_file.with_suffix(html_ext)
    html_file = (
        possible_html_file
        if possible_html_file.exists()
        else Path(str(base_html_file) + html_ext)
    )

    # Recall that time is measured in seconds since the epoch,
    # so that larger = newer.
    try:
        if html_file.stat().st_mtime > source_file.stat().st_mtime:
            return str(html_file), ""
        else:
            return (
                str(html_file),
                "The file {} is older than the source file {}.".format(
                    html_file, source_file
                ),
            )
    except OSError as e:
        return (
            str(html_file),
            "Error checking modification time of {}: {}".format(html_file, e),
        )


# Convert an external project
async def _convert_external_project(
    text: str, file_path_: str, tool_or_project_path: str, q: asyncio.Queue
) -> Tuple[str, str]:
    # Run from the directory containing the project file.
    project_path = str(Path(tool_or_project_path).parent)
    q.put(
        GetResultReturn(
            GetResultType.build,
            "Loading project file {}.\n".format(tool_or_project_path),
        )
    )

    # Read the project configuration.
    try:
        with open(tool_or_project_path, encoding="utf-8") as f:
            data = f.read()
    except Exception as e:
        return "", "{}::ERROR: Unable to open. {}".format(tool_or_project_path, e)

    # Parse it and check the format
    try:
        d = ast.literal_eval(data)
    except Exception as e:
        return "", "{}::ERROR: Unable to parse. {}".format(tool_or_project_path, e)
    if not isinstance(d, dict):
        return (
            "",
            "{}::ERROR: Unexpected type; file should contain a dict, but saw a {}".format(
                tool_or_project_path, type(d)
            ),
        )
    args = d.get("args")
    if not isinstance(args, list):
        return (
            "",
            "{}::ERROR: missing args or wrong type; saw {} (type was {}).".format(
                tool_or_project_path, args, type(args)
            ),
        )
    source_path = d.get("source_path", ".")
    if not isinstance(source_path, str):
        return (
            "",
            "{}::ERROR: missing source_path or wrong type; saw {} (type was {}).".format(
                tool_or_project_path, source_path, type(source_path)
            ),
        )
    output_path = d.get("output_path")
    if not isinstance(output_path, str):
        return (
            "",
            "{}::ERROR: missing output_path or wrong type; saw {} (type was {}).".format(
                tool_or_project_path, output_path, type(output_path)
            ),
        )
    html_ext = d.get("html_ext", ".html")
    if not isinstance(html_ext, str):
        return (
            "",
            "{}::ERROR: wrong type for html_ext; saw {} (type was {}).".format(
                file_path_, html_ext, type(html_ext)
            ),
        )

    # Make paths absolute.
    def abs_path(path: str) -> Path:
        path_ = Path(path)
        if not path_.is_absolute():
            path_ = project_path / path_
        return path_

    source_path = abs_path(source_path)
    output_path = abs_path(output_path)
    file_path = Path(file_path_)

    # Determine first guess at the location of the rendered HTML.
    try:
        base_html_file = output_path / file_path.relative_to(source_path)
    except Exception as e:
        return (
            "",
            "{}::ERROR: unable to compute path relative to {}. {}".format(
                file_path, source_path, e
            ),
        )

    # Compare dates to see if the rendered file is current
    html_file, error = _checkModificationTime(file_path, base_html_file, html_ext)

    # If not, render and try again.
    if error:
        # Perform replacement on the args.
        args = [
            s.format(
                project_path=project_path,
                source_path=source_path,
                output_path=output_path,
            )
            for s in args
        ]
        # Render.
        stdout, stderr = await _run_subprocess(args, project_path, None, True, q)
        html_file, error = _checkModificationTime(file_path, base_html_file, html_ext)
    else:
        stderr = ""

    # Display an error in the main window if one exists.
    if error:
        stderr += error
    return html_file, stderr


# Run a subprocess, optionally streaming the stdout.
async def _run_subprocess(
    args: List[str],
    cwd: str,
    input_text: Optional[str],
    stream_stdout: bool,
    q: asyncio.Queue,
) -> Tuple[str, str]:
    # Explain what's going on.
    q.put(GetResultReturn(GetResultType.build, "{} > {}\n".format(cwd, " ".join(args))))

    # Start the process.
    try:
        proc = await asyncio.create_subprocess_exec(
            *args,
            cwd=cwd,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
    except Exception as e:
        return "", "external command:: ERROR:When starting. {}".format(e)

    # Provide a way to send stdout from the process a line at a time to the web client.
    async def stdout_streamer(stdout_stream: asyncio.StreamReader):
        # Use an `incremental decoder <https://docs.python.org/3/library/codecs.html#codecs.getincrementaldecoder>`_ to decode a stream.
        decoder_ = codecs.getincrementaldecoder("utf-8")(errors="backslashreplace")
        # Wrap than with an incremental decoder for universal newlines. The `docs <https://docs.python.org/3/library/io.html#io.IncrementalNewlineDecoder>`_ are very sparse. From the Visual Studio Code help that pops up (likely from https://github.com/python/cpython/blob/master/Modules/_io/textio.c#L237):
        #
        #   IncrementalNewlineDecoder(decoder: Optional[codecs.IncrementalDecoder], translate: bool, errors: str=...)
        #
        #   Codec used when reading a file in universal newlines mode.
        #   It wraps another incremental decoder, translating \r\n and \r into \n. It also records the types of newlines encountered.  When used with translate=False, it ensures that the newline sequence is returned in one piece. When used with decoder=None, it expects unicode strings as decode input and translates newlines without first invoking an external decoder.
        decoder = io.IncrementalNewlineDecoder(decoder_, True, "")
        while True:
            ret = await stdout_stream.read(80)
            if ret:
                q.put(GetResultReturn(GetResultType.build, decoder.decode(ret)))
            else:
                # Tell the decoder the stream is done and collect any last output.
                s = decoder.decode(b"", True)
                if s:
                    q.put(GetResultReturn(GetResultType.build, s))
                break

    # An awaitable sequence to interact with the subprocess.
    aws = [proc.communicate(None if input_text is None else input_text.encode("utf-8"))]

    # If we have an output file, then stream the stdout.
    if stream_stdout:
        assert proc.stdout
        aws.append(stdout_streamer(proc.stdout))
        # Hack: make it look like there's no stdout, so communicate won't use it.
        proc.stdout = None

    # Run the subprocess.
    try:
        (stdout, stderr), *junk = await asyncio.gather(*aws)
    except Exception as e:
        return "", "external command:: ERROR:When running. {}".format(e)

    return (
        stdout and stdout.decode("utf-8", errors="backslashreplace"),
        stderr.decode("utf-8", errors="backslashreplace"),
    )


@contextmanager
def _dummy_context_manager() -> Generator:
    yield


# If need_temp_file is True, provide a NamedTemporaryFile; otherwise, return a dummy context manager.
def _optional_temp_file(need_temp_file: bool) -> Any:
    return (
        NamedTemporaryFile(mode="w", encoding="utf-8")
        if need_temp_file
        else _dummy_context_manager()
    )


# Fake renderers
# ==============
# "Convert" (pass through) the provided text.
def _pass_through(text: str, file_path: str) -> Tuple[str, str]:
    return text, ""


# The "error converter" when a converter can't be found.
def _error_converter(text: str, file_path: str) -> Tuple[str, str]:
    return "", "{}:: ERROR: no converter found for this file.".format(file_path)


# ClientState
# ===========
# Store data for about each client.
class ClientState:
    def __init__(self):
        # A queue of messages for the client. This can be accessed by any thread.
        self.q = Queue()

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


# Select and invoke a renderer
# ============================
# Build a map of file names/extensions to the converter to use.
#
# TODO:
#
# #.    Read this from a JSON file instead.
# #.    Use Pandoc to offer lots of other format conversions.
GLOB_TO_CONVERTER: Dict[str, Tuple[Callable, Optional[List[Union[bool, str]]]]] = {
    glob: (_convertCodeChat, None) for glob in SUPPORTED_GLOBS
}
GLOB_TO_CONVERTER.update(
    {
        # Leave (X)HTML unchanged.
        "*.xhtml": (_pass_through, None),
        "*.html": (_pass_through, None),
        "*.htm": (_pass_through, None),
        # Use the integrated Python libraries for these.
        "*.md": (_convertMarkdown, None),
        "*.rst": (_convertReST, None),
        # External tools
        #
        # `Textile <https://www.promptworks.com/textile>`_:
        "*.textile": (
            _convert_external,
            [
                # Does this tool read the input file from stdin?
                True,
                # Does this tool produce the output on stdout?
                True,
                # The remaining elements are the arguments used to invoke the tool.
                "pandoc",
                # Specify the input format https://pandoc.org/MANUAL.html#option--to>`_.
                "--from=textile",
                # `Output to HTML <https://pandoc.org/MANUAL.html#option--from>`_.
                "--to=html",
                # `Produce a complete (standalone) HTML file <https://pandoc.org/MANUAL.html#option--standalone>`_, not a fragment.
                "--standalone",
            ],
        ),
    }
)


# Return the converter for the provided file.
def _select_converter(
    file_path: str,
) -> Tuple[Callable, Union[None, str, List[Union[bool, str]]], bool]:
    # Search for an external builder configuration file.
    for project_path in Path(file_path).parents:
        project_file = project_path / "codechat_config.json"
        if project_file.exists():
            return _convert_external_project, str(project_file), True

    # Otherwise, look for a single-file converter.
    for glob, (converter, tool_or_project_path) in GLOB_TO_CONVERTER.items():
        if fnmatch.fnmatch(file_path, glob):
            return converter, tool_or_project_path, False
    return _error_converter, None, False


# Run the appropriate converter for the provided file or return an error.
async def convert_file(text: str, file_path: str, cs: ClientState) -> None:
    converter, tool_or_project_path, is_project = _select_converter(file_path)
    # Projects require a clean file in order to render.
    if is_project and cs._to_render_is_dirty:
        return

    if asyncio.iscoroutinefunction(converter):
        # Coroutines get the queue, so they can report progress during the build.
        html_string, err_string = await converter(
            text, file_path, tool_or_project_path, cs.q
        )
    else:
        assert tool_or_project_path is None
        html_string, err_string = converter(text, file_path)

    # Update the client's state, now that the rendering is complete.
    cs._editor_text = text
    # For projects, the rendered HTML is already on disk.
    if is_project:
        cs._file_path = html_string
        cs._html = None
    else:
        cs._file_path = file_path
        cs._html = html_string

    # Send any errors. An empty error string will clear any errors from a previous build, and should still be sent.
    cs.q.put(GetResultReturn(GetResultType.errors, err_string))

    # Sending the HTML signals the end of this build.
    #
    # For Windows, make the path contain forward slashes.
    uri = path_to_uri(cs._file_path)
    # Encode this, for Windows paths which contain a colon (or unusual Linux paths).
    cs.q.put(GetResultReturn(GetResultType.html, urllib.parse.quote(uri)))


# RenderManager / render thread
# ==============================
class RenderManager:
    # Determine if the provided id exists and is not being deleted. Return the ClientState for the id if so; otherwise, return False.
    def _get_client_state(self, id: int) -> Union[bool, ClientState]:
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

    # Create a new client. Returns the client id on success or False on failure.
    def create_client(self) -> int:
        future = asyncio.run_coroutine_threadsafe(self._create_client(), self._loop)
        return future.result()

    async def _create_client(self) -> int:
        if self._is_shutdown:
            return -1
        self._last_id += 1
        id = self._last_id
        if id in self._client_state_dict:
            # Indicate failure if this id exists.
            return False
        self._client_state_dict[id] = ClientState()
        return id

    def delete_client(self, id: int) -> bool:
        future = asyncio.run_coroutine_threadsafe(self._delete_client(id), self._loop)
        return future.result()

    async def _delete_client(self, id: int) -> bool:
        cs = self._client_state_dict.get(id)
        if cs:
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
        future = asyncio.run_coroutine_threadsafe(
            self._start_render(editor_text, file_path, id, is_dirty), self._loop
        )
        return future.result()

    async def _start_render(
        self, editor_text: str, file_path: str, id: int, is_dirty: bool
    ) -> bool:
        cs = self._get_client_state(id)
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
    def get_queue(self, id: int) -> Optional[Queue]:
        future = asyncio.run_coroutine_threadsafe(self._get_queue(id), self._loop)
        return future.result()

    async def _get_queue(self, id: int) -> Optional[Queue]:
        cs = self._get_client_state(id)
        return cast(ClientState, cs).q if cs else None

    # Given a URL, see if it matches with the latest render; if so, return the resulting HTML. If there's no match to the URL or the ID doesn't exist, return False. Note that the "HTML" can be None, meaning the render was stored to disk and the URL is a path to the rendered file.
    def get_render_results(self, id: int, url_path: str) -> Union[None, str, bool]:
        future = asyncio.run_coroutine_threadsafe(
            self._get_render_results(id, url_path), self._loop
        )
        return future.result()

    async def _get_render_results(
        self, id: int, url_path: str
    ) -> Union[None, str, bool]:
        cs = self._get_client_state(id)
        return (
            cast(ClientState, cs)._html
            if cs and path_to_uri(cast(ClientState, cs)._file_path) == url_path
            else False
        )

    # Shut down the render manager.
    def shutdown(self):
        future = asyncio.run_coroutine_threadsafe(
            self._shutdown(), self._loop
        )
        return future.result()

    async def _shutdown(self):
        self._is_shutdown = True
        # Stop each client. This will tell the web client to shut down and also delete the render client.
        for id, cs in self._client_state_dict.items():
            cs.q.put(GetResultReturn(GetResultType.command, "shutdown"))

    # Start the render manager. This typically never returns.
    def run(self, *args, debug: bool=True) -> None:
        # The default Windows event loop doesn't support asyncio subprocesses.
        is_win = sys.platform.startswith("win")
        if is_win:
            asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

        # Let the user know that the server is now ready -- this is the last piece of it to start.
        print("Ready.")
        asyncio.run(self._run(*args), debug=debug)

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

        await asyncio.gather(*[self._worker() for i in range(num_workers)])

    # Process items in the render queue.
    async def _worker(self) -> None:
        while True:
            # Get an item to process.
            id = await self._job_q.get()
            # Check for shutdown.
            if id is None:
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
                # When shutdown is complete, end all the workers.
                if self._is_shutdown and len(self._client_state_dict) == 0:
                    for i in range(self._num_workers):
                        await self._job_q.put(None)
            else:
                # Sync first.
                # TODO: sync.

                # Render next.
                await convert_file(
                    cs._to_render_editor_text, cs._to_render_file_path, cs
                )

                # If this client received more work to do while working on the current job, add it back to the queue -- it can't safely be added to the queue while in the job is in process. Otherwise, we would potentially allow two workers to render the same job in parallel, which would confuse the renderer.
                if cs._needs_processing:
                    self._job_q.put_nowait(id)
                else:
                    cs._in_job_q = False
