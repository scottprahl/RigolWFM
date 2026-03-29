"""
Adapter layer for Tektronix oscilloscope waveform files (.wfm).

Normalises the parsed KSY data into the header/data shape expected by
`RigolWFM.wfm.Wfm` and `RigolWFM.channel`.

Two format versions are supported:

  WFM#001 (TDS6000/B/C, TDS/CSA7000/B):
    ksy/tek_wfm_001_le.ksy → RigolWFM/tek_wfm_001_le.py   (LE)
    ksy/tek_wfm_001_be.ksy → RigolWFM/tek_wfm_001_be.py   (BE)

  WFM#002/003 (TDS5000B, DPO7000, DPO70000, DSA70000):
    ksy/tek_wfm_002_le.ksy → RigolWFM/tek_wfm_002_le.py   (LE)
    ksy/tek_wfm_002_be.ksy → RigolWFM/tek_wfm_002_be.py   (BE)

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
  (i = 0 is the first sample in the curve buffer; valid data starts at
   curve.first_valid_sample)
"""
from __future__ import annotations

import io as _io
from typing import Any, Optional

import numpy as np
import numpy.typing as npt
from kaitaistruct import KaitaiStream  # type: ignore[import]

import RigolWFM.channel
import RigolWFM.tek_wfm_001_be
import RigolWFM.tek_wfm_001_le
import RigolWFM.tek_wfm_002_be
import RigolWFM.tek_wfm_002_le

_TekWfm001Le: Any = RigolWFM.tek_wfm_001_le.TekWfm001Le  # type: ignore[attr-defined]
_TekWfm001Be: Any = RigolWFM.tek_wfm_001_be.TekWfm001Be  # type: ignore[attr-defined]
_TekWfm002Le: Any = RigolWFM.tek_wfm_002_le.TekWfm002Le  # type: ignore[attr-defined]
_TekWfm002Be: Any = RigolWFM.tek_wfm_002_be.TekWfm002Be  # type: ignore[attr-defined]

_TEK_MAGIC = b"WFM#"

# Explicit-dimension format codes → numpy dtype
_FORMAT_DTYPE: dict[int, str] = {
    0: "int16",   # EXPLICIT_INT16
    1: "int32",   # EXPLICIT_INT32
    2: "uint32",  # EXPLICIT_UINT32
    3: "uint64",  # EXPLICIT_UINT64
    4: "float32", # EXPLICIT_FP32
    5: "float64", # EXPLICIT_FP64
    6: "uint8",   # EXPLICIT_UINT8  (WFM#003)
    7: "int8",    # EXPLICIT_INT8   (WFM#003)
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
    n_pts: int
    x_origin: float
    x_increment: float
    ch: list[ChannelHeader]
    raw_data: list[Optional[npt.NDArray]]
    channel_data: list[Optional[npt.NDArray[np.float32]]]

    def __init__(self) -> None:
        """Initialize an empty Tektronix header."""
        self.model = ""
        self.n_pts = 0
        self.x_origin = 0.0
        self.x_increment = 1e-6
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

    def __init__(self) -> None:
        """Initialize the normalized Tektronix wrapper."""
        self.header = Header()

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
    base_dtype = _FORMAT_DTYPE.get(fmt_code, "int16")
    dtype = np.dtype(f"{byte_order}{base_dtype}")
    arr = np.frombuffer(raw_bytes, dtype=dtype)
    if len(arr) > n_pts > 0:
        arr = arr[:n_pts]
    return arr


def from_file(file_name: str) -> TekWaveform:
    """Parse a Tektronix .wfm file and normalize it for `Wfm.from_file()`.

    Handles WFM#001, WFM#002, and WFM#003 formats in both little-endian
    and big-endian byte orders.

    Args:
        file_name: path to a Tektronix .wfm waveform file.

    Returns:
        A `TekWaveform` object whose `header` follows the shape expected
        by `RigolWFM.channel.Channel` and `RigolWFM.wfm.Wfm`.

    Raises:
        ValueError: if the file cannot be parsed as a valid Tektronix waveform.
    """
    data = _read_file_bytes(file_name)

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
        raise ValueError(
            f"File '{file_name}' has unrecognised byte_order field: "
            f"0x{data[0]:02X}{data[1]:02X}"
        )

    # Detect version from version_number string at offset 2 (8 bytes)
    version_str = data[2:10].split(b"\x00")[0].decode("ascii", errors="ignore").strip()
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

    # Waveform label → model identifier
    try:
        label = sfi.waveform_label.split(b"\x00")[0].decode("ascii", errors="ignore").strip()
    except Exception:
        label = ""
    model_str = label or "Tektronix"

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
        raise ValueError(
            f"No waveform data in '{file_name}' (file may be truncated): {exc}"
        ) from exc

    data_start = int(curve.data_start_offset)
    data_end = int(curve.postcharge_start_offset)
    if data_end <= data_start:
        data_end = data_start + n_pts * bytes_per_point

    raw_bytes = bytes(curve_buf[data_start:data_end])
    if not raw_bytes:
        raise ValueError(f"No waveform data in '{file_name}'")

    # Decode ADC samples
    adc = _decode_adc(raw_bytes, fmt_code, byte_order, n_pts)
    n_pts = len(adc)

    # Calibrate to volts:  volts = scale * adc + offset
    dim_scale = float(exp1.dim_scale)
    dim_offset = float(exp1.dim_offset)
    volts = (dim_scale * adc.astype(np.float64) + dim_offset).astype(np.float32)

    # Volts per division: user_scale from user-view data (volts/div)
    volt_per_div = float(exp1.user_scale) if float(exp1.user_scale) != 0 else abs(dim_scale) * 25

    # Time axis: t[i] = dim_offset + (first_valid_sample + i) * dim_scale
    t_scale = float(imp1.dim_scale)
    t_origin = float(imp1.dim_offset) + int(curve.first_valid_sample) * t_scale
    x_increment = t_scale

    # Build normalized objects
    obj = TekWaveform()
    h = obj.header
    h.model = model_str
    h.n_pts = n_pts
    h.x_origin = t_origin
    h.x_increment = x_increment

    # Tektronix .wfm files capture a single channel per file
    slot = 0
    ch = h.ch[slot]
    ch.name = "CH1"
    ch.enabled = True
    ch.coupling = "DC"
    ch.probe_value = 1.0
    ch.volt_per_division = volt_per_div
    ch.volt_scale = dim_scale
    ch.volt_offset = dim_offset

    h.channel_data[slot] = volts

    # raw_data: store as uint8 proxy (high byte for 16-bit, direct for 8-bit)
    adc_arr = adc.astype(np.int16) if bytes_per_point <= 2 else adc.astype(np.int32)
    if bytes_per_point == 2:
        raw8 = (adc_arr.view(np.uint16) >> 8).astype(np.uint8)
    else:
        raw8 = np.full(n_pts, 127, dtype=np.uint8)
    h.raw_data[slot] = raw8

    return obj
