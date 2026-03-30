"""Snapshot tests for Rigol 1000Z-family `wfmconvert info` output."""

import csv
from pathlib import Path

import numpy as np
import pytest
import RigolWFM.wfm
import RigolWFM.wfm1000z

from tests.cli_helpers import assert_wfmconvert_info_snapshot

_Z_INFO_CASES = [
    "DS1202Z-E",
    "DS1074Z-C",
    "DS1054Z-A",
    "MSO1104",
    "DS1074Z-A",
    "DS1074Z-B",
]

_Z_SP3_CSV_CASES = [
    ("DS1054Z-ch1SquareCH2Uart", (1, 2)),
    ("DS1054Z-ch1SquareCH4Uart", (1, 4)),
]

_Z_SP4_CSV_CASES = [
    ("DS1054Z-A", 1),
    ("DS1054Z-A", 2),
    ("DS1054Z-A", 3),
    ("DS1054Z-B", 1),
    ("DS1054Z-B", 2),
    ("DS1054Z-B", 3),
    ("DS1054Z-B", 4),
    ("DS1054Z-C", 1),
    ("DS1054Z-C", 3),
]

_Z_WAVEFORM_CASES = [
    "DS1074Z-C",
    "DS1054Z-A",
    "MSO1104",
    "DS1074Z-A",
    "DS1074Z-B",
] + [stem for stem, _channels in _Z_SP3_CSV_CASES]


def _read_csv_channels(stem):
    """Return channel-numbered CSV traces for a checked-in Z-family fixture."""
    path = Path("tests/files/wfm") / f"{stem}.csv"
    with path.open(newline="") as handle:
        rows = list(csv.reader(handle))

    headers = rows[0]
    data_rows = rows[2:]
    channels = {}
    for index, label in enumerate(headers[1:], start=1):
        if label.startswith("CH"):
            channels[int(label[2:])] = np.array(
                [float(row[index]) for row in data_rows],
                dtype=np.float64,
            )

    return channels


def _center_crop(values, count):
    """Return the centered `count` samples from `values`."""
    extra = len(values) - count
    start = max(extra // 2, 0)
    return values[start : start + count]


def _sorted_voltage_error(actual, expected):
    """Return sorted-voltage error statistics for two same-length traces."""
    delta = np.sort(actual) - np.sort(expected)
    return {
        "mean": float(np.mean(delta)),
        "rms": float(np.sqrt(np.mean(delta**2))),
        "max": float(np.max(np.abs(delta))),
    }


@pytest.mark.parametrize("stem", _Z_INFO_CASES)
def test_wfmconvert_z_info_matches_snapshot(stem):
    """`wfmconvert Z info` should match the checked-in snapshot output."""
    assert_wfmconvert_info_snapshot("Z", stem, "z")


def test_ds1202ze_uses_header_enable_mask():
    """Two-channel DS1202Z-E files should ignore junk in unused channel slots."""
    waveform = RigolWFM.wfm.Wfm.from_file("tests/files/wfm/DS1202Z-E.wfm", "Z")
    raw = RigolWFM.wfm1000z.Wfm1000z.from_file("tests/files/wfm/DS1202Z-E.wfm")

    assert [channel.channel_number for channel in waveform.channels] == [1]
    assert raw.header.ch3_enabled is False
    assert raw.header.ch4_enabled is False
    assert raw.header.ch[2].enabled is True
    assert raw.header.ch[3].enabled is True


@pytest.mark.parametrize("stem", _Z_WAVEFORM_CASES)
def test_ds1000z_time_grid_matches_sample_period(stem):
    """Adjacent DS1000Z timestamps should match the reported sample period."""
    waveform = RigolWFM.wfm.Wfm.from_file(f"tests/files/wfm/{stem}.wfm", "Z")
    for channel in waveform.channels:
        if channel.enabled:
            assert channel.times[1] - channel.times[0] == pytest.approx(channel.seconds_per_point)


@pytest.mark.parametrize("stem", _Z_WAVEFORM_CASES)
def test_ds1000z_parser_tracks_documented_display_fields(stem):
    """The low-level Z parser should expose the display address fields."""
    path = Path("tests/files/wfm") / f"{stem}.wfm"
    waveform = RigolWFM.wfm1000z.Wfm1000z.from_file(str(path))
    data_pos = waveform.header.horizontal_offset + waveform.header.horizontal_size

    assert waveform.header.display_delay >= 0
    assert waveform.header.display_address >= 0
    assert waveform.header.display_fine >= 0
    assert waveform.header.memory_address >= 0
    assert data_pos + len(waveform.data.raw) == path.stat().st_size


@pytest.mark.parametrize("stem", _Z_WAVEFORM_CASES)
def test_ds1000z_horizontal_normalized_table_matches_header(stem):
    """The duplicated horizontal table should mirror header scale/shift values."""
    path = Path("tests/files/wfm") / f"{stem}.wfm"
    waveform = RigolWFM.wfm1000z.Wfm1000z.from_file(str(path))
    normalized_a = waveform.horizontal.normalized_a
    normalized_b = waveform.horizontal.normalized_b

    assert normalized_a.range_norm == normalized_b.range_norm
    assert normalized_a.shift_norm == normalized_b.shift_norm
    assert normalized_a.enabled_norm == normalized_b.enabled_norm

    for index, channel in enumerate(waveform.header.ch):
        normalization = 10.0 / channel.probe_value
        expected_range = channel.scale * 100000.0 * normalization
        expected_shift = channel.shift * 100000.0 * normalization

        assert normalized_a.range_norm[index] == pytest.approx(expected_range, abs=1.0)
        assert normalized_a.shift_norm[index] == pytest.approx(expected_shift, abs=1.0)
        assert normalized_a.enabled_norm[index] == int(channel.enabled)


@pytest.mark.parametrize("stem, channels", _Z_SP3_CSV_CASES)
def test_ds1000z_sp3_two_channel_levels_match_csv(stem, channels):
    """SP3 two-channel DS1000Z captures should match CSV DC levels."""
    waveform = RigolWFM.wfm.Wfm.from_file(f"tests/files/wfm/{stem}.wfm", "Z")
    actual_channels = {channel.channel_number: channel for channel in waveform.channels if channel.enabled}
    expected_channels = _read_csv_channels(stem)

    for channel_number in channels:
        actual = _center_crop(
            actual_channels[channel_number].volts,
            len(expected_channels[channel_number]),
        )
        expected = expected_channels[channel_number]
        level_error = float(np.mean(actual[:1000] - expected[:1000]))
        assert abs(level_error) < 0.06


@pytest.mark.parametrize("stem, channel_number", _Z_SP4_CSV_CASES)
def test_ds1000z_sp4_voltage_distribution_matches_csv(stem, channel_number):
    """Selected SP4 Rigol CSV fixtures should agree with the parsed voltages."""
    waveform = RigolWFM.wfm.Wfm.from_file(f"tests/files/wfm/{stem}.wfm", "Z")
    actual_channels = {channel.channel_number: channel for channel in waveform.channels if channel.enabled}
    expected_channels = _read_csv_channels(stem)

    count = min(
        len(actual_channels[channel_number].volts),
        len(expected_channels[channel_number]),
    )
    actual = _center_crop(actual_channels[channel_number].volts, count)
    expected = _center_crop(expected_channels[channel_number], count)
    stats = _sorted_voltage_error(actual, expected)

    assert abs(stats["mean"]) < 0.4
    assert stats["rms"] < 0.5
    assert stats["max"] < 0.6
