"""
Adapter layer for Rigol DHO800/DHO1000 waveform files.

This module is the handwritten bridge between the generated DHO parsers and the
rest of RigolWFM.  It normalizes both DHO `.bin` and proprietary DHO `.wfm`
inputs into the header/data shape expected by `RigolWFM.wfm.Wfm` and
`RigolWFM.channel`.

The generated Kaitai modules are intentionally not called directly by
`RigolWFM.wfm.Wfm.from_file()`:

    - `RigolWFM.bindho1000` only knows the official DHO `.bin` export format.
      It parses per-channel float32 sample buffers, but it does not produce the
      common `header.ch`, `header.channel_data`, `header.raw_data`,
      `header.model_number` structure used by the rest of the project.

    - `RigolWFM.wfmdho1000` only knows the low-level proprietary `.wfm` block
      layout.  It is still not a complete project-level waveform reader because
      DHO `.wfm` files need runtime work after the Kaitai parse: decompress
      block payloads, scan past the zero-padding region, locate the sample
      header, de-interleave channel data, and apply per-channel calibration.

If `wfm.py` called either generated module directly, all of that DHO-specific
normalization logic would leak back into `wfm.py` or `channel.py`, and callers
would have to care whether the source file was `.bin` or `.wfm`.  Keeping the
adapter in `dho.py` lets the generated files stay generated, keeps the
handwritten DHO interpretation in one place, and gives the rest of the project
one stable DHO entry point.
"""
from __future__ import annotations

import struct
import zlib
from enum import IntEnum
from typing import Any, Optional

import numpy as np
import numpy.typing as npt
from kaitaistruct import BytesIO, KaitaiStream

import RigolWFM.bindho1000
import RigolWFM.wfmdho1000

_Bindho1000: Any = RigolWFM.bindho1000.Bindho1000  # type: ignore[attr-defined]
_Wfmdho1000: Any = RigolWFM.wfmdho1000.Wfmdho1000  # type: ignore[attr-defined]

_DHO_FILE_HEADER_SIZE = 24
_DHO_BLOCK_HEADER_SIZE = 12
_DHO_ADC_MIDPOINT = 32768
_DHO_X_INCREMENT_SCALE = 1e-8
_DHO_X_INCREMENT_SCALE_DHO800 = 1e-9


class UnitEnum(IntEnum):
    """Unit types used by DHO waveforms."""

    unknown = 0
    v = 1
    s = 2
    constant = 3
    a = 4
    db = 5
    hz = 6


class CouplingEnum(IntEnum):
    """Coupling modes used by DHO waveforms."""

    dc = 0
    ac = 1
    gnd = 2


class ChannelHeader:
    """Normalized per-channel metadata for DHO captures."""

    name: str
    enabled: bool
    unit_code: int
    coupling: CouplingEnum
    inverted: bool
    volt_per_division: float
    volt_offset: float
    volt_scale: float
    probe_value: float
    unit: UnitEnum

    def __init__(self, name: str, enabled: bool, unit_code: int = 0) -> None:
        """Initialize channel metadata."""
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
    def y_scale(self) -> float:
        """DHO voltage data is already calibrated."""
        return 1.0

    @property
    def y_offset(self) -> float:
        """DHO voltage data is already calibrated."""
        return 0.0


class Header:
    """Normalized header used by `Wfm.from_file()` for DHO captures."""

    cookie: str
    n_waveforms: int
    n_pts: int
    x_origin: float
    x_increment: float
    model: str
    firmware: str
    volt_scale: float
    volt_offset: float
    volt_per_div: float
    ch: list[ChannelHeader]
    raw_data: list[Optional[npt.NDArray[np.uint16]]]
    channel_data: list[Optional[npt.NDArray[np.float32]]]

    def __init__(self) -> None:
        """Initialize an empty DHO header."""
        self.cookie = ""
        self.n_waveforms = 0
        self.n_pts = 0
        self.x_origin = 0.0
        self.x_increment = 1e-6
        self.model = ""
        self.firmware = "unknown"
        self.volt_scale = 1.0
        self.volt_offset = 0.0
        self.volt_per_div = 0.1
        self.ch = []
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
        """Number of sample points."""
        return self.n_pts

    @property
    def firmware_version(self) -> str:
        """Firmware version if known."""
        return self.firmware

    @property
    def model_number(self) -> str:
        """Scope model string if known."""
        return self.model


class DhoWaveform:
    """Normalized DHO parser result consumed by `Channel`."""

    header: Header

    def __init__(self) -> None:
        """Initialize the normalized DHO wrapper."""
        self.header = Header()

    @property
    def parser_name(self) -> str:
        """Return the normalized parser name used by `Wfm.from_file()`."""
        return "dho1000"

    def __str__(self) -> str:
        """Return a parser tag compatible with the rest of `Wfm.from_file()`."""
        return f"x.{self.parser_name}"


