# pylint: disable=invalid-name
# pylint: disable=too-many-instance-attributes
# pylint: disable=too-many-branches
# pylint: disable=too-many-statements

"""
Parsers for Rigol DHO800/DHO1000 series oscilloscope waveform files.

Two file formats are supported:

.bin  Official binary format documented in DHO1000 User Guide, §19.2.4.
      Parsed via kaitai-generated Bindho1000 class (see ksy/bindho1000.ksy).
      Contains float32 calibrated voltage samples.  Works identically for
      DHO800 and DHO1000.

.wfm  Proprietary format (reverse-engineered from DHO1074 and DHO800 captures).
      Contains zlib-compressed metadata blocks followed by interleaved uint16
      ADC samples for all enabled channels.

--- .wfm file structure ---

    [File Header: 24 bytes]
    [Metadata blocks: variable count, each 12-byte header + content]
    [Zero padding]
    [Data section header: 40 bytes]
    [Raw ADC samples: n_pts_total × uint16 LE, interleaved by channel]

Block header (12 bytes, all u16 LE):
    block_id      u16  channel/block identifier
    block_type    u16  content type
    decomp_size   u16  decompressed size
    comp_size     u16  compressed size
    padded_size   u16  padded size in file
    zero          u16  always 0

--- DHO1000 (.wfm) calibration blocks ---

    id=1, type=9  - CH1 channel parameters
        bytes[1:9]   i64 LE  scale factor: scale = i64 / 750_000_000_000
    type=6  - trigger/display settings
        bytes[36:40] i32 LE  CH1 voltage center × 1e8

    Voltage: scale = i64/750B, v_center = i32/1e8
    Data section: offset+0 u64 = n_pts + 64 (single channel only)

--- DHO800 (.wfm) calibration blocks (reverse-engineered) ---

    id=1..4, type=5  - per-channel parameters (one block per enabled channel)
        bytes[1:9]   i64 LE  scale factor: scale = i64 / 7_500_000_000_000
        bytes[38:42] i32 LE  -v_center × 1e9 (negated, divisor 1e9)

    Voltage: scale = i64/7.5T, v_center = -i32/1e9
    Data section: offset+0 u64 = n_pts_total (all channels), offset+24 u32 = n_pts/ch
    Multi-channel: samples interleaved as [CH1, CH2, ..., CHn, CH1, CH2, ...]

Common calibration formula (both variants):
    offset  = v_center - scale * 32768
    voltage = scale * raw_uint16 + offset   (RMS error < 0.006 mV vs .bin)

Example:
    >>> import RigolWFM.wfmdho1000 as wdho
    >>> bin_data = wdho.Dho1000.from_file("RigolDS0.bin")
    >>> wfm_data = wdho.WfmDho1000.from_file("RigolDS0.wfm")
"""

import struct
import zlib
from enum import IntEnum

import numpy as np

import RigolWFM.bindho1000


# .wfm parser constants
_WFM_FILE_HEADER_SIZE = 24
_WFM_BLOCK_HEADER_SIZE = 12
_WFM_CH1_BLOCK_ID = 1
_WFM_CH1_BLOCK_TYPE = 9           # DHO1000 channel calibration block type
_WFM_CH_BLOCK_TYPE_DHO800 = 5     # DHO800 channel calibration block type
_WFM_SETTINGS_BLOCK_TYPE = 6
_WFM_SCALE_DIVISOR = 750_000_000_000          # DHO1000 scale divisor
_WFM_SCALE_DIVISOR_DHO800 = 7_500_000_000_000  # DHO800 scale divisor (10× larger)
_WFM_ADC_MIDPOINT = 32768
_WFM_V_CENTER_DIVISOR = 1e8
_WFM_V_CENTER_DIVISOR_DHO800 = 1e9  # DHO800: bytes[38:42] of type=5 block, negated


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
# .bin parser - thin wrapper around kaitai-generated Bindho1000
# ---------------------------------------------------------------------------

def _channel_slot(ch_name, fallback):
    """Derive 0-based channel slot from name like 'CH2' → 1; return fallback on failure."""
    name_upper = ch_name.upper()
    for prefix in ("CH", "C"):
        if name_upper.startswith(prefix):
            try:
                n = int(name_upper[len(prefix):]) - 1
                if 0 <= n < 4:
                    return n
            except ValueError:
                pass
            break
    return fallback


