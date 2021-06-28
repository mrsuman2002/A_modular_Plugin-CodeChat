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
#
# Imports
# =======
# These are listed in the order prescribed by `PEP 8
# <http://www.python.org/dev/peps/pep-0008/#imports>`_.
#
# Standard library
# ----------------
import sys

# Third-party imports
# -------------------
import argh
from argh import arg, expects_obj

# Local application imports
# -------------------------
# None. Delay the import below until after print runs, since the import takes a while to complete.


# This is copied from `watchmedo <https://github.com/gorakhargosh/watchdog/blob/master/src/watchdog/watchmedo.py#L84>`_.
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
# The command-line parsing is based on `watchmedo <https://github.com/gorakhargosh/watchdog/blob/master/src/watchdog/watchmedo.py#L383>`_.
@arg(
    "-w",
    "--watch",
    dest="watch_directories",
    nargs="*",
    default="",
    help="directories to watch",
)
@arg(
    "-p",
    "--pattern",
    "--patterns",
    dest="patterns",
    default="*",
    help="matches event paths with these patterns (separated by ;).",
)
@arg(
    "-i",
    "--ignore-pattern",
    "--ignore-patterns",
    dest="ignore_patterns",
    default="",
    help="ignores event paths with these patterns (separated by ;).",
)
@expects_obj
def _main(args):
    patterns, ignore_patterns = parse_patterns(args.patterns, args.ignore_patterns)

    # This file takes a long time to load and run. Print a status message as it starts.
    print("Loading...")
    from .server import run_servers

    sys.exit(run_servers(args.watch_directories, patterns, ignore_patterns))


def main():
    argh.dispatch_command(_main)


if __name__ == "__main__":
    main()