def _is_bin(file_name: str) -> bool:
    """Return True if the file starts with the `RG` DHO `.bin` cookie."""
    try:
        with open(file_name, "rb") as f:
            return f.read(2) == b"RG"
    except OSError:
        return False


def _channel_slot(ch_name: str, fallback: int) -> int:
    """Map channel names like `CH2` to a zero-based channel slot."""
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


def _try_decompress(data: bytes) -> bytes:
    """Attempt zlib decompression and fall back to the original bytes."""
    try:
        return zlib.decompress(data)
    except zlib.error:
        return data


def _parse_blocks(
    data: bytes,
    file_header_size: int = _DHO_FILE_HEADER_SIZE,
) -> tuple[list[tuple[Any, bytes, int]], int]:
    """Return decompressed DHO metadata blocks and the start of the padding region."""
    parsed = _Wfmdho1000.from_bytes(data)
    blocks: list[tuple[Any, bytes, int]] = []
    offset = file_header_size

    for block in parsed.blocks:
        if block.is_terminator:
            break

        raw_content = block.content_raw[:block.comp_size]
        blocks.append((block, _try_decompress(raw_content), offset))
        offset += _DHO_BLOCK_HEADER_SIZE + block.len_content_raw

    return blocks, offset


def _extract_volt_calibration(
    blocks: list[tuple[Any, bytes, int]],
) -> tuple[bool, dict[int, tuple[float, float, float]]]:
    """Extract DHO channel calibration from parsed metadata blocks."""
    parser = _Wfmdho1000
    block_type_enum = parser.BlockTypeEnum
    dho1000_params_type = parser.Dho1000ChannelParams
    dho800_params_type = parser.Dho800ChannelParams
    settings_type = parser.SettingsBlock

    def parse_payload(payload_type: Any, content: bytes) -> Any:
        return payload_type(KaitaiStream(BytesIO(content)))

    is_dho800 = any(
        getattr(block.block_type, "value", block.block_type) == block_type_enum.dho800_channel_params
        and 1 <= block.block_id <= 4
        for block, _, _ in blocks
    )

    cal: dict[int, tuple[float, float, float]] = {}
    if is_dho800:
        for block, content, _ in blocks:
            block_type = getattr(block.block_type, "value", block.block_type)
            if block_type == block_type_enum.dho800_channel_params and 1 <= block.block_id <= 4:
                params = parse_payload(dho800_params_type, content)
                cal[block.block_id] = (params.scale, params.v_center, params.offset)
    else:
        for block, content, _ in blocks:
            block_type = getattr(block.block_type, "value", block.block_type)
            if block_type == block_type_enum.channel_params and 1 <= block.block_id <= 4:
                params = parse_payload(dho1000_params_type, content)
                cal[block.block_id] = (params.scale, params.v_center, params.offset)

        if not cal:
            scale = None
            v_center = None
            for block, content, _ in blocks:
                block_type = getattr(block.block_type, "value", block.block_type)
                if block.block_id == 1 and block_type == block_type_enum.channel_params:
                    params = parse_payload(dho1000_params_type, content)
                    scale = params.scale
                elif block_type == block_type_enum.settings:
                    settings = parse_payload(settings_type, content)
                    v_center = settings.v_center
            if scale is not None and v_center is not None:
                cal[1] = (scale, v_center, -v_center - scale * _DHO_ADC_MIDPOINT)

    return is_dho800, cal


