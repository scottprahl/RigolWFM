"""Tests for Agilent / Keysight `AGxx` `.bin` waveform parsing."""

from __future__ import annotations

from pathlib import Path
import struct

import numpy as np
import pytest

import RigolWFM.agilent
import RigolWFM.agilent_bin
import RigolWFM.wfm

_ROOT = Path(__file__).resolve().parents[1]
_BIN_DIR = _ROOT / "tests" / "files" / "bin"
_MSOX4154A = _ROOT / "docs" / "vendors" / "wavebin-master" / "samples" / "MSOX4154A.bin"
_skip_no_msox4154a = pytest.mark.skipif(
    not _MSOX4154A.exists(),
    reason="wavebin MSOX4154A sample file is not present",
)
_WAVEFORM_HEADER = struct.Struct("<5if3d2i16s16s24s16sdI")
_DATA_HEADER = struct.Struct("<IHHI")

_AGILENT_CASES = [
    ("agilent_1", 1, 2000, -5.000631603125e-4, 5.0e-7, [True, False, False, False], [1]),
    ("agilent_2", 2, 20000, -1.0e-5, 1.0e-9, [True, False, False, False], [1]),
    ("agilent_3", 2, 4000, -1.0e-6, 5.0e-10, [True, True, False, False], [1, 2]),
    ("agilent_4", 1, 1953, -9.999999999999998e-4, 1.024e-6, [True, False, False, False], [1]),
    ("agilent_5", 1, 999999, 0.8839843868396875, 5.0e-8, [True, False, False, False], [1]),
]


def _fixture_path(stem: str) -> Path:
    """Return the path to a checked-in Agilent `.bin` fixture."""
    return _BIN_DIR / f"{stem}.bin"


def _fixed_ascii(text: str, size: int) -> bytes:
    """Return a NUL-padded ASCII field for synthetic AGxx fixtures."""
    raw = text.encode("ascii")
    return raw[:size].ljust(size, b"\x00")


def _float_payload(values: list[float]) -> bytes:
    """Encode a float32 payload."""
    return struct.pack(f"<{len(values)}f", *values)


def _u8_payload(values: list[int]) -> bytes:
    """Encode a byte payload."""
    return bytes(values)


def _build_agilent_fixture(waveforms: list[dict]) -> bytes:
    """Build a synthetic AG10 file for regression tests."""
    body = bytearray()
    for waveform in waveforms:
        buffers = waveform["buffers"]
        body.extend(
            _WAVEFORM_HEADER.pack(
                140,
                waveform.get("waveform_type", 1),
                len(buffers),
                waveform["n_pts"],
                waveform.get("count", 0),
                waveform.get("x_display_range", waveform["n_pts"] * waveform["x_increment"]),
                waveform.get("x_display_origin", waveform["x_origin"]),
                waveform["x_increment"],
                waveform["x_origin"],
                waveform.get("x_units", 2),
                waveform.get("y_units", 1),
                _fixed_ascii(waveform.get("date", ""), 16),
                _fixed_ascii(waveform.get("time", ""), 16),
                _fixed_ascii(waveform.get("frame_string", "DSO-X 1102G:CNTEST"), 24),
                _fixed_ascii(waveform.get("waveform_label", "1"), 16),
                waveform.get("time_tag", 0.0),
                waveform.get("segment_index", 0),
            )
        )
        for buffer in buffers:
            payload = buffer["payload"]
            body.extend(
                _DATA_HEADER.pack(
                    12,
                    buffer["buffer_type"],
                    buffer["bytes_per_point"],
                    len(payload),
                )
            )
            body.extend(payload)

    return b"AG10" + struct.pack("<II", 12 + len(body), len(waveforms)) + bytes(body)


def _expected_analog_waveforms(raw):
    """Return analog float32 waveform buffers keyed by their 0-based channel slot."""
    expected = {}
    for waveform in raw.waveforms:
        label = waveform.wfm_header.waveform_label.strip()
        for buffer in waveform.buffers:
            buffer_type = int(buffer.data_header.buffer_type)
            if buffer.data_header.bytes_per_point != 4 or buffer_type not in {1, 2, 3}:
                continue
            if label.isdigit():
                slot = int(label) - 1
            else:
                slot = len(expected)
            expected.setdefault(slot, np.frombuffer(buffer.data_raw, dtype="<f4"))
    return expected


