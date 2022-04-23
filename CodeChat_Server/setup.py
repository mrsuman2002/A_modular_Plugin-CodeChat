# .. Copyright (C) 2012-2022 Bryan A. Jones.
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
# ***************************************************
# |docname| - Package and install the CodeChat Server
# ***************************************************
# Builds and installs CodeChat.
#
# Contents
# ========
# .. toctree::
#   :maxdepth: 2
#
#   setup.cfg
#   MANIFEST.in
#
#
# Release procedure
# =================
# - Update the version in `CodeChat_Server/__init__.py`.
# - Run `tests/pre_commit_check.py`.
# - Create a source distribution, a built distribution, then upload both to `CodeChat_Server at PyPI <https://pypi.python.org/pypi/CodeChat_Server>`_:
#
#   .. code-block:: console
#       :linenos:
#
#       python -m pip install -U pip setuptools wheel twine
#       python setup.py sdist bdist_wheel
#       python -m twine upload dist/*
#
# For `development
# <https://pythonhosted.org/setuptools/setuptools.html#development-mode>`_:
#
# .. code-block:: console
#   :linenos:
#
#   pip install -e .[test]
#
#
# Packaging script
# ================
#
# PyPA copied code
# ----------------
# From `PyPA's sample setup.py
# <https://github.com/pypa/sampleproject/blob/master/setup.py>`__,
# read ``long_description`` from a file. This code was last updated on
# 15-Jun-2020 based on `this commit
# <https://github.com/pypa/sampleproject/commit/3b73bd9433d031f0873a6cbc5bd04cea2e3407cb>`_.
#
# Always prefer setuptools over distutils
from setuptools import setup, find_packages  # type: ignore
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, "README.rst"), encoding="utf-8") as f:
    long_description = f.read()


# This code was copied from `version parse code <https://packaging.python.org/guides/single-sourcing-package-version/>`_ then lightly modified. See ``version`` in the call to ``setup`` below.
def read(rel_path):
    with open(path.join(here, rel_path), "r", encoding="utf-8") as fp:
        return fp.read()


def get_version(rel_path):
    for line in read(rel_path).splitlines():
        if line.startswith("__version__"):
            delim = '"' if '"' in line else "'"
            return line.split(delim)[1]
    else:
        raise RuntimeError("Unable to find version string.")


# My code
# -------
setup(
    # This must comply with `PEP 0426
    # <http://legacy.python.org/dev/peps/pep-0426/#name>`_'s
    # name requirements.
    name="CodeChat_Server",
    version=get_version("CodeChat_Server/__init__.py"),
    description="The CodeChat Server for software documentation",
    long_description=long_description,
    # The project's main homepage.
    url="http://codechat.readthedocs.io/en/latest/",
    author="Bryan A. Jones",
    author_email="bjones@ece.msstate.edu",
    license="GPLv3+",
    # These are taken from the `full list
    # <https://pypi.python.org/pypi?%3Aaction=list_classifiers>`_.
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Operating System :: OS Independent",
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Topic :: Software Development :: Documentation",
        "Topic :: Text Processing :: Markup",
    ],
    keywords="literate programming",
    packages=find_packages(),
    # List run-time dependencies here.  These will be installed by pip when
    # your project is installed. For an analysis of "install_requires" vs pip's
    # requirements files see:
    # https://packaging.python.org/en/latest/requirements.html
    install_requires=(
        [
            "bottle",
            "CodeChat",
            "markdown",
            "psutil",
            "Sphinx",
            "strictyaml",
            "thrift",
            "typer",
            "watchdog",
            "websockets",
        ]
    ),
    # List additional groups of dependencies here (e.g. development
    # dependencies). You can install these using the following syntax,
    # for example:
    #
    #    ``$ pip install -e .[test]``
    extras_require={
        "test": ["black", "coverage", "flake8", "mypy", "pytest", "requests", "tox"]
    },
    # To package data files, I'm using ``include_package_data=True`` then
    # putting the files in :doc:`MANIFEST.in <MANIFEST.in>`. See `including data
    # files <http://pythonhosted.org/setuptools/setuptools.html#including-data-files>`_.
    include_package_data=True,
    # _`Python version support`: the program uses ``asyncio.run``, which was introduced in Python 3.7. `Tox` tests also run beginning at Python 3.7.
    python_requires=">=3.7",
    # Make it easy to run the server.
    entry_points={
        "console_scripts": ["CodeChat_Server = CodeChat_Server.__main__:app"]
    },
)
