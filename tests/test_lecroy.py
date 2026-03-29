"""
Tests for the LeCroy .trc adapter (`RigolWFM.lecroy`) and `Wfm.from_file()`.

No real .trc files are shipped with this repository, so tests use synthetically
constructed LECROY_2_3 binary blobs that exercise the parser with known values.

WAVEDESC field layout (little-endian, total 346 bytes):
  offset  size  field
       0    16  descriptor_name ("WAVEDESC[NUL][NUL]...")
      16    16  template_name
      32     2  comm_type (u2)     0=byte, 1=word
      34     2  comm_order (u2)    0=BE, 1=LE
      36     4  wave_descriptor (s4)  = 346
      40     4  user_text_len (s4)
      44     4  res_desc1 (s4)
      48     4  trigtime_array_len (s4)
      52     4  ris_time_array_len (s4)
      56     4  res_array1 (s4)
      60     4  wave_array_1_len (s4)  bytes of sample data
      64     4  wave_array_2_len (s4)
      68     4  res_array2 (s4)
      72     4  res_array3 (s4)
      76    16  instrument_name
      92     4  instrument_number (s4)
      96    16  trace_label
     112     2  reserved1 (s2)
     114     2  reserved2 (s2)
     116     4  wave_array_count (s4)
     120     4  pnts_per_screen (s4)
     124     4  first_valid_pnt (s4)
     128     4  last_valid_pnt (s4)
     132     4  first_point (s4)
     136     4  sparsing_factor (s4)
     140     4  segment_index (s4)
     144     4  subarray_count (s4)
     148     4  sweeps_per_acq (s4)
     152     2  points_per_pair (s2)
     154     2  pair_offset (s2)
     156     4  vertical_gain (f4)
     160     4  vertical_offset (f4)
     164     4  max_value (f4)
     168     4  min_value (f4)
     172     2  nominal_bits (s2)
     174     2  nom_subarray_count (s2)
     176     4  horiz_interval (f4)
     180     8  horiz_offset (f8)
     188     8  pixel_offset (f8)
     196    48  vert_unit
     244    48  hor_unit
     292     4  horiz_uncertainty (f4)
     296    16  trigger_time (f8 + u1 u1 u1 u1 s2 s2)
     312     4  acq_duration (f4)
     316     2  record_type (u2)
     318     2  processing_done (u2)
     320     2  reserved5 (s2)
     322     2  ris_sweeps (s2)
     324     2  timebase (u2)
     326     2  vert_coupling (u2)
     328     4  probe_att (f4)
     332     2  fixed_vert_gain (u2)
     334     2  bandwidth_limit (u2)
     336     4  vertical_vernier (f4)
     340     4  acq_vert_offset (f4)
     344     2  wave_source (u2)  0=CH1, 1=CH2, ...
"""
# pylint: disable=unsubscriptable-object  # numpy NDArray subscripting triggers false positives

import struct
from pathlib import Path

import numpy as np
import pytest

import RigolWFM.lecroy
import RigolWFM.wfm

_WAVEDESC_SIZE = 346


