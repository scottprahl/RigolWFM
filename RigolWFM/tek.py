"""
Adapter layer for Tektronix oscilloscope waveform files (.wfm).

Normalises the parsed KSY data into the header/data shape expected by
`RigolWFM.wfm.Wfm` and `RigolWFM.channel`.

Two format versions are supported:

  WFM#001 (TDS6000/B/C, TDS/CSA7000/B):
    ksy/tektronix_wfm_001_le_wfm.ksy → RigolWFM/tektronix_wfm_001_le_wfm.py   (LE)
    ksy/tektronix_wfm_001_be_wfm.ksy → RigolWFM/tektronix_wfm_001_be_wfm.py   (BE)

  WFM#002/003 (TDS5000B, DPO7000, DPO70000, DSA70000):
    ksy/tektronix_wfm_002_le_wfm.ksy → RigolWFM/tektronix_wfm_002_le_wfm.py   (LE)
    ksy/tektronix_wfm_002_be_wfm.ksy → RigolWFM/tektronix_wfm_002_be_wfm.py   (BE)

Endianness detection
--------------------
byte_order at offset 0 of the file is 0x0F0F for little-endian (Intel) and
0xF0F0 for big-endian (PPC).

Version detection
-----------------
version_number at offset 2 is "WFM#001", "WFM#002", or "WFM#003".

Voltage calibration
-------------------
  volts[i] = exp_dim1.dim_scale * adc[i] + exp_dim1.dim_offset

Time axis
---------
  t[i] = imp_dim1.dim_offset + i * imp_dim1.dim_scale

where ``i = 0`` is the first *valid* sample.  A curve buffer may open with a
precharge region, which ``curve.data_start_offset`` skips; ``dim_offset`` is
already measured from the first valid sample, not from the buffer start.
"""

import io as _io
import struct as _struct
from typing import Any, Optional

import numpy as np
import numpy.typing as npt
from kaitaistruct import KaitaiStream  # type: ignore[import]

import RigolWFM.channel
import RigolWFM.tektronix_wfm_001_be_wfm
import RigolWFM.tektronix_wfm_001_le_wfm
import RigolWFM.tektronix_wfm_002_be_wfm
import RigolWFM.tektronix_wfm_002_le_wfm

_TekWfm001Le: Any = RigolWFM.tektronix_wfm_001_le_wfm.TektronixWfm001LeWfm  # type: ignore[attr-defined]
_TekWfm001Be: Any = RigolWFM.tektronix_wfm_001_be_wfm.TektronixWfm001BeWfm  # type: ignore[attr-defined]
_TekWfm002Le: Any = RigolWFM.tektronix_wfm_002_le_wfm.TektronixWfm002LeWfm  # type: ignore[attr-defined]
_TekWfm002Be: Any = RigolWFM.tektronix_wfm_002_be_wfm.TektronixWfm002BeWfm  # type: ignore[attr-defined]

_TEK_MAGIC = b"WFM#"
_LLWFM_MAGIC = b"LLWFM"

# Explicit-dimension format codes → numpy dtype
_FORMAT_DTYPE: dict[int, str] = {
    0: "i2",  # EXPLICIT_INT16
    1: "i4",  # EXPLICIT_INT32
    2: "u4",  # EXPLICIT_UINT32
    3: "u8",  # EXPLICIT_UINT64
    4: "f4",  # EXPLICIT_FP32
    5: "f8",  # EXPLICIT_FP64
    6: "u1",  # EXPLICIT_UINT8  (WFM#003)
    7: "i1",  # EXPLICIT_INT8   (WFM#003)
}


