# ****************************************************
# |docname| - Tests for `../CodeChat_Server/server.py`
# ****************************************************
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
# Local imports
# -------------
from CodeChat_Server.server import is_port_in_use


def test_1():
    assert is_port_in_use(5000) is True
