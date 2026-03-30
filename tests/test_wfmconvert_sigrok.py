"""Integration checks for `wfmconvert` sigrok export."""

from __future__ import annotations

from pathlib import Path
import tempfile
import shlex

from tests.cli_helpers import run_command
from tests.test_isf import _build_isf
from tests.test_lecroy import _build_trc
from tests.test_siglent import _build_siglent_v6
from tests.test_yokogawa import _build_yokogawa_wfm


_ROOT = Path(__file__).resolve().parents[1]
_KEYSIGHT = _ROOT / "tests" / "files" / "bin" / "agilent_1.bin"
_ROHDE = _ROOT / "docs" / "vendors" / "rohde & schwarz" / "rs_file_reader-main" / "tests" / "testdata" / "singleChan.bin"


def _quote(path: Path | str) -> str:
    """Shell-quote a path for CLI integration."""
    return shlex.quote(str(path))


def _newer_sigrok_cases(tmp_path: Path) -> list[tuple[str, str]]:
    """Return newer-family sigrok fixtures."""
    siglent = tmp_path / "synthetic_siglent_v6.bin"
    siglent.write_bytes(_build_siglent_v6())

    lecroy = tmp_path / "synthetic_lecroy.trc"
    lecroy.write_bytes(_build_trc(n_pts=4, samples=[0, 1, 2, 3]))

    isf = tmp_path / "synthetic_tek.isf"
    isf.write_bytes(_build_isf(samples=[-10, 0, 10, 20]))

    yokogawa = tmp_path / "synthetic_yokogawa.wfm"
    yokogawa.write_bytes(_build_yokogawa_wfm(raw_samples=[0.0, 1.0, -2.0, 4.0]))

    return [
        ("Keysight", _quote(_KEYSIGHT)),
        ("RohdeSchwarz", _quote(_ROHDE)),
        ("Siglent", _quote(siglent)),
        ("LeCroy", _quote(lecroy)),
        ("ISF", _quote(isf)),
        ("Yokogawa", _quote(yokogawa)),
    ]


def test_wfmconvert_sigrok(tmp_path):
    """Verify sigrok export succeeds for representative scopes."""
    cases = [
        ("B", "tests/files/wfm/DS1204B-A.wfm"),
        ("C", "tests/files/wfm/DS1202CA-A.wfm"),
        ("D", "tests/files/wfm/DS1102D-A.wfm"),
        ("E", "tests/files/wfm/DS1102E-A.wfm"),
        ("Z", "tests/files/wfm/MSO1104.wfm"),
        ("2", "tests/files/wfm/DS2202.wfm"),
        ("4", "tests/files/wfm/DS4022-A.wfm"),
    ]

    for scope, path in cases:
        run_command(f"wfmconvert --model {scope} --output-dir {tmp_path} sigrok {path}")
    for scope, path in _newer_sigrok_cases(tmp_path):
        run_command(f"wfmconvert --model {scope} --output-dir {_quote(tmp_path)} sigrok {path}")


# Run the tests
if __name__ == "__main__":
    with tempfile.TemporaryDirectory() as tmpdir:
        test_wfmconvert_sigrok(Path(tmpdir))
    print("All tests passed!")