class ChannelHeader:
    """Normalized per-channel metadata for a Tektronix .wfm capture."""

    name: str
    enabled: bool
    volt_per_division: float
    volt_offset: float
    volt_scale: float
    probe_value: float
    inverted: bool
    coupling: str

    def __init__(self, name: str, enabled: bool) -> None:
        """Initialize channel metadata with safe defaults."""
        self.name = name
        self.enabled = enabled
        self.volt_per_division = 1.0
        self.volt_offset = 0.0
        self.volt_scale = 1.0
        self.probe_value = 1.0
        self.inverted = False
        self.coupling = "DC"

    @property
    def unit(self) -> RigolWFM.channel.UnitEnum:
        """Return the unit enum for volts."""
        return RigolWFM.channel.UnitEnum.v

    @property
    def y_scale(self) -> float:
        """Tektronix voltage data is already calibrated; no additional scaling."""
        return 1.0

    @property
    def y_offset(self) -> float:
        """Tektronix voltage data is already calibrated; no additional offset."""
        return 0.0


class Header:
    """Normalized header used by `Wfm.from_file()` for Tektronix .wfm captures."""

    model: str
    trace_label: str
    n_pts: int
    x_origin: float
    x_increment: float
    ch: list[ChannelHeader]
    raw_data: list[Optional[npt.NDArray]]
    channel_data: list[Optional[npt.NDArray[np.float32]]]
    frame_count: int
    frame_index: int
    frame_trigger_seconds: int
    frame_trigger_fraction: float
    frame_trigger_offset: float

    def __init__(self) -> None:
        """Initialize an empty Tektronix header."""
        self.model = ""
        self.trace_label = ""
        self.n_pts = 0
        self.x_origin = 0.0
        self.x_increment = 1e-6
        self.frame_count = 1
        self.frame_index = 0
        self.frame_trigger_seconds = 0
        self.frame_trigger_fraction = 0.0
        self.frame_trigger_offset = 0.0
        self.ch = [ChannelHeader(f"CH{i + 1}", enabled=False) for i in range(4)]
        self.raw_data = [None] * 4
        self.channel_data = [None] * 4

    @property
    def seconds_per_point(self) -> float:
        """Time between samples in seconds."""
        return self.x_increment

    @property
    def time_scale(self) -> float:
        """Time per division (10 divisions per screen)."""
        if self.n_pts > 0 and self.x_increment > 0:
            return self.n_pts * self.x_increment / 10.0
        return 1e-3

    @property
    def points(self) -> int:
        """Number of valid sample points."""
        return self.n_pts

    @property
    def firmware_version(self) -> str:
        """Tektronix .wfm files do not embed firmware information."""
        return "unknown"

    @property
    def model_number(self) -> str:
        """Oscilloscope instrument label from the waveform label field."""
        return self.model


class TekWaveform:
    """Normalized Tektronix parser result consumed by `Channel`."""

    header: Header
    logic_channels: dict[str, npt.NDArray[np.uint8]]
    logic_x_increment: Optional[float]
    logic_x_origin: Optional[float]
    tekmeta: dict[str, Any]

    def __init__(self) -> None:
        """Initialize the normalized Tektronix wrapper."""
        self.header = Header()
        self.logic_channels = {}
        self.logic_x_increment = None
        self.logic_x_origin = None
        self.tekmeta = {}

    @property
    def parser_name(self) -> str:
        """Return the normalized parser name used by `Wfm.from_file()`."""
        return "tek_wfm"

    def __str__(self) -> str:
        """Return a parser tag compatible with the rest of `Wfm.from_file()`."""
        return f"x.{self.parser_name}"


def _read_file_bytes(file_name: str) -> bytes:
    """Read file contents, raising ValueError on OS errors."""
    try:
        with open(file_name, "rb") as f:
            return f.read()
    except OSError as exc:
        raise ValueError(f"Cannot open Tektronix file '{file_name}': {exc}") from exc


def _decode_adc(raw_bytes: bytes, fmt_code: int, byte_order: str, n_pts: int) -> npt.NDArray:
    """Decode curve buffer bytes into a signed/float ADC array.

    Args:
        raw_bytes: raw bytes from the curve buffer.
        fmt_code:  EXPLICIT_* format enum value from exp_dim1.format.
        byte_order: '<' for little-endian, '>' for big-endian.
        n_pts:     number of valid samples to extract.

    Returns:
        1-D numpy array of ADC values.
    """
    base_dtype = _FORMAT_DTYPE.get(fmt_code, "i2")
    dtype = np.dtype(f"{byte_order}{base_dtype}")
    arr = np.frombuffer(raw_bytes, dtype=dtype)
    if len(arr) > n_pts > 0:
        arr = arr[:n_pts]
    return arr


