"""Snapshot tests for Rigol 1000E-family `wfmconvert info` output."""

import pytest
import RigolWFM.wfm

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

_DS1102E_POINT_CASES = [
    ("DS1102E-A", (16384,)),
    ("DS1102E-B", (16384,)),
    ("DS1102E-C", (16384,)),
    ("DS1102E-D", (8192, 8192)),
    ("DS1102E-E", (1048576,)),
    ("DS1102E-F", (16384,)),
    ("DS1102E-G", (16384,)),
]


@pytest.mark.parametrize("stem", _E_INFO_CASES)
def test_wfmconvert_e_info_matches_snapshot(stem):
    """`wfmconvert E info` should match the checked-in snapshot output."""
    assert_wfmconvert_info_snapshot("E", stem, "e")


@pytest.mark.parametrize("stem, expected_points", _DS1102E_POINT_CASES)
def test_ds1102e_channel_counts_follow_memory_depth(stem, expected_points):
    """DS1102E captures should preserve the full stored analog memory depth."""
    waveform = RigolWFM.wfm.Wfm.from_file(f"wfm/{stem}.wfm", "E")
    actual_points = tuple(channel.points for channel in waveform.channels if channel.enabled)
    assert actual_points == expected_points


@pytest.mark.parametrize("stem, _expected_points", _DS1102E_POINT_CASES)
def test_ds1102e_time_grid_matches_sample_period(stem, _expected_points):
    """Adjacent timestamps should be spaced by the reported sample period."""
    waveform = RigolWFM.wfm.Wfm.from_file(f"wfm/{stem}.wfm", "E")
    for channel in waveform.channels:
        if channel.enabled:
            assert channel.times[1] - channel.times[0] == pytest.approx(
                channel.seconds_per_point
            )
