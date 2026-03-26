"""
Tests for Rigol DHO800 parsing through `RigolWFM.wfm`.

Validates that the normalized DHO path correctly handles DHO800 `.bin` and `.wfm` files,
including multi-channel captures and WFM vs BIN voltage correlation.

Test files (in wfm/ directory, captured from a DHO824 oscilloscope):
    wfm/DHO824-ch1.bin    wfm/DHO824-ch1.wfm    - CH1 only
    wfm/DHO824-ch12.bin   wfm/DHO824-ch12.wfm   - CH1 + CH2
    wfm/DHO824-ch1234.bin wfm/DHO824-ch1234.wfm - CH1-CH4

DHO800 WFM format differences vs DHO1000 (reverse-engineered):
    - CH calibration block type: 9 (DHO1000) → 5 (DHO800)
    - Scale divisor: 750_000_000_000 → 7_500_000_000_000
    - v_center: from type=6 block / 1e8 → from type=5 block bytes[38:42], negated, /1e9
    - Data section u64: n_pts+64 (DHO1000) → n_pts_total (DHO800)
    - Multi-channel: samples interleaved as [CH1, CH2, ..., CHn, CH1, ...]
"""

from pathlib import Path

import numpy as np
import pytest

import RigolWFM.dho
import RigolWFM.wfm

_WFM_DIR = Path(__file__).resolve().parent.parent / "wfm"

_CH1_BIN    = _WFM_DIR / "DHO824-ch1.bin"
_CH1_WFM    = _WFM_DIR / "DHO824-ch1.wfm"
_CH12_BIN   = _WFM_DIR / "DHO824-ch12.bin"
_CH12_WFM   = _WFM_DIR / "DHO824-ch12.wfm"
_CH1234_BIN = _WFM_DIR / "DHO824-ch1234.bin"
_CH1234_WFM = _WFM_DIR / "DHO824-ch1234.wfm"

_skip_no_ch1    = pytest.mark.skipif(not (_CH1_BIN.exists() and _CH1_WFM.exists()),
                                     reason="DHO824-ch1 files not found in wfm/")
_skip_no_ch12   = pytest.mark.skipif(not (_CH12_BIN.exists() and _CH12_WFM.exists()),
                                     reason="DHO824-ch12 files not found in wfm/")
_skip_no_ch1234 = pytest.mark.skipif(not (_CH1234_BIN.exists() and _CH1234_WFM.exists()),
                                     reason="DHO824-ch1234 files not found in wfm/")

_CORRELATION_THRESHOLD = 0.99
_RMS_THRESHOLD_MV = 0.1


def _check_wfm_bin_correlation(wfm_path, bin_path, n_ch):
    """Assert that matching WFM and BIN channel voltages closely agree."""
    wfm_obj = RigolWFM.dho.dho_from_file(str(wfm_path))
    bin_obj = RigolWFM.dho.dho_from_file(str(bin_path))
    for i in range(n_ch):
        v_wfm = wfm_obj.header.channel_data[i]
        v_bin = bin_obj.header.channel_data[i]
        assert v_wfm is not None, f"WFM CH{i + 1} data is None"
        assert v_bin is not None, f"BIN CH{i + 1} data is None"
        n = min(len(v_wfm), len(v_bin))
        vw = v_wfm[:n].astype(np.float64)
        vb = v_bin[:n].astype(np.float64)
        corr = float(np.corrcoef(vw, vb)[0, 1])
        rms_mv = float(np.sqrt(np.mean((vw - vb) ** 2))) * 1000
        assert corr > _CORRELATION_THRESHOLD, \
            f"CH{i + 1}: correlation {corr:.6f} < {_CORRELATION_THRESHOLD}"
        assert rms_mv < _RMS_THRESHOLD_MV, \
            f"CH{i + 1}: RMS {rms_mv:.4f} mV exceeds {_RMS_THRESHOLD_MV} mV"


def _check_wfm_bin_time_axis(wfm_path, bin_path):
    """Assert that matching WFM and BIN files reconstruct the same time axis."""
    wfm_header = RigolWFM.dho.dho_from_file(str(wfm_path)).header
    bin_header = RigolWFM.dho.dho_from_file(str(bin_path)).header

    assert wfm_header.n_pts == bin_header.n_pts
    assert wfm_header.x_increment == pytest.approx(bin_header.x_increment, rel=1e-6, abs=1e-15)
    assert wfm_header.x_origin == pytest.approx(bin_header.x_origin, rel=1e-6, abs=1e-15)


# ---------------------------------------------------------------------------
# DHO800 .bin parser tests
# ---------------------------------------------------------------------------

