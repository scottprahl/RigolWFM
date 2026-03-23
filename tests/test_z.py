"""Snapshot tests for Rigol 1000Z-family `wfmconvert info` output."""

import pytest

from tests.cli_helpers import assert_wfmconvert_info_snapshot

_Z_INFO_CASES = [
    "DS1074Z-C",
    "DS1054Z-A",
    "MSO1104",
    "DS1074Z-A",
    "DS1074Z-B",
]


@pytest.mark.parametrize("stem", _Z_INFO_CASES)
def test_wfmconvert_z_info_matches_snapshot(stem):
    """`wfmconvert Z info` should match the checked-in snapshot output."""
    assert_wfmconvert_info_snapshot("Z", stem, "z")
