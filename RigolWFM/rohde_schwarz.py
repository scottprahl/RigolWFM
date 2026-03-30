"""
Adapter layer for Rohde & Schwarz RTP oscilloscope waveform exports.

R&S oscilloscopes represented by the checked-in vendor parsers save waveform
captures as an XML metadata file with a `.bin` extension plus a sibling
`.Wfm.bin` payload file containing the sample bytes. The low-level Kaitai
schema only describes the binary payload header and bytes; this module combines
that payload with the XML metadata and normalizes single-acquisition analog
captures into the existing `Wfm` / `Channel` interfaces.
"""

from __future__ import annotations

import os
import re
import xml.etree.ElementTree as ET
from typing import Any, Optional

import numpy as np
import numpy.typing as npt

import RigolWFM.rohde_schwarz_rtp_wfm
from RigolWFM.mso5000 import ChannelHeader, _proxy_raw

_SOURCE_PREFIX = "eRS_SIGNAL_SOURCE_"
_BYTE_ORDER_PREFIX = "eRS_BYTE_ORDER_"
_TRACE_TYPE_PREFIX = "eRS_TRACE_TYPE_"


class Header:
    """Normalized header used by `Wfm.from_file()` for R&S RTP captures."""

    format_code: int
    n_waveforms: int
    n_pts: int
    x_origin: float
    x_increment: float
    x_display_range: float
    model: str
    serial_number: str
    fw_version: str
    ch: list[ChannelHeader]
    raw_data: list[Optional[npt.NDArray[np.uint8]]]
    channel_data: list[Optional[npt.NDArray[np.float32]]]

    def __init__(self) -> None:
        """Initialize an empty normalized header."""
        self.format_code = -1
        self.n_waveforms = 0
        self.n_pts = 0
        self.x_origin = 0.0
        self.x_increment = 1e-6
        self.x_display_range = 0.0
        self.model = ""
        self.serial_number = ""
        self.fw_version = "unknown"
        self.ch = [ChannelHeader(f"CH{i + 1}", enabled=False, unit_code=1) for i in range(4)]
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
        """Return the firmware version embedded in the XML metadata."""
        return self.fw_version or "unknown"

    @property
    def model_number(self) -> str:
        """Return the parsed instrument model string."""
        return self.model


class RohdeSchwarzWaveform:
    """Normalized parser result consumed by `RigolWFM.channel.Channel`."""

    header: Header

    def __init__(self) -> None:
        """Initialize the normalized wrapper."""
        self.header = Header()

    @property
    def parser_name(self) -> str:
        """Return the normalized parser name used by `Wfm.from_file()`."""
        return "rohde_schwarz_bin"

    def __str__(self) -> str:
        """Return a parser tag compatible with the rest of `Wfm.from_file()`."""
        return f"x.{self.parser_name}"


def _load_xml_tags(file_name: str) -> tuple[ET.Element, dict[str, dict[str, str]]]:
    """Parse the XML metadata file and flatten `Name` attributes into a dict."""
    root = ET.parse(file_name).getroot()
    tags: dict[str, dict[str, str]] = {}
    for elem in root.iter():
        name = elem.attrib.get("Name")
        if name and name not in tags:
            tags[name] = elem.attrib
    return root, tags


def _require_tag(tags: dict[str, dict[str, str]], key: str) -> dict[str, str]:
    """Return a required XML tag dictionary or raise a clear error."""
    if key not in tags:
        raise ValueError(f"Rohde & Schwarz metadata is missing required tag '{key}'")
    return tags[key]


def _tag_value(tags: dict[str, dict[str, str]], key: str) -> str:
    """Return the `Value` attribute for a required XML tag."""
    tag = _require_tag(tags, key)
    try:
        return tag["Value"]
    except KeyError as exc:
        raise ValueError(f"Rohde & Schwarz tag '{key}' is missing a Value attribute") from exc


def _tag_float(tags: dict[str, dict[str, str]], key: str) -> float:
    """Return a required XML numeric value as float."""
    raw = _tag_value(tags, key)
    try:
        return float(raw)
    except ValueError as exc:
        raise ValueError(f"Rohde & Schwarz tag '{key}' is not numeric: {raw!r}") from exc


