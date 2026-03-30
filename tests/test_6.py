"""Synthetic regression tests for Rigol 6000-family waveform parsing."""

import io
import struct

import pytest

import RigolWFM.wfm
import RigolWFM.rigol_6000_wfm


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
    channel_offsets=None,
    storage_depth=16,
    z_pt_offset=3,
    wfm_len=6,
):
    """Build a minimal DS6000 waveform file for parser tests."""
    if channel_offsets is None:
        channel_offsets = (wfm_offset, wfm_offset + 16, 0, 0)

    enabled_mask = sum(1 << index for index, offset in enumerate(channel_offsets) if offset != 0)
    raw_ch1 = bytes(range(10, 10 + storage_depth))
    raw_ch2 = bytes(range(110, 110 + storage_depth))
    private_words = (11, 22, 33, 44)

    header = io.BytesIO()
    header.write(b"\xa5\xa5\x38\x00")
    header.write(_padded_ascii("DS6104", 20))
    header.write(_padded_ascii("00.00.00.SP0", 20))
    header.write(struct.pack("<HHIHH", 1, 1, 0, 0, 0))

    assert header.tell() == 56

    header.write(struct.pack("<IHHH", 0, 360, 1, enabled_mask))
    header.write(struct.pack("<H", 0))
    header.write(struct.pack("<IIII", *channel_offsets))
    header.write(struct.pack("<HHH", 3, 2, 0))
    header.write(struct.pack("<H", 0))
    header.write(struct.pack("<IfH", storage_depth, 1.0e9, 0))
    header.write(struct.pack("<H", 0))
    header.write(struct.pack("<qq", 1_000, 0))
    header.write(
        _channel_header(
            enabled=int(channel_offsets[0] != 0),
            volt_per_division=1.0,
            volt_offset=0.25,
        )
    )
    header.write(
        _channel_header(
            enabled=int(channel_offsets[1] != 0),
            volt_per_division=2.0,
            volt_offset=-0.5,
        )
    )
    header.write(
        _channel_header(
            enabled=int(channel_offsets[2] != 0),
            volt_per_division=1.0,
            volt_offset=0.0,
        )
    )
    header.write(
        _channel_header(
            enabled=int(channel_offsets[3] != 0),
            volt_per_division=1.0,
            volt_offset=0.0,
        )
    )
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
    header.write(struct.pack("<B", 0))
    header.write(struct.pack("<qqqqQ", 0, 0, 0, 0, 0))
    header.write(struct.pack("<iiiIIIII", 0, 0, 0, 0, 0, 0, 0, 0))
    header.write(struct.pack("<hhHHHH", -3, 4, 0, 0, 0, 0))
    header.write(struct.pack("<II", 7, 9))
    header.write(struct.pack("<IIII", *private_words))

    assert header.tell() == 416

    header.write(struct.pack("<HHH2xI", 0xA5A5, 12, 1, storage_depth))
    header.write(struct.pack("<II", 8, 0))

    assert header.tell() == 436

    header.write(b"\0" * (wfm_offset - 436))

    payload = bytearray(header.getvalue())

    last_offset = max((offset + storage_depth for offset in channel_offsets if offset != 0), default=len(payload))
    if len(payload) < last_offset:
        payload.extend(b"\0" * (last_offset - len(payload)))

    if channel_offsets[0] != 0:
        payload[channel_offsets[0] : channel_offsets[0] + len(raw_ch1)] = raw_ch1
    if channel_offsets[1] != 0:
        payload[channel_offsets[1] : channel_offsets[1] + len(raw_ch2)] = raw_ch2

    return bytes(payload)


def test_ds6000_parser_uses_wfm_offset_and_channel_offsets(tmp_path):
    """Low-level DS6000 parsing should honor documented absolute offsets and tail fields."""
    path = tmp_path / "synthetic-ds6000.wfm"
    path.write_bytes(_build_ds6000_file())

    waveform = RigolWFM.rigol_6000_wfm.Rigol6000Wfm.from_file(str(path))
    assert waveform.header.points == 6
    assert waveform.header.structure_size == 360
    assert waveform.header.acquisition_mode.name == "high_resolution"
    assert waveform.header.raw_1 == bytes([13, 14, 15, 16, 17, 18])
    assert waveform.header.raw_2 == bytes([113, 114, 115, 116, 117, 118])
    assert waveform.header.s16_adc1_clock_delay == -3
    assert waveform.header.s16_adc2_clock_delay == 4
    assert waveform.header.record_frame_index == 7
    assert waveform.header.frame_cur == 9
    assert waveform.header.private == [11, 22, 33, 44]
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


def test_ds6000_zero_channel_offset_means_no_saved_trace(tmp_path):
    """A zero waveform point offset means the file does not contain that trace."""
    path = tmp_path / "synthetic-ds6000-missing-ch1.wfm"
    path.write_bytes(_build_ds6000_file(channel_offsets=(0, 528, 0, 0)))

    waveform = RigolWFM.rigol_6000_wfm.Rigol6000Wfm.from_file(str(path))
    assert not waveform.header.enabled.channel_1
    assert waveform.header.raw_1 is None
    assert waveform.header.raw_2[0] == 113
