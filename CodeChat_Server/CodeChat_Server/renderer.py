# .. Copyright (C) 2012-2020 Bryan A. Jones.
#
#    This file is part of the CodeChat plugin.
#
#    The CodeChat plugin is free software: you can redistribute it and/or
#    modify it under the terms of the GNU General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    The CodeChat plugin is distributed in the hope that it will be
#    useful, but WITHOUT ANY WARRANTY; without even the implied warranty
#    of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
#    General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with the CodeChat plugin.  If not, see
#    <http://www.gnu.org/licenses/>.
#
# *********************************************
# |docname| - Renderers for the CodeChat server
# *********************************************
# These functions convert from a text to HTML for a variety of formats.

# Imports
# =======
# Library imports
# ---------------
import asyncio
from contextlib import contextmanager
import fnmatch
import io
import os.path
from pathlib import Path
from queue import Queue
import sys
from tempfile import NamedTemporaryFile
import urllib.parse

# Third-party imports
# -------------------
import markdown
import docutils.core
import docutils.writers.html4css1
from CodeChat.CodeToRest import code_to_html_string
from CodeChat.CommentDelimiterInfo import SUPPORTED_GLOBS

# Local imports
# -------------
from .gen_py.CodeChat_Services.ttypes import (
    GetResultType,
    GetResultReturn,
)


# Functions and classes
# =====================
# Convert a path to a URI component: make it absolute and use forward (POSIX) slashes. If the provided ``file_path`` is falsey, just return it.
def path_to_uri(file_path):
    return Path(file_path).resolve().as_posix() if file_path else file_path


# A handy Markdown extension.
class _StrikeThroughExtension(markdown.Extension):
    DEL_RE = r"(~~)(.*?)~~"

    def extendMarkdown(self, md, md_globals):
        # Create the del pattern
        delTag = markdown.inlinepatterns.SimpleTagPattern(self.DEL_RE, "del")
        # Insert del pattern into markdown parser
        md.inlinePatterns.add("del", delTag, ">not_strong")


# Convert Markdown to HTML
def _convertMarkdown(text, filePath):
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


# Convert reStructuredText (reST) to HTML.
def _convertReST(text, filePath):

    errStream = io.StringIO()
    docutilsHtmlWriterPath = os.path.abspath(
        os.path.dirname(docutils.writers.html4css1.__file__)
    )
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
        # On some Windows PC, docutils will complain that it can't find its
        # template or stylesheet. On other Windows PCs with the same setup, it
        # works fine. ??? So, specify a path to both here.
        "template": (
            os.path.join(
                docutilsHtmlWriterPath,
                docutils.writers.html4css1.Writer.default_template,
            )
        ),
        "stylesheet_dirs": (
            docutilsHtmlWriterPath,
            os.path.join(
                os.path.abspath(os.path.dirname(os.path.realpath(__file__))),
                "rst_templates",
            ),
        ),
        "stylesheet_path": "default.css",
    }
    htmlString = docutils.core.publish_string(
        bytes(text, encoding="utf-8"),
        writer_name="html",
        settings_overrides=settingsDict,
    )
    errString = errStream.getvalue()
    errStream.close()
    return htmlString, errString


# Convert source code to HTML.
def _convertCodeChat(text, filePath):
    # Use StringIO to pass CodeChat compilation information back to
    # the client.
    errStream = io.StringIO()
    try:
        htmlString = code_to_html_string(text, errStream, filename=filePath)
    except KeyError:
        # Although the file extension may be in the list of supported
        # extensions, CodeChat may not support the lexer chosen by Pygments.
        # For example, a ``.v`` file may be Verilog (supported by CodeChat)
        # or Coq (not supported). In this case, provide an error message
        errStream.write(
            "{}:ERROR: this file is not supported by CodeChat.".format(filePath)
        )
        htmlString = ""
    errString = errStream.getvalue()
    errStream.close()
    return htmlString, errString


@contextmanager
def _dummy_context_manager():
    yield


