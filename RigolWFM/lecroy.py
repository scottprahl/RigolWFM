"""
Adapter layer for Teledyne LeCroy oscilloscope waveform files (.trc).

This module bridges the generated LeCroy KSY parsers and the rest of RigolWFM.
It normalises the binary data into the header/data shape expected by
`RigolWFM.wfm.Wfm` and `RigolWFM.channel`.

Two template versions are supported:

  LECROY_2_3 (346-byte WAVEDESC):
    ksy/lecroy_2_3_le_trc.ksy → RigolWFM/lecroy_2_3_le_trc.py   (LOFIRST / LE)
    ksy/lecroy_2_3_be_trc.ksy → RigolWFM/lecroy_2_3_be_trc.py   (HIFIRST / BE)

  LECROY_1_0 (320-byte WAVEDESC, older format):
    ksy/lecroy_1_0_le_trc.ksy → RigolWFM/lecroy_1_0_le_trc.py  (LOFIRST / LE)
    ksy/lecroy_1_0_be_trc.ksy → RigolWFM/lecroy_1_0_be_trc.py  (HIFIRST / BE)

SCPI prefix
-----------
Files transferred via GPIB/SCPI may carry an IEEE 488.2 block-data prefix of
the form  ``#N<N digits of byte count>``  before the WAVEDESC marker.  This
module searches for ``WAVEDESC`` and strips any such prefix before handing the
bytes to the KSY parser.

Endianness detection
--------------------
COMM_ORDER is a u2 at offset 34 inside the WAVEDESC block.  The low byte at
that position is 0 for big-endian (HIFIRST) and 1 for little-endian (LOFIRST).

LECROY_1_0 calibration:
  volts[i] = VERTICAL_GAIN * adc[i] - ACQ_VERT_OFFSET

LECROY_2_3 calibration:
  volts[i] = VERTICAL_GAIN * adc[i] - VERTICAL_OFFSET

Time axis (both versions):
  t[i] = HORIZ_OFFSET + i * HORIZ_INTERVAL   (i = 0 … WAVE_ARRAY_COUNT − 1)
"""

import io as _io
from typing import Any, Optional

import numpy as np
import numpy.typing as npt
from kaitaistruct import KaitaiStream  # type: ignore[import]

import RigolWFM.channel
import RigolWFM.lecroy_1_0_be_trc
import RigolWFM.lecroy_1_0_le_trc
import RigolWFM.lecroy_2_3_be_trc
import RigolWFM.lecroy_2_3_le_trc

_Lecroy23Le: Any = RigolWFM.lecroy_2_3_le_trc.Lecroy23LeTrc  # type: ignore[attr-defined]
_Lecroy23Be: Any = RigolWFM.lecroy_2_3_be_trc.Lecroy23BeTrc  # type: ignore[attr-defined]
_Lecroy10Le: Any = RigolWFM.lecroy_1_0_le_trc.Lecroy10LeTrc  # type: ignore[attr-defined]
_Lecroy10Be: Any = RigolWFM.lecroy_1_0_be_trc.Lecroy10BeTrc  # type: ignore[attr-defined]

_LECROY_MAGIC = b"WAVEDESC"
_COUPLING_MAP = {
    0: "DC",  # dc_50_ohm
    1: "GND",  # ground
    2: "DC",  # dc_1m_ohm
    3: "GND",  # ground_b
    4: "AC",  # ac_1m_ohm
}


class ChannelHeader:
    """Normalized per-channel metadata for a LeCroy .trc capture."""

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
        """LeCroy voltage data is already calibrated; no additional scaling."""
        return 1.0

    @property
    def y_offset(self) -> float:
        """LeCroy voltage data is already calibrated; no additional offset."""
        return 0.0


class Header:
    """Normalized header used by `Wfm.from_file()` for LeCroy .trc captures."""

    model: str
    n_pts: int
    x_origin: float
    x_increment: float
    ch: list[ChannelHeader]
    raw_data: list[Optional[npt.NDArray]]
    channel_data: list[Optional[npt.NDArray[np.float32]]]

    def __init__(self) -> None:
        """Initialize an empty LeCroy header."""
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
        """Number of sample points."""
        return self.n_pts

    @property
    def firmware_version(self) -> str:
        """LeCroy .trc files do not embed firmware information."""
        return "unknown"

    @property
    def model_number(self) -> str:
        """Oscilloscope instrument name string."""
        return self.model


class LeCroyWaveform:
    """Normalized LeCroy parser result consumed by `Channel`."""

    header: Header

    def __init__(self) -> None:
        """Initialize the normalized LeCroy wrapper."""
        self.header = Header()

    @property
    def parser_name(self) -> str:
        """Return the normalized parser name used by `Wfm.from_file()`."""
        return "lecroy_trc"

    def __str__(self) -> str:
        """Return a parser tag compatible with the rest of `Wfm.from_file()`."""
        return f"x.{self.parser_name}"


def _find_wavedesc(data: bytes) -> int:
    """Return the byte offset of the WAVEDESC marker in data.

    Searches the file for the first plausible 8-byte ASCII string
    ``WAVEDESC`` and validates the surrounding header bytes enough to avoid
    obvious false positives in arbitrary payload data.
    """
    start = 0
    while True:
        pos = data.find(_LECROY_MAGIC, start)
        if pos < 0:
            raise ValueError("WAVEDESC marker not found in file")
        candidate = data[pos:]
        if len(candidate) >= 35 and candidate[34] in (0, 1):
            return pos
        start = pos + 1


def _read_file_bytes(file_name: str) -> bytes:
    """Read file contents, raising ValueError on OS errors."""
    try:
        with open(file_name, "rb") as f:
            return f.read()
    except OSError as exc:
        raise ValueError(f"Cannot open LeCroy file '{file_name}': {exc}") from exc


