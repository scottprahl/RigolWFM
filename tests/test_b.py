"""Snapshot tests for Rigol 1000B-family `wfmconvert info` output."""

import pytest

from tests.cli_helpers import assert_wfmconvert_info_snapshot

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
    assert_wfmconvert_info_snapshot("B", stem, "b")
