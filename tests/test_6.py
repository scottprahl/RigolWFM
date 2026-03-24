"""Synthetic regression tests for Rigol 6000-family waveform parsing."""

import io
import struct

import pytest

import RigolWFM.wfm
import RigolWFM.wfm6000


def _padded_ascii(text, size):
    """Return an ASCII string padded with trailing NUL bytes."""
    data = text.encode("ascii")
    return data + b"\0" * (size - len(data))


def _channel_header(
    *,
    enabled,
    volt_per_division,
    volt_offset,
    invert=0,
    unit=2,
    coupling=0,
    probe_ratio=6,
    probe_impedance=1,
):
    """Build one DS6000 `CVertPara` block."""
    return struct.pack(
        "<BBBBBBBBffBBBBII",
        enabled,
        coupling,
        0,
        0,
        probe_ratio,
        0,
        0,
        probe_impedance,
        volt_per_division,
        volt_offset,
        invert,
        unit,
        0,
        0,
        0,
        0,
    )


def _build_ds6000_file(
    *,
    wfm_offset=512,
    channel_offsets=(0, 16, 0, 0),
    storage_depth=16,
    z_pt_offset=3,
    wfm_len=6,
):
    """Build a minimal DS6000 waveform file for parser tests."""
    enabled_mask = 0x03
    raw_ch1 = bytes(range(10, 10 + storage_depth))
    raw_ch2 = bytes(range(110, 110 + storage_depth))

    header = io.BytesIO()
    header.write(b"\xA5\xA5\x38\x00")
    header.write(_padded_ascii("DS6104", 20))
    header.write(_padded_ascii("00.00.00.SP0", 20))
    header.write(struct.pack("<HH", 1, 1))
    header.write(b"\0" * 18)
    header.write(struct.pack("<B", enabled_mask))
    header.write(struct.pack("<IIII", *channel_offsets))
    header.write(struct.pack("<BHHIfHqq", 0, 2, 0, storage_depth, 1.0e9, 0, 1_000, 0))
    header.write(_channel_header(enabled=1, volt_per_division=1.0, volt_offset=0.25))
    header.write(_channel_header(enabled=1, volt_per_division=2.0, volt_offset=-0.5))
    header.write(_channel_header(enabled=0, volt_per_division=1.0, volt_offset=0.0))
    header.write(_channel_header(enabled=0, volt_per_division=1.0, volt_offset=0.0))
    header.write(struct.pack("<III", wfm_offset - 436, 436, wfm_offset))
    header.write(struct.pack("<III", storage_depth, z_pt_offset, wfm_len))
    header.write(struct.pack("<HH", 0, 0))
    header.write(struct.pack("<HH", 0, 0))
    header.write(struct.pack("<HH", 0, 0))
    header.write(struct.pack("<II", 0, 0))
    header.write(struct.pack("<II", storage_depth, storage_depth))
    header.write(struct.pack("<II", 0, 0))
    header.write(struct.pack("<II", storage_depth, storage_depth))
    header.write(struct.pack("<HBBBBB", 0, 0, 0, 0, 0, 0))
    header.write(struct.pack("<qqqqQ", 0, 0, 0, 0, 0))
    header.write(struct.pack("<iiiIIIII", 0, 0, 0, 0, 0, 0, 0, 0))
    header.write(struct.pack("<HHHHHH", 0, 0, 0, 0, 0, 0))
    header.write(struct.pack("<I", 0))

    payload = bytearray(header.getvalue())
    if len(payload) < wfm_offset:
        payload.extend(b"\0" * (wfm_offset - len(payload)))

    data_len = max(channel_offsets[0] + len(raw_ch1), channel_offsets[1] + len(raw_ch2))
    data = bytearray(b"\0" * data_len)
    data[channel_offsets[0] : channel_offsets[0] + len(raw_ch1)] = raw_ch1
    data[channel_offsets[1] : channel_offsets[1] + len(raw_ch2)] = raw_ch2
    payload.extend(data)
    return bytes(payload)


def test_ds6000_parser_uses_wfm_offset_and_channel_offsets(tmp_path):
    """Low-level DS6000 parsing should honor dynamic offsets and effective length."""
    path = tmp_path / "synthetic-ds6000.wfm"
    path.write_bytes(_build_ds6000_file())

    waveform = RigolWFM.wfm6000.Wfm6000.from_file(str(path))
    assert waveform.header.points == 6
    assert waveform.header.raw_1 == bytes([13, 14, 15, 16, 17, 18])
    assert waveform.header.raw_2 == bytes([113, 114, 115, 116, 117, 118])
    assert waveform.header.ch[0].enabled
    assert waveform.header.ch[1].enabled
    assert not waveform.header.ch[2].enabled
    assert waveform.header.ch[0].volt_scale == pytest.approx(1.0 / 25.0)


def test_ds6000_runtime_uses_effective_window_and_exact_dt(tmp_path):
    """The DS6000 adapter should expose the sliced raw bytes with exact sample spacing."""
    path = tmp_path / "synthetic-ds6000.wfm"
    path.write_bytes(_build_ds6000_file())

    waveform = RigolWFM.wfm.Wfm.from_file(str(path), "6")
    channel_1 = waveform.channels[0]
    channel_2 = waveform.channels[1]

    assert channel_1.enabled
    assert channel_1.points == 6
    assert channel_1.raw.tolist() == [13, 14, 15, 16, 17, 18]
    assert channel_2.raw.tolist() == [113, 114, 115, 116, 117, 118]
    assert channel_1.times[0] == pytest.approx(-5e-9)
    assert channel_1.times[1] - channel_1.times[0] == pytest.approx(1e-9)


def test_ds6000_channel_offset_zero_is_valid(tmp_path):
    """Channel 1 data may start at offset zero inside the waveform payload."""
    path = tmp_path / "synthetic-ds6000-zero-offset.wfm"
    path.write_bytes(_build_ds6000_file(channel_offsets=(0, 24, 0, 0)))

    waveform = RigolWFM.wfm6000.Wfm6000.from_file(str(path))
    assert waveform.header.raw_1[0] == 13
    assert waveform.header.raw_2[0] == 113
