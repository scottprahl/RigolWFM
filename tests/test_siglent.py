"""Tests for Siglent waveform binary parsing."""

import struct

import numpy as np
import pytest

import RigolWFM.siglent
import RigolWFM.wfm

_ANALOG_8 = bytes([128, 153, 103, 128])
_ANALOG_8_V4 = bytes([128, 158, 98, 128])
_ANALOG_16_LE = struct.pack("<4H", 32768, 32798, 32738, 32768)


def _put(buf: bytearray, offset: int, data: bytes) -> None:
    buf[offset : offset + len(data)] = data


def _ascii(text: str, size: int) -> bytes:
    return text.encode("ascii")[:size].ljust(size, b"\x00")


def _scaled16(value: float, magnitude: int, unit: int) -> bytes:
    return struct.pack("<dII", value, magnitude, unit)


def _scaled40(value: float, magnitude: int, basic_unit: int) -> bytes:
    return struct.pack("<dI7I", value, magnitude, basic_unit, 1, 1, 0, 1, 0, 1)


def _scaled16x4(value: float, magnitude: int, unit: int) -> bytes:
    return b"".join(_scaled16(value, magnitude, unit) for _ in range(4))


def _scaled40x4(value: float, magnitude: int, basic_unit: int) -> bytes:
    return b"".join(_scaled40(value, magnitude, basic_unit) for _ in range(4))


def _build_siglent_old_platform() -> bytes:
    buf = bytearray(0x1470 + len(_ANALOG_8))
    _put(buf, 0xBC, struct.pack("<4f", 1000.0, 1000.0, 1000.0, 1000.0))
    _put(buf, 0xDC, struct.pack("<4i", 220, 220, 220, 220))
    _put(buf, 0x100, struct.pack("<4i", 1, 0, 0, 0))
    _put(buf, 0x248, struct.pack("<i", 9))
    _put(buf, 0x1470, _ANALOG_8)
    return bytes(buf)


def _build_siglent_v0_1() -> bytes:
    buf = bytearray(0x8A60 + len(_ANALOG_8))
    _put(buf, 0x44, struct.pack("<i", 1))
    _put(buf, 0xC0, struct.pack("<i", 0))
    _put(buf, 0x13C, struct.pack("<i", 0))
    _put(buf, 0x1B8, struct.pack("<i", 0))
    _put(buf, 0x90, _scaled16(1.0, 8, 0))
    _put(buf, 0x10C, _scaled16(1.0, 8, 0))
    _put(buf, 0x188, _scaled16(1.0, 8, 0))
    _put(buf, 0x204, _scaled16(1.0, 8, 0))
    _put(buf, 0xA0, _scaled16(0.0, 8, 0))
    _put(buf, 0x11C, _scaled16(0.0, 8, 0))
    _put(buf, 0x198, _scaled16(0.0, 8, 0))
    _put(buf, 0x214, _scaled16(0.0, 8, 0))
    _put(buf, 0xA84, _scaled16(1.0, 6, 14))
    _put(buf, 0xA94, _scaled16(0.0, 8, 14))
    _put(buf, 0xAA4, struct.pack("<I", 4))
    _put(buf, 0xAA8, _scaled16(1.0, 10, 15))
    _put(buf, 0x8A60, _ANALOG_8)
    return bytes(buf)


def _build_siglent_v0_2() -> bytes:
    buf = bytearray(0x932C + len(_ANALOG_8))
    _put(buf, 0x44, struct.pack("<i", 1))
    _put(buf, 0xE8, struct.pack("<i", 0))
    _put(buf, 0x18C, struct.pack("<i", 0))
    _put(buf, 0x230, struct.pack("<i", 0))
    _put(buf, 0xB4, _scaled16(1.0, 8, 0))
    _put(buf, 0x158, _scaled16(1.0, 8, 0))
    _put(buf, 0x1FC, _scaled16(1.0, 8, 0))
    _put(buf, 0x2A0, _scaled16(1.0, 8, 0))
    _put(buf, 0xC4, _scaled16(0.0, 8, 0))
    _put(buf, 0x168, _scaled16(0.0, 8, 0))
    _put(buf, 0x20C, _scaled16(0.0, 8, 0))
    _put(buf, 0x2B0, _scaled16(0.0, 8, 0))
    _put(buf, 0xDB8, _scaled16(1.0, 6, 14))
    _put(buf, 0xDC8, _scaled16(0.0, 8, 14))
    _put(buf, 0xDD8, struct.pack("<I", 4))
    _put(buf, 0xDDC, _scaled16(1.0, 10, 15))
    _put(buf, 0x932C, _ANALOG_8)
    return bytes(buf)