class BinHeader:
    """Interface object holding parsed DHO .bin data for use by channel.py."""

    def __init__(self):
        """Initialize empty header."""
        self.cookie = ""
        self.n_waveforms = 0
        self.n_pts = 0
        self.x_origin = 0.0
        self.x_increment = 1e-6
        self.model = ""
        self.ch = []
        self.channel_data = []

    @property
    def seconds_per_point(self):
        """Time between samples in seconds."""
        return self.x_increment

    @property
    def time_scale(self):
        """Time per division (12 divisions per screen)."""
        return self.n_pts * self.x_increment / 12.0

    @property
    def points(self):
        """Number of sample points."""
        return self.n_pts

    @property
    def firmware_version(self):
        """Firmware version (not stored in .bin format)."""
        return "unknown"

    @property
    def model_number(self):
        """Model string from file header."""
        return self.model


class Dho1000:
    """Wrapper around kaitai Bindho1000 for DHO800/DHO1000 .bin files."""

    def __init__(self):
        """Initialize parser."""
        self.header = BinHeader()

    def __str__(self):
        """Return string representation for parser name extraction."""
        return "x.dho1000"

    @classmethod
    def from_file(cls, file_name):
        """
        Parse a DHO series .bin file using the kaitai-generated Bindho1000 parser.

        Args:
            file_name: path to .bin file

        Returns:
            Dho1000 object with header and per-channel voltage data
        """
        raw = RigolWFM.bindho1000.Bindho1000.from_file(file_name)
        supported_buffer_types = {
            RigolWFM.bindho1000.Bindho1000.BufferTypeEnum.float32_normal,
            RigolWFM.bindho1000.Bindho1000.BufferTypeEnum.float32_maximum,
            RigolWFM.bindho1000.Bindho1000.BufferTypeEnum.float32_minimum,
        }

        obj = cls()
        h = obj.header

        h.cookie = raw.file_header.cookie.decode("ascii", errors="ignore")
        h.n_waveforms = raw.file_header.n_waveforms
        h.ch = [ChannelHeader(f"CH{i + 1}", enabled=False) for i in range(4)]
        h.channel_data = [None] * 4

        for i, wfm in enumerate(raw.waveforms):
            wh = wfm.wfm_header
            buffer_type = wfm.data_header.buffer_type
            bytes_per_point = wfm.data_header.bytes_per_point

            if i == 0:
                h.n_pts = wh.n_pts
                h.x_increment = wh.x_increment
                h.x_origin = wh.x_origin
                h.model = wh.model

            ch_name = wh.channel_name.strip() or f"CH{i + 1}"
            slot = _channel_slot(ch_name, fallback=i)

            if buffer_type not in supported_buffer_types or bytes_per_point != 4:
                raise ValueError(
                    "Unsupported DHO .bin waveform buffer "
                    f"(channel={ch_name!r}, buffer_type={int(buffer_type)}, "
                    f"bytes_per_point={bytes_per_point}). "
                    "Only float32 analog buffers are currently supported."
                )

            y_units_code = wh.y_units.value
            h.ch[slot] = ChannelHeader(ch_name, enabled=True, unit_code=y_units_code)

            data = np.array(wfm.samples.values, dtype=np.float32)
            np.nan_to_num(data, copy=False)
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
        self.raw_data = None        # per-channel list of uint16 arrays, or None
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

    Detects DHO800 (type=5 CH blocks) vs DHO1000 (type=9 CH block) format automatically.

    Returns:
        (is_dho800, cal) where cal is a dict {ch_id: (scale, v_center, offset)}.
        voltage = scale * raw_uint16 + offset
        Returns (False, {}) if required blocks not found.
    """
    # Detect format by presence of type=5 vs type=9 CH calibration blocks (id 1-4)
    is_dho800 = any(
        bt == _WFM_CH_BLOCK_TYPE_DHO800 and 1 <= bid <= 4
        for bid, bt, _, _ in blocks
    )

    cal = {}
    if is_dho800:
        for block_id, block_type, content, _ in blocks:
            if block_type == _WFM_CH_BLOCK_TYPE_DHO800 and 1 <= block_id <= 4:
                if len(content) >= 42:
                    (i64_val,) = struct.unpack_from("<q", content, 1)
                    scale = i64_val / _WFM_SCALE_DIVISOR_DHO800
                    (i32_val,) = struct.unpack_from("<i", content, 38)
                    v_center = -i32_val / _WFM_V_CENTER_DIVISOR_DHO800
                    cal[block_id] = (scale, v_center, v_center - scale * _WFM_ADC_MIDPOINT)
    else:
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
        if scale is not None and v_center is not None:
            cal[1] = (scale, v_center, v_center - scale * _WFM_ADC_MIDPOINT)

    return is_dho800, cal


def _find_data_section(data, blocks_end_offset, is_dho800=False):
    """
    Find the start of the data section after zero padding.

    DHO800: u64 at offset+0 is total sample count (all channels); n_pts/ch at offset+24.
    DHO1000: u64 at offset+0 is n_pts + 64 (single channel only).

    Returns:
        (n_pts, n_ch, x_origin, x_increment, data_start_offset)
        or (None, None, None, None, None) on failure
    """
    offset = blocks_end_offset
    while offset < len(data) and data[offset] == 0:
        offset += 1

    if offset + 40 >= len(data):
        return None, None, None, None, None

    (n_pts_u64,) = struct.unpack_from("<Q", data, offset)

    if is_dho800:
        if n_pts_u64 == 0 or n_pts_u64 > 2_000_000_000:
            return None, None, None, None, None
        if offset + 28 > len(data):
            return None, None, None, None, None
        (n_pts_per_ch,) = struct.unpack_from("<I", data, offset + 24)
        if n_pts_per_ch == 0:
            return None, None, None, None, None
        n_ch = int(n_pts_u64 // n_pts_per_ch)
    else:
        if n_pts_u64 <= 64 or n_pts_u64 > 2_000_000_000:
            return None, None, None, None, None
        n_pts_per_ch = n_pts_u64 - 64
        n_ch = 1

    (x_increment_ns,) = struct.unpack_from("<I", data, offset + 16)
    if x_increment_ns == 0 or x_increment_ns > 1_000_000_000:
        x_increment_ns = 1

    x_increment = x_increment_ns * 1e-9
    x_origin = -(n_pts_per_ch / 2) * x_increment
    data_start = offset + 40

    return n_pts_per_ch, n_ch, x_origin, x_increment, data_start


class WfmDho1000:
    """Parser for DHO800/DHO1000 .wfm files."""

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

        is_dho800, cal = _extract_volt_calibration(blocks)

        if not cal:
            raise ValueError(
                f"Could not extract voltage calibration from {file_name}. "
                "Ensure this is a DHO series .wfm file."
            )

        n_pts, n_ch, x_origin, x_increment, data_start = _find_data_section(
            data, blocks_end, is_dho800=is_dho800
        )

        if n_pts is None:
            raise ValueError(f"Could not locate data section in {file_name}")

        if data_start + n_pts * n_ch * 2 > len(data):
            raise ValueError(
                f"Data section claims {n_pts * n_ch} samples but file is too small"
            )

        scale1, v_center1, offset1 = cal.get(1, next(iter(cal.values())))
        h.n_pts = n_pts
        h.x_origin = x_origin
        h.x_increment = x_increment
        h.volt_scale = scale1
        h.volt_offset = offset1
        h.volt_per_div = abs(scale1 * 65536 / 8)

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

        raw_bytes = data[data_start:data_start + n_pts * n_ch * 2]
        raw_all = np.frombuffer(raw_bytes, dtype="<u2").copy()

        # Interleaved multi-channel layout: [CH1, CH2, ..., CHn, CH1, CH2, ...]
        h.channel_data = [None] * 4
        h.raw_data = [None] * 4
        h.ch = []

        for ch_idx in range(n_ch):
            ch_num = ch_idx + 1
            raw_ch = raw_all[ch_idx::n_ch]
            sc, vc, off_c = cal.get(ch_num, (scale1, v_center1, offset1))
            volts = (sc * raw_ch.astype(np.float64) + off_c).astype(np.float32)
            h.channel_data[ch_idx] = volts
            h.raw_data[ch_idx] = raw_ch
            ch_hdr = ChannelHeader(f"CH{ch_num}", enabled=True)
            ch_hdr.volt_per_division = abs(sc * 65536 / 8)
            ch_hdr.volt_offset = vc
            h.ch.append(ch_hdr)

        for i in range(n_ch, 4):
            h.ch.append(ChannelHeader(f"CH{i + 1}", enabled=False))

        return obj
