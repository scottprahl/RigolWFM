"""Tests for Tektronix ISF parsing and metadata normalization."""

from __future__ import annotations

from pathlib import Path

import numpy as np

import RigolWFM.isf
import RigolWFM.wfm


def _build_isf(
    *,
    samples: list[int],
    byt_or: str = "MSB",
    xincr: float = 2.5e-9,
    xzero: float = -5.0e-9,
    pt_off: float = 2.0,
    ymult: float = 0.02,
    yoff: float = 5.0,
    yzero: float = 0.25,
    wfid: str = "Ch1, DC coupling, 1.0V/div",
) -> bytes:
    """Build a minimal Tektronix ISF file."""
    dtype = np.dtype(">i2" if byt_or == "MSB" else "<i2")
    curve = np.asarray(samples, dtype=dtype).tobytes()

    header = (
        f':WFMP:BYT_N 2;BIT_N 16;BN_F RI;BYT_O {byt_or};'
        f'WFI "{wfid}";NR_P {len(samples)};PT_F Y;XIN {xincr};'
        f'XZE {xzero};PT_O {pt_off};YMU {ymult};YOF {yoff};'
        f'YZE {yzero};:CURV '
    ).encode("ascii")
    count = str(len(curve)).encode("ascii")
    return header + b"#" + str(len(count)).encode("ascii") + count + curve


def test_isf_generic_header_name_and_scaling(tmp_path: Path):
    """WFID should be preserved as a trace label, not reported as the scope model."""
    samples = [-10, 0, 10, 20]
    payload = _build_isf(samples=samples)
    path = tmp_path / "synthetic.isf"
    path.write_bytes(payload)

    obj = RigolWFM.isf.from_file(str(path))
    expected_volts = 0.25 + 0.02 * (np.asarray(samples, dtype=np.float64) - 5.0)

    assert obj.header.model == "Tektronix"
    assert obj.header.trace_label.startswith("Ch1")
    np.testing.assert_allclose(obj.header.channel_data[0], expected_volts)

    waveform = RigolWFM.wfm.Wfm.from_file(str(path), "ISF", "1")
    expected_times = -5.0e-9 + (np.arange(len(samples), dtype=np.float64) - 2.0) * 2.5e-9

    assert waveform.parser_name == "tek_isf"
    assert waveform.header_name == "Tektronix"
    np.testing.assert_allclose(waveform.channels[0].volts, expected_volts)
    np.testing.assert_allclose(waveform.channels[0].times, expected_times)


def test_isf_autodetect(tmp_path: Path):
    """detect_model() should still recognize ISF files after metadata cleanup."""
    path = tmp_path / "auto.isf"
    path.write_bytes(_build_isf(samples=[-1, 0, 1]))

    assert RigolWFM.wfm.detect_model(str(path)) == "ISF"
