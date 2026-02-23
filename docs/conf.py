"""
Sphinx configuration for RigolWFM documentation.

Uses:
- sphinx.ext.napoleon for Google-style docstrings
- nbsphinx for rendering Jupyter notebooks (pre-executed; no execution on RTD)
"""

import re
from importlib.metadata import PackageNotFoundError
from importlib.metadata import version as pkg_version
from pathlib import Path

project = "RigolWFM"
try:
    release = pkg_version(project)
except PackageNotFoundError:
    init_path = Path(__file__).resolve().parents[1] / project / "__init__.py"
    init_text = init_path.read_text(encoding="utf-8")
    match = re.search(r'__version__\s*=\s*["\']([^"\']+)["\']', init_text)
    release = match.group(1) if match else "0.0.0"
version = release

root_doc = "index"

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "sphinx.ext.mathjax",
    "sphinx_automodapi.automodapi",
    "nbsphinx",
]

napoleon_use_param = False
napoleon_use_rtype = False
numpydoc_show_class_members = False

exclude_patterns = [
    "_build",
    ".ipynb_checkpoints",
    "first_version",
    "sources",
    "manuals",
]

nbsphinx_execute = "never"
nbsphinx_allow_errors = True

html_theme = "sphinx_rtd_theme"
html_scaled_image_link = False
html_sourcelink_suffix = ""
