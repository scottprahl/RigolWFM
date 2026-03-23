"""Snapshot tests for Rigol 1000C-family `wfmconvert info` output."""

import pytest

from tests.cli_helpers import assert_wfmconvert_info_snapshot

_C_INFO_CASES = [
    "DS1202CA-A",
    "DS1042C-A",
]


@pytest.mark.parametrize("stem", _C_INFO_CASES)
def test_wfmconvert_c_info_matches_snapshot(stem):
    """`wfmconvert C info` should match the checked-in snapshot output."""
    assert_wfmconvert_info_snapshot("C", stem, "c")
