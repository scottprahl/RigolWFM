"""Tests for Yokogawa single-file `.wfm` parsing."""

from __future__ import annotations

from pathlib import Path

import numpy as np

import RigolWFM.wfm
import RigolWFM.yokogawa


def _build_yokogawa_wfm(
    *,
    raw_samples: list[float],
    pt_off: float = 2.0,
    xin: float = 5.0e-9,
    ymu: float = 0.5,
    yof: float = -0.25,
) -> bytes:
    """Build a minimal Yokogawa ASCII-header `.wfm` file."""
    header = (
        "YOKOGAWA WFM\n"
        f"HDR NR_PT:{len(raw_samples)},PT_O:{pt_off},XIN:{xin},"
        f"YMU:{ymu},YOF:{yof},BIT:32,BYT:4,\n"
    ).encode("ascii")
    payload = np.asarray(raw_samples, dtype="<f4").tobytes()
    return header + payload


def test_yokogawa_from_file(tmp_path: Path):
    """Synthetic Yokogawa `.wfm` files should parse and scale correctly."""
    raw = [0.0, 1.0, -2.0, 4.0]
    path = tmp_path / "synthetic_yoko.wfm"
    path.write_bytes(_build_yokogawa_wfm(raw_samples=raw))

    obj = RigolWFM.yokogawa.from_file(str(path))
    expected_volts = -0.25 + 0.5 * np.asarray(raw, dtype=np.float64)
    expected_times = (np.arange(len(raw), dtype=np.float64) - 2.0) * 5.0e-9

    assert obj.header.model == "Yokogawa"
    np.testing.assert_allclose(obj.header.channel_data[0], expected_volts)

    waveform = RigolWFM.wfm.Wfm.from_file(str(path), "Yokogawa", "1")
    assert waveform.parser_name == "yokogawa_wfm"
    assert waveform.header_name == "Yokogawa"
    np.testing.assert_allclose(waveform.channels[0].volts, expected_volts)
    np.testing.assert_allclose(waveform.channels[0].times, expected_times)


def test_yokogawa_autodetect(tmp_path: Path):
    """detect_model() should recognize Yokogawa ASCII-header `.wfm` files."""
    path = tmp_path / "synthetic_yoko_auto.wfm"
    path.write_bytes(_build_yokogawa_wfm(raw_samples=[0.0, 1.0]))

    assert RigolWFM.wfm.detect_model(str(path)) == "Yokogawa"
    auto_wave = RigolWFM.wfm.Wfm.from_file(str(path))
    assert auto_wave.parser_name == "yokogawa_wfm"
