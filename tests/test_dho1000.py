"""
Tests for Rigol DHO800/DHO1000 parsing through `RigolWFM.dho`.

Validates normalized DHO sample count, voltage range, time axis, and channel
count for both `.bin` and `.wfm` inputs.

Test files:
    wfm/DHO1074.bin   (10000 samples, 4 channels enabled, DHO1074)
    wfm/DHO1074.wfm   (10000 samples per channel, 4 channels enabled, DHO1074)

These files are checked into the repo under `wfm/`.
"""

from pathlib import Path

import numpy as np
import pytest

import RigolWFM.dho
import RigolWFM.wfm

_WFM_DIR = Path(__file__).resolve().parent.parent / "wfm"
_DHO1074_BIN = _WFM_DIR / "DHO1074.bin"
_DHO1074_WFM = _WFM_DIR / "DHO1074.wfm"

_skip_no_bin = pytest.mark.skipif(
    not _DHO1074_BIN.exists(), reason="DHO1074.bin not found in wfm/"
)
_skip_no_wfm = pytest.mark.skipif(
    not _DHO1074_WFM.exists(), reason="DHO1074.wfm not found in wfm/"
)
_skip_no_pair = pytest.mark.skipif(
    not (_DHO1074_BIN.exists() and _DHO1074_WFM.exists()),
    reason="DHO1074.bin/.wfm pair not found in wfm/",
)


# ---------------------------------------------------------------------------
# DHO .bin parser tests
# ---------------------------------------------------------------------------

@_skip_no_bin
def test_dho1074_bin_sample_count():
    """DHO1074.bin should have exactly 10000 samples."""
    obj = RigolWFM.dho.dho_from_file(str(_DHO1074_BIN))
    assert obj.header.n_pts == 10000


@_skip_no_bin
def test_dho1074_bin_cookie():
    """DHO1074.bin should have the 'RG' cookie."""
    obj = RigolWFM.dho.dho_from_file(str(_DHO1074_BIN))
    assert obj.header.cookie == "RG"


@_skip_no_bin
def test_dho1074_bin_all_channels_enabled():
    """DHO1074.bin should have all 4 channels enabled."""
    obj = RigolWFM.dho.dho_from_file(str(_DHO1074_BIN))
    enabled = [ch for ch in obj.header.ch if ch.enabled]
    assert len(enabled) == 4


@_skip_no_bin
def test_dho1074_bin_channel_count():
    """DHO1074.bin should have exactly 4 channel headers."""
    obj = RigolWFM.dho.dho_from_file(str(_DHO1074_BIN))
    assert len(obj.header.ch) == 4
    assert obj.header.n_waveforms == 4


@_skip_no_bin
def test_dho1074_bin_all_channel_data():
    """DHO1074.bin should have voltage data for all 4 channels."""
    obj = RigolWFM.dho.dho_from_file(str(_DHO1074_BIN))
    assert len(obj.header.channel_data) == 4
    for i, data in enumerate(obj.header.channel_data):
        assert len(data) == 10000, f"CH{i + 1} should have 10000 samples"


@_skip_no_bin
def test_dho1074_bin_time_axis():
    """DHO1074.bin should expose normalized negative pre-trigger time."""
    obj = RigolWFM.dho.dho_from_file(str(_DHO1074_BIN))
    assert obj.header.x_origin < 0.0, "x_origin should be negative (pre-trigger)"
    assert 1e-12 < obj.header.x_increment < 1.0


@_skip_no_bin
def test_dho1074_bin_str_parser_name():
    """str(obj) should contain 'dho1000' for parser name extraction."""
    obj = RigolWFM.dho.dho_from_file(str(_DHO1074_BIN))
    assert "dho1000" in str(obj)


# ---------------------------------------------------------------------------
# DHO .wfm parser tests
# ---------------------------------------------------------------------------

@_skip_no_wfm
def test_dho1074_wfm_parse():
    """DHO1074.wfm should parse without errors."""
    obj = RigolWFM.dho.dho_from_file(str(_DHO1074_WFM))
    assert obj is not None
    assert obj.header is not None


@_skip_no_wfm
def test_dho1074_wfm_sample_count():
    """DHO1074.wfm should have 10000 samples."""
    obj = RigolWFM.dho.dho_from_file(str(_DHO1074_WFM))
    assert obj.header.n_pts == 10000