# If need_temp_file is True, provide a NamedTemporaryFile; otherwise, return a dummy context manager.
def _optional_temp_file(need_temp_file):
    return (
        NamedTemporaryFile(mode="w", encoding="utf-8")
        if need_temp_file
        else _dummy_context_manager()
    )


# Run a subprocess, optionally streaming the stdout.
async def _run_subprocess(args, cwd, input_text, stream_stdout, q):
    # Explain what's going on.
    q.put(GetResultReturn(GetResultType.build, "{} > {}".format(cwd, " ".join(args))))

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
    async def stdout_streamer(stdout_stream):
        while True:
            ret = await stdout_stream.read(80)
            if ret:
                # TODO: what if the bytes got split between a UTF-8 multibyte sequence? Oh, fun...
                q.put(GetResultReturn(GetResultType.build, ret.decode("utf-8")))
            else:
                break

    # An awaitable sequence to interact with the subprocess.
    aws = [proc.communicate(input_text and input_text.encode("utf-8"))]

    # If we have an output file, then stream the stdout.
    if stream_stdout:
        aws.append(stdout_streamer(proc.stdout))
        # Hack: make it look like there's no stdout, so communicate won't use it.
        proc.stdout = None

    # Run the subprocess.
    try:
        (stdout, stderr), *junk = await asyncio.gather(*aws)
    except Exception as e:
        return "", "external command:: ERROR:When running. {}".format(e)

    return stdout and stdout.decode("utf-8"), stderr.decode("utf-8")


# Convert a file using an external program.
async def _convert_external(text, file_path, tool_or_project_path, q):
    # Split the provided tool path.
    uses_stdin, uses_stdout, *args = tool_or_project_path

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


# "Convert" (pass through) the provided text.
def _pass_through(text, file_path):
    return text, ""


# The "error converter" when a converter can't be found.
def _error_converter(text, file_path):
    return "", "{}:: ERROR: no converter found for this file.".format(file_path)


# Build a map of file names/extensions to the converter to use.
#
# TODO:
#
# #.    Read this from a JSON file instead.
# #.    Use Pandoc to offer lots of other format conversions.
GLOB_TO_CONVERTER = {glob: (_convertCodeChat, None) for glob in SUPPORTED_GLOBS}
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
def _select_converter(file_path):
    # TODO: search for an external builder configuration file.
    # return _project_builder, path
    for glob, (converter, tool_or_project_path) in GLOB_TO_CONVERTER.items():
        if fnmatch.fnmatch(file_path, glob):
            return converter, tool_or_project_path
    return _error_converter, None


# Run the appropriate converter for the provided file or return an error.
async def convert_file(text, file_path, cs):
    converter, tool_or_project_path = _select_converter(file_path)
    if asyncio.iscoroutinefunction(converter):
        # Coroutines get the queue, so they can report progress during the build.
        html_string, err_string = await converter(
            text, file_path, tool_or_project_path, cs.q
        )
    else:
        assert tool_or_project_path is None
        html_string, err_string = converter(text, file_path)

    # Update the client's state, now that the rendering is complete.
    cs._file_path = file_path
    cs._text = text
    cs._html = html_string

    # Send any errors. An empty error string will clear any errors from a previous build, and should still be sent.
    cs.q.put(GetResultReturn(GetResultType.errors, err_string))

    # Sending the HTML signals the end of this build.
    #
    # For Windows, make the path contain forward slashes.
    uri = path_to_uri(file_path)
    # Encode this, for Windows paths which contain a colon (or unusual Linux paths).
    cs.q.put(GetResultReturn(GetResultType.html, urllib.parse.quote(uri)))


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

        # A bucket to hold text and the associated file to render.
        self._to_render_editor_text = None
        self._to_render_file_path = None

        # A bucket to hold a sync request.
        #
        # The index into either the editor text or HTML converted to text.
        self._to_sync_index = None
        self._to_sync_from_editor = None
        # The HTML converted to text.
        self._html_as_text = None

        # A flag to indicate if this client is in the process of deletion.
        self._is_deleting = False