def _tag_int(tags: dict[str, dict[str, str]], key: str) -> int:
    """Return a required XML numeric value as int."""
    raw = _tag_value(tags, key)
    try:
        return int(raw)
    except ValueError as exc:
        raise ValueError(f"Rohde & Schwarz tag '{key}' is not an integer: {raw!r}") from exc


def _strip_prefix(value: str, prefix: str) -> str:
    """Strip a vendor enum prefix when present."""
    return value[len(prefix) :] if value.startswith(prefix) else value


def _source_slot(source_name: str) -> Optional[int]:
    """Map R&S source names like `CH1_TR1` or `C1W1` to zero-based slots."""
    cleaned = _strip_prefix(source_name, _SOURCE_PREFIX).upper()
    match = re.search(r"(?:CH|C)(\d)", cleaned)
    if match is None:
        return None
    slot = int(match.group(1)) - 1
    return slot if 0 <= slot < 4 else None


def _display_name(source_name: str, fallback_slot: int) -> str:
    """Return a stable public-facing channel name."""
    slot = _source_slot(source_name)
    if slot is not None:
        return f"CH{slot + 1}"
    cleaned = _strip_prefix(source_name, _SOURCE_PREFIX).upper()
    return cleaned or f"CH{fallback_slot + 1}"


def _active_sources(tags: dict[str, dict[str, str]]) -> list[tuple[str, int, Optional[str]]]:
    """Return active sources as `(source_name, slot, xml_index)` tuples."""
    multi_export = _strip_prefix(_tag_value(tags, "MultiChannelExport"), "eRS_ONOFF_")
    if multi_export == "ON":
        state = _require_tag(tags, "MultiChannelExportState")
        source = _require_tag(tags, "MultiChannelSource")
        active: list[tuple[str, int, Optional[str]]] = []
        for key in ("I_0", "I_1", "I_2", "I_3"):
            if state.get(key) != "eRS_ONOFF_ON":
                continue
            source_name = source.get(key, "eRS_SIGNAL_SOURCE_NONE")
            slot = _source_slot(source_name)
            if slot is None:
                continue
            active.append((source_name, slot, key))
        return active

    source_name = _tag_value(tags, "Source")
    slot = _source_slot(source_name)
    if slot is None:
        slot = 0
    return [(source_name, slot, None)]


def _channel_vertical_scale(tags: dict[str, dict[str, str]], xml_index: Optional[str]) -> float:
    """Return the volts-per-division setting for one channel."""
    if xml_index is None:
        return _tag_float(tags, "VerticalScale")
    tag = _require_tag(tags, "MultiChannelVerticalScale")
    try:
        return float(tag[xml_index])
    except KeyError as exc:
        raise ValueError(f"Rohde & Schwarz metadata is missing channel scale for {xml_index}") from exc


def _raw_scaling(tags: dict[str, dict[str, str]], xml_index: Optional[str]) -> tuple[float, float]:
    """Return `(conversion_factor, offset)` for raw integer sample formats."""
    quantisation_levels = _tag_int(tags, "NofQuantisationLevels")
    if quantisation_levels <= 0:
        raise ValueError("Rohde & Schwarz metadata reports a non-positive quantisation level count")

    if xml_index is None:
        position_div = _tag_float(tags, "VerticalPosition")
        vertical_scale = _tag_float(tags, "VerticalScale")
        offset = _tag_float(tags, "VerticalOffset")
        step_factor = float(_require_tag(tags, "VerticalScale")["StepFactor"])
    else:
        position_tag = _require_tag(tags, "MultiChannelVerticalPosition")
        scale_tag = _require_tag(tags, "MultiChannelVerticalScale")
        offset_tag = _require_tag(tags, "MultiChannelVerticalOffset")
        try:
            position_div = float(position_tag[xml_index])
            vertical_scale = float(scale_tag[xml_index])
            offset = float(offset_tag[xml_index])
            step_factor = float(scale_tag["StepFactor"])
        except KeyError as exc:
            raise ValueError(f"Rohde & Schwarz multi-channel scaling is missing data for {xml_index}") from exc

    position = position_div * vertical_scale
    conversion_factor = (step_factor * vertical_scale) / float(quantisation_levels)
    return conversion_factor, offset - position


