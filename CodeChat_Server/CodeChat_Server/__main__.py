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
import argparse
from pathlib import Path
import sys

# Third-party imports
# -------------------
# None.
#
# Local application imports
# -------------------------
# None. Delay the import below until after print runs, since the import takes a while to complete.


# This is copied from `watchmedo <https://github.com/gorakhargosh/watchdog/blob/master/src/watchdog/watchmedo.py#L84>`__.
def parse_patterns(patterns_spec, ignore_patterns_spec, separator=";"):
    """
    Parses pattern argument specs and returns a two-tuple of
    (patterns, ignore_patterns).
    """
    patterns = patterns_spec.split(separator)
    ignore_patterns = ignore_patterns_spec.split(separator)
    if ignore_patterns == [""]:
        ignore_patterns = []
    return (patterns, ignore_patterns)


# Main
# ====
def parse_args(args=None):
    # TODO: This should instead be a CLI using Click with two groups: serve (the default -- use ``click-default-group``) and watch. At some later point, have the watch command start its own client and also run the server; this would allow multiple instances of the client to run. Then, there would be three groups: serve (the default), watch, and build.
    parser = argparse.ArgumentParser(
        description="The CodeChat Server works with editor/IDE extensions/plugin to transform source code and textual documents to beautiful web pages. See https://codechat-system.readthedocs.io/."
    )
    parser.add_argument(
        "--watch",
        "-w",
        nargs="*",
        # For user-friendliness, allow users to either specify a list of directories, or multiple sets of this option with one (or more) directories.
        action="extend",
        help="One or more directories to watch for changes; a change triggers a render of that file or project. If a directory is not provided, defaults to the current directory.",
    )
    parser.add_argument(
        "--patterns",
        "--pattern",
        "-p",
        nargs="*",
        default=[],
        action="extend",
        help="A list of globs which list files to monitor for changes in the specified --watch directories; defaults to montoring all files.",
    )
    parser.add_argument(
        "--ignore-patterns",
        "--ignore-pattern",
        "-i",
        nargs="*",
        default=[],
        action="extend",
        help="A list of globs of files which will not trigger a build if they change when using --watch.",
    )
    parser.add_argument(
        "--build",
        "-b",
        nargs="*",
        default=[],
        action="extend",
        help="One or more paths of files/projects to build.",
    )

    # If the ``--watch`` option was provided with no arguments, assume the current directory. If the option wasn't provided, make it an empty list.
    parsed_args = parser.parse_args(args)
    if parsed_args.watch == []:
        parsed_args.watch = [str(Path(".").absolute())]
    if parsed_args.watch is None:
        parsed_args.watch = []
    # If a pattern wasn't specified, assume ``*``.
    if not parsed_args.patterns:
        parsed_args.patterns = ["*"]

    return parsed_args


def main():
    args = parse_args()

    # This file takes a long time to load and run. Print a status message as it starts.
    print("Loading...")
    from .server import run_servers

    sys.exit(run_servers(args.watch, args.patterns, args.ignore_patterns))


if __name__ == "__main__":
    main()
