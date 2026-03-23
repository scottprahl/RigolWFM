"""Snapshot tests for Rigol 1000E-family `wfmconvert info` output."""

import pytest

from tests.cli_helpers import assert_wfmconvert_info_snapshot

_E_INFO_CASES = [
    "DS1102E-A",
    "DS1102E-B",
    "DS1102E-C",
    "DS1102E-D",
    "DS1102E-E",
    "DS1102E-F",
    "DS1102E-G",
    "DS1052E",
    "DS1000E-A",
    "DS1000E-B",
    "DS1000E-C",
    "DS1000E-D",
]


@pytest.mark.parametrize("stem", _E_INFO_CASES)
def test_wfmconvert_e_info_matches_snapshot(stem):
    """`wfmconvert E info` should match the checked-in snapshot output."""
    assert_wfmconvert_info_snapshot("E", stem, "e")