def _build_siglent_v1() -> bytes:
    buf = bytearray(0x800 + len(_ANALOG_8))
    _put(buf, 0x00, struct.pack("<4i", 1, 0, 0, 0))
    _put(buf, 0x10, _scaled16x4(1.0, 8, 0))
    _put(buf, 0x50, _scaled16x4(0.0, 8, 0))
    _put(buf, 0xD4, _scaled16(1.0, 6, 14))
    _put(buf, 0xE4, _scaled16(0.0, 8, 14))
    _put(buf, 0xF4, struct.pack("<I", 4))
    _put(buf, 0xF8, _scaled16(1.0, 10, 15))
    _put(buf, 0x800, _ANALOG_8)
    return bytes(buf)


def _build_siglent_v2() -> bytes:
    buf = bytearray(0x800 + len(_ANALOG_8))
    _put(buf, 0x00, struct.pack("<I", 2))
    _put(buf, 0x04, struct.pack("<4i", 1, 0, 0, 0))
    _put(buf, 0x14, _scaled40x4(1.0, 8, 0))
    _put(buf, 0xB4, _scaled40x4(0.0, 8, 0))
    _put(buf, 0x198, _scaled40(1.0, 6, 0))
    _put(buf, 0x1C0, _scaled40(0.0, 8, 0))
    _put(buf, 0x1E8, struct.pack("<I", 4))
    _put(buf, 0x1EC, _scaled40(1.0, 10, 7))
    _put(buf, 0x240, struct.pack("<4d", 1.0, 1.0, 1.0, 1.0))
    _put(buf, 0x260, b"\x00")
    _put(buf, 0x800, _ANALOG_8)
    return bytes(buf)


def _build_siglent_v3() -> bytes:
    buf = bytearray(0x800 + len(_ANALOG_16_LE))
    _put(buf, 0x00, struct.pack("<I", 3))
    _put(buf, 0x04, struct.pack("<4i", 1, 0, 0, 0))
    _put(buf, 0x14, _scaled40x4(1.0, 8, 0))
    _put(buf, 0xB4, _scaled40x4(0.0, 8, 0))
    _put(buf, 0x198, _scaled40(1.0, 6, 0))
    _put(buf, 0x1C0, _scaled40(2.0, 6, 0))
    _put(buf, 0x1E8, struct.pack("<I", 4))
    _put(buf, 0x1EC, _scaled40(1.0, 10, 7))
    _put(buf, 0x240, struct.pack("<4d", 1.0, 1.0, 1.0, 1.0))
    _put(buf, 0x260, b"\x01")
    _put(buf, 0x261, b"\x00")
    _put(buf, 0x268, struct.pack("<i", 10))
    _put(buf, 0x26C, struct.pack("<4i", 30, 30, 30, 30))
    _put(buf, 0x800, _ANALOG_16_LE)
    return bytes(buf)


def _build_siglent_v4() -> bytes:
    buf = bytearray(0x1000 + len(_ANALOG_8_V4))
    _put(buf, 0x00, struct.pack("<I", 4))
    _put(buf, 0x04, struct.pack("<I", 0x1000))
    _put(buf, 0x08, struct.pack("<4i", 1, 0, 0, 0))
    _put(buf, 0x18, _scaled40x4(1.0, 8, 0))
    _put(buf, 0xB8, _scaled40x4(0.0, 8, 0))
    _put(buf, 0x19C, _scaled40(1.0, 6, 0))
    _put(buf, 0x1C4, _scaled40(2.0, 6, 0))
    _put(buf, 0x1EC, struct.pack("<I", 4))
    _put(buf, 0x1F0, _scaled40(1.0, 10, 7))
    _put(buf, 0x244, struct.pack("<4d", 1.0, 1.0, 1.0, 1.0))
    _put(buf, 0x264, b"\x00")
    _put(buf, 0x265, b"\x00")
    _put(buf, 0x26C, struct.pack("<i", 10))
    _put(buf, 0x270, struct.pack("<4i", 30, 30, 30, 30))
    _put(buf, 0x1000, _ANALOG_8_V4)
    return bytes(buf)


