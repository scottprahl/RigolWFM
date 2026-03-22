# pylint: disable=invalid-name
# pylint: disable=too-many-instance-attributes
# pylint: disable=too-many-branches
# pylint: disable=too-many-statements

"""
Parsers for Rigol DHO800/DHO900/DHO1000 series oscilloscope waveform files.

Two file formats are supported:

.bin  Official binary format documented in DHO1000 User Guide, §19.2.4.
      Contains float32 calibrated voltage samples.

.wfm  Proprietary format (reverse-engineered from DHO1074 captures).
      Contains zlib-compressed metadata blocks followed by uint16 ADC samples.

--- .bin file structure (Tables 19.1–19.4) ---

    [File Header: 16 bytes]
    For each waveform (channel):
        [Waveform Header: 140 bytes]
        [Waveform Data Header: 16 bytes]
        [Channel Data: buffer_size bytes (float32 LE)]

File Header (16 bytes):
    Cookie              2 bytes   "RG"
    Version             2 bytes   file version
    File Size           8 bytes   u64le, total file size
    Number of Waveforms 4 bytes   u32le

Waveform Header (140 bytes):
    Header Size         4 bytes   u32le (= 140)
    Waveform Type       4 bytes   u32le (1=Normal, 2=Peak, 3=Average, 6=Logic)
    Number of Buffers   4 bytes   u32le (= 1)
    Number of Points    4 bytes   u32le
    Count               4 bytes   u32le (= 0)
    X Display Range     4 bytes   f32le
    X Display Origin    8 bytes   f64le
    X Increment         8 bytes   f64le
    X Origin            8 bytes   f64le  (positive = distance from trigger)
    X Units             4 bytes   u32le
    Y Units             4 bytes   u32le
    Date               16 bytes   ASCII
    Time               16 bytes   ASCII
    Model              24 bytes   ASCII "MODEL#:SERIAL#"
    Channel Name       16 bytes   ASCII
    (padding)          12 bytes   zeros

Waveform Data Header (16 bytes):
    Header Size         4 bytes   u32le (= 16)
    Buffer Type         2 bytes   u16le (1=Normal float32)
    Bytes Per Point     2 bytes   u16le (= 4)
    Buffer Size         8 bytes   u64le

--- .wfm file structure ---

    [File Header: 24 bytes]
    [Metadata blocks: variable count, each 12-byte header + content]
    [Zero padding]
    [Data section header: 40 bytes]
    [Raw ADC samples: n_pts × uint16 LE]

Block header (12 bytes, all u16 LE):
    block_id      u16  channel/block identifier
    block_type    u16  content type
    decomp_size   u16  decompressed size
    comp_size     u16  compressed size
    padded_size   u16  padded size in file
    zero          u16  always 0

Key blocks:
    id=1, type=9  (96 bytes decompressed)  - CH1 channel parameters
        bytes[1:9]   i64 LE  voltage scale factor: scale = i64 / 750_000_000_000
    type=6  (~1628 bytes decompressed)  - trigger/display settings
        bytes[36:40] i32 LE  CH1 voltage center × 1e8

Voltage calibration (verified, RMS error < 0.012 mV):
    scale    = i64_ch1 / 750_000_000_000
    v_center = i32_settings / 1e8
    offset   = v_center - scale * 32768
    voltage  = scale * raw_uint16 + offset

Data section layout (40 bytes before samples):
    offset+0:   u64  n_pts + 64
    offset+8:   8B   capture marker
    offset+16:  u32  x_increment in nanoseconds
    offset+20:  u32  unknown (79 in observed files)
    offset+24:  u32  n_pts (repeated)
    offset+28:  u32  n_pts (repeated)
    offset+32:  u32  timestamp/unknown
    offset+36:  u32  unknown (120 in observed files)
    offset+40:  uint16 samples begin

    x_origin is not stored; derived as -(n_pts / 2) × x_increment.

Example:
    >>> import RigolWFM.wfmdho1000 as wdho
    >>> bin_data = wdho.Dho1000.from_file("RigolDS0.bin")
    >>> wfm_data = wdho.WfmDho1000.from_file("RigolDS0.wfm")
"""

