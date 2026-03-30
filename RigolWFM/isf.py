"""
Adapter layer for Tektronix ISF (Internal Save Format) oscilloscope files (.isf).

Normalises the parsed KSY data into the header/data shape expected by
`RigolWFM.wfm.Wfm` and `RigolWFM.channel`.

File structure
--------------
  <text_header> '#' <n_digits> <byte_count_str> <curve_data>

The text header is a semicolon-delimited sequence of KEY VALUE pairs.  Field
names appear in a long form (older firmware) or short form (newer firmware):

  Long form:   BYT_NR, BIT_NR, ENCDG, BN_FMT, BYT_OR, WFID, NR_PT,
               PT_FMT, XUNIT, XINCR, XZERO, PT_OFF, YUNIT, YMULT, YOFF, YZERO
  Short form:  BYT_N,  BIT_N,  ENC,   BN_F,   BYT_O,  WFI,  NR_P,
               PT_F,   XUN,    XIN,   XZE,    PT_O,   YUN,  YMU,  YOF,  YZE

Voltage calibration
-------------------
  volts[i] = YZERO + YMULT * (adc[i] - YOFF)

Time axis (PT_FMT = "Y")
-------------------------
  t[i] = XZERO + XINCR * (i - PT_OFF)   (i = 0 … NR_PT-1)

Envelope mode (PT_FMT = "ENV")
-------------------------------
  sample_count = NR_PT / 2
  adc_min[i] = adc[2*i]
  adc_max[i] = adc[2*i + 1]
  t[i] = XZERO + XINCR * (2*i - PT_OFF)
"""

from __future__ import annotations

import io as _io
import re
from typing import Any, Optional

import numpy as np
import numpy.typing as npt
from kaitaistruct import KaitaiStream  # type: ignore[import]

import RigolWFM.channel
import RigolWFM.tektronix_internal_isf

_TektronixInternalIsf: Any = RigolWFM.tektronix_internal_isf.TektronixInternalIsf  # type: ignore[attr-defined]

# Maps both long-form and short-form field names to a canonical key
_FIELD_ALIASES: dict[str, str] = {
    # bytes per sample
    "BYT_NR": "byt_nr",
    "BYT_N": "byt_nr",
    # bytes per point — synonym used in some headers
    "BN_FMT": "bn_fmt",
    "BN_F": "bn_fmt",
    # byte order
    "BYT_OR": "byt_or",
    "BYT_O": "byt_or",
    # waveform identifier / label
    "WFID": "wfid",
    "WFI": "wfid",
    # number of points
    "NR_PT": "nr_pt",
    "NR_P": "nr_pt",
    # point format
    "PT_FMT": "pt_fmt",
    "PT_F": "pt_fmt",
    # x increment (time per sample)
    "XINCR": "xincr",
    "XIN": "xincr",
    # x zero
    "XZERO": "xzero",
    "XZE": "xzero",
    # point offset
    "PT_OFF": "pt_off",
    "PT_O": "pt_off",
    # y multiplier
    "YMULT": "ymult",
    "YMU": "ymult",
    # y offset (ADC count)
    "YOFF": "yoff",
    "YOF": "yoff",
    # y zero (baseline volts)
    "YZERO": "yzero",
    "YZE": "yzero",
    # volts per division (optional)
    "VSCALE": "vscale",
}


def _parse_header(text: str) -> dict[str, str]:
    """Parse an ISF text header into a canonical field dict.

    Handles both long-form and short-form field names, and strips the
    optional ':WFMP:' SCPI prefix from field names.

    Args:
        text: the raw ASCII header string (without the trailing '#').

    Returns:
        dict mapping canonical field name (e.g. ``'nr_pt'``) to raw string value.
    """
    result: dict[str, str] = {}
    for fragment in text.split(";"):
        fragment = fragment.strip()
        if not fragment:
            continue
        # Strip optional :WFMP: or :CURVE / :CURV prefix
        fragment = re.sub(r"^:[A-Z]+:", "", fragment)
        # Split into key and value on first whitespace
        parts = fragment.split(None, 1)
        if len(parts) < 2:
            continue
        key_raw = parts[0].upper()
        value = parts[1].strip().strip('"')
        canonical = _FIELD_ALIASES.get(key_raw)
        if canonical is not None:
            result[canonical] = value
    return result


def _float_field(fields: dict[str, str], key: str, default: float = 0.0) -> float:
    """Return a float from the header dict, falling back to ``default``."""
    raw = fields.get(key)
    if raw is None:
        return default
    try:
        return float(raw)
    except ValueError:
        return default


def _int_field(fields: dict[str, str], key: str, default: int = 0) -> int:
    """Return an int from the header dict, falling back to ``default``."""
    raw = fields.get(key)
    if raw is None:
        return default
    try:
        return int(float(raw))
    except ValueError:
        return default


# ---------------------------------------------------------------------------
# Normalized header objects (same shape as tek.py's Header / ChannelHeader)
# ---------------------------------------------------------------------------


class ChannelHeader:
    """Normalized per-channel metadata for a Tektronix ISF capture."""

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
        """ISF voltage data is already calibrated; no additional scaling."""
        return 1.0

    @property
    def y_offset(self) -> float:
        """ISF voltage data is already calibrated; no additional offset."""
        return 0.0