def from_file(file_name: str) -> LeCroyWaveform:
    """Parse a LeCroy .trc file and normalize it for `Wfm.from_file()`.

    Handles both LECROY_2_3 and LECROY_1_0 WAVEDESC formats.  Files with a
    leading SCPI ``#N<digits>`` block-data prefix are automatically detected
    and stripped before parsing.

    Args:
        file_name: path to a LeCroy .trc waveform file.

    Returns:
        A `LeCroyWaveform` object whose `header` follows the shape expected
        by `RigolWFM.channel.Channel` and `RigolWFM.wfm.Wfm`.

    Raises:
        ValueError: if the file cannot be parsed as a valid LeCroy waveform.
    """
    data = _read_file_bytes(file_name)

    try:
        wavedesc_pos = _find_wavedesc(data)
    except ValueError as exc:
        raise ValueError(f"Not a valid LeCroy file '{file_name}': {exc}") from exc

    # Slice to WAVEDESC so the KSY parser sees offset 0 = start of WAVEDESC
    payload = data[wavedesc_pos:]

    # Determine endianness from COMM_ORDER low byte at WAVEDESC offset 34
    if len(payload) < 35:
        raise ValueError(f"File '{file_name}' WAVEDESC block is too short")
    is_le = payload[34] == 1

    # Determine template version from WAVEDESC offsets 16–31
    template_bytes = payload[16:32]
    template = template_bytes.split(b"\x00")[0].decode("ascii", errors="ignore").strip()
    is_v1 = template == "LECROY_1_0"

    try:
        stream = KaitaiStream(_io.BytesIO(payload))
        if is_v1:
            raw = _Lecroy10Le(stream) if is_le else _Lecroy10Be(stream)
        else:
            raw = _Lecroy23Le(stream) if is_le else _Lecroy23Be(stream)
    except Exception as exc:
        raise ValueError(f"Could not parse LeCroy file '{file_name}': {exc}") from exc

    wd = raw.wavedesc

    # Decode instrument name (null-terminated ASCII, 16 bytes)
    try:
        model_str = wd.instrument_name.split(b"\x00")[0].decode("ascii", errors="ignore").strip()
    except Exception:
        model_str = "LeCroy"

    # --- LECROY_1_0: wave_source is a plain s2, 1-indexed (1=CH1 … 4=CH4) ---
    # --- LECROY_2_3: wave_source is an IntEnum, 0-indexed (0=CH1 … 3=CH4)  ---
    if is_v1:
        wave_source_val = int(wd.wave_source)
        slot = max(0, min(3, wave_source_val - 1))  # 1-indexed → 0-based
    else:
        wave_source_val = getattr(wd.wave_source, "value", int(wd.wave_source))
        slot = max(0, min(3, wave_source_val))

    ch_name = f"CH{slot + 1}"

    coupling_val = getattr(wd.vert_coupling, "value", int(wd.vert_coupling))
    coupling_str = _COUPLING_MAP.get(coupling_val, "DC")

    probe_att = float(getattr(wd, "probe_att", 1.0))
    if probe_att <= 0:
        probe_att = 1.0

    is_16bit = bool(wd.is_16bit)
    n_pts = int(wd.wave_array_count)
    vertical_gain = float(wd.vertical_gain)

    # Calibration offset differs between template versions
    if is_v1:
        vertical_offset = float(wd.acq_vert_offset)
    else:
        vertical_offset = float(wd.vertical_offset)

    try:
        raw_bytes = raw.wave_array_1
    except Exception as exc:
        raise ValueError(f"No waveform data in '{file_name}' (file may be truncated): {exc}") from exc
    if not raw_bytes:
        raise ValueError(f"No waveform data in '{file_name}'")

    # Decode sample array
    byte_order = "<" if is_le else ">"
    if is_16bit:
        dtype = np.dtype(f"{byte_order}i2")
        adc = np.frombuffer(raw_bytes, dtype=dtype).astype(np.int16)
    else:
        adc = np.frombuffer(raw_bytes, dtype=np.int8).copy()

    # Clamp to declared sample count
    if len(adc) > n_pts > 0:
        adc = adc[:n_pts]
    n_pts = len(adc)

    volts = (vertical_gain * adc.astype(np.float64) - vertical_offset).astype(np.float32)

    # MAX_VALUE and MIN_VALUE are ADC counts in both LECROY_1_0 and LECROY_2_3.
    # volt_per_div = (adc_range) * volts_per_count / 8 divisions
    max_value = float(wd.max_value)
    min_value = float(wd.min_value)
    adc_range = max_value - min_value
    volt_per_div = adc_range * abs(vertical_gain) / 8.0 if adc_range != 0 else 1.0

    # Build normalized objects
    obj = LeCroyWaveform()
    h = obj.header
    h.model = model_str or "LeCroy"
    h.n_pts = n_pts
    h.x_origin = float(wd.horiz_offset)
    h.x_increment = float(wd.horiz_interval)

    ch = h.ch[slot]
    ch.name = ch_name
    ch.enabled = True
    ch.coupling = coupling_str
    ch.probe_value = probe_att
    ch.volt_per_division = volt_per_div
    ch.volt_scale = vertical_gain
    ch.volt_offset = vertical_offset

    h.channel_data[slot] = volts

    # raw_data stored as uint8 (high byte for 16-bit, direct cast for 8-bit)
    if is_16bit:
        raw16 = adc.astype(np.int16).view(np.uint16)
        h.raw_data[slot] = (raw16 >> 8).astype(np.uint8)
    else:
        h.raw_data[slot] = adc.view(np.uint8)

    return obj