import struct
import zlib
from enum import IntEnum

import numpy as np


# .bin parser constants
_BIN_FILE_HEADER_SIZE = 16
_BIN_DATA_HEADER_SIZE = 16

# .wfm parser constants
_WFM_FILE_HEADER_SIZE = 24
_WFM_BLOCK_HEADER_SIZE = 12
_WFM_CH1_BLOCK_ID = 1
_WFM_CH1_BLOCK_TYPE = 9
_WFM_SETTINGS_BLOCK_TYPE = 6
_WFM_SCALE_DIVISOR = 750_000_000_000
_WFM_ADC_MIDPOINT = 32768
_WFM_V_CENTER_DIVISOR = 1e8


class UnitEnum(IntEnum):
    """Unit types from DHO1000 User Guide Table 19.3."""

    unknown = 0
    v = 1
    s = 2
    constant = 3
    a = 4
    db = 5
    hz = 6


class CouplingEnum(IntEnum):
    """Coupling modes."""

    dc = 0
    ac = 1
    gnd = 2


class ChannelHeader:
    """Per-channel metadata for DHO series files."""

    def __init__(self, name, enabled, unit_code=0):
        """Initialize channel header."""
        self.name = name
        self.enabled = enabled
        self.unit_code = unit_code
        self.coupling = CouplingEnum.dc
        self.inverted = False
        self.volt_per_division = 1.0
        self.volt_offset = 0.0
        self.volt_scale = 1.0
        self.probe_value = 1.0
        self.unit = UnitEnum(unit_code) if 0 <= unit_code <= 6 else UnitEnum.unknown

    @property
    def y_scale(self):
        """Not used for DHO (data is already in volts)."""
        return 1.0

    @property
    def y_offset(self):
        """Not used for DHO (data is already in volts)."""
        return 0.0


# ---------------------------------------------------------------------------
# .bin parser
# ---------------------------------------------------------------------------

class BinHeader:
    """Parsed header from DHO .bin file."""

    def __init__(self):
        """Initialize empty header."""
        self.cookie = ""
        self.version = ""
        self.file_size = 0
        self.n_waveforms = 0

        self.waveform_header_size = 0
        self.waveform_type = 0
        self.n_buffers = 0
        self.n_pts = 0
        self.count = 0
        self.x_range = 0.0
        self.x_disp_origin = 0.0
        self.x_increment = 0.0
        self.x_origin = 0.0
        self.x_units_code = 0
        self.y_units_global = 0
        self.f_date = ""
        self.f_time = ""
        self.model = ""

        self.data_header_size = 0
        self.buffer_type = 0
        self.bytes_per_point = 0
        self.buffer_size = 0

        self.ch = []
        self.channel_data = []

    @property
    def seconds_per_point(self):
        """Time between samples."""
        return self.x_increment

    @property
    def time_offset(self):
        """Horizontal trigger position."""
        return 0.0

    @property
    def time_scale(self):
        """Time per division (12 divs)."""
        return self.n_pts * self.x_increment / 12.0

    @property
    def storage_depth(self):
        """Number of sample points."""
        return self.n_pts

    @property
    def points(self):
        """Number of sample points."""
        return self.n_pts

    @property
    def firmware_version(self):
        """Firmware version (not available in .bin format)."""
        return "unknown"

    @property
    def model_number(self):
        """Model string from file header."""
        return self.model


def _read_exact(f, n):
    """Read exactly n bytes or raise EOFError."""
    b = f.read(n)
    if len(b) != n:
        raise EOFError(f"Unexpected EOF: wanted {n} bytes, got {len(b)}")
    return b


