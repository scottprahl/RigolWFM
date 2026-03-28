"""Integration checks for `wfmconvert` sigrok export."""

from pathlib import Path
import tempfile

from tests.cli_helpers import run_command


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


# Run the tests
if __name__ == "__main__":
    with tempfile.TemporaryDirectory() as tmpdir:
        test_wfmconvert_sigrok(Path(tmpdir))
    print("All tests passed!")