def _parse_legacy_llwfm(data: bytes, file_name: str) -> TekWaveform:
    """Parse the older big-endian Tektronix ``LLWFM`` layout."""
    start = data[:8].find(_LLWFM_MAGIC)
    if start < 0:
        raise ValueError(f"File '{file_name}' does not start with a supported LLWFM header")
    offset = start + len(_LLWFM_MAGIC)
    if offset < len(data) and data[offset : offset + 1] == b"#":
        offset += 1

    def read(fmt: str) -> Any:
        nonlocal offset
        size = _struct.calcsize(fmt)
        if offset + size > len(data):
            raise ValueError(f"Legacy Tektronix file '{file_name}' is truncated")
        values = _struct.unpack_from(fmt, data, offset)
        offset += size
        return values[0] if len(values) == 1 else values

    if offset >= len(data):
        raise ValueError(f"Legacy Tektronix file '{file_name}' is truncated before byte-count metadata")
    count_len_char = chr(data[offset])
    offset += 1
    if not count_len_char.isdigit():
        raise ValueError(f"Legacy Tektronix file '{file_name}' has invalid byte-count length")
    count_len = int(count_len_char)
    if offset + count_len > len(data):
        raise ValueError(f"Legacy Tektronix file '{file_name}' is truncated in byte-count metadata")
    offset += count_len

    _magic_num = read(">i")
    length = int(read(">i"))

    # Reference header (display state only)
    _vert_pos_ref = read(">d")
    _horz_pos_ref = read(">d")
    _vert_zoom = read(">d")
    _horz_zoom = read(">d")

    # Waveform header
    _acq_mode = read(">h")
    _min_max_format = read(">h")
    _duration = read(">d")
    vert_coupling = int(read(">h"))
    _horz_unit = read(">h")
    horz_scale = float(read(">d"))
    _vert_unit = read(">h")
    vert_offset = float(read(">d"))
    vert_pos = float(read(">d"))
    vert_gain = float(read(">d"))
    record_length = int(read(">I"))
    trig_pos = float(read(">h"))
    _wfm_header_version = read(">h")
    _sample_density = read(">h")
    _burst_segment_length = read(">h")
    _source_wfm = read(">h")
    _video_header1 = read(">3h")
    _video_header2 = read(">d")
    _video_header3 = read(">h")

    extended_header_len = length - 2 * record_length - 64
    if extended_header_len == 196:
        raise ValueError(f"Legacy Tektronix extended headers are not yet supported: '{file_name}'")

    preamble_bytes = 16 * 2
    curve_bytes = record_length * 2
    postamble_bytes = 16 * 2
    checksum_bytes = 2
    if offset + preamble_bytes + curve_bytes + postamble_bytes + checksum_bytes > len(data):
        raise ValueError(f"Legacy Tektronix file '{file_name}' is truncated in the curve buffer")

    offset += preamble_bytes
    adc = np.frombuffer(data[offset : offset + curve_bytes], dtype=">i2").astype(np.int16)

    volts = (adc.astype(np.float64) * (vert_gain / (25.0 * 256.0)) + vert_offset - vert_pos * vert_gain).astype(
        np.float32
    )

    obj = TekWaveform()
    h = obj.header
    h.model = "Tektronix"
    h.n_pts = len(volts)
    h.x_origin = -(record_length * trig_pos / 100.0) * horz_scale
    h.x_increment = horz_scale

    ch = h.ch[0]
    ch.name = "CH1"
    ch.enabled = True
    ch.coupling = {565: "DC", 566: "AC"}.get(vert_coupling, "DC")
    ch.probe_value = 1.0
    ch.volt_per_division = abs(vert_gain) if vert_gain != 0 else 1.0
    ch.volt_scale = vert_gain / (25.0 * 256.0)
    ch.volt_offset = vert_offset - vert_pos * vert_gain

    h.channel_data[0] = volts
    h.raw_data[0] = (adc.view(np.uint16) >> 8).astype(np.uint8)

    return obj


