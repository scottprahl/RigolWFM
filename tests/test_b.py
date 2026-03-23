"""Snapshot tests for Rigol 1000B-family `wfmconvert info` output."""

from pathlib import Path

import pytest

from tests.cli_helpers import assert_command_matches_file

_EXPECTED_DIR = Path(__file__).resolve().parent / "expected_info" / "b"
_B_INFO_CASES = [
    "DS1204B-A",
    "DS1204B-B",
    "DS1204B-C",
    "DS1204B-D",
    "DS1204B-E",
]


@pytest.mark.parametrize("stem", _B_INFO_CASES)
def test_wfmconvert_b_info_matches_snapshot(stem):
    """`wfmconvert B info` should match the checked-in snapshot output."""
    command = f"wfmconvert B info wfm/{stem}.wfm"
    expected = _EXPECTED_DIR / f"{stem}.txt"
    assert_command_matches_file(command, expected)
