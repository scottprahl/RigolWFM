"""Tests for the `.github/scripts/update_citation.py` release helper.

The script only runs when a release is published, so a mistake in it stays
invisible until the worst possible moment.  It failed on the 1.6.0 release
because it could not read a version that carries a type annotation.
"""

import importlib.util
from pathlib import Path

import pytest

import RigolWFM

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / ".github" / "scripts" / "update_citation.py"


def _load_script():
    """Import the release helper from its path; it is not on a package path."""
    spec = importlib.util.spec_from_file_location("update_citation", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_reads_the_version_this_package_actually_declares():
    """The helper must read the real `RigolWFM/__init__.py`, annotation and all."""
    assert _load_script().get_code_version() == RigolWFM.__version__


@pytest.mark.parametrize(
    "declaration",
    [
        '__version__ = "1.2.3"',
        "__version__ = '1.2.3'",
        '__version__: str = "1.2.3"',  # what this package writes
        '__version__:str="1.2.3"',
        '__version__ : str = "1.2.3"',
    ],
)
def test_accepts_every_spelling_of_the_version_assignment(tmp_path, monkeypatch, declaration):
    """An annotation, or the lack of one, should not change the answer."""
    module = _load_script()

    package = tmp_path / module.REPO
    package.mkdir()
    (package / "__init__.py").write_text(f'"""Docstring."""\n\n{declaration}\n', encoding="utf-8")

    monkeypatch.chdir(tmp_path)
    assert module.get_code_version() == "1.2.3"


def test_reports_a_missing_version_clearly(tmp_path, monkeypatch):
    """A file with no version at all should still fail loudly."""
    module = _load_script()

    package = tmp_path / module.REPO
    package.mkdir()
    (package / "__init__.py").write_text('"""No version here."""\n', encoding="utf-8")

    monkeypatch.chdir(tmp_path)
    with pytest.raises(RuntimeError, match="Could not find"):
        module.get_code_version()
