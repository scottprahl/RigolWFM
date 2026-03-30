"""Tests for Tektronix WFM parsing, including WFM#003 layout handling."""

from __future__ import annotations

import io
import struct

import numpy as np
import pytest
from kaitaistruct import KaitaiStream  # type: ignore[import]

import RigolWFM.tek
import RigolWFM.tektronix_wfm_002_le_wfm
import RigolWFM.wfm


def _ascii_padded(text: str, size: int) -> bytes:
    """Return ASCII text truncated/padded to `size` bytes with NULs."""
    return text.encode("ascii")[:size].ljust(size, b"\x00")


def _write_exp_dim(
    buf: bytearray,
    offset: int,
    *,
    point_density_is_f8: bool,
    dim_scale: float,
    dim_offset: float,
    user_scale: float,
    units: str = "Volts",
    user_units: str = "V",
    format_code: int = 7,
    storage_type: int = 0,
) -> int:
    """Write an explicit-dimension block and return the byte just after it."""
    pos = offset

    def put(fmt: str, *values: object) -> None:
        nonlocal pos
        struct.pack_into("<" + fmt, buf, pos, *values)
        pos += struct.calcsize("<" + fmt)

    put("d", dim_scale)
    put("d", dim_offset)
    put("I", 1)
    buf[pos : pos + 20] = _ascii_padded(units, 20)
    pos += 20
    put("d", -5.0)
    put("d", 5.0)
    put("d", abs(dim_scale))
    put("d", 0.0)
    put("i", format_code)
    put("i", storage_type)
    buf[pos : pos + 20] = b"\x00" * 20
    pos += 20
    put("d", user_scale)
    buf[pos : pos + 20] = _ascii_padded(user_units, 20)
    pos += 20
    put("d", 0.0)
    if point_density_is_f8:
        put("d", 1.0)
    else:
        put("I", 1)
    put("d", 50.0)
    put("d", 0.0)

    return pos


def _write_imp_dim(
    buf: bytearray,
    offset: int,
    *,
    point_density_is_f8: bool,
    dim_scale: float,
    dim_offset: float,
    dim_size: int,
    user_scale: float,
    units: str = "Seconds",
    user_units: str = "s",
) -> int:
    """Write an implicit-dimension block and return the byte just after it."""
    pos = offset

    def put(fmt: str, *values: object) -> None:
        nonlocal pos
        struct.pack_into("<" + fmt, buf, pos, *values)
        pos += struct.calcsize("<" + fmt)

    put("d", dim_scale)
    put("d", dim_offset)
    put("I", dim_size)
    buf[pos : pos + 20] = _ascii_padded(units, 20)
    pos += 20
    put("d", 0.0)
    put("d", dim_scale * max(dim_size - 1, 0))
    put("d", dim_scale)
    put("d", 0.0)
    put("I", 1)
    put("d", user_scale)
    buf[pos : pos + 20] = _ascii_padded(user_units, 20)
    pos += 20
    put("d", 0.0)
    if point_density_is_f8:
        put("d", 1.0)
    else:
        put("I", 1)
    put("d", 50.0)
    put("d", 0.0)

    return pos


