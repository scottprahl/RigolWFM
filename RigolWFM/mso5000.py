"""
Adapter layer for Rigol MSO5000-family binary waveform exports.

`RigolWFM.rigol_mso5000_bin` is the generated low-level Kaitai parser for the
exported `.bin` container, but the rest of RigolWFM expects a normalized object
with fixed analog channel slots, common timing fields, and decoded sample
arrays.

This module performs that normalization for standard RG01 captures, including
analog float32 records and logic-analyzer records such as the checked-in
`MSO5074-C.bin` fixture.
"""

import os
from enum import IntEnum
from typing import Any, Optional

import numpy as np
import numpy.typing as npt

import RigolWFM.rigol_mso5000_bin


class UnitEnum(IntEnum):
    """Unit types used by MSO5000 waveform exports."""

    unknown = 0
    v = 1
    s = 2
    constant = 3
    a = 4
    db = 5
    hz = 6


class ChannelHeader:
    """Normalized per-channel metadata for MSO5000 captures."""

    name: str
    enabled: bool
    unit: UnitEnum
    inverted: bool
    probe_value: float
    volt_per_division: float
    volt_offset: float
    volt_scale: float

    def __init__(self, name: str, enabled: bool, unit_code: int = 0) -> None:
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
    def y_scale(self) -> float:
        """MSO5000 `.bin` voltage data is already calibrated."""
        return 1.0

    @property
    def y_offset(self) -> float:
        """MSO5000 `.bin` voltage data is already calibrated."""
        return 0.0


class Header:
    """Normalized header used by `Wfm.from_file()` for MSO5000 captures."""

    cookie: str
    version: str
    n_waveforms: int
    n_pts: int
    x_origin: float
    x_increment: float
    x_display_range: float
    model: str
    ch: list[ChannelHeader]
    raw_data: list[Optional[npt.NDArray[np.uint8]]]
    channel_data: list[Optional[npt.NDArray[np.float32]]]

    def __init__(self) -> None:
        """Initialize an empty MSO5000 header."""
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
    def seconds_per_point(self) -> float:
        """Time between samples in seconds."""
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
    def time_offset(self) -> float:
        """Horizontal offset relative to the screen center."""
        if self.n_pts > 0:
            return self.n_pts * self.x_increment / 2.0 - self.x_origin
        return -self.x_origin

    @property
    def points(self) -> int:
        """Number of sample points."""
        return self.n_pts

    @property
    def firmware_version(self) -> str:
        """Return the file format version string."""
        return self.version

    @property
    def model_number(self) -> str:
        """Return the scope model string if present."""
        return self.model


class Mso5000Waveform:
    """Normalized MSO5000 parser result consumed by `Channel`."""

    header: Header
    logic_channels: dict[str, npt.NDArray[np.uint8]]
    logic_observed_channels: dict[str, npt.NDArray[np.uint8]]
    logic_mapping: str
    logic_x_increment: float | None
    logic_x_origin: float | None

    def __init__(self) -> None:
        """Initialize the normalized MSO5000 wrapper."""
        self.header = Header()
        self.logic_channels = {}
        self.logic_observed_channels = {}
        self.logic_mapping = ""
        self.logic_x_increment = None
        self.logic_x_origin = None

    @property
    def parser_name(self) -> str:
        """Return the normalized parser name used by `Wfm.from_file()`."""
        return "bin5000"

    def __str__(self) -> str:
        """Return a parser tag compatible with the rest of `Wfm.from_file()`."""
        return f"x.{self.parser_name}"


def _channel_slot(label: str, fallback: int) -> Optional[int]:
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


def _estimate_volts_per_division(values: npt.NDArray[np.float32]) -> float:
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


def _proxy_raw(values: npt.NDArray[np.float32]) -> npt.NDArray[np.uint8]:
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


def _model_from_frame(frame_string: str) -> str:
    """Extract the model name from `MODEL:SERIAL` frame strings."""
    if ":" in frame_string:
        return frame_string.split(":", 1)[0]
    return frame_string


def _expected_rg01_file_size(raw: Any) -> int:
    """Return the expected byte size for a standard RG01 file."""
    total = 12
    for waveform in raw.waveforms:
        total += waveform.wfm_header.header_size
        total += waveform.data_header.header_size
        total += waveform.data_header.buffer_size
    return total


def _looks_like_malformed_5074(file_name: str) -> bool:
    """Return True for the old concatenated MSO5074 export style we no longer support."""
    with open(file_name, "rb") as handle:
        raw = handle.read()

    return (
        raw.startswith(b"RG01")
        and raw.count(b"RG01") > 1
        and len(raw) >= 16
        and int.from_bytes(raw[12:16], "little") == 144
    )


def _validate_standard_rg01_layout(file_name: str, raw: Any) -> None:
    """Reject malformed concatenated RG01 files that are not standard MSO5000 exports."""
    expected = _expected_rg01_file_size(raw)
    actual = os.path.getsize(file_name)
    if expected != actual and _looks_like_malformed_5074(file_name):
        raise ValueError(
            "Unsupported malformed MSO5074 concatenated RG01 export. "
            "Use a standard MSO5000/MSO5074 RG01 waveform file instead."
        )