def _read_str(f, n):
    """Read n bytes as ASCII string, strip nulls."""
    raw = _read_exact(f, n)
    return raw.decode("ascii", errors="ignore").rstrip("\x00 ").strip()


def _unpack(f, fmt):
    """Read and unpack little-endian struct from file."""
    fmt_le = "<" + fmt
    size = struct.calcsize(fmt_le)
    return struct.unpack(fmt_le, _read_exact(f, size))


class Dho1000:
    """Parser for DHO800/DHO900/DHO1000 .bin files per official spec."""

    def __init__(self):
        """Initialize parser."""
        self.header = BinHeader()

    def __str__(self):
        """Return string representation for parser name extraction."""
        return "x.dho1000"

    @classmethod
    def from_file(cls, file_name):
        """
        Parse a DHO series .bin file.

        Format documented in DHO1000 User Guide, Section 19.2.4,
        Tables 19.1 through 19.4.

        Args:
            file_name: path to .bin file

        Returns:
            Dho1000 object with parsed header and channel data
        """
        obj = cls()
        h = obj.header

        with open(file_name, "rb") as f:
            # === File Header (16 bytes) ===
            h.cookie = _read_str(f, 2)
            if h.cookie != "RG":
                raise ValueError(
                    f"Not a Rigol DHO .bin file: cookie='{h.cookie}', expected 'RG'"
                )
            h.version = _read_str(f, 2)
            (h.file_size,) = _unpack(f, "Q")
            (h.n_waveforms,) = _unpack(f, "I")

            h.ch = [ChannelHeader(f"CH{i + 1}", enabled=False) for i in range(4)]
            h.channel_data = [None] * 4

            for i in range(h.n_waveforms):
                wfm_start = f.tell()

                # === Waveform Header (140 bytes) ===
                (wfm_header_size,) = _unpack(f, "I")
                (waveform_type,) = _unpack(f, "I")
                (n_buffers,) = _unpack(f, "I")
                (n_pts,) = _unpack(f, "I")
                (count,) = _unpack(f, "I")
                (x_range,) = _unpack(f, "f")
                (x_disp_origin,) = _unpack(f, "d")
                (x_increment,) = _unpack(f, "d")
                (x_origin,) = _unpack(f, "d")
                (x_units_code,) = _unpack(f, "I")
                (y_units_code,) = _unpack(f, "I")
                f_date = _read_str(f, 16)
                f_time = _read_str(f, 16)
                model = _read_str(f, 24)
                ch_name = _read_str(f, 16) or f"CH{i + 1}"

                f.seek(wfm_start + wfm_header_size)

                if i == 0:
                    h.waveform_header_size = wfm_header_size
                    h.waveform_type = waveform_type
                    h.n_buffers = n_buffers
                    h.n_pts = n_pts
                    h.count = count
                    h.x_range = x_range
                    h.x_disp_origin = x_disp_origin
                    h.x_increment = x_increment
                    h.x_origin = x_origin
                    h.x_units_code = x_units_code
                    h.y_units_global = y_units_code
                    h.f_date = f_date
                    h.f_time = f_time
                    h.model = model

                # Derive the real channel slot from ch_name ("CH2" → slot 1).
                # Fall back to loop index so files without a name still work.
                slot = i
                name_upper = ch_name.upper()
                for prefix in ("CH", "C"):
                    if name_upper.startswith(prefix):
                        try:
                            n = int(name_upper[len(prefix):]) - 1
                            if 0 <= n < 4:
                                slot = n
                        except ValueError:
                            pass
                        break

                h.ch[slot] = ChannelHeader(ch_name, enabled=True, unit_code=y_units_code)

                # === Waveform Data Header (16 bytes) ===
                (data_hdr_size,) = _unpack(f, "I")
                (buffer_type,) = _unpack(f, "H")
                (bytes_per_point,) = _unpack(f, "H")
                (buffer_size,) = _unpack(f, "Q")

                if i == 0:
                    h.data_header_size = data_hdr_size
                    h.buffer_type = buffer_type
                    h.bytes_per_point = bytes_per_point
                    h.buffer_size = buffer_size

                # === Channel Data ===
                raw = _read_exact(f, buffer_size)
                data = np.frombuffer(raw, dtype="<f4").copy()
                data = np.nan_to_num(data, copy=False)
                h.channel_data[slot] = data

        return obj


