#!/usr/bin/env python3
# ****************************************************************************************
# |docname| - Run a series of checks that should all pass before submitting a pull request
# ****************************************************************************************
# In a perfect world, these would also pass before every commit.
#
#
# Imports
# =======
# These are listed in the order prescribed by `PEP 8`_.
#
# Standard library
# ----------------
# None.
#
# Third-party imports
# -------------------
# None.
#
# Local application imports
# -------------------------
from ci_utils import xqt, pushd


# Checks
# ======
def checks():
    xqt(
        # fmt: off
        "black --check .",
        "flake8",
        "mypy",
        "tox",
        # fmt: on
    )
    with pushd(".."):
        xqt(
            # Check the docs. Again, these only require fixes to comments, and should still be relatively easy to correct.
            #
            # Force a `full build <https://www.sphinx-doc.org/en/master/man/sphinx-build.html>`_:
            #
            # -E    Don’t use a saved environment (the structure caching all cross-references), but rebuild it completely.
            # -a    If given, always write all output files.
            "sphinx-build -E -a . _build",
        )


if __name__ == "__main__":
    checks()
