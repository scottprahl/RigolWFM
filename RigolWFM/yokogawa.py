"""
Adapter layer for Yokogawa ASCII-header waveform files (.wfm).

This parser matches the single-file Yokogawa import path used by the vendor
MATLAB readers in ``docs/vendors/SMASHtoolbox``: an ASCII header at the start
of the file followed by a packed binary sample array.

The second text line contains a whitespace-prefixed, comma-delimited set of
``KEY:VALUE`` pairs.  The vendor reader uses the following fields:

  NR_PT  - number of points
  PT_O   - trigger point offset
  XIN    - seconds per point
  YMU    - vertical scale factor
  YOF    - vertical offset
  BIT    - sample width in bits
  BYT    - sample width in bytes

Voltage calibration:
  volts[i] = YOF + YMU * raw[i]

Time axis:
  t[i] = XIN * (i - PT_O)

The MATLAB implementation reads the binary payload as 32-bit floats.  This
adapter mirrors that behavior and currently supports only ``BIT=32`` and
``BYT=4`` captures.
"""
from __future__ import annotations

from typing import Optional

import numpy as np
import numpy.typing as npt

import RigolWFM.channel


class ChannelHeader:
    """Normalized per-channel metadata for a Yokogawa .wfm capture."""

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
        """Yokogawa voltage data is already calibrated; no extra scaling."""
        return 1.0

    @property
    def y_offset(self) -> float:
        """Yokogawa voltage data is already calibrated; no extra offset."""
        return 0.0


class Header:
    """Normalized header used by `Wfm.from_file()` for Yokogawa .wfm captures."""

    model: str
    n_pts: int
    x_origin: float
    x_increment: float
    ch: list[ChannelHeader]
    raw_data: list[Optional[npt.NDArray]]
    channel_data: list[Optional[npt.NDArray[np.float32]]]

    def __init__(self) -> None:
        """Initialize an empty Yokogawa header."""
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
        """Yokogawa `.wfm` files do not embed firmware information."""
        return "unknown"

    @property
    def model_number(self) -> str:
        """Return the normalized instrument name."""
        return self.model


class YokogawaWaveform:
    """Normalized Yokogawa parser result consumed by `Channel`."""

    header: Header

    def __init__(self) -> None:
        """Initialize the normalized Yokogawa wrapper."""
        self.header = Header()

    @property
    def parser_name(self) -> str:
        """Return the normalized parser name used by `Wfm.from_file()`."""
        return "yokogawa_wfm"

    def __str__(self) -> str:
        """Return a parser tag compatible with the rest of `Wfm.from_file()`."""
        return f"x.{self.parser_name}"


def _read_file_bytes(file_name: str) -> bytes:
    try:
        with open(file_name, "rb") as f:
            return f.read()
    except OSError as exc:
        raise ValueError(f"Cannot open Yokogawa file '{file_name}': {exc}") from exc


def _parse_info_line(data: bytes) -> dict[str, str]:
    prefix = data[:1024].decode("latin-1", errors="ignore")
    lines = prefix.splitlines()
    if len(lines) < 2:
        raise ValueError("Yokogawa header is missing the second metadata line")

    second = lines[1]
    parts = second.split(None, 1)
    if len(parts) < 2:
        raise ValueError("Yokogawa metadata line does not contain KEY:VALUE fields")

    info: dict[str, str] = {}
    for fragment in parts[1].split(","):
        fragment = fragment.strip()
        if not fragment or ":" not in fragment:
            continue
        key, value = fragment.split(":", 1)
        info[key.strip().replace(".", "_")] = value.strip()
    return info


def _require_float(info: dict[str, str], key: str) -> float:
    raw = info.get(key)
    if raw is None:
        raise ValueError(f"Yokogawa header is missing required field '{key}'")
    try:
        return float(raw)
    except ValueError as exc:
        raise ValueError(f"Yokogawa header field '{key}' is not numeric: {raw!r}") from exc


def _require_int(info: dict[str, str], key: str) -> int:
    return int(_require_float(info, key))


def from_file(file_name: str) -> YokogawaWaveform:
    """Parse a Yokogawa single-file `.wfm` capture and normalize it."""
    data = _read_file_bytes(file_name)
    info = _parse_info_line(data)

    n_pts = _require_int(info, "NR_PT")
    pt_off = _require_float(info, "PT_O")
    x_increment = _require_float(info, "XIN")
    y_scale = _require_float(info, "YMU")
    y_offset = _require_float(info, "YOF")
    bit_width = _require_int(info, "BIT")
    byte_width = _require_int(info, "BYT")

    if bit_width != 32 or byte_width != 4:
        raise ValueError(
            f"Unsupported Yokogawa sample format in '{file_name}': "
            f"BIT={bit_width}, BYT={byte_width}; only 32-bit float samples are supported"
        )

    data_bytes = n_pts * byte_width
    header_bytes = len(data) - data_bytes
    if header_bytes < 0:
        raise ValueError(f"Yokogawa file '{file_name}' is shorter than its declared sample payload")

    payload = data[header_bytes:]
    if len(payload) != data_bytes:
        raise ValueError(
            f"Yokogawa file '{file_name}' has inconsistent payload size: "
            f"expected {data_bytes} bytes, found {len(payload)}"
        )

    raw = np.frombuffer(payload, dtype="<f4")
    volts = (y_offset + y_scale * raw.astype(np.float64)).astype(np.float32)

    obj = YokogawaWaveform()
    h = obj.header
    h.model = "Yokogawa"
    h.n_pts = len(volts)
    h.x_origin = -pt_off * x_increment
    h.x_increment = x_increment

    ch = h.ch[0]
    ch.name = "CH1"
    ch.enabled = True
    ch.coupling = "DC"
    ch.probe_value = 1.0
    ch.volt_per_division = abs(y_scale) * 32.0 if y_scale != 0 else 1.0
    ch.volt_scale = y_scale
    ch.volt_offset = y_offset

    h.channel_data[0] = volts
    h.raw_data[0] = np.full(len(volts), 127, dtype=np.uint8)

    return obj