# ---------------------------------------------------------------------------
# .wfm parser
# ---------------------------------------------------------------------------

class WfmHeader:
    """Parsed header and data from DHO .wfm file."""

    def __init__(self):
        """Initialize empty header."""
        self.n_pts = 0
        self.x_origin = 0.0
        self.x_increment = 1e-9
        self.model = ""
        self.firmware = "unknown"

        self.volt_scale = 1.0
        self.volt_offset = 0.0
        self.volt_per_div = 0.1

        self.ch = []
        self.raw_data = None
        self.channel_data = []

    @property
    def seconds_per_point(self):
        """Time between samples in seconds."""
        return self.x_increment

    @property
    def time_offset(self):
        """Horizontal trigger position."""
        return 0.0

    @property
    def time_scale(self):
        """Time per division (12 divisions per screen)."""
        if self.n_pts > 0 and self.x_increment > 0:
            return self.n_pts * self.x_increment / 12.0
        return 1e-3

    @property
    def storage_depth(self):
        """Number of sample points."""
        return self.n_pts

    @property
    def points(self):
        """Number of sample points."""
        return self.n_pts

    @property
    def firmware_version(self):
        """Firmware version string."""
        return self.firmware

    @property
    def model_number(self):
        """Model string."""
        return self.model


def _try_decompress(data):
    """Attempt zlib decompression; return original data on failure."""
    try:
        return zlib.decompress(data)
    except zlib.error:
        return data


def _parse_blocks(data, file_header_size=_WFM_FILE_HEADER_SIZE):
    """
    Parse all metadata blocks from WFM file data.

    Returns:
        list of (block_id, block_type, decompressed_content, file_offset) tuples
        and the file offset just past the last block
    """
    blocks = []
    offset = file_header_size

    while offset + _WFM_BLOCK_HEADER_SIZE <= len(data):
        hdr = struct.unpack_from("<6H", data, offset)
        block_id, block_type, decomp_size, comp_size, padded_size, _zero = hdr

        if padded_size == 0 and decomp_size == 0 and comp_size == 0:
            break

        content_start = offset + _WFM_BLOCK_HEADER_SIZE
        content_end = content_start + padded_size

        if content_end > len(data):
            break

        raw_content = data[content_start:content_start + comp_size]
        content = _try_decompress(raw_content)

        blocks.append((block_id, block_type, content, offset))
        offset = content_end

    return blocks, offset


def _extract_volt_calibration(blocks):
    """
    Extract voltage calibration parameters from metadata blocks.

    Returns:
        (scale, v_center, offset) where voltage = scale * raw_uint16 + offset
        Returns (None, None, None) if required blocks not found.
    """
    scale = None
    v_center = None

    for block_id, block_type, content, _ in blocks:
        if block_id == _WFM_CH1_BLOCK_ID and block_type == _WFM_CH1_BLOCK_TYPE:
            if len(content) >= 9:
                (i64_val,) = struct.unpack_from("<q", content, 1)
                scale = i64_val / _WFM_SCALE_DIVISOR

        elif block_type == _WFM_SETTINGS_BLOCK_TYPE and len(content) >= 40:
            (i32_val,) = struct.unpack_from("<i", content, 36)
            v_center = i32_val / _WFM_V_CENTER_DIVISOR

    if scale is None or v_center is None:
        return None, None, None

    offset = v_center - scale * _WFM_ADC_MIDPOINT
    return scale, v_center, offset


