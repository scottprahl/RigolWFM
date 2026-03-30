"""Tests for Rigol 5000-family `.bin` waveform parsing."""

from pathlib import Path

import pytest
import RigolWFM.rigol_mso5000_bin
import RigolWFM.mso5000
import RigolWFM.wfm

from tests.cli_helpers import assert_wfmconvert_info_snapshot_file

_5_CASES = [
    (
        "MSO5000-A",
        1000,
        4.999999873689376e-06,
        0.002499999936844688,
    ),
    (
        "MSO5000-B",
        1_000_000,
        1.0000000116860974e-07,
        0.05000000058430487,
    ),
]


def _example_path(stem):
    """Return the path to a checked-in MSO5000 example file."""
    return Path("tests/files/bin") / f"{stem}.bin"


@pytest.mark.parametrize("stem, _points, _dt, _xorigin", _5_CASES)
def test_wfmconvert_5_info_matches_snapshot(stem, _points, _dt, _xorigin):
    """`wfmconvert 5 info` should match the checked-in snapshot output."""
    assert_wfmconvert_info_snapshot_file("5", _example_path(stem), "5", stem)


@pytest.mark.parametrize("stem, points, dt, xorigin", _5_CASES)
def test_bin5000_low_level_header_matches_examples(stem, points, dt, xorigin):
    """The low-level MSO5000 parser should match the shipped example headers."""
    waveform = RigolWFM.rigol_mso5000_bin.RigolMso5000Bin.from_file(str(_example_path(stem)))

    assert waveform.file_header.cookie == b"RG"
    assert waveform.file_header.n_waveforms == 4

    first = waveform.waveforms[0]
    assert first.wfm_header.header_size == 140
    assert first.wfm_header.n_pts == points
    assert first.wfm_header.x_increment == pytest.approx(dt)
    assert first.wfm_header.x_origin == pytest.approx(xorigin)
    assert first.data_header.header_size == 12
    assert first.data_header.bytes_per_point == 4
    assert first.data_header.buffer_size == points * 4


@pytest.mark.parametrize("stem, points, dt, xorigin", _5_CASES)
def test_mso5000_adapter_exposes_exact_timing(stem, points, dt, xorigin):
    """The normalized MSO5000 adapter should preserve timing and samples."""
    waveform = RigolWFM.mso5000.from_file(str(_example_path(stem)))

    assert waveform.header.model_number.startswith("MSO5")
    assert waveform.header.points == points
    assert waveform.header.seconds_per_point == pytest.approx(dt)
    assert waveform.header.x_origin == pytest.approx(xorigin)
    assert [channel.enabled for channel in waveform.header.ch] == [True] * 4


@pytest.mark.parametrize("stem, _points, dt, xorigin", _5_CASES)
def test_mso5000_time_grid_matches_sample_period(stem, _points, dt, xorigin):
    """Adjacent MSO5000 timestamps should match the reported sample period."""
    waveform = RigolWFM.wfm.Wfm.from_file(str(_example_path(stem)), "5")
    for channel in waveform.channels:
        assert channel.times[0] == pytest.approx(-xorigin)
        assert channel.times[1] - channel.times[0] == pytest.approx(dt)