def _build_tek_wfm(
    *,
    version: str,
    samples: list[int],
    dim_scale: float = 0.02,
    dim_offset: float = -1.0,
    time_scale: float = 2.5e-9,
    time_offset: float = -5.0e-9,
    label: str = "TEK-SYNTH",
    time_base_spacing: int = 7,
    update_real_point_offset: int = 123,
) -> bytes:
    """Build a minimal little-endian WFM#002 or WFM#003 file."""
    assert version in {"WFM#002", "WFM#003"}

    point_density_is_f8 = version == "WFM#003"
    exp_dim_size = 160 if point_density_is_f8 else 156
    imp_dim_size = 136 if point_density_is_f8 else 132

    exp_dim1_off = 168
    exp_dim2_off = exp_dim1_off + exp_dim_size
    imp_dim1_off = exp_dim2_off + exp_dim_size
    imp_dim2_off = imp_dim1_off + imp_dim_size
    time_base1_off = imp_dim2_off + imp_dim_size
    time_base2_off = time_base1_off + 12
    update_spec_off = time_base2_off + 12
    curve_off = update_spec_off + 24
    curve_buffer_off = curve_off + 30

    file_size = curve_buffer_off + len(samples)
    buf = bytearray(file_size)

    def put(offset: int, fmt: str, *values: object) -> None:
        struct.pack_into("<" + fmt, buf, offset, *values)

    # Static file info (78 bytes)
    put(0, "H", 0x0F0F)
    buf[2:9] = version.encode("ascii")
    buf[9] = 0
    put(10, "B", 0)
    put(11, "i", file_size - 15)
    put(15, "B", 1)
    put(16, "i", curve_buffer_off)
    put(20, "i", 0)
    put(24, "f", 0.0)
    put(28, "d", 0.0)
    put(36, "f", 0.0)
    buf[40:72] = _ascii_padded(label, 32)
    put(72, "I", 0)
    put(76, "H", curve_buffer_off - 78)

    # WFM header pre-dimension fields
    put(78, "i", 0)  # set_type = single_waveform
    put(82, "I", 1)  # wfm_cnt
    put(86, "Q", 1)  # acq_counter
    put(94, "Q", 2)  # transaction_counter
    put(102, "i", 0)  # slot_id
    put(106, "i", 0)  # is_static_flag
    put(110, "I", 1)  # wfm_update_spec_count
    put(114, "I", 2)  # imp_dim_ref_count
    put(118, "I", 2)  # exp_dim_ref_count
    put(122, "i", 2)  # data_type = vector
    put(126, "Q", 0)  # gen_purpose_counter
    put(134, "I", 1)  # accum_wfm_count
    put(138, "I", 1)  # target_accum_count
    put(142, "I", 1)  # curve_ref_count
    put(146, "I", 0)  # num_requested_fast_frames
    put(150, "I", 0)  # num_acquired_fast_frames
    put(154, "H", 0)  # summary_frame_type
    put(156, "i", 1)  # pix_map_display_format
    put(160, "Q", 0)  # pix_map_max_value

    next_off = _write_exp_dim(
        buf,
        exp_dim1_off,
        point_density_is_f8=point_density_is_f8,
        dim_scale=dim_scale,
        dim_offset=dim_offset,
        user_scale=0.5,
    )
    assert next_off == exp_dim2_off

    next_off = _write_exp_dim(
        buf,
        exp_dim2_off,
        point_density_is_f8=point_density_is_f8,
        dim_scale=0.0,
        dim_offset=0.0,
        user_scale=0.0,
        units="",
        user_units="",
    )
    assert next_off == imp_dim1_off

    next_off = _write_imp_dim(
        buf,
        imp_dim1_off,
        point_density_is_f8=point_density_is_f8,
        dim_scale=time_scale,
        dim_offset=time_offset,
        dim_size=len(samples),
        user_scale=1e-8,
    )
    assert next_off == imp_dim2_off

    next_off = _write_imp_dim(
        buf,
        imp_dim2_off,
        point_density_is_f8=point_density_is_f8,
        dim_scale=0.0,
        dim_offset=0.0,
        dim_size=0,
        user_scale=0.0,
        units="",
        user_units="",
    )
    assert next_off == time_base1_off

    # time_base_info blocks
    put(time_base1_off, "I", time_base_spacing)
    put(time_base1_off + 4, "i", 1)  # sweep_sample
    put(time_base1_off + 8, "i", 0)  # base_time
    put(time_base2_off, "I", 0)
    put(time_base2_off + 4, "i", 1)
    put(time_base2_off + 8, "i", 0)

    # update_spec
    put(update_spec_off, "I", update_real_point_offset)
    put(update_spec_off + 4, "d", 0.0)
    put(update_spec_off + 12, "d", 0.0)
    put(update_spec_off + 20, "i", 0)

    # curve object
    curve_len = len(samples)
    put(curve_off, "I", 0)  # state_flags
    put(curve_off + 4, "i", 0)  # checksum_type = none
    put(curve_off + 8, "h", 0)  # checksum
    put(curve_off + 10, "I", 0)  # precharge_start_offset
    put(curve_off + 14, "I", 0)  # data_start_offset
    put(curve_off + 18, "I", curve_len)  # postcharge_start_offset
    put(curve_off + 22, "I", curve_len)  # postcharge_stop_offset
    put(curve_off + 26, "I", curve_len)  # end_of_curve_buffer_offset

    struct.pack_into(f"<{len(samples)}b", buf, curve_buffer_off, *samples)

    return bytes(buf)


def _build_legacy_llwfm(
    *,
    samples: list[int],
    vert_gain: float = 0.5,
    vert_offset: float = -0.125,
    vert_pos: float = 0.25,
    horz_scale: float = 2.0e-9,
    trig_pos: int = 40,
) -> bytes:
    """Build a minimal big-endian legacy Tektronix LLWFM file."""
    record_length = len(samples)

    body = bytearray()
    body.extend(struct.pack(">i", 0x13579BDF))
    body.extend(struct.pack(">i", 2 * record_length + 64))

    # Reference header
    body.extend(struct.pack(">d", vert_pos))
    body.extend(struct.pack(">d", 0.0))
    body.extend(struct.pack(">d", 1.0))
    body.extend(struct.pack(">d", 1.0))

    # Waveform header
    body.extend(struct.pack(">h", 0))  # acqmode
    body.extend(struct.pack(">h", 0))  # minMaxFormat
    body.extend(struct.pack(">d", record_length * horz_scale))
    body.extend(struct.pack(">h", 565))  # vertCpl = DC
    body.extend(struct.pack(">h", 610))  # horzUnit = seconds
    body.extend(struct.pack(">d", horz_scale))
    body.extend(struct.pack(">h", 609))  # vertUnit = volts
    body.extend(struct.pack(">d", vert_offset))
    body.extend(struct.pack(">d", vert_pos))
    body.extend(struct.pack(">d", vert_gain))
    body.extend(struct.pack(">I", record_length))
    body.extend(struct.pack(">h", trig_pos))
    body.extend(struct.pack(">h", 1))  # header version
    body.extend(struct.pack(">h", 1))  # sample density
    body.extend(struct.pack(">h", 0))  # burst segment length
    body.extend(struct.pack(">h", 0))  # source waveform
    body.extend(struct.pack(">3h", 0, 0, 0))
    body.extend(struct.pack(">d", 0.0))
    body.extend(struct.pack(">h", 0))

    body.extend(struct.pack(">16h", *([0] * 16)))
    body.extend(struct.pack(f">{record_length}h", *samples))
    body.extend(struct.pack(">16h", *([0] * 16)))
    body.extend(struct.pack(">h", 0))

    count = str(len(body)).encode("ascii")
    return b":LLWFM#" + str(len(count)).encode("ascii") + count + bytes(body)