def _expected_format_code(signal_format: str) -> int:
    """Map XML signal-format enums onto the observed payload header codes."""
    if signal_format == "eRS_SIGNAL_FORMAT_INT8BIT":
        return 0
    if signal_format == "eRS_SIGNAL_FORMAT_INT16BIT":
        return 1
    if signal_format == "eRS_SIGNAL_FORMAT_FLOAT":
        return 4
    if signal_format == "eRS_SIGNAL_FORMAT_XYDOUBLEFLOAT":
        return 6
    raise ValueError(f"Unsupported Rohde & Schwarz SignalFormat: {signal_format}")


def _decode_single_acquisition(
    payload: bytes,
    signal_format: str,
    channel_count: int,
    hardware_record_length: int,
    leading_samples: int,
    record_length: int,
    active_sources: list[tuple[str, int, Optional[str]]],
    tags: dict[str, dict[str, str]],
) -> tuple[float, float, list[npt.NDArray[np.float32]]]:
    """Decode a single-acquisition RTP payload into calibrated per-channel arrays."""
    if record_length <= 0:
        raise ValueError("Rohde & Schwarz metadata reports a non-positive RecordLength")
    if hardware_record_length <= 0:
        raise ValueError("Rohde & Schwarz metadata reports a non-positive SignalHardwareRecordLength")
    if leading_samples < 0 or leading_samples + record_length > hardware_record_length:
        raise ValueError(
            "Rohde & Schwarz metadata reports an invalid LeadingSettlingSamples / RecordLength combination"
        )

    expected_rows = hardware_record_length

    if signal_format == "eRS_SIGNAL_FORMAT_FLOAT":
        values = np.frombuffer(payload, dtype="<f4")
        if values.size != expected_rows * channel_count:
            raise ValueError(
                "Rohde & Schwarz float payload length does not match its XML metadata: "
                f"expected {expected_rows * channel_count} float32 values, found {values.size}"
            )
        rows = values.reshape(expected_rows, channel_count)
        x_origin = _tag_float(tags, "XStart")
        x_stop = _tag_float(tags, "XStop")
        x_increment = (x_stop - x_origin) / record_length
        channel_data = [
            rows[leading_samples : leading_samples + record_length, idx].astype(np.float32, copy=True)
            for idx in range(channel_count)
        ]
        return x_origin, x_increment, channel_data

    if signal_format == "eRS_SIGNAL_FORMAT_INT8BIT":
        values = np.frombuffer(payload, dtype=np.int8)
        if values.size != expected_rows * channel_count:
            raise ValueError(
                "Rohde & Schwarz int8 payload length does not match its XML metadata: "
                f"expected {expected_rows * channel_count} values, found {values.size}"
            )
        rows = values.reshape(expected_rows, channel_count)
        x_origin = _tag_float(tags, "XStart")
        x_stop = _tag_float(tags, "XStop")
        x_increment = (x_stop - x_origin) / record_length
        channel_data = []
        for idx, (_, _, xml_index) in enumerate(active_sources):
            factor, offset = _raw_scaling(tags, xml_index)
            volts = rows[leading_samples : leading_samples + record_length, idx].astype(np.float32) * factor + offset
            channel_data.append(volts.astype(np.float32, copy=False))
        return x_origin, x_increment, channel_data

    if signal_format == "eRS_SIGNAL_FORMAT_INT16BIT":
        values = np.frombuffer(payload, dtype="<i2")
        if values.size != expected_rows * channel_count:
            raise ValueError(
                "Rohde & Schwarz int16 payload length does not match its XML metadata: "
                f"expected {expected_rows * channel_count} values, found {values.size}"
            )
        rows = values.reshape(expected_rows, channel_count)
        x_origin = _tag_float(tags, "XStart")
        x_stop = _tag_float(tags, "XStop")
        x_increment = (x_stop - x_origin) / record_length
        channel_data = []
        for idx, (_, _, xml_index) in enumerate(active_sources):
            factor, offset = _raw_scaling(tags, xml_index)
            volts = rows[leading_samples : leading_samples + record_length, idx].astype(np.float32) * factor + offset
            channel_data.append(volts.astype(np.float32, copy=False))
        return x_origin, x_increment, channel_data

    if signal_format == "eRS_SIGNAL_FORMAT_XYDOUBLEFLOAT":
        row_dtype = np.dtype([("time", "<f8"), ("channels", "<f4", (channel_count,))])
        rows = np.frombuffer(payload, dtype=row_dtype)
        if rows.size != expected_rows:
            raise ValueError(
                "Rohde & Schwarz XYDOUBLEFLOAT payload length does not match its XML metadata: "
                f"expected {expected_rows} rows, found {rows.size}"
            )
        window = rows[leading_samples : leading_samples + record_length]
        if window.size != record_length:
            raise ValueError("Rohde & Schwarz XYDOUBLEFLOAT payload is shorter than its requested RecordLength")
        times = window["time"].astype(np.float64, copy=True)
        x_origin = float(times[0])
        x_increment = (
            float(times[1] - times[0])
            if len(times) > 1
            else (_tag_float(tags, "XStop") - _tag_float(tags, "XStart")) / record_length
        )
        channel_data = [window["channels"][:, idx].astype(np.float32, copy=True) for idx in range(channel_count)]
        return x_origin, x_increment, channel_data

    raise ValueError(f"Unsupported Rohde & Schwarz SignalFormat: {signal_format}")