def _find_data_section(
    data: bytes,
    blocks_end_offset: int,
    is_dho800: bool = False,
) -> Optional[tuple[int, int, float, float, int]]:
    """Locate the DHO sample data section after the metadata padding region."""
    offset = blocks_end_offset
    while offset < len(data) and data[offset] == 0:
        offset += 1

    if offset + 40 >= len(data):
        return None

    (n_pts_u64,) = struct.unpack_from("<Q", data, offset)
    if offset + 28 > len(data):
        return None

    if is_dho800:
        if n_pts_u64 == 0 or n_pts_u64 > 2_000_000_000:
            return None
        total_pts = n_pts_u64
    else:
        if n_pts_u64 <= 64 or n_pts_u64 > 2_000_000_000:
            return None
        total_pts = n_pts_u64 - 64

    (n_pts_hint,) = struct.unpack_from("<I", data, offset + 24)
    if n_pts_hint > 0 and total_pts % n_pts_hint == 0:
        n_pts_per_ch = n_pts_hint
        n_ch = int(total_pts // n_pts_hint)
    else:
        n_pts_per_ch = total_pts
        n_ch = 1

    if n_pts_per_ch == 0 or n_ch <= 0 or n_ch > 4:
        return None

    (x_increment_ns,) = struct.unpack_from("<I", data, offset + 16)
    if x_increment_ns == 0 or x_increment_ns > 1_000_000_000:
        x_increment_ns = 1

    scale = _DHO_X_INCREMENT_SCALE_DHO800 if is_dho800 else _DHO_X_INCREMENT_SCALE
    x_increment = x_increment_ns * scale
    x_origin = -(n_pts_per_ch / 2) * x_increment
    return int(n_pts_per_ch), int(n_ch), x_origin, x_increment, offset + 40


def _parse_model(blocks: list[tuple[Any, bytes, int]]) -> str:
    """Return the first printable DHO/MSO model string found in metadata blocks."""
    for _, content, _ in blocks:
        try:
            text = content.decode("ascii", errors="ignore")
        except Exception:
            continue

        for prefix in ("DHO", "MSO"):
            idx = text.find(prefix)
            if idx < 0:
                continue
            model = ""
            for char in text[idx:idx + 20]:
                if char.isprintable() and char != "\x00":
                    model += char
                else:
                    break
            if len(model) >= 3:
                return model
    return ""


def _from_bin(file_name: str) -> DhoWaveform:
    """Parse a DHO `.bin` file and normalize it for `Wfm.from_file()`."""
    raw = _Bindho1000.from_file(file_name)
    supported_buffer_types = {
        _Bindho1000.BufferTypeEnum.float32_normal,
        _Bindho1000.BufferTypeEnum.float32_maximum,
        _Bindho1000.BufferTypeEnum.float32_minimum,
    }

    obj = DhoWaveform()
    h = obj.header
    h.cookie = raw.file_header.cookie.decode("ascii", errors="ignore")
    h.n_waveforms = raw.file_header.n_waveforms
    h.ch = [ChannelHeader(f"CH{i + 1}", enabled=False) for i in range(4)]

    for i, waveform in enumerate(raw.waveforms):
        wh = waveform.wfm_header
        buffer_type = waveform.data_header.buffer_type
        bytes_per_point = waveform.data_header.bytes_per_point

        if i == 0:
            h.n_pts = wh.n_pts
            h.x_increment = wh.x_increment
            h.x_origin = -wh.x_origin
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
        data = np.array(waveform.samples.values, dtype=np.float32)
        np.nan_to_num(data, copy=False)
        h.channel_data[slot] = data

    return obj


def _from_wfm(file_name: str) -> DhoWaveform:
    """Parse a DHO `.wfm` file and normalize it for `Wfm.from_file()`."""
    with open(file_name, "rb") as f:
        data = f.read()

    if len(data) < _DHO_FILE_HEADER_SIZE + _DHO_BLOCK_HEADER_SIZE:
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

    _data_section = _find_data_section(data, blocks_end, is_dho800=is_dho800)
    if _data_section is None:
        raise ValueError(f"Could not locate data section in {file_name}")
    n_pts, n_ch, x_origin, x_increment, data_start = _data_section
    if data_start + n_pts * n_ch * 2 > len(data):
        raise ValueError(
            f"Data section claims {n_pts * n_ch} samples but file is too small"
        )

    obj = DhoWaveform()
    h = obj.header
    scale1, v_center1, offset1 = cal.get(1, next(iter(cal.values())))
    h.n_pts = n_pts
    h.x_origin = x_origin
    h.x_increment = x_increment
    h.volt_scale = scale1
    h.volt_offset = offset1
    h.volt_per_div = abs(scale1 * 65536 / 8)
    h.model = _parse_model(blocks)

    raw_bytes = data[data_start:data_start + n_pts * n_ch * 2]
    raw_all = np.frombuffer(raw_bytes, dtype="<u2").copy()
    h.ch = [ChannelHeader(f"CH{i + 1}", enabled=False) for i in range(4)]

    for ch_idx in range(n_ch):
        ch_num = ch_idx + 1
        raw_ch = raw_all[ch_idx::n_ch]
        sc, vc, off_c = cal.get(ch_num, (scale1, v_center1, offset1))
        volts = (sc * raw_ch.astype(np.float64) + off_c).astype(np.float32)
        h.channel_data[ch_idx] = volts
        h.raw_data[ch_idx] = raw_ch
        h.ch[ch_idx] = ChannelHeader(f"CH{ch_num}", enabled=True)
        h.ch[ch_idx].volt_per_division = abs(sc * 65536 / 8)
        h.ch[ch_idx].volt_offset = vc

    return obj


def from_file(file_name: str) -> DhoWaveform:
    """Parse and normalize either DHO `.bin` or `.wfm` input."""
    if _is_bin(file_name):
        return _from_bin(file_name)
    return _from_wfm(file_name)


def dho_from_file(file_name: str) -> DhoWaveform:
    """Backward-compatible alias for older callers of the DHO adapter."""
    return from_file(file_name)
