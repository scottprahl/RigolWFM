"""
Adapter layer for Agilent / Keysight oscilloscope binary waveform exports.

This module bridges the generated `agilent_agxx_bin` Kaitai parser and the rest of
RigolWFM. The container layout is described by the checked-in vendor parsers,
the wavebin sample corpus, and the Agilent 6000 / InfiniiVision 2000 manuals.

The `AGxx` file family stores one or more waveform records in a simple binary
container. Analog traces are already calibrated and stored as float32 sample
arrays. Peak Detect captures can store multiple analog buffers per waveform
header, and segmented-memory captures can repeat the same channel label for
multiple segments.
"""

import math
from typing import Any, Optional

import numpy as np
import numpy.typing as npt

import RigolWFM.agilent_agxx_bin
from RigolWFM.mso5000 import ChannelHeader, _estimate_volts_per_division, _proxy_raw


class Header:
    """Normalized header used by `Wfm.from_file()` for `AGxx` captures."""

    cookie: str
    version: str
    n_waveforms: int
    n_pts: int
    x_origin: float
    x_increment: float
    x_display_range: float
    x_origins: list[Optional[float]]
    x_increments: list[Optional[float]]
    model: str
    serial_number: str
    ch: list[ChannelHeader]
    raw_data: list[Optional[npt.NDArray[np.uint8]]]
    channel_data: list[Optional[npt.NDArray[np.float32]]]

    def __init__(self) -> None:
        """Initialize an empty normalized header."""
        self.cookie = ""
        self.version = ""
        self.n_waveforms = 0
        self.n_pts = 0
        self.x_origin = 0.0
        self.x_increment = 1e-6
        self.x_display_range = 0.0
        self.x_origins = [None] * 4
        self.x_increments = [None] * 4
        self.model = ""
        self.serial_number = ""
        self.ch = [ChannelHeader(f"CH{i + 1}", enabled=False) for i in range(4)]
        self.raw_data = [None] * 4
        self.channel_data = [None] * 4

    @property
    def seconds_per_point(self) -> float:
        """Time between adjacent samples in seconds."""
        return self.x_increment

    @property
    def time_scale(self) -> float:
        """Horizontal time base in seconds per division."""
        if self.x_display_range > 0:
            return self.x_display_range / 10.0
        if self.n_pts > 0 and self.x_increment > 0:
            return self.n_pts * self.x_increment / 10.0
        return 1e-3

    @property
    def points(self) -> int:
        """Number of sample points per enabled analog trace."""
        return self.n_pts

    @property
    def firmware_version(self) -> str:
        """The `AGxx` export container does not embed firmware information."""
        return "unknown"

    @property
    def model_number(self) -> str:
        """Return the parsed instrument model string."""
        return self.model


class AgilentWaveform:
    """Normalized parser result consumed by `RigolWFM.channel.Channel`."""

    header: Header

    def __init__(self) -> None:
        """Initialize the normalized wrapper."""
        self.header = Header()

    @property
    def parser_name(self) -> str:
        """Return the normalized parser name used by `Wfm.from_file()`."""
        return "agilent_bin"

    def __str__(self) -> str:
        """Return a parser tag compatible with the rest of `Wfm.from_file()`."""
        return f"x.{self.parser_name}"


def _frame_parts(frame_string: str) -> tuple[str, str]:
    """Split `MODEL:SERIAL` frame strings into their components."""
    cleaned = frame_string.strip()
    if ":" in cleaned:
        model, serial = cleaned.split(":", 1)
        return model.strip(), serial.strip()
    return cleaned, ""


def _channel_slot(label: str, fallback: int) -> Optional[int]:
    """Map waveform labels onto zero-based analog channel slots."""
    label_upper = label.upper().strip()
    if not label_upper:
        return fallback
    if label_upper in {"EXT", "EXTERNAL"} or label_upper.startswith("LA"):
        return None
    if label_upper.startswith("CH"):
        suffix = label_upper[2:]
    else:
        suffix = label_upper
    try:
        index = int(suffix) - 1
    except ValueError:
        return fallback
    if 0 <= index < 4:
        return index
    return None


def _normalized_channel_name(label: str, slot: int) -> str:
    """Return a stable public-facing channel name."""
    cleaned = label.strip().upper()
    if cleaned.startswith("CH"):
        return cleaned
    if cleaned.isdigit():
        return f"CH{cleaned}"
    return cleaned or f"CH{slot + 1}"


def _is_segmented_waveform(wfm_header: Any) -> bool:
    """Return True when the waveform header represents a saved segment."""
    return bool(wfm_header.segment_index) or not math.isclose(wfm_header.time_tag, 0.0, abs_tol=1e-15)


