"""
This file is intended to be the target of a pytest run.

It recursively finds all `.ipynb` files in the docs directory, ignoring
directories that start with '.' and any files matching patterns found in the file
`.testignore`

Sample invocations of pytest which make the output nicely readable::

    pytest --verbose --durations=5 test_all_notebooks.py

If you install `pytest-xdist` you can run tests in parallel with::

    pytest --verbose --durations=5 -n 4 test_all_notebooks.py

Original version is licensed under GPL 3.0 so this modified one is as well.

The original is at::

    https://github.com/alchemyst/Dynamics-and-Control/blob/main/test_all_notebooks.py
"""

import os.path
import pathlib
import pytest
import nbformat
import nbconvert.preprocessors

_SAMPLE_FILES = pathlib.Path(__file__).resolve().parents[1] / "tests" / "files"

# Prepended to every notebook before it runs.  See the comment inside.
_OFFLINE_SETUP_TEMPLATE = '''
# Injected by tests/test_all_notebooks.py.  The notebooks fetch their sample
# captures from raw.githubusercontent.com, which is the right thing for a reader
# running one on its own but makes the test suite depend on the network being up
# and on GitHub not rate-limiting ~40 requests.  Every one of those files is
# already in this checkout, so serve them from there and leave the notebook's own
# code, and what it demonstrates, untouched.
import pathlib as _pathlib
import urllib.parse as _urlparse
import urllib.request as _urlrequest

import requests as _requests

import RigolWFM.wfm as _wfm

_SAMPLES = _pathlib.Path(__SAMPLES__)
_PREFIX = "https://raw.githubusercontent.com/scottprahl/RigolWFM/main/tests/files/"


def _local_copy(url):
    """Return the checked-out file a sample URL refers to, or None."""
    text = str(url)
    if not text.startswith(_PREFIX):
        return None
    relative = _urlparse.urlparse(text[len(_PREFIX) :]).path
    candidate = _SAMPLES / relative
    return candidate if candidate.is_file() else None


_real_from_url = _wfm.Wfm.from_url


def _from_url(cls, url, *args, **kwargs):
    local = _local_copy(url)
    if local is not None:
        return cls.from_file(str(local), *args, **kwargs)
    return _real_from_url(url, *args, **kwargs)


_wfm.Wfm.from_url = classmethod(_from_url)

_real_urlretrieve = _urlrequest.urlretrieve


def _urlretrieve(url, filename=None, *args, **kwargs):
    local = _local_copy(url)
    if local is not None and filename is not None:
        import shutil as _shutil

        _shutil.copyfile(local, filename)
        return str(filename), None
    return _real_urlretrieve(url, filename, *args, **kwargs)


_urlrequest.urlretrieve = _urlretrieve

_real_urlopen = _urlrequest.urlopen


def _urlopen(url, *args, **kwargs):
    # imageio reaches the reference screenshots through urlopen, and patching the
    # primitive covers anything else on urllib rather than each caller.
    target = url.full_url if hasattr(url, "full_url") else url
    local = _local_copy(target)
    if local is not None:
        return open(local, "rb")
    return _real_urlopen(url, *args, **kwargs)


_urlrequest.urlopen = _urlopen

_real_get = _requests.get


class _LocalResponse:
    """The small part of a requests response the notebooks actually use."""

    def __init__(self, data):
        self.content = data
        self.status_code = 200

    @property
    def text(self):
        return self.content.decode("utf-8")

    def raise_for_status(self):
        return None


def _get(url, *args, **kwargs):
    local = _local_copy(url)
    if local is not None:
        return _LocalResponse(local.read_bytes())
    return _real_get(url, *args, **kwargs)


_requests.get = _get

import numpy as _np

_real_genfromtxt = _np.genfromtxt


def _genfromtxt(fname, *args, **kwargs):
    local = _local_copy(fname) if isinstance(fname, str) else None
    return _real_genfromtxt(str(local) if local is not None else fname, *args, **kwargs)


_np.genfromtxt = _genfromtxt

_real_loadtxt = _np.loadtxt


def _loadtxt(fname, *args, **kwargs):
    local = _local_copy(fname) if isinstance(fname, str) else None
    return _real_loadtxt(str(local) if local is not None else fname, *args, **kwargs)


_np.loadtxt = _loadtxt
'''

_OFFLINE_SETUP = _OFFLINE_SETUP_TEMPLATE.replace("__SAMPLES__", repr(str(_SAMPLE_FILES)))

# Default search path is the current directory
searchpath = pathlib.Path(".")

# Read patterns from .testignore file
ignores = []
if os.path.exists(".testignore"):
    with open(".testignore", encoding="utf-8") as file:
        ignores = [line.strip() for line in file if line.strip()]

# Ignore hidden folders (startswith('.')) and files matching ignore patterns
notebooks = [
    notebook
    for notebook in searchpath.glob("docs/*.ipynb")
    if not (
        any(parent.startswith(".") for parent in notebook.parent.parts)
        or any(notebook.match(pattern) for pattern in ignores)
    )
]

notebooks.sort()
ids = [str(n) for n in notebooks]

# Notebooks with known pre-existing failures not related to RigolWFM itself.
# These are marked xfail so CI reports them as expected failures rather than errors.
KNOWN_FAILURES = {}


@pytest.mark.parametrize("notebook", notebooks, ids=ids)
def test_run_notebook(notebook):
    """Read and execute notebook.

    The method here is directly from the nbconvert docs

    There is no error handling as any errors will be caught by pytest
    """
    reason = KNOWN_FAILURES.get(str(notebook))
    if reason:
        pytest.xfail(reason)

    with open(notebook, encoding="utf-8") as f:
        nb = nbformat.read(f, as_version=4)

    # Serve the notebook's downloads from this checkout.  The notebook itself is
    # not modified on disk; this cell only exists for the duration of the run.
    nb.cells.insert(0, nbformat.v4.new_code_cell(_OFFLINE_SETUP))
    # Quiet the kernel's own logger.  Starting it over TCP makes ipykernel warn
    # about unencrypted transport on every notebook, which is noise here: the
    # kernel is local and short-lived.  IPC transport would also silence it, but
    # it is not available on Windows.  Execution errors still reach us, since
    # they are raised by preprocess() rather than logged.
    ep = nbconvert.preprocessors.ExecutePreprocessor(timeout=600, extra_arguments=["--log-level=ERROR"])
    try:
        ep.preprocess(nb, {"metadata": {"path": notebook.parent}})
    except PermissionError as exc:
        if "Operation not permitted" in str(exc):
            pytest.skip("Notebook execution requires local kernel ports, unavailable in this environment.")
        raise
