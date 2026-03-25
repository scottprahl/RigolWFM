"""Tests for Rigol MSO5074 binary waveform parsing."""

from pathlib import Path

import pytest
import RigolWFM.mso5074
import RigolWFM.wfm

from tests.cli_helpers import assert_wfmconvert_info_snapshot_file

_5074_CASES = [
    # (stem, n_channels, n_pts_per_channel)
    ("MSO5074-A", 2, 1000),
    ("MSO5074-B", 4, 100000),
]


def _example_path(stem):
    """Return the path to a checked-in MSO5074 example file."""
    return Path("wfm") / f"{stem}.bin"


@pytest.mark.parametrize("stem, _n_ch, _pts", _5074_CASES)
def test_wfmconvert_5074_info_matches_snapshot(stem, _n_ch, _pts):
    """`wfmconvert 5074 info` should match the checked-in snapshot output."""
    assert_wfmconvert_info_snapshot_file("5074", _example_path(stem), "5074", stem)


@pytest.mark.parametrize("stem, n_channels, pts_per_channel", _5074_CASES)
def test_mso5074_adapter_channel_count(stem, n_channels, pts_per_channel):
    """The MSO5074 adapter should detect the correct number of channels."""
    obj = RigolWFM.mso5074.from_file(str(_example_path(stem)))
    enabled = [ch for ch in obj.header.ch if ch.enabled]
    assert len(enabled) == n_channels
    assert obj.header.n_pts == pts_per_channel


@pytest.mark.parametrize("stem, _n_channels, _pts_per_channel", _5074_CASES)
def test_mso5074_adapter_model_name(stem, _n_channels, _pts_per_channel):
    """The MSO5074 adapter should extract the model name from the frame string."""
    obj = RigolWFM.mso5074.from_file(str(_example_path(stem)))
    assert obj.header.model.startswith("MSO5074")


@pytest.mark.parametrize("stem, n_channels, pts_per_channel", _5074_CASES)
def test_mso5074_wfm_channels(stem, n_channels, pts_per_channel):
    """Wfm.from_file with model '5074' should expose all enabled channels."""
    waveform = RigolWFM.wfm.Wfm.from_file(str(_example_path(stem)), "5074")
    assert len(waveform.channels) == n_channels
    for channel in waveform.channels:
        assert len(channel.volts) == pts_per_channel
        assert len(channel.times) == pts_per_channel
        assert len(channel.raw) == pts_per_channel