@_skip_no_ch1
def test_ch1_bin_cookie():
    """DHO800 .bin should have the 'RG' cookie."""
    obj = RigolWFM.dho.dho_from_file(str(_CH1_BIN))
    assert obj.header.cookie == "RG"


@_skip_no_ch1
def test_ch1_bin_sample_count():
    """DHO824-ch1.bin should have 10000 samples."""
    obj = RigolWFM.dho.dho_from_file(str(_CH1_BIN))
    assert obj.header.n_pts == 10000


@_skip_no_ch1
def test_ch1_bin_channel_data():
    """DHO824-ch1.bin CH1 should have 10000 float32 samples."""
    obj = RigolWFM.dho.dho_from_file(str(_CH1_BIN))
    data = obj.header.channel_data[0]
    assert data is not None
    assert len(data) == 10000
    assert data.dtype == np.float32


@_skip_no_ch1
def test_ch1_bin_voltage_range():
    """DHO824-ch1.bin voltages should be in the ±10 V range."""
    obj = RigolWFM.dho.dho_from_file(str(_CH1_BIN))
    v = obj.header.channel_data[0]
    assert float(v.max()) > -10.0
    assert float(v.max()) < 10.0


@_skip_no_ch1234
def test_ch1234_bin_all_channels():
    """DHO824-ch1234.bin should have 4 enabled channels with 10000 samples each."""
    obj = RigolWFM.dho.dho_from_file(str(_CH1234_BIN))
    assert obj.header.n_waveforms == 4
    for i in range(4):
        data = obj.header.channel_data[i]
        assert data is not None, f"CH{i + 1} data should not be None"
        assert len(data) == 10000


# ---------------------------------------------------------------------------
# DHO800 .wfm parser tests
# ---------------------------------------------------------------------------

@_skip_no_ch1
def test_ch1_wfm_parse():
    """DHO824-ch1.wfm should parse without errors."""
    obj = RigolWFM.dho.dho_from_file(str(_CH1_WFM))
    assert obj is not None
    assert obj.header is not None


@_skip_no_ch1
def test_ch1_wfm_sample_count():
    """DHO824-ch1.wfm should have 10000 samples per channel."""
    obj = RigolWFM.dho.dho_from_file(str(_CH1_WFM))
    assert obj.header.n_pts == 10000


@_skip_no_ch1
def test_ch1_wfm_channel_data_structure():
    """DHO824-ch1.wfm: channel_data is a 4-slot list; slot 0 has data."""
    obj = RigolWFM.dho.dho_from_file(str(_CH1_WFM))
    assert len(obj.header.channel_data) == 4
    assert obj.header.channel_data[0] is not None
    assert len(obj.header.channel_data[0]) == 10000


@_skip_no_ch1
def test_ch1_wfm_channel_headers():
    """DHO824-ch1.wfm should have 4 headers: 1 enabled, 3 disabled."""
    obj = RigolWFM.dho.dho_from_file(str(_CH1_WFM))
    assert len(obj.header.ch) == 4
    assert obj.header.ch[0].enabled
    for i in range(1, 4):
        assert not obj.header.ch[i].enabled


@_skip_no_ch1
def test_ch1_wfm_time_axis():
    """DHO824-ch1.wfm time parameters should be physically plausible."""
    obj = RigolWFM.dho.dho_from_file(str(_CH1_WFM))
    assert 1e-12 < obj.header.x_increment < 1.0


@_skip_no_ch1
def test_ch1_wfm_raw_data():
    """DHO824-ch1.wfm raw_data[0] should be uint16 with 10000 samples."""
    obj = RigolWFM.dho.dho_from_file(str(_CH1_WFM))
    raw = obj.header.raw_data[0]
    assert raw is not None
    assert raw.dtype == np.dtype("<u2")
    assert len(raw) == 10000


@_skip_no_ch12
def test_ch12_wfm_two_channels():
    """DHO824-ch12.wfm should have 2 enabled channels."""
    obj = RigolWFM.dho.dho_from_file(str(_CH12_WFM))
    assert obj.header.n_pts == 10000
    assert obj.header.channel_data[0] is not None
    assert obj.header.channel_data[1] is not None
    enabled = [ch for ch in obj.header.ch if ch.enabled]
    assert len(enabled) == 2


@_skip_no_ch1234
def test_ch1234_wfm_four_channels():
    """DHO824-ch1234.wfm should have 4 enabled channels."""
    obj = RigolWFM.dho.dho_from_file(str(_CH1234_WFM))
    assert obj.header.n_pts == 10000
    for i in range(4):
        assert obj.header.channel_data[i] is not None, f"CH{i + 1} data missing"
    enabled = [ch for ch in obj.header.ch if ch.enabled]
    assert len(enabled) == 4