def from_file(file_name: str) -> AgilentWaveform:
    """Parse an Agilent / Keysight `AGxx` `.bin` file and normalize it."""
    AgilentAgxxBin: Any = RigolWFM.agilent_agxx_bin.AgilentAgxxBin  # type: ignore[attr-defined]
    raw = AgilentAgxxBin.from_file(file_name)
    supported_buffer_types = {
        AgilentAgxxBin.BufferTypeEnum.normal_float32,
        AgilentAgxxBin.BufferTypeEnum.maximum_float32,
        AgilentAgxxBin.BufferTypeEnum.minimum_float32,
    }
    ignored_buffer_types = {
        AgilentAgxxBin.BufferTypeEnum.counts_i32,
        AgilentAgxxBin.BufferTypeEnum.logic_u8,
        AgilentAgxxBin.BufferTypeEnum.digital_u8,
    }

    obj = AgilentWaveform()
    header = obj.header
    header.cookie = raw.file_header.cookie.decode("ascii", errors="ignore")
    header.version = raw.file_header.version
    header.n_waveforms = raw.file_header.n_waveforms

    analog_found = 0
    analog_slot = 0

    for waveform in raw.waveforms:
        wfm_header = waveform.wfm_header
        label = wfm_header.waveform_label.strip()
        waveform_type = int(wfm_header.waveform_type)

        if _is_segmented_waveform(wfm_header):
            raise ValueError(
                "Segmented Agilent/Keysight captures are not yet supported by "
                "the normalized parser. Use RigolWFM.agilent_agxx_bin.AgilentAgxxBin for "
                "low-level access to per-segment waveforms."
            )

        analog_buffers = []
        for buffer in waveform.buffers:
            data_header = buffer.data_header
            buffer_type = data_header.buffer_type
            is_digital = waveform_type == AgilentAgxxBin.WaveformTypeEnum.logic or buffer_type in ignored_buffer_types
            if is_digital:
                continue

            if data_header.bytes_per_point != 4 or buffer_type not in supported_buffer_types:
                raise ValueError(
                    "Unsupported Agilent/Keysight waveform buffer "
                    f"(buffer_type={int(buffer_type)}, "
                    f"bytes_per_point={data_header.bytes_per_point}). "
                    "Only normal, minimum, and maximum float32 waveform buffers "
                    "are supported."
                )

            analog_buffers.append(buffer)

        if not analog_buffers:
            continue

        if len(analog_buffers) > 1:
            raise ValueError(
                "Peak Detect / multi-buffer Agilent/Keysight waveforms are not "
                "yet supported by the normalized parser. Use "
                "RigolWFM.agilent_agxx_bin.AgilentAgxxBin to inspect all buffers."
            )

        slot = _channel_slot(label, analog_slot)
        if slot is None or slot >= 4:
            continue

        if header.channel_data[slot] is not None:
            raise ValueError(
                "Multiple Agilent/Keysight waveform records map to the same "
                "analog channel slot. Repeated channel labels usually indicate "
                "segmented-memory output, which is not yet normalized by "
                "Wfm.from_file()."
            )

        analog_buffer = analog_buffers[0]
        data = np.frombuffer(analog_buffer.data_raw, dtype="<f4").copy()
        if len(data) != wfm_header.n_pts:
            raise ValueError(
                "Agilent/Keysight waveform point count does not match its "
                f"float32 buffer length. Header reports {wfm_header.n_pts}, "
                f"buffer contains {len(data)} samples."
            )
        np.nan_to_num(data, copy=False)
        raw_proxy = _proxy_raw(data)

        if header.n_pts == 0:
            header.n_pts = len(data)
            header.x_origin = wfm_header.x_origin
            header.x_increment = wfm_header.x_increment
            header.x_display_range = wfm_header.x_display_range
            model, serial = _frame_parts(wfm_header.frame_string)
            header.model = model or "Keysight"
            header.serial_number = serial
        elif len(data) != header.n_pts:
            raise ValueError(
                "Agilent/Keysight analog channels have mismatched point counts. "
                f"Expected {header.n_pts}, found {len(data)}."
            )

        unit_code = getattr(wfm_header.y_units, "value", int(wfm_header.y_units))
        channel = ChannelHeader(_normalized_channel_name(label, slot), enabled=True, unit_code=unit_code)
        channel.volt_per_division = _estimate_volts_per_division(data)

        header.ch[slot] = channel
        header.x_origins[slot] = wfm_header.x_origin
        header.x_increments[slot] = wfm_header.x_increment
        header.channel_data[slot] = data
        header.raw_data[slot] = raw_proxy
        analog_found += 1
        analog_slot += 1

    if analog_found == 0:
        raise ValueError("No supported analog waveform records were found in this Agilent/Keysight capture.")

    return obj