def _build_siglent_v5() -> bytes:
    buf = bytearray(0x1BA2)
    _put(buf, 0x00, struct.pack("<I", 5))
    _put(buf, 0x76, struct.pack("<i", 1))
    _put(buf, 0xF0, struct.pack("<i", 0))
    _put(buf, 0x194, struct.pack("<i", 0))
    _put(buf, 0x238, struct.pack("<i", 0))
    _put(buf, 0xAB, _scaled16(1.0, 8, 0))
    _put(buf, 0x160, _scaled16(1.0, 8, 0))
    _put(buf, 0x204, _scaled16(1.0, 8, 0))
    _put(buf, 0x2A8, _scaled16(1.0, 8, 0))
    _put(buf, 0xBC, _scaled16(0.0, 8, 0))
    _put(buf, 0x170, _scaled16(0.0, 8, 0))
    _put(buf, 0x214, _scaled16(0.0, 8, 0))
    _put(buf, 0x2B8, _scaled16(0.0, 8, 0))
    _put(buf, 0x1B68, _scaled16(1.0, 6, 14))
    _put(buf, 0x1B78, _scaled16(0.0, 8, 14))
    _put(buf, 0x1B88, struct.pack("<I", 4))
    _put(buf, 0x1B92, _scaled16(1.0, 10, 15))
    _put(buf, 0x800, _ANALOG_8)
    return bytes(buf)


def _build_siglent_v6() -> bytes:
    file_header = (
        struct.pack("<IHH", 6, 108, 0)
        + _ascii("SDS1002X-E", 32)
        + _ascii("SN000001", 32)
        + _ascii("V1.3.27", 32)
        + struct.pack("<I", 1)
    )
    waveform_header = (
        struct.pack("<IIIHH", 0, 264, 0, 0, 1)
        + _ascii("CH1", 16)
        + _ascii("2026 03 29", 16)
        + _ascii("12-00-00 000000000", 32)
        + struct.pack("<4d", 1.0e-6, 0.0, 0.0, 1.0e-6)
        + struct.pack("<8I", *([0] * 8))
        + _ascii("s", 16)
        + struct.pack("<4d", 1.0, 0.0, 128.0, 0.04)
        + struct.pack("<8I", *([0] * 8))
        + _ascii("V", 16)
        + struct.pack("<IIQQ", 0, 0, 4, 4)
    )
    return file_header + waveform_header + _ANALOG_8


_LOW_LEVEL_CASES = [
    ("old", _build_siglent_old_platform, lambda raw: raw.ch_on.entries == [1, 0, 0, 0]),
    ("v0_1", _build_siglent_v0_1, lambda raw: int(raw.wave_length) == 4),
    ("v0_2", _build_siglent_v0_2, lambda raw: int(raw.wave_length) == 4),
    ("v1", _build_siglent_v1, lambda raw: raw.ch_on.entries == [1, 0, 0, 0]),
    ("v2", _build_siglent_v2, lambda raw: int(raw.version) == 2),
    ("v3", _build_siglent_v3, lambda raw: raw.ch_vert_code_per_div.entries[0] == 30),
    ("v4", _build_siglent_v4, lambda raw: int(raw.data_offset_byte) == 0x1000),
    ("v5", _build_siglent_v5, lambda raw: int(raw.version) == 5 and int(raw.wave_length) == 4),
    (
        "v6",
        _build_siglent_v6,
        lambda raw: int(raw.file_header.version) == 6 and int(raw.waveforms[0].header.data_number) == 4,
    ),
]