@_skip_no_ch1
def test_ch1_wfm_str_parser_name():
    """str(obj) should contain 'dho1000' for parser name extraction."""
    obj = RigolWFM.dho.dho_from_file(str(_CH1_WFM))
    assert "dho1000" in str(obj)


# ---------------------------------------------------------------------------
# Cross-validation: WFM vs BIN voltage correlation
# ---------------------------------------------------------------------------

@_skip_no_ch1
def test_ch1_wfm_bin_correlation():
    """CH1 WFM vs BIN: correlation > 0.99, RMS < 0.1 mV."""
    _check_wfm_bin_correlation(_CH1_WFM, _CH1_BIN, 1)


@_skip_no_ch1
def test_ch1_wfm_bin_time_axis_matches():
    """CH1 WFM vs BIN should reconstruct the same sample times."""
    _check_wfm_bin_time_axis(_CH1_WFM, _CH1_BIN)


@_skip_no_ch12
def test_ch12_wfm_bin_correlation():
    """CH1+CH2 WFM vs BIN: correlation > 0.99, RMS < 0.1 mV each."""
    _check_wfm_bin_correlation(_CH12_WFM, _CH12_BIN, 2)


@_skip_no_ch12
def test_ch12_wfm_bin_time_axis_matches():
    """CH1+CH2 WFM vs BIN should reconstruct the same sample times."""
    _check_wfm_bin_time_axis(_CH12_WFM, _CH12_BIN)


@_skip_no_ch1234
def test_ch1234_wfm_bin_correlation():
    """CH1-CH4 WFM vs BIN: correlation > 0.99, RMS < 0.1 mV each."""
    _check_wfm_bin_correlation(_CH1234_WFM, _CH1234_BIN, 4)


@_skip_no_ch1234
def test_ch1234_wfm_bin_time_axis_matches():
    """CH1-CH4 WFM vs BIN should reconstruct the same sample times."""
    _check_wfm_bin_time_axis(_CH1234_WFM, _CH1234_BIN)


# ---------------------------------------------------------------------------
# Integration tests: Wfm.from_file() round-trip
# ---------------------------------------------------------------------------

@_skip_no_ch1
def test_bin_ch1_times_and_volts():
    """Wfm.from_file() on DHO824-ch1.bin returns valid times and volts."""
    w = RigolWFM.wfm.Wfm.from_file(str(_CH1_BIN), "DHO", "1")
    ch = w.channels[0]
    assert ch.volts is not None
    assert ch.times is not None
    assert len(ch.volts) == len(ch.times)


@_skip_no_ch1
def test_bin_ch1_times_start_negative():
    """DHO824-ch1.bin: first sample time should be negative (pre-trigger)."""
    w = RigolWFM.wfm.Wfm.from_file(str(_CH1_BIN), "DHO", "1")
    assert w.channels[0].times[0] < 0.0


@_skip_no_ch1234
def test_bin_ch1234_all_channels():
    """Wfm.from_file() with '1234' returns 4 channels with volts/times."""
    w = RigolWFM.wfm.Wfm.from_file(str(_CH1234_BIN), "DHO", "1234")
    assert len(w.channels) == 4
    for ch in w.channels:
        assert ch.volts is not None
        assert ch.times is not None


@_skip_no_ch1
def test_wfm_ch1_times_and_volts():
    """Wfm.from_file() on DHO824-ch1.wfm returns valid times and volts."""
    w = RigolWFM.wfm.Wfm.from_file(str(_CH1_WFM), "DHO", "1")
    ch = w.channels[0]
    assert ch.volts is not None
    assert ch.times is not None
    assert len(ch.volts) > 0


@_skip_no_ch12
def test_wfm_ch12_two_channels():
    """Wfm.from_file() on DHO824-ch12.wfm with '12' returns 2 channels."""
    w = RigolWFM.wfm.Wfm.from_file(str(_CH12_WFM), "DHO", "12")
    assert len(w.channels) == 2
    for ch in w.channels:
        assert ch.volts is not None


@_skip_no_ch1234
def test_wfm_ch1234_four_channels():
    """Wfm.from_file() on DHO824-ch1234.wfm with '1234' returns 4 channels."""
    w = RigolWFM.wfm.Wfm.from_file(str(_CH1234_WFM), "DHO", "1234")
    assert len(w.channels) == 4
    for ch in w.channels:
        assert ch.volts is not None
