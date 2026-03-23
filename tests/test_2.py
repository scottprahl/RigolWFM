"""Snapshot tests for Rigol 2000-family `wfmconvert info` output."""

import pytest

from tests.cli_helpers import assert_wfmconvert_info_snapshot

_2_INFO_CASES = [
    "DS2072A-1",
    "DS2072A-2",
    "DS2072A-3",
    "DS2072A-4",
    "DS2072A-5",
    "DS2072A-6",
    "DS2072A-7",
    "DS2072A-8",
    "DS2072A-9",
    "DS2000-A",
    "DS2000-B",
]


@pytest.mark.parametrize("stem", _2_INFO_CASES)
def test_wfmconvert_2_info_matches_snapshot(stem):
    """`wfmconvert 2 info` should match the checked-in snapshot output."""
    assert_wfmconvert_info_snapshot("2", stem, "2")