@_skip_no_wfm
def test_dho1074_wfm_channel_data():
    """DHO1074.wfm should expose calibrated voltage data for all four channels."""
    obj = RigolWFM.dho.dho_from_file(str(_DHO1074_WFM))
    assert len(obj.header.channel_data) == 4
    for i, volts in enumerate(obj.header.channel_data):
        assert volts is not None, f"CH{i + 1} voltage data should not be None"
        assert len(volts) == 10000


@_skip_no_wfm
def test_dho1074_wfm_raw_data():
    """DHO1074.wfm raw_data should contain four uint16 arrays of 10000 samples."""
    obj = RigolWFM.dho.dho_from_file(str(_DHO1074_WFM))
    assert obj.header.raw_data is not None
    for i, raw in enumerate(obj.header.raw_data):
        assert raw is not None, f"CH{i + 1} raw data should not be None"
        assert raw.dtype == np.dtype("<u2")
        assert len(raw) == 10000


@_skip_no_wfm
def test_dho1074_wfm_voltage_range():
    """DHO1074.wfm should expose finite, nontrivial voltage traces for all channels."""
    obj = RigolWFM.dho.dho_from_file(str(_DHO1074_WFM))
    ch1, ch2, ch3, ch4 = obj.header.channel_data
    for i, volts in enumerate((ch1, ch2, ch3, ch4), start=1):
        assert np.isfinite(volts).all(), f"CH{i} should not contain NaNs"
    assert float(ch1.max() - ch1.min()) > 40.0
    assert float(ch2.max() - ch2.min()) > 40.0
    assert float(ch3.max() - ch3.min()) > 2.0
    assert float(ch4.max() - ch4.min()) > 20.0


@_skip_no_wfm
def test_dho1074_wfm_channel_offsets():
    """DHO1074.wfm channel headers should preserve the displayed vertical centers."""
    obj = RigolWFM.dho.dho_from_file(str(_DHO1074_WFM))
    expected_offsets = [154.0, 19.2, -3.76, -71.2]
    for i, (ch, expected) in enumerate(zip(obj.header.ch, expected_offsets), start=1):
        assert ch.enabled, f"CH{i} should be enabled"
        assert ch.volt_offset == pytest.approx(expected, abs=0.01)


@_skip_no_wfm
def test_dho1074_wfm_time_axis():
    """DHO1074.wfm time parameters should match the 200 kSa/s capture."""
    obj = RigolWFM.dho.dho_from_file(str(_DHO1074_WFM))
    assert obj.header.n_pts == 10000
    assert obj.header.x_increment == pytest.approx(5e-6)
    assert obj.header.x_origin == pytest.approx(-0.025)


@_skip_no_wfm
def test_dho1074_wfm_channel_headers():
    """DHO1074.wfm should have 4 enabled channel headers labeled CH1-CH4."""
    obj = RigolWFM.dho.dho_from_file(str(_DHO1074_WFM))
    assert len(obj.header.ch) == 4
    for i, ch in enumerate(obj.header.ch, start=1):
        assert ch.enabled, f"CH{i} should be enabled"
        assert ch.name == f"CH{i}"


@_skip_no_wfm
def test_dho1074_wfm_str_parser_name():
    """str(obj) should contain 'dho1000' for parser name extraction."""
    obj = RigolWFM.dho.dho_from_file(str(_DHO1074_WFM))
    assert "dho1000" in str(obj)


# ---------------------------------------------------------------------------
# Cross-validation: BIN vs WFM correlation
# ---------------------------------------------------------------------------

@_skip_no_pair
def test_wfm_bin_rms_error():
    """Each DHO1074 channel should match BIN to within 10 mV RMS."""
    wfm_obj = RigolWFM.dho.dho_from_file(str(_DHO1074_WFM))
    bin_obj = RigolWFM.dho.dho_from_file(str(_DHO1074_BIN))
    for i, (wfm_v, bin_v) in enumerate(
        zip(wfm_obj.header.channel_data, bin_obj.header.channel_data), start=1
    ):
        n = min(len(wfm_v), len(bin_v))
        rms = float(np.sqrt(np.mean((wfm_v[:n].astype(np.float64) - bin_v[:n].astype(np.float64)) ** 2)))
        assert rms < 0.01, f"CH{i} RMS error {rms:.6f} V exceeds 10 mV"


