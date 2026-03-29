"""Tests for Agilent / Keysight `AGxx` `.bin` waveform parsing."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest

import RigolWFM.agilent
import RigolWFM.agilent_bin
import RigolWFM.wfm

_ROOT = Path(__file__).resolve().parents[1]
_SAMPLES = _ROOT / "docs" / "vendors" / "wavebin-master" / "samples"
_DSOX = _SAMPLES / "DSOX1102G"
_SINGLE = _DSOX / "single.bin"
_DUAL = _DSOX / "dual.bin"
_DIGITAL = _DSOX / "digital.bin"
_MSOX4154A = _SAMPLES / "MSOX4154A.bin"

pytestmark = pytest.mark.skipif(
    not all(path.exists() for path in (_SINGLE, _DUAL, _DIGITAL, _MSOX4154A)),
    reason="wavebin Agilent/Keysight sample files are not present",
)


def test_agilent_bin_low_level_header_matches_wavebin_single():
    """The low-level Kaitai parser should match the checked-in single-trace sample."""
    waveform = RigolWFM.agilent_bin.AgilentBin.from_file(str(_SINGLE))

    assert waveform.file_header.cookie == b"AG"
    assert waveform.file_header.version == "10"
    assert waveform.file_header.version_num == 10
    assert waveform.file_header.file_size == _SINGLE.stat().st_size
    assert waveform.file_header.n_waveforms == 1

    first = waveform.waveforms[0]
    assert first.wfm_header.header_size == 140
    assert first.wfm_header.n_pts == 1953
    assert first.wfm_header.x_display_origin == pytest.approx(-1.0e-3)
    assert first.wfm_header.x_increment == pytest.approx(1.024e-6)
    assert first.data_header.header_size == 12
    assert first.data_header.bytes_per_point == 4
    assert first.data_header.buffer_size == 7812


def test_agilent_adapter_preserves_single_trace_samples():
    """The normalized adapter should preserve the calibrated float32 waveform."""
    raw = RigolWFM.agilent_bin.AgilentBin.from_file(str(_SINGLE))
    obj = RigolWFM.agilent.from_file(str(_SINGLE))

    assert obj.header.model_number == "DSO-X 1102G"
    assert obj.header.serial_number == "CN00000000"
    assert obj.header.points == 1953
    assert obj.header.seconds_per_point == pytest.approx(1.024e-6)
    assert obj.header.x_origin == pytest.approx(-1.0e-3)
    assert [channel.enabled for channel in obj.header.ch] == [True, False, False, False]

    expected = np.frombuffer(raw.waveforms[0].data_raw, dtype="<f4")
    np.testing.assert_allclose(obj.header.channel_data[0], expected)


def test_agilent_dual_capture_round_trips_through_wfm():
    """Auto-detected dual-channel captures should expose both analog channels."""
    waveform = RigolWFM.wfm.Wfm.from_file(str(_DUAL))

    assert waveform.parser_name == "agilent_bin"
    assert waveform.header_name == "DSO-X 1102G"
    assert waveform.serial_number == "CN00000000"
    assert [channel.channel_number for channel in waveform.channels] == [1, 2]

    for channel in waveform.channels:
        assert channel.times is not None
        assert channel.volts is not None
        assert channel.times[0] == pytest.approx(-1.0e-6)
        assert channel.times[1] - channel.times[0] == pytest.approx(5.0e-10)


def test_agilent_digital_capture_skips_ext_u8_record():
    """Mixed analog/digital captures should keep the analog trace and ignore EXT digital data."""
    obj = RigolWFM.agilent.from_file(str(_DIGITAL))
    waveform = RigolWFM.wfm.Wfm.from_file(str(_DIGITAL))

    assert obj.header.n_waveforms == 2
    assert [channel.enabled for channel in obj.header.ch] == [True, False, False, False]
    assert len(waveform.channels) == 1
    assert waveform.channels[0].channel_number == 1
    assert waveform.channels[0].times[0] == pytest.approx(-1.0e-5)
    assert waveform.channels[0].times[1] - waveform.channels[0].times[0] == pytest.approx(1.0e-9)


def test_agilent_msox4154a_exposes_four_channels():
    """Four-channel MSO-X captures should normalize all four analog traces."""
    obj = RigolWFM.agilent.from_file(str(_MSOX4154A))
    waveform = RigolWFM.wfm.Wfm.from_file(str(_MSOX4154A))

    assert obj.header.model_number == "MSO-X 4154A"
    assert obj.header.serial_number == "MY00000000"
    assert obj.header.points == 2_000_000
    assert [channel.enabled for channel in obj.header.ch] == [True, True, True, True]
    assert len(waveform.channels) == 4
    assert waveform.channels[0].times[0] == pytest.approx(-0.001027)
    assert waveform.channels[0].times[1] - waveform.channels[0].times[0] == pytest.approx(8.0e-10)