def _build_trc(
    *,
    n_pts: int = 100,
    vertical_gain: float = 0.01,
    vertical_offset: float = 0.0,
    horiz_interval: float = 1e-6,
    horiz_offset: float = -50e-6,
    wave_source: int = 0,
    comm_type: int = 0,   # 0=byte (int8), 1=word (int16)
    comm_order: int = 1,  # 1=LOFIRST (little-endian)
    instrument_name: str = "WAVERUNNER",
    samples: list | None = None,
) -> bytes:
    """Build a minimal LECROY_2_3 .trc file as bytes.

    Returns a valid binary blob that the `lecroy_trc` KSY parser can read.
    """
    if samples is None:
        samples = list(range(n_pts))

    if comm_type == 0:
        sample_bytes = bytes([s & 0xFF for s in samples])
        wave_array_1_len = n_pts
    else:
        wave_array_1_len = n_pts * 2
        bo = "<" if comm_order == 1 else ">"
        sample_bytes = struct.pack(f"{bo}{n_pts}h", *samples)

    inst_bytes = instrument_name.encode("ascii")[:15].ljust(16, b"\x00")

    wavedesc = bytearray(346)
    # descriptor_name at 0
    wavedesc[0:16] = b"WAVEDESC\x00\x00\x00\x00\x00\x00\x00\x00"
    # template_name at 16
    wavedesc[16:32] = b"LECROY_2_3\x00\x00\x00\x00\x00\x00"

    b = "<" if comm_order == 1 else ">"

    def pack_into(fmt, offset, *values):
        struct.pack_into(b + fmt[1:], wavedesc, offset, *values)

    pack_into("<H", 32, comm_type)   # comm_type and comm_order are always written
    pack_into("<H", 34, comm_order)  # with native-neutral single-byte clarity
    pack_into("<i", 36, _WAVEDESC_SIZE)
    pack_into("<i", 40, 0)   # user_text_len
    pack_into("<i", 44, 0)   # res_desc1
    pack_into("<i", 48, 0)   # trigtime_array_len
    pack_into("<i", 52, 0)   # ris_time_array_len
    pack_into("<i", 56, 0)   # res_array1
    pack_into("<i", 60, wave_array_1_len)
    pack_into("<i", 64, 0)   # wave_array_2_len
    pack_into("<i", 68, 0)   # res_array2
    pack_into("<i", 72, 0)   # res_array3
    wavedesc[76:92] = inst_bytes
    pack_into("<i", 92, 1)   # instrument_number
    # trace_label at 96
    wavedesc[96:112] = b"CH1\x00" + b"\x00" * 12
    pack_into("<h", 112, 0)  # reserved1
    pack_into("<h", 114, 0)  # reserved2
    pack_into("<i", 116, n_pts)           # wave_array_count
    pack_into("<i", 120, n_pts)           # pnts_per_screen
    pack_into("<i", 124, 0)              # first_valid_pnt
    pack_into("<i", 128, n_pts - 1)      # last_valid_pnt
    pack_into("<i", 132, 0)              # first_point
    pack_into("<i", 136, 1)              # sparsing_factor
    pack_into("<i", 140, 0)              # segment_index
    pack_into("<i", 144, 1)              # subarray_count
    pack_into("<i", 148, 1)              # sweeps_per_acq
    pack_into("<h", 152, 0)              # points_per_pair
    pack_into("<h", 154, 0)              # pair_offset
    pack_into("<f", 156, vertical_gain)
    pack_into("<f", 160, vertical_offset)
    pack_into("<f", 164, 1.27)           # max_value
    pack_into("<f", 168, -1.28)          # min_value
    pack_into("<h", 172, 8)              # nominal_bits
    pack_into("<h", 174, 1)              # nom_subarray_count
    pack_into("<f", 176, horiz_interval)
    pack_into("<d", 180, horiz_offset)
    pack_into("<d", 188, 0.0)            # pixel_offset
    wavedesc[196:244] = b"V\x00" + b"\x00" * 46   # vert_unit
    wavedesc[244:292] = b"s\x00" + b"\x00" * 46   # hor_unit
    pack_into("<f", 292, 0.0)            # horiz_uncertainty
    # trigger_time at 296: seconds(f8) min(u1) hr(u1) day(u1) month(u1) year(s2) unused(s2)
    pack_into("<d", 296, 0.0)
    pack_into("<B", 304, 0)
    pack_into("<B", 305, 0)
    pack_into("<B", 306, 1)
    pack_into("<B", 307, 1)
    pack_into("<h", 308, 2024)
    pack_into("<h", 310, 0)
    pack_into("<f", 312, 0.0)            # acq_duration
    pack_into("<H", 316, 0)              # record_type (single_sweep)
    pack_into("<H", 318, 0)              # processing_done (no_processing)
    pack_into("<h", 320, 0)              # reserved5
    pack_into("<h", 322, 1)              # ris_sweeps
    pack_into("<H", 324, 9)              # timebase (index 9 → 10 ms/div)
    pack_into("<H", 326, 2)              # vert_coupling (dc_1m_ohm → "DC")
    pack_into("<f", 328, 1.0)            # probe_att
    pack_into("<H", 332, 9)              # fixed_vert_gain
    pack_into("<H", 334, 0)              # bandwidth_limit (bw_full)
    pack_into("<f", 336, 1.0)            # vertical_vernier
    pack_into("<f", 340, 0.0)            # acq_vert_offset
    pack_into("<H", 344, wave_source)

    return bytes(wavedesc) + sample_bytes


