"""Tests for Tektronix WFM parsing, including WFM#003 layout handling."""

import io
from pathlib import Path
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
    buf[2:10] = f":{version}".encode("ascii")
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


def test_wfm002_synthetic_autodetect(tmp_path):
    """detect_model() should classify Synthetic WFM#002 files as Tek."""
    samples = [-8, -1, 0, 7, 12]
    data = _build_tek_wfm(version="WFM#002", samples=samples)
    path = tmp_path / "synthetic_002_autodetect.wfm"
    path.write_bytes(data)

    assert RigolWFM.wfm.detect_model(str(path)) == "Tek"


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


def test_wfm003_synthetic_autodetect(tmp_path):
    """detect_model() should classify Synthetic WFM#003 files as Tek."""
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
    path = tmp_path / "synthetic_003_auto.wfm"
    path.write_bytes(data)

    assert RigolWFM.wfm.detect_model(str(path)) == "Tek"


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


# Real WFM#003 captures published by Tektronix.  The expected values below were
# read from the same files with Tektronix's own `tm_data_types` library, so they
# pin this parser to the vendor's interpretation rather than to itself.
_TEK_SAMPLES = Path(__file__).resolve().parents[1] / "tests" / "files" / "wfm-tek"

_TEK_GOLDEN = [
    # name, points, t0, dt, first volts, last volts
    ("analog_waveform.wfm", 50_000, -1.0e-6, 4.0e-11, -0.148, 0.144),
    ("data_test_waveform.wfm", 1_000, -2.0e-8, 4.0e-11, -0.004, -0.008),
    ("golden_analog.wfm", 6, -3.0, 1.0, 0.0003051851, 0.9834284494),
]


@pytest.mark.parametrize("name, points, t0, dt, first_volts, last_volts", _TEK_GOLDEN)
def test_tektronix_sample_matches_vendor_reader(name, points, t0, dt, first_volts, last_volts):
    """Published Tektronix captures should decode the way Tektronix decodes them."""
    channel = RigolWFM.wfm.Wfm.from_file(str(_TEK_SAMPLES / name)).channels[0]

    assert channel.points == points
    assert len(channel.times) == points
    assert channel.times[0] == pytest.approx(t0, rel=1e-9)
    assert channel.times[1] - channel.times[0] == pytest.approx(dt, rel=1e-9)
    assert channel.volts[0] == pytest.approx(first_volts, abs=1e-6)
    assert channel.volts[-1] == pytest.approx(last_volts, abs=1e-6)


def test_tektronix_precharge_does_not_shift_the_time_axis():
    """A curve buffer opening with precharge must not double-count it in t0.

    `analog_waveform.wfm` carries 32 precharge samples and a 50000-sample record
    centered on the trigger, so the axis has to run from -1 us to +1 us.  Adding
    `first_valid_sample` to `dim_offset` pushed it 32 samples late.
    """
    channel = RigolWFM.wfm.Wfm.from_file(str(_TEK_SAMPLES / "analog_waveform.wfm")).channels[0]

    assert channel.times[0] == pytest.approx(-1.0e-6, rel=1e-9)
    assert channel.times[-1] == pytest.approx(1.0e-6 - 4.0e-11, rel=1e-9)


def test_tektronix_iq_capture_splits_into_i_and_q():
    """An IQ capture holds interleaved pairs and must come back as two traces.

    The 7250 stored samples are 3625 I/Q pairs; `imp_dim1.dim_scale` already
    steps one whole pair, so both traces share the file's time axis unchanged.
    """
    waveform = RigolWFM.wfm.Wfm.from_file(str(_TEK_SAMPLES / "iq_waveform.wfm"))

    assert [channel.name for channel in waveform.channels] == ["I", "Q"]
    for channel in waveform.channels:
        assert channel.points == 3625
        assert channel.times[0] == pytest.approx(-1.4496063e-3, rel=1e-6)
        assert channel.times[1] - channel.times[0] == pytest.approx(4.00002e-7, rel=1e-5)

    # even samples are in phase, odd are quadrature
    assert waveform.channels[0].volts[0] == pytest.approx(0.1625, abs=1e-6)
    assert waveform.channels[1].volts[0] == pytest.approx(-0.1482812, abs=1e-6)