def test_wfm002_synthetic_from_file(tmp_path):
    """Synthetic WFM#002 files should still parse correctly after the WFM#003 fix."""
    samples = [-8, -1, 0, 7, 12]
    data = _build_tek_wfm(version="WFM#002", samples=samples)
    path = tmp_path / "synthetic_002.wfm"
    path.write_bytes(data)

    obj = RigolWFM.tek.from_file(str(path))

    expected = (0.02 * np.asarray(samples, dtype=np.float64) - 1.0).astype(np.float32)
    np.testing.assert_allclose(obj.header.channel_data[0], expected)
    assert obj.header.x_origin == pytest.approx(-5.0e-9)
    assert obj.header.x_increment == pytest.approx(2.5e-9)


def test_wfm003_parser_uses_post_point_density_offsets():
    """WFM#003 should parse fields after point_density at their correct shifted offsets."""
    samples = [-3, 1, 4, 8]
    data = _build_tek_wfm(
        version="WFM#003",
        samples=samples,
        time_base_spacing=11,
        update_real_point_offset=321,
    )

    raw = RigolWFM.tektronix_wfm_002_le_wfm.TektronixWfm002LeWfm(KaitaiStream(io.BytesIO(data)))

    assert raw.is_wfm003 is True
    assert raw.wfm_header.time_base1.real_point_spacing == 11
    assert raw.wfm_header.update_spec.real_point_offset == 321
    assert raw.wfm_header.curve.postcharge_start_offset == len(samples)
    assert raw.static_file_info.byte_offset_to_curve_buffer == 838


def test_wfm003_synthetic_from_file(tmp_path):
    """Synthetic WFM#003 files should reconstruct the correct time and voltage arrays."""
    samples = [-10, -5, 0, 5, 10]
    data = _build_tek_wfm(
        version="WFM#003",
        samples=samples,
        dim_scale=0.05,
        dim_offset=0.25,
        time_scale=1.25e-9,
        time_offset=-2.5e-9,
        label="DPO7000",
    )
    path = tmp_path / "synthetic_003.wfm"
    path.write_bytes(data)

    waveform = RigolWFM.wfm.Wfm.from_file(str(path), "Tek", "1")

    expected_volts = 0.05 * np.asarray(samples, dtype=np.float64) + 0.25
    expected_times = -2.5e-9 + np.arange(len(samples), dtype=np.float64) * 1.25e-9

    assert waveform.parser_name == "tek_wfm"
    assert waveform.header_name == "Tektronix"
    assert len(waveform.channels) == 1
    np.testing.assert_allclose(waveform.channels[0].volts, expected_volts)
    np.testing.assert_allclose(waveform.channels[0].times, expected_times)


def test_legacy_llwfm_synthetic_from_file(tmp_path):
    """Legacy LLWFM files should parse through the Tek adapter."""
    samples = [-2048, -1024, 0, 1024, 2047]
    data = _build_legacy_llwfm(samples=samples, vert_gain=0.4, vert_offset=0.1, vert_pos=0.5)
    path = tmp_path / "legacy_llwfm.wfm"
    path.write_bytes(data)

    waveform = RigolWFM.wfm.Wfm.from_file(str(path), "Tek", "1")
    expected_volts = np.asarray(samples, dtype=np.float64) * (0.4 / (25.0 * 256.0)) + 0.1 - 0.5 * 0.4
    expected_times = -(len(samples) * 40 / 100.0) * 2.0e-9 + np.arange(len(samples)) * 2.0e-9

    assert waveform.parser_name == "tek_wfm"
    assert waveform.header_name == "Tektronix"
    np.testing.assert_allclose(waveform.channels[0].volts, expected_volts)
    np.testing.assert_allclose(waveform.channels[0].times, expected_times)


def test_legacy_llwfm_autodetect(tmp_path):
    """detect_model() should classify legacy LLWFM files as Tek."""
    path = tmp_path / "legacy_auto.wfm"
    path.write_bytes(_build_legacy_llwfm(samples=[-1, 0, 1]))

    assert RigolWFM.wfm.detect_model(str(path)) == "Tek"