# ---------------------------------------------------------------------------
# Low-level adapter tests (RigolWFM.lecroy.from_file)
# ---------------------------------------------------------------------------

def test_from_file_8bit(tmp_path):
    """8-bit LE .trc file: from_file() should return a LeCroyWaveform."""
    n_pts = 50
    samples = list(range(-25, 25))
    trc = _build_trc(n_pts=n_pts, samples=samples)
    p = tmp_path / "test.trc"
    p.write_bytes(trc)

    obj = RigolWFM.lecroy.from_file(str(p))
    assert obj is not None
    assert obj.header is not None


def test_from_file_8bit_sample_count(tmp_path):
    """8-bit LE .trc: header should reflect declared n_pts."""
    n_pts = 64
    trc = _build_trc(n_pts=n_pts, samples=list(range(n_pts)))
    p = tmp_path / "test.trc"
    p.write_bytes(trc)

    obj = RigolWFM.lecroy.from_file(str(p))
    assert obj.header.n_pts == n_pts


def test_from_file_8bit_channel_enabled(tmp_path):
    """8-bit LE .trc: CH1 slot (index 0) should be enabled."""
    trc = _build_trc(n_pts=10, samples=[0] * 10, wave_source=0)
    p = tmp_path / "test.trc"
    p.write_bytes(trc)

    obj = RigolWFM.lecroy.from_file(str(p))
    assert obj.header.ch[0].enabled
    for i in range(1, 4):
        assert not obj.header.ch[i].enabled


def test_from_file_8bit_voltage_formula(tmp_path):
    """volts[i] = vertical_gain * adc[i] - vertical_offset (8-bit)."""
    n_pts = 4
    gain = 0.01
    offset = 0.5
    adc = [10, 20, -10, -20]
    expected = [gain * a - offset for a in adc]

    trc = _build_trc(n_pts=n_pts, vertical_gain=gain, vertical_offset=offset, samples=adc)
    p = tmp_path / "test.trc"
    p.write_bytes(trc)

    obj = RigolWFM.lecroy.from_file(str(p))
    volts = obj.header.channel_data[0]
    assert isinstance(volts, np.ndarray)
    for i, exp in enumerate(expected):
        assert volts[i] == pytest.approx(exp, abs=1e-5)


def test_from_file_8bit_time_axis(tmp_path):
    """Time axis: t[i] = horiz_offset + i * horiz_interval."""
    n_pts = 5
    h_interval = 1e-6
    h_offset = -2e-6
    trc = _build_trc(n_pts=n_pts, horiz_interval=h_interval, horiz_offset=h_offset)
    p = tmp_path / "test.trc"
    p.write_bytes(trc)

    obj = RigolWFM.lecroy.from_file(str(p))
    assert obj.header.x_origin == pytest.approx(h_offset, abs=1e-12)
    assert obj.header.x_increment == pytest.approx(h_interval, abs=1e-14)


def test_from_file_instrument_name(tmp_path):
    """Instrument name from WAVEDESC should appear in header.model_number."""
    trc = _build_trc(n_pts=10, instrument_name="WAVEPRO")
    p = tmp_path / "test.trc"
    p.write_bytes(trc)

    obj = RigolWFM.lecroy.from_file(str(p))
    assert "WAVEPRO" in obj.header.model_number


def test_from_file_parser_name(tmp_path):
    """parser_name should be 'lecroy_trc'."""
    trc = _build_trc(n_pts=10)
    p = tmp_path / "test.trc"
    p.write_bytes(trc)

    obj = RigolWFM.lecroy.from_file(str(p))
    assert obj.parser_name == "lecroy_trc"


def test_from_file_16bit(tmp_path):
    """16-bit LE .trc: voltages should use the same formula with s16 ADC values."""
    n_pts = 4
    gain = 1e-4
    offset = 0.0
    adc = [1000, -1000, 500, -500]
    expected = [gain * a - offset for a in adc]

    trc = _build_trc(
        n_pts=n_pts,
        vertical_gain=gain,
        vertical_offset=offset,
        samples=adc,
        comm_type=1,
    )
    p = tmp_path / "test16.trc"
    p.write_bytes(trc)

    obj = RigolWFM.lecroy.from_file(str(p))
    volts = obj.header.channel_data[0]
    assert isinstance(volts, np.ndarray)
    for i, exp in enumerate(expected):
        assert volts[i] == pytest.approx(exp, abs=1e-5)


