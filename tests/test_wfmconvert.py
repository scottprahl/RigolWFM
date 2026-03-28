"""Integration checks for core `wfmconvert` output modes."""

from tests.cli_helpers import run_command


_LEGACY_INFO = [
    ("B",    "tests/files/wfm/DS1204B-A.wfm"),
    ("C",    "tests/files/wfm/DS1202CA-A.wfm"),
    ("D",    "tests/files/wfm/DS1102D-A.wfm"),
    ("E",    "tests/files/wfm/DS1102E-A.wfm"),
    ("Z",    "tests/files/wfm/MSO1104.wfm"),
    ("2",    "tests/files/wfm/DS2202.wfm"),
    ("4",    "tests/files/wfm/DS4022-A.wfm"),
]

_BIN_INFO = [
    ("5",    "tests/files/bin/MSO5000-A.bin"),
    ("5074", "tests/files/bin/MSO5074-A.bin"),
    ("DHO",  "tests/files/bin/DHO1074.bin"),
    ("DHO",  "tests/files/bin/DHO824-ch1.bin"),
]


def test_wfmconvert_info():
    """Verify `info` conversion succeeds for representative scopes."""
    for scope, path in _LEGACY_INFO + _BIN_INFO:
        run_command(f"wfmconvert --model {scope} info {path}")


def test_wfmconvert_csv(tmp_path):
    """Verify CSV export succeeds for representative scopes."""
    for scope, path in _LEGACY_INFO + _BIN_INFO:
        run_command(f"wfmconvert --model {scope} --output-dir {tmp_path} csv {path}")


def test_wfmconvert_wav(tmp_path):
    """Verify WAV export succeeds for representative scopes."""
    for scope, path in _LEGACY_INFO + _BIN_INFO:
        run_command(f"wfmconvert --model {scope} --channel 1 --output-dir {tmp_path} wav {path}")


def test_wfmconvert_vcsv(tmp_path):
    """Verify VCSV export succeeds for representative scopes."""
    for scope, path in _LEGACY_INFO + _BIN_INFO:
        run_command(f"wfmconvert --model {scope} --output-dir {tmp_path} vcsv {path}")


def test_wfmconvert_sigrok(tmp_path):
    """Verify sigrok export succeeds (or gracefully skips if sigrok-cli absent)."""
    for scope, path in _LEGACY_INFO + _BIN_INFO:
        run_command(f"wfmconvert --model {scope} --output-dir {tmp_path} sigrok {path}")