def test_tektronix_iq_matches_vendor_reader():
    """The in-phase trace should match Tektronix's own decode of the same file."""
    # tm_data_types returns 3625 normalized values for this capture, beginning
    # 0.1625, 0.163125, 0.16390625 and ending 0.11609375.
    channel = RigolWFM.wfm.Wfm.from_file(str(_TEK_SAMPLES / "iq_waveform.wfm")).channels[0]

    np.testing.assert_allclose(channel.volts[:3], [0.1625, 0.163125, 0.16390625], atol=1e-6)
    assert channel.volts[-1] == pytest.approx(0.11609375, abs=1e-6)
    assert channel.times[-1] == pytest.approx(0.0, abs=1e-12)


def test_tektronix_iq_parameters_are_reported():
    """`Wfm` should carry the acquisition parameters an IQ capture records."""
    waveform = RigolWFM.wfm.Wfm.from_file(str(_TEK_SAMPLES / "iq_waveform.wfm"))

    assert waveform.iq_info["IQ_centerFrequency"] == pytest.approx(1e6)
    assert waveform.iq_info["IQ_rbw"] == pytest.approx(1e3)
    described = waveform.describe()
    assert "Center Freq  = 1.000 MHz" in described
    assert "Window       = Blackharris" in described


def test_tektronix_fastframe_exposes_every_frame():
    """A FastFrame capture holds many frames of one channel, selected by index."""
    path = str(_TEK_SAMPLES / "FF5MhzX100From5Series.wfm")
    waveform = RigolWFM.wfm.Wfm.from_file(path)

    assert waveform.frame_count == 100
    assert waveform.frame_index == 0  # frame 0 by default
    assert waveform.channels[0].points == 2500

    last = RigolWFM.wfm.Wfm.from_file(path, frame=99)
    assert last.frame_index == 99
    assert last.channels[0].points == 2500

    # frames share every scale factor and differ only in their samples
    np.testing.assert_allclose(last.channels[0].times, waveform.channels[0].times)
    assert not np.array_equal(last.channels[0].volts, waveform.channels[0].volts)


def test_tektronix_fastframe_matches_vendor_reader():
    """Frames should decode the way Tektronix decodes them.

    Spot values read from the same file with `tm_data_types`, whose per-frame
    arrays agree with these to float32 rounding across all 100 frames.
    """
    path = str(_TEK_SAMPLES / "FF5MhzX100From5Series.wfm")

    expected = {
        0: [0.0, 0.004, 0.008, 0.008],
        1: [-0.004, 0.0, 0.004, 0.004],
        50: [0.0, 0.0, 0.004, 0.004],
        99: [-0.004, -0.004, 0.0, 0.0],
    }
    for index, first_four in expected.items():
        volts = RigolWFM.wfm.Wfm.from_file(path, frame=index).channels[0].volts
        np.testing.assert_allclose(volts[:4], first_four, atol=1e-6)


def test_tektronix_fastframe_records_each_frame_trigger_time():
    """Per-frame trigger stamps place the frames against one another in time.

    They are held as whole seconds plus a fraction: the capture triggers about
    602 ns apart, which adding a fraction to a ~1.8e9 second count would lose.
    """
    path = str(_TEK_SAMPLES / "FF5MhzX100From5Series.wfm")

    offsets = [RigolWFM.wfm.Wfm.from_file(path, frame=i).frame_trigger_offset for i in range(4)]

    assert offsets[0] == 0.0
    steps = np.diff(offsets)
    np.testing.assert_allclose(steps, 602e-9, atol=5e-9)


def test_tektronix_fastframe_rejects_a_frame_that_does_not_exist():
    """An out-of-range frame should say how many the file actually holds."""
    path = str(_TEK_SAMPLES / "FF5MhzX100From5Series.wfm")

    with pytest.raises(ValueError, match="holds 100 frame"):
        RigolWFM.wfm.Wfm.from_file(path, frame=100)