def test_from_file_ch2_slot(tmp_path):
    """wave_source=1 should populate slot 1 (CH2), not slot 0."""
    trc = _build_trc(n_pts=10, wave_source=1)
    p = tmp_path / "test_ch2.trc"
    p.write_bytes(trc)

    obj = RigolWFM.lecroy.from_file(str(p))
    assert not obj.header.ch[0].enabled
    assert obj.header.ch[1].enabled
    assert obj.header.channel_data[1] is not None
    assert obj.header.channel_data[0] is None


def test_from_file_seconds_per_point(tmp_path):
    """seconds_per_point property should equal horiz_interval."""
    h_interval = 2e-8
    trc = _build_trc(n_pts=10, horiz_interval=h_interval)
    p = tmp_path / "test.trc"
    p.write_bytes(trc)

    obj = RigolWFM.lecroy.from_file(str(p))
    assert obj.header.seconds_per_point == pytest.approx(h_interval, rel=1e-5)


# ---------------------------------------------------------------------------
# Integration: Wfm.from_file() round-trip
# ---------------------------------------------------------------------------

def test_wfm_from_file_lecroy(tmp_path):
    """Wfm.from_file() with model='LeCroy' should return a valid Wfm object."""
    n_pts = 20
    trc = _build_trc(n_pts=n_pts, samples=list(range(n_pts)))
    p = tmp_path / "test.trc"
    p.write_bytes(trc)

    w = RigolWFM.wfm.Wfm.from_file(str(p), "LeCroy", "1")
    assert len(w.channels) == 1
    ch = w.channels[0]
    assert ch.volts is not None
    assert ch.times is not None
    assert len(ch.volts) == n_pts
    assert len(ch.times) == n_pts


def test_wfm_from_file_lecroy_voltage_values(tmp_path):
    """Wfm.from_file(): channel.volts should match vertical_gain*adc-offset."""
    gain = 0.02
    offset = 1.0
    adc = [0, 10, -10, 50]
    expected = [gain * a - offset for a in adc]

    trc = _build_trc(n_pts=len(adc), vertical_gain=gain, vertical_offset=offset, samples=adc)
    p = tmp_path / "test.trc"
    p.write_bytes(trc)

    w = RigolWFM.wfm.Wfm.from_file(str(p), "LeCroy", "1")
    ch = w.channels[0]
    for i, exp in enumerate(expected):
        assert float(ch.volts[i]) == pytest.approx(exp, abs=1e-4)


def test_wfm_from_file_lecroy_time_values(tmp_path):
    """Wfm.from_file(): channel.times should match t[i]=horiz_offset+i*horiz_interval."""
    n_pts = 5
    h_interval = 1e-7
    h_offset = -2e-7

    trc = _build_trc(n_pts=n_pts, horiz_interval=h_interval, horiz_offset=h_offset)
    p = tmp_path / "test.trc"
    p.write_bytes(trc)

    w = RigolWFM.wfm.Wfm.from_file(str(p), "LeCroy", "1")
    ch = w.channels[0]
    for i in range(n_pts):
        expected_t = h_offset + i * h_interval
        assert float(ch.times[i]) == pytest.approx(expected_t, abs=1e-14)


def test_wfm_from_file_lecroy_header_name(tmp_path):
    """Wfm.from_file() header_name should include the instrument name."""
    trc = _build_trc(n_pts=10, instrument_name="WAVERUNNER")
    p = tmp_path / "test.trc"
    p.write_bytes(trc)

    w = RigolWFM.wfm.Wfm.from_file(str(p), "LeCroy", "1")
    assert "WAVERUNNER" in w.header_name


def test_wfm_autodetect_lecroy(tmp_path):
    """detect_model() should identify WAVEDESC-headed files as 'LeCroy'."""
    trc = _build_trc(n_pts=10)
    p = tmp_path / "test.trc"
    p.write_bytes(trc)

    detected = RigolWFM.wfm.detect_model(str(p))
    assert detected == "LeCroy"


