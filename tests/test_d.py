"""Snapshot tests for Rigol 1000D-family `wfmconvert info` output."""

from tests.cli_helpers import assert_wfmconvert_info_snapshot


def test_wfmconvert_d_info_matches_snapshot():
    """`wfmconvert D info` should match the checked-in snapshot output."""
    assert_wfmconvert_info_snapshot("D", "DS1102D-A", "d")
