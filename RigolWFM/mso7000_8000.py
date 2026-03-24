"""
Adapter layer for Rigol MSO7000/DS7000 and MSO8000 binary waveform exports.

`RigolWFM.bin7000_8000` is the generated low-level Kaitai parser for the
UltraVision `.bin` container documented in the 7000 and 8000 manuals, but the
rest of RigolWFM expects a normalized object with fixed channel slots, common
timing fields, and calibrated sample arrays.

This module performs that normalization for analog float32 records. Logic and
other non-analog buffers are detected and rejected explicitly until we have
checked-in fixtures that exercise those paths.
"""

from enum import IntEnum

import numpy as np

import RigolWFM.bin7000_8000


class UnitEnum(IntEnum):
    """Unit types used by UltraVision binary waveform exports."""

    unknown = 0
    v = 1
    s = 2
    constant = 3
    a = 4
    db = 5
    hz = 6


class ChannelHeader:
    """Normalized per-channel metadata for 7000/8000 captures."""

    def __init__(self, name, enabled, unit_code=0):
        """Initialize channel metadata."""
        self.name = name
        self.enabled = enabled
        self.unit = UnitEnum(unit_code) if 0 <= unit_code <= 6 else UnitEnum.unknown
        self.inverted = False
        self.probe_value = 1.0
        self.volt_per_division = 1.0
        self.volt_offset = 0.0
        self.volt_scale = 1.0

    @property
    def y_scale(self):
        """7000/8000 `.bin` voltage data is already calibrated."""
        return 1.0

    @property
    def y_offset(self):
        """7000/8000 `.bin` voltage data is already calibrated."""
        return 0.0


class Header:
    """Normalized header used by `Wfm.from_file()` for 7000/8000 captures."""

    def __init__(self):
        """Initialize an empty 7000/8000 header."""
        self.cookie = ""
        self.version = ""
        self.n_waveforms = 0
        self.n_pts = 0
        self.x_origin = 0.0
        self.x_increment = 1e-6
        self.x_display_range = 0.0
        self.model = ""
        self.ch = []
        self.raw_data = [None] * 4
        self.channel_data = [None] * 4

    @property
    def seconds_per_point(self):
        """Time between samples in seconds."""
        return self.x_increment

    @property
    def time_scale(self):
        """Horizontal time base in seconds per division."""
        if self.x_display_range > 0:
            return self.x_display_range / 10.0
        if self.n_pts > 0 and self.x_increment > 0:
            return self.n_pts * self.x_increment / 10.0
        return 1e-3

    @property
    def time_offset(self):
        """Horizontal offset relative to the screen center."""
        if self.n_pts > 0:
            return self.n_pts * self.x_increment / 2.0 - self.x_origin
        return -self.x_origin

    @property
    def points(self):
        """Number of sample points."""
        return self.n_pts

    @property
    def firmware_version(self):
        """Return the file format version string."""
        return self.version

    @property
    def model_number(self):
        """Return the scope model string if present."""
        return self.model


class Mso7000_8000Waveform:
    """Normalized parser result consumed by `Channel`."""

    def __init__(self):
        """Initialize the normalized wrapper."""
        self.header = Header()

    @property
    def parser_name(self):
        """Return the normalized parser name used by `Wfm.from_file()`."""
        return "bin7000_8000"

    def __str__(self):
        """Return a parser tag compatible with the rest of `Wfm.from_file()`."""
        return f"x.{self.parser_name}"


def _channel_slot(label, fallback):
    """Map channel labels like `CH2` to zero-based channel slots."""
    label_upper = label.upper()
    if label_upper.startswith("LA"):
        return None
    if label_upper.startswith("CH"):
        try:
            index = int(label_upper[2:]) - 1
            if 0 <= index < 4:
                return index
        except ValueError:
            pass
    return fallback


def _estimate_volts_per_division(values):
    """Estimate a readable volts/division from calibrated samples."""
    if values.size == 0:
        return 1.0

    finite = values[np.isfinite(values)]
    if finite.size == 0:
        return 1.0

    span = float(np.max(finite) - np.min(finite))
    if span <= 0:
        return max(abs(float(finite[0])) / 4.0, 1e-3)
    return max(span / 8.0, 1e-3)