def test_frames_are_rejected_for_formats_that_have_none():
    """Only Tektronix FastFrame files have frames; asking elsewhere is an error."""
    with pytest.raises(RigolWFM.wfm.Parse_WFM_Error, match="single frame"):
        RigolWFM.wfm.Wfm.from_file("tests/files/wfm/DS1102E-A.wfm", "E", frame=2)


def test_tektronix_ordinary_capture_reports_one_frame():
    """A normal capture is a one-frame file, and says so."""
    waveform = RigolWFM.wfm.Wfm.from_file(str(_TEK_SAMPLES / "analog_waveform.wfm"))

    assert waveform.frame_count == 1
    assert "FastFrame" not in waveform.describe()


def test_tektronix_analog_capture_is_not_treated_as_iq():
    """Only captures with IQ metadata split; ordinary analog files stay single."""
    waveform = RigolWFM.wfm.Wfm.from_file(str(_TEK_SAMPLES / "analog_waveform.wfm"))

    assert len(waveform.channels) == 1
    assert not waveform.iq_info


def test_tektronix_tekmeta_is_decoded():
    """The trailing `tekmeta!` block should decode to its key/value pairs."""
    waveform = RigolWFM.tek.from_file(str(_TEK_SAMPLES / "iq_waveform.wfm"))

    assert waveform.tekmeta["IQ_centerFrequency"] == pytest.approx(1e6)
    assert waveform.tekmeta["IQ_span"] == pytest.approx(1e6)
    assert waveform.tekmeta["IQ_windowType"] == "Blackharris"


def test_tektronix_tekmeta_survives_a_missing_or_broken_block():
    """Metadata is optional, so an absent or truncated block must not raise."""
    assert not RigolWFM.tek._parse_tekmeta(b"no metadata here", "<")
    # a well-formed header promising an entry the file does not contain
    truncated = b"tekmeta!" + struct.pack("<I", 1) + struct.pack("<I", 4) + b"ke"
    assert not RigolWFM.tek._parse_tekmeta(truncated, "<")


def test_tektronix_digital_capture_yields_logic_traces():
    """A digital capture should expose one 0/1 trace per line, not fake volts."""
    waveform = RigolWFM.wfm.Wfm.from_file(str(_TEK_SAMPLES / "digital_waveform.wfm"))

    # the bytes are packed logic states, so there is no analog channel at all
    assert not waveform.channels
    assert list(waveform.logic_channels) == [f"d{bit}" for bit in range(8)]

    for trace in waveform.logic_channels.values():
        assert len(trace) == 2500
        assert set(np.unique(trace)) <= {0, 1}

    assert waveform.logic_seconds_per_point == pytest.approx(4.0e-11)
    assert waveform.logic_times[0] == pytest.approx(-5.0e-8)


def test_tektronix_digital_lines_carry_the_recorded_pulse():
    """Each line holds one pulse, staggered by the capture's channel skew.

    Every line starts high, drops near -29.8 ns and returns high near +16 ns.
    Reading the bytes as a voltage instead of unpacking their bits hid this.
    """
    waveform = RigolWFM.wfm.Wfm.from_file(str(_TEK_SAMPLES / "digital_waveform.wfm"))
    times = np.asarray(waveform.logic_times)

    for name, trace in waveform.logic_channels.items():
        edges = np.flatnonzero(np.diff(np.asarray(trace)))
        assert len(edges) == 2, f"{name} should hold exactly one pulse"
        assert trace[0] == 1
        assert times[edges[0]] == pytest.approx(-29.8e-9, abs=0.5e-9)
        assert times[edges[1]] == pytest.approx(16.3e-9, abs=1.5e-9)


def test_tektronix_digital_bit_order_puts_d0_in_the_least_significant_bit():
    """Line order follows bit order, d0 first."""
    packed = bytes([0b00000001, 0b10000000, 0b00000000])
    lines = RigolWFM.tek._unpack_digital_lines(packed, [f"d{bit}" for bit in range(8)])

    np.testing.assert_array_equal(lines["d0"], [1, 0, 0])
    np.testing.assert_array_equal(lines["d7"], [0, 1, 0])
