"""Snapshot tests for Rigol 4000-family `wfmconvert info` output."""

import pytest

from tests.cli_helpers import assert_wfmconvert_info_snapshot

_4_INFO_CASES = [
    "DS4022-A",
    "DS4022-B",
    "DS4024-A",
    "DS4024-B",
]


@pytest.mark.parametrize("stem", _4_INFO_CASES)
def test_wfmconvert_4_info_matches_snapshot(stem):
    """`wfmconvert 4 info` should match the checked-in snapshot output."""
    assert_wfmconvert_info_snapshot("4", stem, "4")
