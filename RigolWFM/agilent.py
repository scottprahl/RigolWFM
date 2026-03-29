"""
Adapter layer for Agilent / Keysight oscilloscope binary waveform exports.

This module bridges the generated `agilent_bin` Kaitai parser and the rest of
RigolWFM. The reverse-engineered container format comes from the checked-in
`docs/vendors/wavebin-master` sample corpus and parser implementation.

The `AGxx` file family stores one or more waveform records in a simple binary
container. Analog traces are already calibrated and stored as float32 sample
arrays. Digital or logic-style records use `u1` samples in the same container;
those records are skipped by the normalization layer because RigolWFM's public
API is still analog-channel oriented.
"""
from __future__ import annotations

from typing import Any, Optional

import numpy as np
import numpy.typing as npt

import RigolWFM.agilent_bin
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


def from_file(file_name: str) -> AgilentWaveform:
    """Parse an Agilent / Keysight `AGxx` `.bin` file and normalize it."""
    AgilentBin: Any = RigolWFM.agilent_bin.AgilentBin  # type: ignore[attr-defined]
    raw = AgilentBin.from_file(file_name)
    supported_buffer_types = {
        AgilentBin.BufferTypeEnum.normal_float32,
        AgilentBin.BufferTypeEnum.maximum_float32,
        AgilentBin.BufferTypeEnum.minimum_float32,
        AgilentBin.BufferTypeEnum.time_float32,
        AgilentBin.BufferTypeEnum.counts_float32,
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
        data_header = waveform.data_header
        label = wfm_header.waveform_label.strip()
        buffer_type = data_header.buffer_type
        waveform_type = int(wfm_header.waveform_type)

        is_digital = (
            waveform_type == AgilentBin.WaveformTypeEnum.logic
            or buffer_type == AgilentBin.BufferTypeEnum.digital_u8
        )
        if is_digital:
            continue

        if data_header.bytes_per_point != 4 or buffer_type not in supported_buffer_types:
            raise ValueError(
                "Unsupported Agilent/Keysight waveform buffer "
                f"(buffer_type={int(buffer_type)}, "
                f"bytes_per_point={data_header.bytes_per_point}). "
                "Only float32 analog-style waveform buffers are supported."
            )

        slot = _channel_slot(label, analog_slot)
        if slot is None or slot >= 4:
            continue

        data = np.frombuffer(waveform.data_raw, dtype="<f4").copy()
        np.nan_to_num(data, copy=False)
        raw_proxy = _proxy_raw(data)

        if header.n_pts == 0:
            header.n_pts = len(data)
            # `x_display_origin` / `x_display_range` define the horizontal axis
            # used by the reference wavebin viewer and match the checked-in
            # capture summaries more closely than the raw `x_origin` field.
            header.x_origin = wfm_header.x_display_origin
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
        header.channel_data[slot] = data
        header.raw_data[slot] = raw_proxy
        analog_found += 1
        analog_slot += 1

    if analog_found == 0:
        raise ValueError(
            "No supported analog waveform records were found in this "
            "Agilent/Keysight capture."
        )

    return obj