def from_file(file_name: str) -> RohdeSchwarzWaveform:
    """Parse an R&S RTP XML `.bin` file and normalize a single-acquisition capture."""
    root, tags = _load_xml_tags(file_name)
    signal_format = _tag_value(tags, "SignalFormat")
    trace_type = _strip_prefix(_tag_value(tags, "TraceType"), _TRACE_TYPE_PREFIX)
    if trace_type not in {"NORMAL", "AVERAGE"}:
        raise ValueError(f"Unsupported Rohde & Schwarz TraceType: {trace_type}")

    number_of_acquisitions = _tag_int(tags, "NumberOfAcquisitions")
    if number_of_acquisitions != 1:
        raise ValueError(
            "Rohde & Schwarz multi-acquisition / history captures are not yet "
            "supported by the normalized parser. Use the low-level RTP parser "
            "and metadata directly to inspect all acquisitions."
        )

    raw_file_name = os.path.splitext(file_name)[0] + ".Wfm.bin"
    if not os.path.exists(raw_file_name):
        raise ValueError(f"Companion Rohde & Schwarz payload file not found: {raw_file_name}")

    raw = RigolWFM.rohde_schwarz_rtp_wfm.RohdeSchwarzRtpWfm.from_file(raw_file_name)
    expected_format = _expected_format_code(signal_format)
    actual_format = int(raw.format_code)
    if actual_format != expected_format:
        raise ValueError(
            "Rohde & Schwarz payload header format code does not match its XML metadata: "
            f"header={actual_format}, xml={expected_format}"
        )

    hardware_record_length = _tag_int(tags, "SignalHardwareRecordLength")
    if raw.record_length != hardware_record_length:
        raise ValueError(
            "Rohde & Schwarz payload header record length does not match its XML metadata: "
            f"payload={raw.record_length}, xml={hardware_record_length}"
        )

    active_sources = _active_sources(tags)
    if not active_sources:
        raise ValueError("Rohde & Schwarz metadata does not enable any supported analog channels")

    channel_count = len(active_sources)
    record_length = _tag_int(tags, "RecordLength")
    leading_samples = _tag_int(tags, "LeadingSettlingSamples")
    x_origin, x_increment, channel_data = _decode_single_acquisition(
        raw.payload,
        signal_format,
        channel_count,
        hardware_record_length,
        leading_samples,
        record_length,
        active_sources,
        tags,
    )

    obj = RohdeSchwarzWaveform()
    header = obj.header
    header.format_code = actual_format
    header.n_waveforms = channel_count
    header.n_pts = record_length
    header.x_origin = x_origin
    header.x_increment = x_increment
    header.x_display_range = _tag_float(tags, "XStop") - _tag_float(tags, "XStart")
    header.model = "Rohde & Schwarz"
    header.serial_number = ""
    header.fw_version = root.attrib.get("FWVersion", "") or "unknown"

    for idx, (source_name, slot, xml_index) in enumerate(active_sources):
        volts = channel_data[idx]
        raw_proxy = _proxy_raw(volts)
        channel = ChannelHeader(_display_name(source_name, slot), enabled=True, unit_code=1)
        vertical_scale = _channel_vertical_scale(tags, xml_index)
        channel.volt_per_division = abs(vertical_scale)
        channel.volt_scale = abs(vertical_scale)
        header.ch[slot] = channel
        header.channel_data[slot] = volts.astype(np.float32, copy=False)
        header.raw_data[slot] = raw_proxy

    return obj
