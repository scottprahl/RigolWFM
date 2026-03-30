"""Tests for Rohde & Schwarz waveform parsing."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest

import RigolWFM.rohde_schwarz
import RigolWFM.rohde_schwarz_rtp_wfm
import RigolWFM.wfm

_ROOT = Path(__file__).resolve().parents[1]
_RTP_DIR = _ROOT / "tests" / "files" / "rs"


def _rtp_path(name: str) -> Path:
    """Return the absolute path to a checked-in R&S RTP fixture."""
    return _RTP_DIR / name


def _load_waveform_csv(path: Path) -> np.ndarray:
    """Load a vendor waveform CSV into a consistently 2-D float array."""
    data = np.loadtxt(path, delimiter=",", dtype=np.float64)
    if data.ndim == 1:
        data = data[:, np.newaxis]
    return data


def test_rohde_schwarz_rtp_low_level_header():
    """The low-level RTP payload parser should expose the 8-byte file header."""
    path = _rtp_path("rs_rtp_01.Wfm.bin")

    raw = RigolWFM.rohde_schwarz_rtp_wfm.RohdeSchwarzRtpWfm.from_file(str(path))

    assert raw.format_code == RigolWFM.rohde_schwarz_rtp_wfm.RohdeSchwarzRtpWfm.FormatCodeEnum.float32
    assert raw.record_length == 4070
    assert raw.payload_size == path.stat().st_size - 8


@pytest.mark.parametrize(
    "metadata_name, csv_name, expected_channels, has_time_column",
    [
        ("rs_rtp_01.bin", "rs_rtp_01.Wfm.csv", [1], False),
        ("rs_rtp_02.bin", "rs_rtp_02.Wfm.csv", [1, 2], False),
        ("rs_rtp_03.bin", "rs_rtp_01.Wfm.csv", [1], False),
        ("rs_rtp_04.bin", "rs_rtp_04.Wfm.csv", [1], True),
        ("rs_rtp_05.bin", "rs_rtp_05.Wfm.csv", [1, 2], True),
    ],
)
def test_rohde_schwarz_normalized_parser_matches_vendor_csv(
    metadata_name: str,
    csv_name: str,
    expected_channels: list[int],
    has_time_column: bool,
):
    """Normalized R&S RTP parsing should agree with the checked-in vendor CSVs."""
    metadata_path = _rtp_path(metadata_name)
    csv_path = _rtp_path(csv_name)

    obj = RigolWFM.rohde_schwarz.from_file(str(metadata_path))
    csv = _load_waveform_csv(csv_path)

    enabled = [idx + 1 for idx, ch in enumerate(obj.header.ch) if ch.enabled]
    assert enabled == expected_channels
    assert obj.header.n_pts == csv.shape[0]

    if has_time_column:
        times = obj.header.x_origin + np.arange(obj.header.n_pts, dtype=np.float64) * obj.header.x_increment
        np.testing.assert_allclose(times, csv[:, 0], rtol=0.0, atol=1e-18)
        csv_channels = csv[:, 1:]
    else:
        csv_channels = csv

    for csv_idx, channel_number in enumerate(expected_channels):
        channel_data = obj.header.channel_data[channel_number - 1]
        assert channel_data is not None
        np.testing.assert_allclose(channel_data, csv_channels[:, csv_idx], rtol=0.0, atol=5e-6)


def test_rohde_schwarz_autodetect_and_wfm_from_file():
    """`detect_model()` and `Wfm.from_file()` should route R&S RTP `.bin` files."""
    path = _rtp_path("rs_rtp_01.bin")

    assert RigolWFM.wfm.detect_model(str(path)) == "RohdeSchwarz"

    waveform = RigolWFM.wfm.Wfm.from_file(str(path))
    assert waveform.parser_name == "rohde_schwarz_bin"
    assert waveform.header_name == "Rohde & Schwarz"
    assert [channel.channel_number for channel in waveform.channels if channel.enabled] == [1]
    assert waveform.channels[0].times is not None
    assert waveform.channels[0].times[0] == pytest.approx(-0.0025)


def test_rohde_schwarz_normalized_parser_rejects_multi_acquisition_history():
    """The normalized parser should fail loudly on history / segmented captures."""
    path = _rtp_path("rs_rtp_history_01.bin")

    with pytest.raises(ValueError, match="multi-acquisition / history"):
        RigolWFM.rohde_schwarz.from_file(str(path))