_NORMALIZED_CASES = [
    ("v0_1", _build_siglent_v0_1, "Siglent V0.1", -7.0e-6, 1.0e-6, [0.0, 1.0, -1.0, 0.0]),
    ("v0_2", _build_siglent_v0_2, "Siglent V0.2", -7.0e-6, 1.0e-6, [0.0, 1.0, -1.0, 0.0]),
    ("v1", _build_siglent_v1, "Siglent V1.0", -7.0e-6, 1.0e-6, [0.0, 1.0, -1.0, 0.0]),
    ("v2", _build_siglent_v2, "Siglent V2.0", -7.0e-6, 1.0e-6, [0.0, 1.0, -1.0, 0.0]),
    ("v3", _build_siglent_v3, "Siglent V3.0", -7.0e-6, 1.0e-6, [0.0, 1.0, -1.0, 0.0]),
    ("v4", _build_siglent_v4, "Siglent V4.0", -7.0e-6, 1.0e-6, [0.0, 1.0, -1.0, 0.0]),
    ("v5", _build_siglent_v5, "Siglent V5.0", -7.0e-6, 1.0e-6, [0.0, 1.0, -1.0, 0.0]),
    ("v6", _build_siglent_v6, "SDS1002X-E", 0.0, 1.0e-6, [0.0, 1.0, -1.0, 0.0]),
]


@pytest.mark.parametrize("revision, builder, checker", _LOW_LEVEL_CASES)
def test_siglent_low_level_parsers_cover_all_documented_revisions(tmp_path, revision, builder, checker):
    """Every documented Siglent waveform revision should have a low-level parser."""
    path = tmp_path / f"{revision}.bin"
    path.write_bytes(builder())

    assert RigolWFM.siglent.detect_revision(str(path)) == revision
    detected_revision, raw = RigolWFM.siglent.parse_low_level(str(path))

    assert detected_revision == revision
    assert checker(raw)


@pytest.mark.parametrize("revision, builder, _checker", _LOW_LEVEL_CASES)
def test_siglent_detect_model_recognizes_documented_revisions(tmp_path, revision, builder, _checker):
    """`detect_model()` should recognize Siglent revisions from synthetic fixtures."""
    path = tmp_path / f"{revision}.bin"
    path.write_bytes(builder())

    expected = "SiglentOld" if revision == "old" else "Siglent"
    assert RigolWFM.wfm.detect_model(str(path)) == expected


@pytest.mark.parametrize("revision, builder, expected_model, x0, dt, expected_volts", _NORMALIZED_CASES)
def test_siglent_supported_revisions_round_trip_through_wfm(
    tmp_path,
    revision,
    builder,
    expected_model,
    x0,
    dt,
    expected_volts,
):
    """Supported Siglent revisions should normalize into calibrated waveforms."""
    path = tmp_path / f"{revision}.bin"
    path.write_bytes(builder())

    waveform = RigolWFM.wfm.Wfm.from_file(str(path))
    explicit = RigolWFM.wfm.Wfm.from_file(str(path), "Siglent")

    assert waveform.user_name == "auto"
    assert waveform.parser_name == "siglent_bin"
    assert waveform.header_name == expected_model
    assert explicit.header_name == expected_model
    assert [channel.channel_number for channel in waveform.channels] == [1]

    channel = waveform.channels[0]
    assert channel.times is not None
    assert channel.volts is not None
    np.testing.assert_allclose(channel.volts, expected_volts)
    assert channel.times[0] == pytest.approx(x0)
    assert channel.times[1] - channel.times[0] == pytest.approx(dt)


def test_siglent_old_platform_is_detectable_but_not_normalized(tmp_path):
    """Old-platform Siglent files should fail loudly in the high-level adapter."""
    path = tmp_path / "old.bin"
    path.write_bytes(_build_siglent_old_platform())

    assert RigolWFM.wfm.detect_model(str(path)) == "SiglentOld"
    with pytest.raises(ValueError, match="does not normalize"):
        RigolWFM.wfm.Wfm.from_file(str(path))