@_skip_no_pair
def test_wfm_bin_correlation():
    """Each DHO1074 channel should correlate with BIN at r > 0.999999."""
    wfm_obj = RigolWFM.dho.dho_from_file(str(_DHO1074_WFM))
    bin_obj = RigolWFM.dho.dho_from_file(str(_DHO1074_BIN))
    for i, (wfm_v, bin_v) in enumerate(
        zip(wfm_obj.header.channel_data, bin_obj.header.channel_data), start=1
    ):
        n = min(len(wfm_v), len(bin_v))
        corr = float(np.corrcoef(wfm_v[:n].astype(np.float64), bin_v[:n].astype(np.float64))[0, 1])
        assert corr > 0.999999, f"CH{i} correlation {corr:.9f} is too low"


@_skip_no_pair
def test_wfm_bin_max_error():
    """Each DHO1074 channel should stay within 10 mV sample-wise error."""
    wfm_obj = RigolWFM.dho.dho_from_file(str(_DHO1074_WFM))
    bin_obj = RigolWFM.dho.dho_from_file(str(_DHO1074_BIN))
    for i, (wfm_v, bin_v) in enumerate(
        zip(wfm_obj.header.channel_data, bin_obj.header.channel_data), start=1
    ):
        n = min(len(wfm_v), len(bin_v))
        max_err = float(np.max(np.abs(wfm_v[:n].astype(np.float64) - bin_v[:n].astype(np.float64))))
        assert max_err < 0.01, f"CH{i} max error {max_err:.6f} V exceeds 10 mV"


# ---------------------------------------------------------------------------
# Integration tests: Wfm.from_file() round-trip
# ---------------------------------------------------------------------------

@_skip_no_bin
def test_wfm_from_file_bin():
    """Wfm.from_file() should return all enabled channels for DHO BIN input."""
    wfm = RigolWFM.wfm.Wfm.from_file(str(_DHO1074_BIN), "DHO", "1")
    assert len(wfm.channels) == 4
    ch = wfm.channels[0]
    assert ch.volts is not None
    assert ch.times is not None
    assert len(ch.volts) == len(ch.times)


@_skip_no_bin
def test_channel_times_start_negative():
    """Channel times should start at a negative value (pre-trigger)."""
    wfm = RigolWFM.wfm.Wfm.from_file(str(_DHO1074_BIN), "DHO", "1")
    assert wfm.channels[0].times[0] < 0.0


@_skip_no_bin
def test_channel_times_monotonic():
    """Channel times should be strictly monotonically increasing."""
    wfm = RigolWFM.wfm.Wfm.from_file(str(_DHO1074_BIN), "DHO", "1")
    assert np.all(np.diff(wfm.channels[0].times) > 0)


@_skip_no_bin
def test_wfm_from_file_bin_multichannel():
    """Wfm.from_file() with channel '1234' should return all 4 channels."""
    wfm = RigolWFM.wfm.Wfm.from_file(str(_DHO1074_BIN), "DHO", "1234")
    assert len(wfm.channels) == 4
    for ch in wfm.channels:
        assert ch.volts is not None
        assert ch.times is not None


@_skip_no_wfm
def test_wfm_from_file_wfm_format():
    """Wfm.from_file() with selected='1' should expose only CH1 data."""
    wfm = RigolWFM.wfm.Wfm.from_file(str(_DHO1074_WFM), "DHO", "1")
    assert len(wfm.channels) == 4
    ch = wfm.channels[0]
    assert ch.volts is not None
    assert ch.times is not None
    assert len(ch.volts) == 10000
    for ch in wfm.channels[1:]:
        assert ch.volts is None
        assert ch.times is None


@_skip_no_pair
def test_wfm_from_file_dho1000_header_name():
    """DHO1074 .wfm/.bin should expose the DHO1000 family label."""
    assert RigolWFM.wfm.Wfm.from_file(str(_DHO1074_WFM), "DHO", "1").header_name == "DHO1000"
    assert RigolWFM.wfm.Wfm.from_file(str(_DHO1074_BIN), "DHO", "1").header_name == "DHO1000 (BIN)"