_TEKMETA_MAGIC = b"tekmeta!"

# tekmeta values are tagged by a single byte: 1 is a length-prefixed string and
# the rest are fixed-width numbers.
_TEKMETA_NUMERIC = {2: ("i", 4), 3: ("d", 8), 4: ("I", 4)}

_DIGITAL_DATA_TYPE = 6
_DIGITAL_LINES = 8

# An IQ capture is only distinguishable by the acquisition parameters it records
# in the tekmeta block; nothing in the fixed header marks it.
_IQ_META_KEYS = (
    "IQ_centerFrequency",
    "IQ_fftLength",
    "IQ_rbw",
    "IQ_span",
    "IQ_windowType",
    "IQ_sampleRate",
)


def _parse_tekmeta(data: bytes, byte_order: str) -> dict[str, Any]:
    """Read the `tekmeta!` key/value block that Tektronix appends after the curve.

    The block is optional and its absence is not an error, so any malformed or
    truncated block yields an empty mapping rather than raising: it is metadata,
    and the waveform itself is still perfectly readable without it.

    Args:
        data: the whole file.
        byte_order: ``"<"`` or ``">"``, matching the file's byte-order marker.

    Returns:
        The decoded key/value pairs, empty when there is no readable block.
    """
    start = data.find(_TEKMETA_MAGIC)
    if start < 0:
        return {}

    meta: dict[str, Any] = {}
    offset = start + len(_TEKMETA_MAGIC)
    try:
        (count,) = _struct.unpack_from(f"{byte_order}I", data, offset)
        offset += 4
        for _ in range(count):
            (key_size,) = _struct.unpack_from(f"{byte_order}I", data, offset)
            offset += 4
            key = data[offset : offset + key_size].decode("utf-8", errors="replace")
            offset += key_size

            tag = data[offset]
            offset += 1
            if tag == 1:
                (value_size,) = _struct.unpack_from(f"{byte_order}I", data, offset)
                offset += 4
                value: Any = data[offset : offset + value_size].decode("utf-8", errors="replace")
                offset += value_size
            elif tag in _TEKMETA_NUMERIC:
                code, width = _TEKMETA_NUMERIC[tag]
                (value,) = _struct.unpack_from(f"{byte_order}{code}", data, offset)
                offset += width
            else:  # an unknown tag makes every later entry unreadable
                break
            meta[key] = value
    except (_struct.error, IndexError, UnicodeDecodeError):
        return meta

    return meta


def _digital_line_names(meta: dict[str, Any]) -> list[str]:
    """Return the digital line names a capture declares, in bit order."""
    return [f"d{bit}" for bit in range(_DIGITAL_LINES) if f"d{bit}" in meta]


def _is_digital(data_type: int, meta: dict[str, Any]) -> bool:
    """Report whether a capture holds packed digital lines rather than volts."""
    return data_type == _DIGITAL_DATA_TYPE or bool(_digital_line_names(meta))


def _is_iq(meta: dict[str, Any]) -> bool:
    """Report whether a capture holds interleaved I/Q pairs rather than one trace."""
    return any(key in meta for key in _IQ_META_KEYS)


def _unpack_digital_lines(raw_bytes: bytes, names: list[str]) -> dict[str, npt.NDArray[np.uint8]]:
    """Split packed digital bytes into one 0/1 trace per line.

    Each byte holds one sample of every line, bit 0 being the first line.

    Args:
        raw_bytes: the valid region of the curve buffer.
        names: line names in bit order, as declared by the capture.

    Returns:
        A mapping of line name to its 0/1 samples.
    """
    packed = np.frombuffer(raw_bytes, dtype=np.uint8)
    return {name: ((packed >> bit) & 1).astype(np.uint8) for bit, name in enumerate(names)}


