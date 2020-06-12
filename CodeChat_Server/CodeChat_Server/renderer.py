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
import fnmatch
import io
import os.path
from pathlib import Path
import traceback
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
# Convert a path to a URI component: make it absolute and use forward (POSIX) slashes.
def path_to_uri(file_path):
    return Path(file_path).resolve().as_posix()


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


# "Convert" (pass through) the provided text.
def _pass_through(text, file_path):
    return text, ""


# The "error converter" when a converter can't be found.
def _error_converter(text, file_path):
    return "", "{}:ERROR: no converter found for this file.".format(file_path)

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
        "*.md": (_convertMarkdown, None),
        "*.rst": (_convertReST, None),
    }
)


# Return the converter for the provided file.
def _select_converter(file_path):
    # TODO: search for an external builder configuration file.
    #return _project_builder, path
    for glob, (converter, tool_or_project_path) in GLOB_TO_CONVERTER.items():
        if fnmatch.fnmatch(file_path, glob):
            return converter, tool_or_project_path
    return _error_converter, None


# Run the appropriate converter for the provided file or return an error.
async def convert_file(text, file_path, cs):
    converter, tool_or_project_path = _select_converter(file_path)
    if asyncio.iscoroutine(converter):
        # Coroutines get the queue, so they can report progress during the build.
        htmlString, errString = await converter(text, file_path, tool_or_project_path, cs.q)
    else:
        assert tool_or_project_path is None
        htmlString, errString = converter(text, file_path)

    # Update the client's state.
    cs.file_path = file_path
    cs.text = text
    cs.html = htmlString

    # Not all renderers produce errors.
    if errString is not None:
        cs.q.put(GetResultReturn(GetResultType.errors, errString))

    # Sending the HTML signals the end of this build.
    #
    # For Windows, make the path contain forward slashes.
    uri = path_to_uri(file_path)
    # Encode this, for Windows paths which contain a colon (or unusual Linux paths).
    cs.q.put(GetResultReturn(GetResultType.html, urllib.parse.quote(uri)))


class Renderer:
    # Place the item in the render queue; must be called from another (non-render) thread.
    def start_render(self, editor_text, file_path, id):
        self._loop.call_soon_threadsafe(self._start_render, editor_text, file_path, id)

    # Once in the render thread, it's safe to update the client state.
    def _start_render(self, editor_text, file_path, id):
        cs = self._client_state_dict[id]
        if (cs.to_render_editor_text is None) and (cs.to_render_file_path is None):
            self._render_q.put_nowait(id)
        cs.to_render_editor_text = editor_text
        cs.to_render_file_path = file_path

    def run(self, *args, debug=False, **kwargs):
        asyncio.run(self._run(*args, **kwargs), debug=debug)

    # Run the rendering thread with the given number of workers.
    async def _run(self, client_state_dict, num_workers=1):
        # This must be created from within the main loop to avoid ``got Future <Future pending> attached to a different loop`` errors.
        self._render_q = asyncio.Queue()
        self._loop = asyncio.get_running_loop()
        self._client_state_dict = client_state_dict

        await asyncio.gather(*[self._worker(i) for i in range(num_workers)])

    # Process items in the render queue.
    async def _worker(self, worker_index):
        while True:
            # Get an item to process.
            id = await self._render_q.get()
            cs = self._client_state_dict[id]

            # Render it.
            await convert_file(cs.to_render_editor_text, cs.to_render_file_path, cs)

            # Mark it as rendered.
            cs.to_render_editor_text = None
            cs.to_render_file_path = None