def _logic_byte_samples(data_header: Any, data_raw: bytes) -> npt.NDArray[np.uint8]:
    """Decode a logic-analyzer buffer into one byte per sample."""
    buffer_type = data_header.buffer_type
    bytes_per_point = data_header.bytes_per_point

    if int(buffer_type) == 6 and bytes_per_point == 1:
        return np.frombuffer(data_raw, dtype=np.uint8).copy()

    if int(buffer_type) == 5 and bytes_per_point == 4:
        data = np.frombuffer(data_raw, dtype="<f4").copy()
        np.nan_to_num(data, copy=False)
        return np.clip(data, 0, 255).astype(np.uint8)

    raise ValueError(
        "Unsupported MSO5000 logic waveform buffer "
        f"(buffer_type={int(buffer_type)}, bytes_per_point={bytes_per_point})."
    )


def _logic_bit_traces(samples: npt.NDArray[np.uint8], bit_base: int) -> dict[str, npt.NDArray[np.uint8]]:
    """Expand packed logic samples into named digital traces."""
    traces: dict[str, npt.NDArray[np.uint8]] = {}
    for bit in range(8):
        traces[f"D{bit_base + bit}"] = ((samples >> bit) & 1).astype(np.uint8)
    return traces


def from_file(file_name: str) -> Mso5000Waveform:
    """Parse a Rigol MSO5000 `.bin` file and normalize it for `Wfm.from_file()`."""
    RigolMso5000Bin: Any = RigolWFM.rigol_mso5000_bin.RigolMso5000Bin  # type: ignore[attr-defined]
    try:
        raw = RigolMso5000Bin.from_file(file_name)
    except Exception as exc:
        if _looks_like_malformed_5074(file_name):
            raise ValueError(
                "Unsupported malformed MSO5074 concatenated RG01 export. "
                "Use a standard MSO5000/MSO5074 RG01 waveform file instead."
            ) from exc
        raise

    _validate_standard_rg01_layout(file_name, raw)
    supported_buffer_types = {
        RigolMso5000Bin.BufferTypeEnum.normal_float32,
        RigolMso5000Bin.BufferTypeEnum.maximum_float32,
        RigolMso5000Bin.BufferTypeEnum.minimum_float32,
        RigolMso5000Bin.BufferTypeEnum.time_float32,
        RigolMso5000Bin.BufferTypeEnum.counts_float32,
    }

    obj = Mso5000Waveform()
    header = obj.header
    header.cookie = raw.file_header.cookie.decode("ascii", errors="ignore")
    header.version = raw.file_header.version
    header.n_waveforms = raw.file_header.n_waveforms
    header.ch = [ChannelHeader(f"CH{i + 1}", enabled=False) for i in range(4)]

    analog_slot = 0
    logic_slot = 0
    for waveform in raw.waveforms:
        wfm_header = waveform.wfm_header
        data_header = waveform.data_header
        label = wfm_header.waveform_label.strip()
        waveform_type = int(wfm_header.waveform_type)
        buffer_type = data_header.buffer_type
        point_count = int(wfm_header.n_pts)

        if header.n_pts == 0:
            header.n_pts = point_count
            header.x_increment = wfm_header.x_increment
            header.x_origin = wfm_header.x_origin
            header.x_display_range = wfm_header.x_display_range
            header.model = _model_from_frame(wfm_header.frame_string)

        if (
            waveform_type == RigolMso5000Bin.WaveformTypeEnum.logic
            or label.upper().startswith("LA")
            or buffer_type == RigolMso5000Bin.BufferTypeEnum.digital_u8
        ):
            samples = _logic_byte_samples(data_header, waveform.data_raw)
            if len(samples) != point_count:
                raise ValueError(
                    "MSO5000 logic waveform point count does not match the RG01 header. "
                    f"Expected {point_count}, found {len(samples)}."
                )

            bit_base = 8 * logic_slot
            obj.logic_channels.update(_logic_bit_traces(samples, bit_base))
            logic_slot += 1
            obj.logic_x_increment = wfm_header.x_increment
            obj.logic_x_origin = wfm_header.x_origin
            continue

        if buffer_type not in supported_buffer_types or data_header.bytes_per_point != 4:
            raise ValueError(
                "Unsupported MSO5000 waveform buffer "
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

        if len(data) != point_count:
            raise ValueError(
                "MSO5000 analog waveform point count does not match the RG01 header. "
                f"Expected {point_count}, found {len(data)}."
            )
        if analog_slot > 0 and len(data) != header.n_pts:
            raise ValueError(
                "MSO5000 analog channels have mismatched point counts. " f"Expected {header.n_pts}, found {len(data)}."
            )

        unit_code = getattr(wfm_header.y_units, "value", int(wfm_header.y_units))
        ch_name = label or f"CH{slot + 1}"
        channel = ChannelHeader(ch_name, enabled=True, unit_code=unit_code)
        channel.volt_per_division = _estimate_volts_per_division(data)

        header.ch[slot] = channel
        header.channel_data[slot] = data
        header.raw_data[slot] = raw_proxy
        analog_slot += 1

    if logic_slot == 1:
        obj.logic_mapping = "LA D7-D0"
    elif logic_slot == 2:
        obj.logic_mapping = "LA D7-D0 + LA D15-D8"
    elif logic_slot > 2:
        obj.logic_mapping = f"{logic_slot} explicit logic byte lanes"

    return obj