def test_wfm_from_file_lecroy_auto(tmp_path):
    """Wfm.from_file() with model='auto' should handle LeCroy files."""
    trc = _build_trc(n_pts=10)
    p = tmp_path / "test.trc"
    p.write_bytes(trc)

    w = RigolWFM.wfm.Wfm.from_file(str(p), "auto", "1")
    assert len(w.channels) == 1


# ---------------------------------------------------------------------------
# Big-endian variant tests
# ---------------------------------------------------------------------------

def test_from_file_big_endian_voltage(tmp_path):
    """Big-endian 8-bit .trc: voltage formula should match regardless of byte order."""
    gain = 0.01
    offset = 0.5
    adc = [10, 20, -10]
    expected = [gain * a - offset for a in adc]

    trc = _build_trc(
        n_pts=len(adc),
        vertical_gain=gain,
        vertical_offset=offset,
        samples=adc,
        comm_order=0,  # big-endian
    )
    p = tmp_path / "test_be.trc"
    p.write_bytes(trc)

    obj = RigolWFM.lecroy.from_file(str(p))
    volts = obj.header.channel_data[0]
    assert isinstance(volts, np.ndarray)
    for i, exp in enumerate(expected):
        assert volts[i] == pytest.approx(exp, abs=1e-5)


def test_from_file_big_endian_16bit(tmp_path):
    """Big-endian 16-bit .trc: voltage formula and byte order should be correct."""
    gain = 1e-4
    offset = 0.0
    adc = [1000, -1000, 500]
    expected = [gain * a - offset for a in adc]

    trc = _build_trc(
        n_pts=len(adc),
        vertical_gain=gain,
        vertical_offset=offset,
        samples=adc,
        comm_type=1,
        comm_order=0,  # big-endian
    )
    p = tmp_path / "test_be16.trc"
    p.write_bytes(trc)

    obj = RigolWFM.lecroy.from_file(str(p))
    volts = obj.header.channel_data[0]
    assert isinstance(volts, np.ndarray)
    for i, exp in enumerate(expected):
        assert volts[i] == pytest.approx(exp, abs=1e-5)


def test_wfm_from_file_big_endian(tmp_path):
    """Wfm.from_file() should handle big-endian LeCroy files."""
    n_pts = 20
    trc = _build_trc(n_pts=n_pts, samples=list(range(n_pts)), comm_order=0)
    p = tmp_path / "test_be.trc"
    p.write_bytes(trc)

    w = RigolWFM.wfm.Wfm.from_file(str(p), "LeCroy", "1")
    assert len(w.channels) == 1
    ch = w.channels[0]
    assert ch.volts is not None
    assert ch.times is not None
    assert len(ch.volts) == n_pts


# ---------------------------------------------------------------------------
# SCPI prefix: files with a "#N<digits>" header before WAVEDESC
# ---------------------------------------------------------------------------

def _add_scpi_prefix(trc_bytes: bytes) -> bytes:
    """Wrap trc_bytes in an IEEE 488.2 block-data prefix (#9<9-digit count>)."""
    count = len(trc_bytes)
    prefix = f"#9{count:09d}".encode("ascii")
    return prefix + trc_bytes


def test_scpi_prefix_parsed(tmp_path):
    """from_file() should strip the SCPI '#N<digits>' prefix before parsing."""
    trc = _build_trc(n_pts=10, vertical_gain=0.01, vertical_offset=0.0, samples=list(range(10)))
    p = tmp_path / "scpi.trc"
    p.write_bytes(_add_scpi_prefix(trc))

    obj = RigolWFM.lecroy.from_file(str(p))
    assert obj.header.n_pts == 10


def test_scpi_prefix_voltage(tmp_path):
    """Voltage values should be correct when a SCPI prefix is present."""
    gain, offset = 0.01, 0.5
    adc = [10, -10, 0]
    trc = _build_trc(n_pts=len(adc), vertical_gain=gain, vertical_offset=offset, samples=adc)
    p = tmp_path / "scpi_v.trc"
    p.write_bytes(_add_scpi_prefix(trc))

    obj = RigolWFM.lecroy.from_file(str(p))
    volts = obj.header.channel_data[0]
    assert isinstance(volts, np.ndarray)
    expected = [gain * a - offset for a in adc]
    for i, exp in enumerate(expected):
        assert volts[i] == pytest.approx(exp, abs=1e-5)


