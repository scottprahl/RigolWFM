"""
Adapter layer for Rigol MSO7000/DS7000 and MSO8000 binary waveform exports.

`RigolWFM.bin7000_8000` is the generated low-level Kaitai parser for the
UltraVision `.bin` container documented in the 7000 and 8000 manuals, but the
rest of RigolWFM expects a normalized object with fixed channel slots, common
timing fields, and calibrated sample arrays.

This module performs that normalization for analog float32 records. Logic and
other non-analog buffers are detected and rejected explicitly until we have
checked-in fixtures that exercise those paths.

The 7000/8000 binary container is structurally identical to the MSO5000 one.
Shared helper types (ChannelHeader, Header, _channel_slot, etc.) are imported
from `RigolWFM.mso5000` rather than duplicated here.
"""
from __future__ import annotations

from typing import Any

import numpy as np

import RigolWFM.bin7000_8000
from RigolWFM.mso5000 import (
    ChannelHeader,
    Header,
    _channel_slot,
    _estimate_volts_per_division,
    _model_from_frame,
    _proxy_raw,
)


class Mso7000_8000Waveform:
    """Normalized parser result consumed by `Channel`."""

    header: Header

    def __init__(self) -> None:
        """Initialize the normalized wrapper."""
        self.header = Header()

    @property
    def parser_name(self) -> str:
        """Return the normalized parser name used by `Wfm.from_file()`."""
        return "bin7000_8000"

    def __str__(self) -> str:
        """Return a parser tag compatible with the rest of `Wfm.from_file()`."""
        return f"x.{self.parser_name}"


def from_file(file_name: str) -> Mso7000_8000Waveform:
    """Parse a Rigol 7000/8000 `.bin` file and normalize it for `Wfm.from_file()`."""
    Bin70008000: Any = RigolWFM.bin7000_8000.Bin70008000  # type: ignore[attr-defined]
    raw = Bin70008000.from_file(file_name)
    supported_buffer_types = {
        Bin70008000.BufferTypeEnum.normal_float32,
        Bin70008000.BufferTypeEnum.maximum_float32,
        Bin70008000.BufferTypeEnum.minimum_float32,
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
            waveform_type == Bin70008000.WaveformTypeEnum.logic
            or label.upper().startswith("LA")
            or buffer_type == Bin70008000.BufferTypeEnum.digital_u8
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