def _proxy_raw(values):
    """Create a stable uint8 proxy for calibrated volt samples."""
    if values.size == 0:
        return np.empty((0,), dtype=np.uint8)

    finite = values[np.isfinite(values)]
    if finite.size == 0:
        return np.full(values.shape, 127, dtype=np.uint8)

    low = float(np.min(finite))
    high = float(np.max(finite))
    if high <= low:
        return np.full(values.shape, 127, dtype=np.uint8)

    center = (high + low) / 2.0
    half_span = max((high - low) / 2.0, 1e-12)
    raw = 127.0 - 127.0 * (values.astype(np.float64) - center) / half_span
    return np.clip(np.rint(raw), 0, 255).astype(np.uint8)


def _model_from_frame(frame_string):
    """Extract the model name from `MODEL:SERIAL` frame strings."""
    if ":" in frame_string:
        return frame_string.split(":", 1)[0]
    return frame_string


def from_file(file_name):
    """Parse a Rigol 7000/8000 `.bin` file and normalize it for `Wfm.from_file()`."""
    raw = RigolWFM.bin7000_8000.Bin70008000.from_file(file_name)
    supported_buffer_types = {
        RigolWFM.bin7000_8000.Bin70008000.BufferTypeEnum.normal_float32,
        RigolWFM.bin7000_8000.Bin70008000.BufferTypeEnum.maximum_float32,
        RigolWFM.bin7000_8000.Bin70008000.BufferTypeEnum.minimum_float32,
    }

    obj = Mso7000_8000Waveform()
    header = obj.header
    header.cookie = raw.file_header.cookie.decode("ascii", errors="ignore")
    header.version = raw.file_header.version
    header.n_waveforms = raw.file_header.n_waveforms
    header.ch = [ChannelHeader(f"CH{i + 1}", enabled=False) for i in range(4)]

    analog_slot = 0
    for waveform in raw.waveforms:
        wfm_header = waveform.wfm_header
        data_header = waveform.data_header
        label = wfm_header.waveform_label.strip()
        waveform_type = int(wfm_header.waveform_type)
        buffer_type = data_header.buffer_type

        if (
            waveform_type == RigolWFM.bin7000_8000.Bin70008000.WaveformTypeEnum.logic
            or label.upper().startswith("LA")
            or buffer_type == RigolWFM.bin7000_8000.Bin70008000.BufferTypeEnum.digital_u8
        ):
            raise ValueError(
                "Unsupported 7000/8000 logic waveform record. "
                "Only analog float32 waveform buffers are currently supported."
            )

        if buffer_type not in supported_buffer_types or data_header.bytes_per_point != 4:
            raise ValueError(
                "Unsupported 7000/8000 waveform buffer "
                f"(buffer_type={int(buffer_type)}, "
                f"bytes_per_point={data_header.bytes_per_point}). "
                "Only float32 analog buffers are currently supported."
            )

        slot = _channel_slot(label, analog_slot)
        if slot is None or slot >= 4:
            continue

        data = np.frombuffer(waveform.data_raw, dtype="<f4").copy()
        np.nan_to_num(data, copy=False)
        raw_proxy = _proxy_raw(data)

        if header.n_pts == 0:
            header.n_pts = len(data)
            header.x_increment = wfm_header.x_increment
            header.x_origin = wfm_header.x_origin
            header.x_display_range = wfm_header.x_display_range
            header.model = _model_from_frame(wfm_header.frame_string)
        elif len(data) != header.n_pts:
            raise ValueError(
                "7000/8000 analog channels have mismatched point counts. "
                f"Expected {header.n_pts}, found {len(data)}."
            )

        unit_code = getattr(wfm_header.y_units, "value", int(wfm_header.y_units))
        ch_name = label or f"CH{slot + 1}"
        channel = ChannelHeader(ch_name, enabled=True, unit_code=unit_code)
        channel.volt_per_division = _estimate_volts_per_division(data)

        header.ch[slot] = channel
        header.channel_data[slot] = data
        header.raw_data[slot] = raw_proxy
        analog_slot += 1

    return obj