class Header:
    """Normalized header used by `Wfm.from_file()` for Tektronix ISF captures."""

    model: str
    trace_label: str
    n_pts: int
    x_origin: float
    x_increment: float
    ch: list[ChannelHeader]
    raw_data: list[Optional[npt.NDArray]]
    channel_data: list[Optional[npt.NDArray[np.float32]]]

    def __init__(self) -> None:
        """Initialize an empty ISF header."""
        self.model = ""
        self.trace_label = ""
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
        """ISF files do not embed firmware version information."""
        return "unknown"

    @property
    def model_number(self) -> str:
        """Oscilloscope instrument label from the waveform identifier field."""
        return self.model


class IsfWaveform:
    """Normalized ISF parser result consumed by `Channel`."""

    header: Header

    def __init__(self) -> None:
        """Initialize the normalized ISF wrapper."""
        self.header = Header()

    @property
    def parser_name(self) -> str:
        """Return the normalized parser name used by `Wfm.from_file()`."""
        return "tek_isf"

    def __str__(self) -> str:
        """Return a parser tag compatible with the rest of `Wfm.from_file()`."""
        return f"x.{self.parser_name}"


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def from_file(file_name: str) -> IsfWaveform:
    """Parse a Tektronix ISF file and normalize it for `Wfm.from_file()`.

    Args:
        file_name: path to a Tektronix ``.isf`` waveform file.

    Returns:
        An `IsfWaveform` object whose ``header`` follows the shape expected
        by `RigolWFM.channel.Channel` and `RigolWFM.wfm.Wfm`.

    Raises:
        ValueError: if the file cannot be read or does not look like a valid
                    Tektronix ISF file.
    """
    try:
        with open(file_name, "rb") as f:
            data = f.read()
    except OSError as exc:
        raise ValueError(f"Cannot open ISF file '{file_name}': {exc}") from exc

    try:
        parsed = _TektronixInternalIsf(KaitaiStream(_io.BytesIO(data)))
        header_text: str = parsed.header_text
        curve_bytes: bytes = bytes(parsed.curve_data)
    except Exception as exc:
        raise ValueError(f"Could not parse ISF file '{file_name}': {exc}") from exc

    fields = _parse_header(header_text)

    # --- Metadata ---
    nr_pt = _int_field(fields, "nr_pt", 0)
    byt_nr = _int_field(fields, "byt_nr", 2)
    byt_or = fields.get("byt_or", "MSB").upper()
    pt_fmt = fields.get("pt_fmt", "Y").upper()
    wfid = fields.get("wfid", "")

    xincr = _float_field(fields, "xincr", 1e-6)
    xzero = _float_field(fields, "xzero", 0.0)
    pt_off = _float_field(fields, "pt_off", 0.0)
    ymult = _float_field(fields, "ymult", 1.0)
    yoff = _float_field(fields, "yoff", 0.0)
    yzero = _float_field(fields, "yzero", 0.0)
    vscale = _float_field(fields, "vscale", 0.0)

    # --- Endianness ---
    byte_order = ">" if byt_or == "MSB" else "<"

    # --- Trim trailing newline that some ISF files append after the data ---
    # Only strip CR/LF bytes; do NOT strip null bytes since they are valid
    # sample data (e.g. the low byte of a zero-valued int16 sample).
    curve_bytes = curve_bytes.rstrip(b"\n\r")

    # --- Decode ADC samples ---
    if byt_nr == 1:
        dtype = np.dtype(f"{byte_order}i1")
    else:
        dtype = np.dtype(f"{byte_order}i2")

    adc_all = np.frombuffer(curve_bytes, dtype=dtype)

    # --- Handle envelope mode ---
    is_env = pt_fmt == "ENV"
    if is_env and len(adc_all) >= 2:
        adc_min = adc_all[0::2]
        adc_max = adc_all[1::2]
        n_pts = len(adc_min)
        # Use the average of min/max as the representative trace
        adc = (adc_min.astype(np.float64) + adc_max.astype(np.float64)) / 2.0
    else:
        adc = adc_all.astype(np.float64)
        n_pts = len(adc)

    if 0 < nr_pt < n_pts:
        adc = adc[:nr_pt]
        n_pts = nr_pt

    # --- Calibrate to volts ---
    volts = (yzero + ymult * (adc - yoff)).astype(np.float32)

    # --- Build time axis ---
    if is_env:
        t0 = xzero + (0 * 2 - pt_off) * xincr
        t_step = xincr * 2
    else:
        t0 = xzero - pt_off * xincr
        t_step = xincr

    # --- Volts per division ---
    if vscale != 0.0:
        volt_per_div = abs(vscale)
    elif ymult != 0.0:
        # estimate: range ≈ 8 divs × 32 counts/div for int16
        volt_per_div = abs(ymult) * 32.0
    else:
        volt_per_div = 1.0

    # --- Build raw proxy (high byte of int16, or direct for int8) ---
    if byt_nr == 2:
        raw8 = (adc.astype(np.int16).view(np.uint16) >> 8).astype(np.uint8)
    else:
        raw8 = adc.astype(np.int8).view(np.uint8)

    # --- Assemble normalized objects ---
    obj = IsfWaveform()
    h = obj.header
    h.model = "Tektronix"
    h.trace_label = wfid
    h.n_pts = n_pts
    h.x_origin = t0
    h.x_increment = t_step

    slot = 0
    ch = h.ch[slot]
    ch.name = "CH1"
    ch.enabled = True
    ch.coupling = "DC"
    ch.probe_value = 1.0
    ch.volt_per_division = volt_per_div
    ch.volt_scale = ymult
    ch.volt_offset = yzero - ymult * yoff

    h.channel_data[slot] = volts
    h.raw_data[slot] = raw8

    return obj