class RenderManager:
    # Determine if the provided id exists and is not being deleted. Return the ClientState for the id if so; otherwise, return False.
    def _get_client_state(self, id):
        if id not in self._client_state_dict:
            # Signal an error if the id can't be found.
            return False
        cs = self._client_state_dict[id]
        if cs._is_deleting:
            # Signal an error if this client is being deleted.
            return False
        return cs

    # Create a new client. Returns the client id on success or False on failure.
    def create_client(self):
        future = asyncio.run_coroutine_threadsafe(self._create_client(), self._loop)
        return future.result()

    async def _create_client(self):
        self._last_id += 1
        id = self._last_id
        if id in self._client_state_dict:
            # Indicate failure if this id exists.
            return False
        self._client_state_dict[id] = ClientState()
        return id

    def delete_client(self, id):
        future = asyncio.run_coroutine_threadsafe(self._delete_client(id), self._loop)
        return future.result()

    async def _delete_client(self, id):
        cs = self._get_client_state(id)
        if cs:
            del self._client_state_dict[id]
            return True
        else:
            return False

    # Place the item in the render queue; must be called from another (non-render) thread. Returns True on success, or False if the provided id doesn't exist.
    def start_render(self, editor_text, file_path, id):
        future = asyncio.run_coroutine_threadsafe(
            self._start_render(editor_text, file_path, id), self._loop
        )
        return future.result()

    async def _start_render(self, editor_text, file_path, id):
        cs = self._get_client_state(id)
        if not cs:
            # Signal an error for an invalid client id.
            return False

        # Add to the job queue unless it's already there.
        if not cs._in_job_q:
            self._job_q.put_nowait(id)
            cs._in_job_q = True

        # Update the job parameters.
        cs._to_render_editor_text = editor_text
        cs._to_render_file_path = file_path

        # Indicate success
        return True

    # Get a client's queue.
    def get_queue(self, id):
        future = asyncio.run_coroutine_threadsafe(self._get_queue(id), self._loop)
        return future.result()

    async def _get_queue(self, id):
        cs = self._get_client_state(id)
        return cs.q if cs else False

    # Return ``(file_path, html)`` if the provided client exists, or False otherwise.
    def get_render_results(self, id):
        future = asyncio.run_coroutine_threadsafe(
            self._get_render_results(id), self._loop
        )
        return future.result()

    async def _get_render_results(self, id):
        cs = self._get_client_state(id)
        return (cs._file_path, cs._html) if cs else False

    # Start the render manager. This typically never returns.
    def run(self, *args, debug=False, **kwargs):
        # The default Windows event loop doesn't support asyncio subprocesses.
        is_win = sys.platform.startswith("win")
        if is_win:
            asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

        asyncio.run(self._run(*args, **kwargs), debug=debug)

    # Run the rendering thread with the given number of workers.
    async def _run(self, num_workers=1):
        # Create a queue of jobs for the renderer to process. This must be created from within the main loop to avoid ``got Future <Future pending> attached to a different loop`` errors.
        self._job_q = asyncio.Queue()
        # Keep a dict of id: ClientState for each client.
        self._client_state_dict = {}
        # The next ID will be 0. Use the lock below to establish ownership before writing this.
        self._last_id = -1
        self._loop = asyncio.get_running_loop()
        self._client_state_dict = {}

        await asyncio.gather(*[self._worker(i) for i in range(num_workers)])

    # Process items in the render queue.
    async def _worker(self, worker_index):
        while True:
            # Get an item to process.
            id = await self._job_q.get()
            cs = self._client_state_dict[id]

            if cs._is_deleting:
                del self.client_state_dict[id]
            else:
                # TODO: sync.

                # Render it.
                assert cs._in_job_q
                await convert_file(
                    cs._to_render_editor_text, cs._to_render_file_path, cs
                )
                cs._in_job_q = False