@pytest.mark.parametrize(
    "stem, n_waveforms, points, x_origin, dt, _enabled, _channels",
    _AGILENT_CASES,
)
def test_agilent_bin_low_level_header_matches_fixtures(
    stem,
    n_waveforms,
    points,
    x_origin,
    dt,
    _enabled,
    _channels,
):
    """The low-level Kaitai parser should match the checked-in Agilent fixtures."""
    path = _fixture_path(stem)
    waveform = RigolWFM.agilent_bin.AgilentBin.from_file(str(path))

    assert waveform.file_header.cookie == b"AG"
    assert waveform.file_header.version == "10"
    assert waveform.file_header.version_num == 10
    assert waveform.file_header.file_size == path.stat().st_size
    assert waveform.file_header.n_waveforms == n_waveforms

    first = waveform.waveforms[0]
    assert first.wfm_header.header_size == 140
    assert first.wfm_header.n_buffers == 1
    assert first.wfm_header.n_pts == points
    assert first.wfm_header.x_origin == pytest.approx(x_origin)
    assert first.wfm_header.x_increment == pytest.approx(dt)
    assert first.buffers[0].data_header.header_size == 12
    assert first.buffers[0].data_header.bytes_per_point == 4
    assert first.buffers[0].data_header.buffer_size == points * 4


@pytest.mark.parametrize(
    "stem, n_waveforms, points, x_origin, dt, enabled, expected_channels",
    _AGILENT_CASES,
)
def test_agilent_local_fixtures_round_trip(
    stem,
    n_waveforms,
    points,
    x_origin,
    dt,
    enabled,
    expected_channels,
):
    """Repo-local Agilent fixtures should parse consistently through both APIs."""
    path = _fixture_path(stem)
    raw = RigolWFM.agilent_bin.AgilentBin.from_file(str(path))
    obj = RigolWFM.agilent.from_file(str(path))
    waveform = RigolWFM.wfm.Wfm.from_file(str(path))

    assert obj.header.model_number == "DSO-X 1102G"
    assert obj.header.serial_number == "CN00000000"
    assert obj.header.n_waveforms == n_waveforms
    assert obj.header.points == points
    assert obj.header.seconds_per_point == pytest.approx(dt)
    assert obj.header.x_origin == pytest.approx(x_origin)
    assert [channel.enabled for channel in obj.header.ch] == enabled

    expected = _expected_analog_waveforms(raw)
    for slot, values in expected.items():
        np.testing.assert_allclose(obj.header.channel_data[slot], values)

    assert waveform.parser_name == "agilent_bin"
    assert waveform.header_name == "DSO-X 1102G"
    assert waveform.serial_number == "CN00000000"
    assert [channel.channel_number for channel in waveform.channels] == expected_channels

    for channel in waveform.channels:
        assert channel.times is not None
        assert channel.volts is not None
        assert channel.times[0] == pytest.approx(x_origin)
        assert channel.times[1] - channel.times[0] == pytest.approx(dt)


def test_agilent_waveform_preserves_per_channel_time_axes(tmp_path):
    """Each normalized Agilent channel should keep its own time origin and increment."""
    path = tmp_path / "per_channel_time.bin"
    path.write_bytes(
        _build_agilent_fixture(
            [
                {
                    "waveform_label": "1",
                    "n_pts": 3,
                    "x_increment": 0.25,
                    "x_origin": 1.5,
                    "buffers": [{"buffer_type": 3, "bytes_per_point": 4, "payload": _float_payload([0.0, 1.0, 2.0])}],
                },
                {
                    "waveform_label": "2",
                    "n_pts": 3,
                    "x_increment": 0.5,
                    "x_origin": 9.5,
                    "buffers": [{"buffer_type": 3, "bytes_per_point": 4, "payload": _float_payload([3.0, 4.0, 5.0])}],
                },
            ]
        )
    )

    obj = RigolWFM.agilent.from_file(str(path))
    waveform = RigolWFM.wfm.Wfm.from_file(str(path))

    assert obj.header.x_origins[:2] == pytest.approx([1.5, 9.5])
    assert obj.header.x_increments[:2] == pytest.approx([0.25, 0.5])

    assert len(waveform.channels) == 2
    ch1, ch2 = waveform.channels
    assert ch1.times is not None
    assert ch2.times is not None
    assert ch1.times[0] == pytest.approx(1.5)
    assert ch1.times[1] - ch1.times[0] == pytest.approx(0.25)
    assert ch2.times[0] == pytest.approx(9.5)
    assert ch2.times[1] - ch2.times[0] == pytest.approx(0.5)


@_skip_no_msox4154a
def test_agilent_msox4154a_exposes_four_channels():
    """Four-channel MSO-X captures should normalize all four analog traces."""
    obj = RigolWFM.agilent.from_file(str(_MSOX4154A))
    waveform = RigolWFM.wfm.Wfm.from_file(str(_MSOX4154A))

    assert obj.header.model_number == "MSO-X 4154A"
    assert obj.header.serial_number == "MY00000000"
    assert obj.header.points == 2_000_000
    assert [channel.enabled for channel in obj.header.ch] == [True, True, True, True]
    assert len(waveform.channels) == 4
    assert waveform.channels[0].times[0] == pytest.approx(-0.000826612890625)
    assert waveform.channels[0].times[1] - waveform.channels[0].times[0] == pytest.approx(8.0e-10)