def _find_data_section(data, blocks_end_offset):
    """
    Find the start of the data section after zero padding.

    Returns:
        (n_pts, x_origin, x_increment, data_start_offset)
        or (None, None, None, None) on failure
    """
    offset = blocks_end_offset
    while offset < len(data) and data[offset] == 0:
        offset += 1

    if offset + 40 >= len(data):
        return None, None, None, None

    (n_pts_plus64,) = struct.unpack_from("<Q", data, offset)
    if n_pts_plus64 <= 64 or n_pts_plus64 > 2_000_000_000:
        return None, None, None, None
    n_pts = n_pts_plus64 - 64

    if offset + 20 > len(data):
        return None, None, None, None

    (x_increment_ns,) = struct.unpack_from("<I", data, offset + 16)

    if x_increment_ns == 0 or x_increment_ns > 1_000_000_000:
        x_increment_ns = 1

    x_increment = x_increment_ns * 1e-9
    x_origin = -(n_pts / 2) * x_increment
    data_start = offset + 40

    return n_pts, x_origin, x_increment, data_start


class WfmDho1000:
    """Parser for DHO800/DHO900/DHO1000 .wfm files."""

    def __init__(self):
        """Initialize parser."""
        self.header = WfmHeader()

    def __str__(self):
        """Return string representation for parser name extraction."""
        return "x.wfmdho1000"

    @classmethod
    def from_file(cls, file_name):
        """
        Parse a DHO series .wfm file.

        Args:
            file_name: path to .wfm file

        Returns:
            WfmDho1000 object with header and channel data
        """
        obj = cls()
        h = obj.header

        with open(file_name, "rb") as f:
            data = f.read()

        if len(data) < _WFM_FILE_HEADER_SIZE + _WFM_BLOCK_HEADER_SIZE:
            raise ValueError(f"File too small to be a valid DHO .wfm file: {file_name}")

        blocks, blocks_end = _parse_blocks(data)

        if not blocks:
            raise ValueError(f"No valid metadata blocks found in {file_name}")

        scale, v_center, volt_offset = _extract_volt_calibration(blocks)

        if scale is None:
            raise ValueError(
                f"Could not extract voltage calibration from {file_name}. "
                "Ensure this is a DHO series .wfm file."
            )

        n_pts, x_origin, x_increment, data_start = _find_data_section(data, blocks_end)

        if n_pts is None:
            raise ValueError(f"Could not locate data section in {file_name}")

        if data_start + n_pts * 2 > len(data):
            raise ValueError(
                f"Data section claims {n_pts} samples but file is too small"
            )

        h.n_pts = n_pts
        h.x_origin = x_origin
        h.x_increment = x_increment
        h.volt_scale = scale
        h.volt_offset = volt_offset
        h.volt_per_div = abs(scale * 65536 / 8)

        for _, _, content, _ in blocks:
            try:
                s = content.decode("ascii", errors="ignore")
                for prefix in ("DHO", "MSO"):
                    idx = s.find(prefix)
                    if idx >= 0:
                        model_str = ""
                        for c in s[idx:idx + 20]:
                            if c.isprintable() and c not in "\x00":
                                model_str += c
                            else:
                                break
                        if len(model_str) >= 3:
                            h.model = model_str
                            break
                if h.model:
                    break
            except Exception:
                continue

        raw_bytes = data[data_start:data_start + n_pts * 2]
        raw = np.frombuffer(raw_bytes, dtype="<u2").copy()
        h.raw_data = raw

        volts = scale * raw.astype(np.float64) + volt_offset
        volts = volts.astype(np.float32)
        h.channel_data = [volts]

        ch1 = ChannelHeader("CH1", enabled=True)
        ch1.volt_per_division = h.volt_per_div
        ch1.volt_offset = v_center
        h.ch = [ch1]
        for i in range(2, 5):
            h.ch.append(ChannelHeader(f"CH{i}", enabled=False))

        return obj