def test_scpi_prefix_autodetect(tmp_path):
    """detect_model() should identify SCPI-prefixed LeCroy files as 'LeCroy'."""
    trc = _build_trc(n_pts=10)
    p = tmp_path / "scpi_detect.trc"
    p.write_bytes(_add_scpi_prefix(trc))

    assert RigolWFM.wfm.detect_model(str(p)) == "LeCroy"


# ---------------------------------------------------------------------------
# LECROY_1_0 format (320-byte WAVEDESC)
# ---------------------------------------------------------------------------

_TRC_DIR = Path(__file__).parent / "files" / "trc"
_TRACE1_000 = _TRC_DIR / "trace1.000"
_LECROY2_TRC = _TRC_DIR / "lecroy_2.trc"


@pytest.mark.skipif(not _TRACE1_000.exists(), reason="tests/files/trc/trace1.000 not present")
def test_lecroy_1_0_parses():
    """LECROY_1_0 files should parse without error."""
    obj = RigolWFM.lecroy.from_file(str(_TRACE1_000))
    assert obj.header.n_pts > 0
    assert obj.header.channel_data[0] is not None


@pytest.mark.skipif(not _TRACE1_000.exists(), reason="tests/files/trc/trace1.000 not present")
def test_lecroy_1_0_instrument_name():
    """LECROY_1_0: instrument name should be decoded correctly."""
    obj = RigolWFM.lecroy.from_file(str(_TRACE1_000))
    assert "LeCroy" in obj.header.model or "7200" in obj.header.model


@pytest.mark.skipif(not _TRACE1_000.exists(), reason="tests/files/trc/trace1.000 not present")
def test_lecroy_1_0_voltage_range():
    """LECROY_1_0: voltage values should be physically plausible (not raw ADC counts)."""
    obj = RigolWFM.lecroy.from_file(str(_TRACE1_000))
    volts = obj.header.channel_data[0]
    # trace1.000 is from a 7200 DSO; voltage should be in a small range (not thousands of counts)
    assert abs(volts.max()) < 100
    assert abs(volts.min()) < 100


@pytest.mark.skipif(not _TRACE1_000.exists(), reason="tests/files/trc/trace1.000 not present")
def test_lecroy_1_0_time_axis():
    """LECROY_1_0: time axis increment should be positive and non-zero."""
    obj = RigolWFM.lecroy.from_file(str(_TRACE1_000))
    assert obj.header.x_increment > 0
    assert obj.header.n_pts > 1


@pytest.mark.skipif(not _TRACE1_000.exists(), reason="tests/files/trc/trace1.000 not present")
def test_lecroy_1_0_autodetect():
    """detect_model() should identify LECROY_1_0 files as 'LeCroy'."""
    assert RigolWFM.wfm.detect_model(str(_TRACE1_000)) == "LeCroy"


# ---------------------------------------------------------------------------
# LECROY_2_3 with SCPI prefix (real files)
# ---------------------------------------------------------------------------

@pytest.mark.skipif(not _LECROY2_TRC.exists(), reason="tests/files/trc/lecroy_2.trc not present")
def test_lecroy_2_3_scpi_parses():
    """LECROY_2_3 files with SCPI prefix should parse without error."""
    obj = RigolWFM.lecroy.from_file(str(_LECROY2_TRC))
    assert obj.header.n_pts > 0


@pytest.mark.skipif(not _LECROY2_TRC.exists(), reason="tests/files/trc/lecroy_2.trc not present")
def test_lecroy_2_3_scpi_voltage_range():
    """LECROY_2_3 with SCPI prefix: voltages should be physically plausible."""
    obj = RigolWFM.lecroy.from_file(str(_LECROY2_TRC))
    slot = next(i for i, c in enumerate(obj.header.ch) if c.enabled)
    volts = obj.header.channel_data[slot]
    assert abs(volts.max()) < 1000
    assert abs(volts.min()) < 1000


@pytest.mark.skipif(not _LECROY2_TRC.exists(), reason="tests/files/trc/lecroy_2.trc not present")
def test_lecroy_2_3_scpi_autodetect():
    """detect_model() should identify SCPI-prefixed LECROY_2_3 files as 'LeCroy'."""
    assert RigolWFM.wfm.detect_model(str(_LECROY2_TRC)) == "LeCroy"
