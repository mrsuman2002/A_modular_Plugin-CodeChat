# ***************************************
# |docname| - pytest fixtures for testing
# ***************************************
#
# Imports
# =======
# These are listed in the order prescribed by `PEP 8
# <http://www.python.org/dev/peps/pep-0008/#imports>`_.
#
# Standard library
# ----------------
import subprocess
import sys
import io

# Third-party imports
# -------------------
import coverage
import pytest

# Local imports
# -------------
# Start code coverage here. The imports below load code that must be covered. This seems cleaner than other solutions (create a separate pytest plugin just for coverage, put coverage code in a ``conftest.py`` that's imported before this one.)
cov = coverage.Coverage()
cov.start()

from CodeChat_Server.__main__ import get_client  # noqa: E402


# .. _code_coverage:
#
# Code coverage
# -------------
# Getting code coverage to work in tricky. This is because code coverage must be collected while running pytest and while running the webserver. Since these run in parallel, trying to create a single coverage data file doesn't work. Therefore, we must set coverage's `parallel flag to True <parallel=True>`, so that each data file will be uniquely named. After pytest finishes, combine these two data files to produce a coverage result. While pytest-cov would be ideal, it `overrides <https://pytest-cov.readthedocs.io/en/latest/config.html>`_ the ``parallel`` flag (sigh).
#
# A simpler solution: invoke ``coverage run -m pytest``, then ``coverage combine``, then ``coverage report``. I opted for this complexity, to make it easy to just invoke pytest and get coverage with no further steps.
# Output a coverage report when testing is done. See the `docs <https://docs.pytest.org/en/latest/reference.html#_pytest.hookspec>`__.pytest_terminal_summary.
def pytest_terminal_summary(terminalreporter):
    cov.stop()
    cov.save()
    # Combine this (pytest) coverage with the webserver coverage. Use a new object, since the ``cov`` object is tried to the data file produced by the pytest run. Otherwise, the report is correct, but the resulting ``.coverage`` data file is empty.
    cov_all = coverage.Coverage()
    cov_all.combine()

    # Report on this combined data.
    f = io.StringIO()
    cov_all.report(file=f)
    terminalreporter.write(f.getvalue())


# Fixtures
# ========
SUBPROCESS_SERVER_ARGS = [
    sys.executable,
    "-m",
    "coverage",
    "run",
    "-m",
    "CodeChat_Server",
]


@pytest.fixture
def run_server():
    subprocess.run(SUBPROCESS_SERVER_ARGS + ["start"], check=True)
    yield
    subprocess.run(SUBPROCESS_SERVER_ARGS + ["stop"], check=True)


@pytest.fixture
def editor_plugin(run_server):
    return get_client()