def _assign_trace(
    header: Header,
    slot: int,
    name: str,
    volts: npt.NDArray[np.float32],
    adc: npt.NDArray,
    bytes_per_point: int,
    volt_per_div: float,
    dim_scale: float,
    dim_offset: float,
) -> None:
    """Fill one normalized analog slot from calibrated volts and their codes.

    Args:
        header: the normalized header to populate.
        slot: zero-based channel slot.
        name: label for the trace, e.g. "CH1" or "I".
        volts: calibrated samples.
        adc: the raw codes those samples came from.
        bytes_per_point: width of a stored code, used for the raw proxy.
        volt_per_div: vertical scale to report.
        dim_scale: volts per code.
        dim_offset: volts at code zero.
    """
    channel = header.ch[slot]
    channel.name = name
    channel.enabled = True
    channel.coupling = "DC"
    channel.probe_value = 1.0
    channel.volt_per_division = volt_per_div
    channel.volt_scale = dim_scale
    channel.volt_offset = dim_offset

    header.channel_data[slot] = volts

    # raw_data: store as uint8 proxy (high byte for 16-bit, direct for 8-bit)
    if bytes_per_point == 2:
        header.raw_data[slot] = (adc.astype(np.int16).view(np.uint16) >> 8).astype(np.uint8)
    else:
        header.raw_data[slot] = np.full(len(volts), 127, dtype=np.uint8)


def _digital_waveform(
    raw_bytes: bytes,
    meta: dict[str, Any],
    model_str: str,
    trace_label: str,
    t_origin: float,
    t_scale: float,
) -> TekWaveform:
    """Build a logic-only waveform from a packed digital curve buffer.

    Digital captures carry no analog channel: every byte is a bit field of the
    logic lines, so the result exposes `logic_channels` and leaves the analog
    slots empty, the same shape the MSO5000 adapter uses.

    Args:
        raw_bytes: the valid region of the curve buffer.
        meta: the decoded `tekmeta!` block, which names the lines.
        model_str: instrument label for the normalized header.
        trace_label: waveform label recorded in the file.
        t_origin: time of the first valid sample.
        t_scale: seconds between samples.

    Returns:
        A `TekWaveform` whose logic traces hold one 0/1 array per line.
    """
    names = _digital_line_names(meta) or [f"d{bit}" for bit in range(_DIGITAL_LINES)]

    obj = TekWaveform()
    header = obj.header
    header.model = model_str
    header.trace_label = trace_label
    header.n_pts = len(raw_bytes)
    header.x_origin = t_origin
    header.x_increment = t_scale

    obj.tekmeta = meta
    obj.logic_channels = _unpack_digital_lines(raw_bytes, names)
    obj.logic_x_increment = t_scale
    obj.logic_x_origin = t_origin
    return obj


