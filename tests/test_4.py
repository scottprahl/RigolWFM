"""Snapshot tests for Rigol 4000-family `wfmconvert info` output."""

import pytest
import RigolWFM.wfm

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


@pytest.mark.parametrize("stem", _4_INFO_CASES)
def test_ds4000_time_grid_matches_sample_period(stem):
    """Adjacent DS4000 timestamps should match the reported sample period."""
    waveform = RigolWFM.wfm.Wfm.from_file(f"wfm/{stem}.wfm", "4")
    for channel in waveform.channels:
        if channel.enabled:
            assert channel.times[1] - channel.times[0] == pytest.approx(
                channel.seconds_per_point
            )