def test_agilent_low_level_parser_supports_multi_buffer_waveforms(tmp_path):
    """The Kaitai parser should expose all waveform buffers for Peak Detect files."""
    path = tmp_path / "peak_detect.bin"
    path.write_bytes(
        _build_agilent_fixture(
            [
                {
                    "waveform_label": "1",
                    "n_pts": 3,
                    "x_increment": 0.25,
                    "x_origin": 1.5,
                    "x_display_origin": 1.0,
                    "buffers": [
                        {"buffer_type": 3, "bytes_per_point": 4, "payload": _float_payload([-1.0, -0.5, -0.25])},
                        {"buffer_type": 2, "bytes_per_point": 4, "payload": _float_payload([1.0, 0.5, 0.25])},
                    ],
                }
            ]
        )
    )

    waveform = RigolWFM.agilent_bin.AgilentBin.from_file(str(path))

    assert waveform.file_header.n_waveforms == 1
    assert waveform.waveforms[0].wfm_header.n_buffers == 2
    assert [int(buffer.data_header.buffer_type) for buffer in waveform.waveforms[0].buffers] == [3, 2]
    np.testing.assert_allclose(
        np.frombuffer(waveform.waveforms[0].buffers[0].data_raw, dtype="<f4"),
        [-1.0, -0.5, -0.25],
    )
    np.testing.assert_allclose(
        np.frombuffer(waveform.waveforms[0].buffers[1].data_raw, dtype="<f4"),
        [1.0, 0.5, 0.25],
    )


def test_agilent_normalized_parser_rejects_peak_detect_multi_buffer_waveforms(tmp_path):
    """The high-level adapter should fail loudly on multi-buffer Peak Detect files."""
    path = tmp_path / "peak_detect.bin"
    path.write_bytes(
        _build_agilent_fixture(
            [
                {
                    "waveform_label": "1",
                    "n_pts": 3,
                    "x_increment": 0.25,
                    "x_origin": 1.5,
                    "buffers": [
                        {"buffer_type": 3, "bytes_per_point": 4, "payload": _float_payload([-1.0, -0.5, -0.25])},
                        {"buffer_type": 2, "bytes_per_point": 4, "payload": _float_payload([1.0, 0.5, 0.25])},
                    ],
                }
            ]
        )
    )

    with pytest.raises(ValueError, match="multi-buffer"):
        RigolWFM.agilent.from_file(str(path))


def test_agilent_low_level_parser_preserves_segment_metadata(tmp_path):
    """The Kaitai parser should expose segment indices and time tags per waveform."""
    path = tmp_path / "segmented.bin"
    path.write_bytes(
        _build_agilent_fixture(
            [
                {
                    "waveform_label": "1",
                    "n_pts": 2,
                    "x_increment": 1e-3,
                    "x_origin": -5e-4,
                    "segment_index": 1,
                    "time_tag": 0.0,
                    "buffers": [
                        {"buffer_type": 1, "bytes_per_point": 4, "payload": _float_payload([0.0, 1.0])},
                    ],
                },
                {
                    "waveform_label": "1",
                    "n_pts": 2,
                    "x_increment": 1e-3,
                    "x_origin": -5e-4,
                    "segment_index": 2,
                    "time_tag": 0.125,
                    "buffers": [
                        {"buffer_type": 1, "bytes_per_point": 4, "payload": _float_payload([2.0, 3.0])},
                    ],
                },
            ]
        )
    )

    waveform = RigolWFM.agilent_bin.AgilentBin.from_file(str(path))

    assert waveform.file_header.n_waveforms == 2
    assert [wave.wfm_header.segment_index for wave in waveform.waveforms] == [1, 2]
    assert [wave.wfm_header.time_tag for wave in waveform.waveforms] == pytest.approx([0.0, 0.125])


def test_agilent_normalized_parser_rejects_segmented_waveforms(tmp_path):
    """The high-level adapter should fail loudly instead of collapsing segments."""
    path = tmp_path / "segmented.bin"
    path.write_bytes(
        _build_agilent_fixture(
            [
                {
                    "waveform_label": "1",
                    "n_pts": 2,
                    "x_increment": 1e-3,
                    "x_origin": -5e-4,
                    "segment_index": 1,
                    "time_tag": 0.0,
                    "buffers": [
                        {"buffer_type": 1, "bytes_per_point": 4, "payload": _float_payload([0.0, 1.0])},
                    ],
                }
            ]
        )
    )

    with pytest.raises(ValueError, match="Segmented"):
        RigolWFM.agilent.from_file(str(path))