def from_file(file_name: str, frame: int = 0) -> TekWaveform:
    """Parse a Tektronix .wfm file and normalize it for `Wfm.from_file()`.

    Handles WFM#001, WFM#002, and WFM#003 formats in both little-endian
    and big-endian byte orders.

    A FastFrame capture stores many frames of one channel in a single file.
    They share every scale factor and differ only in their samples and their
    trigger timestamp, so one frame is returned at a time.

    Args:
        file_name: path to a Tektronix .wfm waveform file.
        frame: zero-based FastFrame index to return; 0 for an ordinary capture.

    Returns:
        A `TekWaveform` object whose `header` follows the shape expected
        by `RigolWFM.channel.Channel` and `RigolWFM.wfm.Wfm`.

    Raises:
        ValueError: if the file cannot be parsed as a valid Tektronix waveform.
    """
    data = _read_file_bytes(file_name)

    if _LLWFM_MAGIC in data[:8]:
        return _parse_legacy_llwfm(data, file_name)

    if len(data) < 16:
        raise ValueError(f"File '{file_name}' is too short to be a Tektronix WFM file")

    # Detect endianness from byte_order field at offset 0
    bo_raw = data[0] | (data[1] << 8)  # read as LE first to check
    if bo_raw == 0x0F0F:
        is_le = True
        byte_order = "<"
    elif data[0] == 0xF0 and data[1] == 0xF0:
        # Big-endian files: byte_order field reads as 0xF0F0 in BE
        is_le = False
        byte_order = ">"
    else:
        raise ValueError(f"File '{file_name}' has unrecognised byte_order field: " f"0x{data[0]:02X}{data[1]:02X}")

    # Detect version from version_number string at offset 3 (7 bytes)
    version_str = data[3:10].split(b"\x00")[0].decode("ascii", errors="ignore").strip()
    if version_str not in {"WFM#001", "WFM#002", "WFM#003"}:
        raise ValueError(f"File '{file_name}' has unsupported Tektronix WFM version '{version_str}'")
    is_v1 = version_str == "WFM#001"

    try:
        stream = KaitaiStream(_io.BytesIO(data))
        if is_v1:
            raw = _TekWfm001Le(stream) if is_le else _TekWfm001Be(stream)
        else:
            raw = _TekWfm002Le(stream) if is_le else _TekWfm002Be(stream)
    except Exception as exc:
        raise ValueError(f"Could not parse Tektronix file '{file_name}': {exc}") from exc

    sfi = raw.static_file_info
    hdr = raw.wfm_header
    exp1 = hdr.exp_dim1
    imp1 = hdr.imp_dim1

    if not is_v1:
        # set_type 0 is a single waveform, 1 is FastFrame; both are handled.
        set_type = getattr(hdr.set_type, "value", int(hdr.set_type))
        if set_type not in (0, 1):
            raise ValueError(f"Tektronix WFM set type {set_type} is not supported: '{file_name}'")
        if int(hdr.curve_ref_count) != 1:
            raise ValueError(f"Multi-curve Tektronix WFM files are not yet supported: '{file_name}'")

    # Waveform label → model identifier
    try:
        trace_label = sfi.waveform_label.split(b"\x00")[0].decode("ascii", errors="ignore").strip()
    except Exception:
        trace_label = ""
    model_str = "Tektronix"

    # Data format and byte-count per point
    fmt_code = getattr(exp1.format, "value", int(exp1.format))
    bytes_per_point = int(sfi.num_bytes_per_point) or 2

    # Number of valid samples from the curve object
    curve = hdr.curve
    n_pts = int(curve.num_valid_samples)
    if n_pts <= 0:
        n_pts = int(imp1.dim_size)  # fallback: full record length

    # Extract valid waveform bytes from curve buffer
    try:
        curve_buf = raw.curve_buffer
    except Exception as exc:
        raise ValueError(f"No waveform data in '{file_name}' (file may be truncated): {exc}") from exc

    frame_count = int(getattr(raw, "n_frames", 1) or 1)
    if not 0 <= frame < frame_count:
        raise ValueError(
            f"'{file_name}' holds {frame_count} frame(s), so frame {frame} does not exist "
            f"(valid range 0..{frame_count - 1})"
        )

    # Frames 1..N describe themselves; frame 0 is the one in the fixed header.
    if frame > 0:
        curve = raw.frame_curve_objects[frame - 1]
        n_pts = int(curve.num_valid_samples) or n_pts

    # Every frame occupies the same span, laid end to end in the curve buffer.
    frame_stride = int(hdr.curve.end_of_curve_buffer_offset)
    base = frame * frame_stride
    data_start = base + int(curve.data_start_offset)
    data_end = base + int(curve.postcharge_start_offset)
    if data_end <= data_start:
        data_end = data_start + n_pts * bytes_per_point

    raw_bytes = bytes(curve_buf[data_start:data_end])
    if not raw_bytes:
        raise ValueError(f"No waveform data in '{file_name}'")

    meta = _parse_tekmeta(data, byte_order)
    data_type = getattr(hdr.data_type, "value", int(hdr.data_type))

    # Each frame records when it triggered, as whole GMT seconds plus a
    # fraction.  Keep the two apart: frames can be well under a microsecond
    # apart, and adding a fraction to a ~1.8e9 second count loses that in
    # float64.  The offset from frame 0 subtracts the whole seconds exactly, so
    # it keeps full resolution.
    spec = hdr.update_spec if frame == 0 else raw.frame_update_specs[frame - 1]
    first = hdr.update_spec
    frame_trigger_seconds = int(spec.gmt_sec)
    frame_trigger_fraction = float(spec.frac_sec)
    frame_trigger_offset = (frame_trigger_seconds - int(first.gmt_sec)) + (
        frame_trigger_fraction - float(first.frac_sec)
    )

    t_scale = float(imp1.dim_scale)
    t_origin = float(imp1.dim_offset)

    if _is_digital(data_type, meta):
        # Packed logic lines, not volts.  Scaling these bytes as a voltage is
        # what produced a meaningless analog trace before.
        digital = _digital_waveform(
            raw_bytes,
            meta,
            model_str=model_str,
            trace_label=trace_label,
            t_origin=t_origin,
            t_scale=t_scale,
        )
        digital.header.frame_count = frame_count
        digital.header.frame_index = frame
        digital.header.frame_trigger_seconds = frame_trigger_seconds
        digital.header.frame_trigger_fraction = frame_trigger_fraction
        digital.header.frame_trigger_offset = frame_trigger_offset
        return digital

    # Decode ADC samples
    adc = _decode_adc(raw_bytes, fmt_code, byte_order, n_pts)
    n_pts = len(adc)

    # Calibrate to volts:  volts = scale * adc + offset
    dim_scale = float(exp1.dim_scale)
    dim_offset = float(exp1.dim_offset)
    volts = (dim_scale * adc.astype(np.float64) + dim_offset).astype(np.float32)

    # Volts per division: user_scale from user-view data (volts/div)
    volt_per_div = float(exp1.user_scale) if float(exp1.user_scale) != 0 else abs(dim_scale) * 25

    # Time axis: t[i] = dim_offset + i * dim_scale.  `adc` was sliced from
    # data_start_offset, so its index 0 is already the first valid sample and
    # dim_offset already refers to that sample -- adding first_valid_sample
    # here would count the precharge region twice.
    x_increment = t_scale

    # Build normalized objects
    obj = TekWaveform()
    obj.tekmeta = meta
    h = obj.header
    h.model = model_str
    h.trace_label = trace_label
    h.x_origin = t_origin
    h.x_increment = x_increment
    h.frame_count = frame_count
    h.frame_index = frame
    h.frame_trigger_seconds = frame_trigger_seconds
    h.frame_trigger_fraction = frame_trigger_fraction
    h.frame_trigger_offset = frame_trigger_offset

    if _is_iq(meta):
        # Interleaved I/Q: even samples are in-phase, odd are quadrature.  One
        # step of imp_dim1.dim_scale already covers a whole pair, so the time
        # axis carries over unchanged and only the point count halves.
        pairs = (len(volts) // 2) * 2
        h.n_pts = pairs // 2
        for slot, (name, start) in enumerate((("I", 0), ("Q", 1))):
            _assign_trace(
                h,
                slot,
                name,
                volts[start:pairs:2],
                adc[start:pairs:2],
                bytes_per_point=bytes_per_point,
                volt_per_div=volt_per_div,
                dim_scale=dim_scale,
                dim_offset=dim_offset,
            )
        return obj

    # Every other Tektronix .wfm captures a single channel per file
    h.n_pts = n_pts
    _assign_trace(
        h,
        0,
        "CH1",
        volts,
        adc,
        bytes_per_point=bytes_per_point,
        volt_per_div=volt_per_div,
        dim_scale=dim_scale,
        dim_offset=dim_offset,
    )
    return obj
