"""
Adapter layer for Siglent oscilloscope binary waveform exports.

Siglent's documented `.bin` formats span several distinct revisions:

- Old Platform: SDS1000X / SDS2000X
- V0.1
- V0.2
- V1.0
- V2.0
- V3.0
- V4.0
- V5.0
- V6.0

This module provides two pieces:

1. Revision detection and low-level parser dispatch for all documented
   revisions.
2. Normalized waveform loading for the revisions whose voltage/time conversion
   rules are documented unambiguously enough for `Wfm.from_file()`.

The old-platform format is exposed at the low-level Kaitai layer but is not
normalized here because the Siglent PDF leaves family-dependent scale
constants ambiguous between SDS1000X and SDS2000X captures.
"""
from __future__ import annotations

import math
import os
import struct
from typing import Any, Optional

import numpy as np
import numpy.typing as npt

import RigolWFM.channel
import RigolWFM.siglent_old_platform
import RigolWFM.siglent_v0_1
import RigolWFM.siglent_v0_2
import RigolWFM.siglent_v1
import RigolWFM.siglent_v2
import RigolWFM.siglent_v3
import RigolWFM.siglent_v4
import RigolWFM.siglent_v5
import RigolWFM.siglent_v6
from RigolWFM.mso5000 import _estimate_volts_per_division

_SiglentOldPlatform: Any = RigolWFM.siglent_old_platform.SiglentOldPlatform  # type: ignore[attr-defined]
_SiglentV01: Any = RigolWFM.siglent_v0_1.SiglentV01  # type: ignore[attr-defined]
_SiglentV02: Any = RigolWFM.siglent_v0_2.SiglentV02  # type: ignore[attr-defined]
_SiglentV1: Any = RigolWFM.siglent_v1.SiglentV1  # type: ignore[attr-defined]
_SiglentV2: Any = RigolWFM.siglent_v2.SiglentV2  # type: ignore[attr-defined]
_SiglentV3: Any = RigolWFM.siglent_v3.SiglentV3  # type: ignore[attr-defined]
_SiglentV4: Any = RigolWFM.siglent_v4.SiglentV4  # type: ignore[attr-defined]
_SiglentV5: Any = RigolWFM.siglent_v5.SiglentV5  # type: ignore[attr-defined]
_SiglentV6: Any = RigolWFM.siglent_v6.SiglentV6  # type: ignore[attr-defined]


class ChannelHeader:
    """Normalized per-channel metadata for a Siglent capture."""

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
        """Siglent voltage data is already calibrated in the normalized form."""
        return 1.0

    @property
    def y_offset(self) -> float:
        """Siglent voltage data is already calibrated in the normalized form."""
        return 0.0


class Header:
    """Normalized header used by `Wfm.from_file()` for Siglent captures."""

    revision: str
    model: str
    serial_number: str
    software_version: str
    n_pts: int
    x_origin: float
    x_increment: float
    x_origins: list[Optional[float]]
    x_increments: list[Optional[float]]
    ch: list[ChannelHeader]
    raw_data: list[Optional[npt.NDArray[np.uint8]]]
    channel_data: list[Optional[npt.NDArray[np.float32]]]

    def __init__(self) -> None:
        """Initialize an empty normalized Siglent header."""
        self.revision = ""
        self.model = ""
        self.serial_number = ""
        self.software_version = ""
        self.n_pts = 0
        self.x_origin = 0.0
        self.x_increment = 1e-6
        self.x_origins = [None] * 4
        self.x_increments = [None] * 4
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
        if self.n_pts > 0 and self.x_increment > 0:
            return self.n_pts * self.x_increment / 10.0
        return 1e-3

    @property
    def points(self) -> int:
        """Number of sample points in the first normalized analog trace."""
        return self.n_pts

    @property
    def firmware_version(self) -> str:
        """Return embedded software/version information when present."""
        return self.software_version or self.revision or "unknown"

    @property
    def model_number(self) -> str:
        """Return the embedded instrument/model label when present."""
        return self.model


class SiglentWaveform:
    """Normalized Siglent parser result consumed by `RigolWFM.channel.Channel`."""

    header: Header

    def __init__(self) -> None:
        """Initialize the normalized wrapper."""
        self.header = Header()

    @property
    def parser_name(self) -> str:
        """Return the normalized parser name used by `Wfm.from_file()`."""
        return "siglent_bin"

    def __str__(self) -> str:
        """Return a parser tag compatible with the rest of `Wfm.from_file()`."""
        return f"x.{self.parser_name}"


def _u16le(data: bytes, offset: int) -> int:
    return struct.unpack_from("<H", data, offset)[0]


def _u32le(data: bytes, offset: int) -> int:
    return struct.unpack_from("<I", data, offset)[0]


def _f64le(data: bytes, offset: int) -> float:
    return struct.unpack_from("<d", data, offset)[0]


def _ascii_slice(data: bytes, start: int, stop: int) -> str:
    raw = data[start:stop].split(b"\x00", 1)[0]
    return raw.decode("ascii", errors="ignore").strip()


def _all_flags(data: bytes, offsets: tuple[int, ...]) -> bool:
    return all(offset + 4 <= len(data) and _u32le(data, offset) in (0, 1) for offset in offsets)


def _looks_like_scaled_value_16(data: bytes, offset: int) -> bool:
    if offset + 16 > len(data):
        return False

    value = _f64le(data, offset)
    magnitude = _u32le(data, offset + 8)
    unit = _u32le(data, offset + 12)
    return math.isfinite(value) and abs(value) < 1e300 and 0 <= magnitude <= 16 and 0 <= unit <= 23


def _looks_like_data_with_unit(data: bytes, offset: int) -> bool:
    if offset + 40 > len(data):
        return False

    value = _f64le(data, offset)
    magnitude = _u32le(data, offset + 8)
    basic_unit = _u32le(data, offset + 12)
    return math.isfinite(value) and abs(value) < 1e300 and 0 <= magnitude <= 16 and 0 <= basic_unit <= 12


def _min_payload_ok(file_size: int, data_offset: int, enabled_count: int, points: int, sample_width: int) -> bool:
    if enabled_count <= 0 or points <= 0 or sample_width <= 0:
        return False
    return file_size >= data_offset + enabled_count * points * sample_width


def _looks_like_v6(data: bytes, file_size: int) -> bool:
    if file_size < 108 or len(data) < 108 or _u32le(data, 0) != 6:
        return False

    header_bytes = _u16le(data, 4)
    wave_number = _u32le(data, 0x68)
    module = _ascii_slice(data, 0x08, 0x28)
    return header_bytes >= 108 and wave_number > 0 and bool(module)


def _looks_like_v5(data: bytes, file_size: int) -> bool:
    enabled = sum(
        int(flag)
        for flag in (
            _u32le(data, 0x76) if len(data) >= 0x7A else 0,
            _u32le(data, 0xF0) if len(data) >= 0xF4 else 0,
            _u32le(data, 0x194) if len(data) >= 0x198 else 0,
            _u32le(data, 0x238) if len(data) >= 0x23C else 0,
        )
    )
    return (
        len(data) >= 0x1BA2
        and _u32le(data, 0x00) == 5
        and _looks_like_scaled_value_16(data, 0x1B68)
        and _looks_like_scaled_value_16(data, 0x1B78)
        and _u32le(data, 0x1B88) > 0
        and _min_payload_ok(file_size, 0x800, enabled, _u32le(data, 0x1B88), 1)
    )


def _looks_like_v4(data: bytes, file_size: int) -> bool:
    if len(data) < 0x280 or _u32le(data, 0x00) != 4:
        return False

    enabled = sum(_u32le(data, off) for off in (0x08, 0x0C, 0x10, 0x14) if off + 4 <= len(data))
    data_offset = _u32le(data, 0x04)
    points = _u32le(data, 0x1EC)
    return (
        data_offset >= 0x1000
        and _all_flags(data, (0x08, 0x0C, 0x10, 0x14))
        and _looks_like_data_with_unit(data, 0x19C)
        and _looks_like_data_with_unit(data, 0x1F0)
        and data[0x264] in (0, 1)
        and data[0x265] in (0, 1)
        and _min_payload_ok(file_size, data_offset, enabled, points, 1 if data[0x264] == 0 else 2)
    )


def _looks_like_v3(data: bytes, file_size: int) -> bool:
    if len(data) < 0x280 or _u32le(data, 0x00) != 3:
        return False

    enabled = sum(_u32le(data, off) for off in (0x04, 0x08, 0x0C, 0x10) if off + 4 <= len(data))
    points = _u32le(data, 0x1E8)
    sample_width = 1 if data[0x260] == 0 else 2
    return (
        _all_flags(data, (0x04, 0x08, 0x0C, 0x10))
        and _looks_like_data_with_unit(data, 0x198)
        and _looks_like_data_with_unit(data, 0x1EC)
        and data[0x260] in (0, 1)
        and data[0x261] in (0, 1)
        and 1 <= _u32le(data, 0x268) <= 20
        and _min_payload_ok(file_size, 0x800, enabled, points, sample_width)
    )


def _looks_like_v2(data: bytes, file_size: int) -> bool:
    if len(data) < 0x261 or _u32le(data, 0x00) != 2:
        return False

    enabled = sum(_u32le(data, off) for off in (0x04, 0x08, 0x0C, 0x10) if off + 4 <= len(data))
    points = _u32le(data, 0x1E8)
    sample_width = 1 if data[0x260] == 0 else 2
    return (
        _all_flags(data, (0x04, 0x08, 0x0C, 0x10))
        and _looks_like_data_with_unit(data, 0x198)
        and _looks_like_data_with_unit(data, 0x1EC)
        and data[0x260] in (0, 1)
        and _min_payload_ok(file_size, 0x800, enabled, points, sample_width)
    )


def _looks_like_v1(data: bytes, file_size: int) -> bool:
    if len(data) < 0x11C:
        return False

    enabled = sum(_u32le(data, off) for off in (0x00, 0x04, 0x08, 0x0C) if off + 4 <= len(data))
    points = _u32le(data, 0xF4)
    return (
        _all_flags(data, (0x00, 0x04, 0x08, 0x0C))
        and _looks_like_scaled_value_16(data, 0xD4)
        and _looks_like_scaled_value_16(data, 0xF8)
        and _min_payload_ok(file_size, 0x800, enabled, points, 1)
    )


def _looks_like_v0_2(data: bytes, file_size: int) -> bool:
    if len(data) < 0xDEC:
        return False

    enabled = sum(_u32le(data, off) for off in (0x44, 0xE8, 0x18C, 0x230) if off + 4 <= len(data))
    points = _u32le(data, 0xDD8)
    return (
        _all_flags(data, (0x44, 0xE8, 0x18C, 0x230))
        and _looks_like_scaled_value_16(data, 0xDB8)
        and _looks_like_scaled_value_16(data, 0xDDC)
        and _min_payload_ok(file_size, 0x932C, enabled, points, 1)
    )


def _looks_like_v0_1(data: bytes, file_size: int) -> bool:
    if len(data) < 0xAB8:
        return False

    enabled = sum(_u32le(data, off) for off in (0x44, 0xC0, 0x13C, 0x1B8) if off + 4 <= len(data))
    points = _u32le(data, 0xAA4)
    return (
        _all_flags(data, (0x44, 0xC0, 0x13C, 0x1B8))
        and _looks_like_scaled_value_16(data, 0xA84)
        and _looks_like_scaled_value_16(data, 0xAA8)
        and _min_payload_ok(file_size, 0x8A60, enabled, points, 1)
    )


def _looks_like_old_platform(data: bytes, file_size: int) -> bool:
    if len(data) < 0x254:
        return False

    enabled = sum(_u32le(data, off) for off in (0x100, 0x104, 0x108, 0x10C) if off + 4 <= len(data))
    if enabled <= 0 or file_size <= 0x1470:
        return False

    time_div_index = _u32le(data, 0x248)
    return _all_flags(data, (0x100, 0x104, 0x108, 0x10C)) and 0 <= time_div_index <= 32


def detect_revision_from_bytes(data: bytes, file_size: int) -> str:
    """Detect the documented Siglent waveform revision from a file prefix."""
    if _looks_like_v6(data, file_size):
        return "v6"
    if _looks_like_v5(data, file_size):
        return "v5"
    if _looks_like_v4(data, file_size):
        return "v4"
    if _looks_like_v3(data, file_size):
        return "v3"
    if _looks_like_v2(data, file_size):
        return "v2"
    if _looks_like_v1(data, file_size):
        return "v1"
    if _looks_like_v0_2(data, file_size):
        return "v0_2"
    if _looks_like_v0_1(data, file_size):
        return "v0_1"
    if _looks_like_old_platform(data, file_size):
        return "old"
    raise ValueError("Unrecognized Siglent waveform revision")


def detect_revision(file_name: str) -> str:
    """Detect the documented Siglent waveform revision from a file."""
    file_size = os.path.getsize(file_name)
    with open(file_name, "rb") as f:
        data = f.read(8192)
    return detect_revision_from_bytes(data, file_size)


def parse_low_level(file_name: str) -> tuple[str, Any]:
    """Parse a Siglent waveform file into its revision-specific Kaitai object."""
    revision = detect_revision(file_name)
    if revision == "old":
        return revision, _SiglentOldPlatform.from_file(file_name)
    if revision == "v0_1":
        return revision, _SiglentV01.from_file(file_name)
    if revision == "v0_2":
        return revision, _SiglentV02.from_file(file_name)
    if revision == "v1":
        return revision, _SiglentV1.from_file(file_name)
    if revision == "v2":
        return revision, _SiglentV2.from_file(file_name)
    if revision == "v3":
        return revision, _SiglentV3.from_file(file_name)
    if revision == "v4":
        return revision, _SiglentV4.from_file(file_name)
    if revision == "v5":
        return revision, _SiglentV5.from_file(file_name)
    if revision == "v6":
        return revision, _SiglentV6.from_file(file_name)
    raise ValueError(f"Unsupported Siglent revision: {revision}")


def _scaled_to_si(node: Any) -> float:
    """Convert Siglent value/unit structs to SI base units."""
    magnitude = int(node.magnitude)
    return float(node.value) * (10.0 ** (3 * (magnitude - 8)))


def _decode_integer_codes(payload: bytes, sample_width: int, byte_order: str) -> npt.NDArray[np.uint64]:
    """Decode unsigned integer sample codes from Siglent waveform bytes."""
    if sample_width == 1:
        return np.frombuffer(payload, dtype=np.uint8).astype(np.uint64)
    if sample_width == 2:
        dtype = np.dtype(f"{byte_order}u2")
        return np.frombuffer(payload, dtype=dtype).astype(np.uint64)
    if sample_width == 4:
        dtype = np.dtype(f"{byte_order}u4")
        return np.frombuffer(payload, dtype=dtype).astype(np.uint64)
    raise ValueError(f"Unsupported Siglent sample width: {sample_width} bytes")


def _raw_proxy_from_codes(codes: npt.NDArray[np.uint64], sample_width: int) -> npt.NDArray[np.uint8]:
    """Return a stable uint8 proxy for raw integer sample codes."""
    if codes.size == 0:
        return np.empty((0,), dtype=np.uint8)
    if sample_width == 1:
        return codes.astype(np.uint8)
    shift = 8 * (sample_width - 1)
    return np.clip(codes >> shift, 0, 255).astype(np.uint8)


def _assign_channel(
    header: Header,
    slot: int,
    name: str,
    volts: npt.NDArray[np.float32],
    raw_proxy: npt.NDArray[np.uint8],
    x_origin: float,
    x_increment: float,
    probe_value: float = 1.0,
    volt_per_division: Optional[float] = None,
) -> None:
    """Populate one normalized analog channel slot."""
    channel = header.ch[slot]
    channel.name = name
    channel.enabled = True
    channel.probe_value = probe_value
    channel.volt_per_division = (
        abs(volt_per_division)
        if volt_per_division is not None and volt_per_division > 0
        else _estimate_volts_per_division(volts)
    )

    header.channel_data[slot] = volts
    header.raw_data[slot] = raw_proxy
    header.x_origins[slot] = x_origin
    header.x_increments[slot] = x_increment

    if header.n_pts == 0:
        header.n_pts = len(volts)
        header.x_origin = x_origin
        header.x_increment = x_increment


def _normalized_waveform(
    revision: str,
    model: str,
    payload: bytes,
    enabled: list[bool],
    volt_divs: list[float],
    vert_offsets: list[float],
    probes: list[float],
    wave_length: int,
    sample_rate: float,
    x_origin: float,
    code_per_divs: list[float],
    sample_width: int = 1,
    byte_order: str = "<",
    serial_number: str = "",
    software_version: str = "",
) -> SiglentWaveform:
    """Normalize Siglent fixed-header analog formats into channel arrays."""
    if sample_rate <= 0:
        raise ValueError(f"Siglent {revision} file reports a non-positive sample rate: {sample_rate}")
    if wave_length <= 0:
        raise ValueError(f"Siglent {revision} file reports a non-positive waveform length: {wave_length}")

    sample_bytes = wave_length * sample_width
    analog_count = sum(int(flag) for flag in enabled[:4])
    if analog_count == 0:
        raise ValueError(f"Siglent {revision} file does not enable any of the first four analog channels")
    if len(payload) < analog_count * sample_bytes:
        raise ValueError(
            f"Siglent {revision} payload is too short for {analog_count} enabled analog channel(s): "
            f"expected at least {analog_count * sample_bytes} bytes, found {len(payload)}"
        )

    obj = SiglentWaveform()
    header = obj.header
    header.revision = revision
    header.model = model
    header.serial_number = serial_number
    header.software_version = software_version
    x_increment = 1.0 / sample_rate

    offset = 0
    for slot in range(min(4, len(enabled))):
        if not enabled[slot]:
            continue

        chunk = payload[offset : offset + sample_bytes]
        offset += sample_bytes
        codes = _decode_integer_codes(chunk, sample_width=sample_width, byte_order=byte_order)
        center_code = float(1 << (8 * sample_width - 1))
        code_per_div = float(code_per_divs[slot])
        if code_per_div <= 0:
            raise ValueError(f"Siglent {revision} channel {slot + 1} has a non-positive code_per_div value")

        volts = (
            (codes.astype(np.float64) - center_code) * (float(volt_divs[slot]) / code_per_div)
            + float(vert_offsets[slot])
        ).astype(np.float32)
        raw_proxy = _raw_proxy_from_codes(codes, sample_width=sample_width)
        _assign_channel(
            header,
            slot,
            f"CH{slot + 1}",
            volts,
            raw_proxy,
            x_origin=x_origin,
            x_increment=x_increment,
            probe_value=float(probes[slot]),
            volt_per_division=float(volt_divs[slot]),
        )

    return obj


def _normalize_v0_1(raw: Any) -> SiglentWaveform:
    enabled = [bool(raw.ch1_on), bool(raw.ch2_on), bool(raw.ch3_on), bool(raw.ch4_on)]
    volt_divs = [_scaled_to_si(raw.ch1_volt_div), _scaled_to_si(raw.ch2_volt_div), _scaled_to_si(raw.ch3_volt_div), _scaled_to_si(raw.ch4_volt_div)]
    vert_offsets = [
        _scaled_to_si(raw.ch1_vert_offset),
        _scaled_to_si(raw.ch2_vert_offset),
        _scaled_to_si(raw.ch3_vert_offset),
        _scaled_to_si(raw.ch4_vert_offset),
    ]
    time_div = _scaled_to_si(raw.time_div)
    sample_rate = _scaled_to_si(raw.sample_rate)
    x_origin = -(time_div * 14.0 / 2.0)
    return _normalized_waveform(
        revision="V0.1",
        model="Siglent V0.1",
        payload=raw.wave_data,
        enabled=enabled,
        volt_divs=volt_divs,
        vert_offsets=vert_offsets,
        probes=[1.0, 1.0, 1.0, 1.0],
        wave_length=int(raw.wave_length),
        sample_rate=sample_rate,
        x_origin=x_origin,
        code_per_divs=[25.0, 25.0, 25.0, 25.0],
    )


def _normalize_v0_2(raw: Any) -> SiglentWaveform:
    enabled = [bool(raw.ch1_on), bool(raw.ch2_on), bool(raw.ch3_on), bool(raw.ch4_on)]
    volt_divs = [_scaled_to_si(raw.ch1_volt_div), _scaled_to_si(raw.ch2_volt_div), _scaled_to_si(raw.ch3_volt_div), _scaled_to_si(raw.ch4_volt_div)]
    vert_offsets = [
        _scaled_to_si(raw.ch1_vert_offset),
        _scaled_to_si(raw.ch2_vert_offset),
        _scaled_to_si(raw.ch3_vert_offset),
        _scaled_to_si(raw.ch4_vert_offset),
    ]
    time_div = _scaled_to_si(raw.time_div)
    sample_rate = _scaled_to_si(raw.sample_rate)
    x_origin = -(time_div * 14.0 / 2.0)
    return _normalized_waveform(
        revision="V0.2",
        model="Siglent V0.2",
        payload=raw.wave_data,
        enabled=enabled,
        volt_divs=volt_divs,
        vert_offsets=vert_offsets,
        probes=[1.0, 1.0, 1.0, 1.0],
        wave_length=int(raw.wave_length),
        sample_rate=sample_rate,
        x_origin=x_origin,
        code_per_divs=[25.0, 25.0, 25.0, 25.0],
    )


def _normalize_v1(raw: Any) -> SiglentWaveform:
    enabled = [bool(value) for value in raw.ch_on.entries]
    volt_divs = [_scaled_to_si(node) for node in raw.ch_volt_div.entries]
    vert_offsets = [_scaled_to_si(node) for node in raw.ch_vert_offset.entries]
    time_div = _scaled_to_si(raw.time_div)
    sample_rate = _scaled_to_si(raw.sample_rate)
    x_origin = -(time_div * 14.0 / 2.0)
    return _normalized_waveform(
        revision="V1.0",
        model="Siglent V1.0",
        payload=raw.wave_data,
        enabled=enabled,
        volt_divs=volt_divs,
        vert_offsets=vert_offsets,
        probes=[1.0, 1.0, 1.0, 1.0],
        wave_length=int(raw.wave_length),
        sample_rate=sample_rate,
        x_origin=x_origin,
        code_per_divs=[25.0, 25.0, 25.0, 25.0],
    )


def _normalize_v2(raw: Any) -> SiglentWaveform:
    enabled = [bool(value) for value in raw.ch_on.entries]
    volt_divs = [_scaled_to_si(node) for node in raw.ch_volt_div.entries]
    vert_offsets = [_scaled_to_si(node) for node in raw.ch_vert_offset.entries]
    time_div = _scaled_to_si(raw.time_div)
    sample_rate = _scaled_to_si(raw.sample_rate)
    x_origin = -(time_div * 14.0 / 2.0)
    sample_width = 1 if int(raw.data_width) == 0 else 2
    probes = [float(value) for value in raw.ch_probe.entries]
    return _normalized_waveform(
        revision="V2.0",
        model="Siglent V2.0",
        payload=raw.wave_data,
        enabled=enabled,
        volt_divs=volt_divs,
        vert_offsets=vert_offsets,
        probes=probes,
        wave_length=int(raw.wave_length),
        sample_rate=sample_rate,
        x_origin=x_origin,
        code_per_divs=[25.0, 25.0, 25.0, 25.0],
        sample_width=sample_width,
    )


def _normalize_v3(raw: Any) -> SiglentWaveform:
    enabled = [bool(value) for value in raw.ch_on.entries]
    volt_divs = [_scaled_to_si(node) for node in raw.ch_volt_div.entries]
    vert_offsets = [_scaled_to_si(node) for node in raw.ch_vert_offset.entries]
    time_div = _scaled_to_si(raw.time_div)
    time_delay = _scaled_to_si(raw.time_delay)
    sample_rate = _scaled_to_si(raw.sample_rate)
    x_origin = -(time_div * float(raw.hori_div_num) / 2.0) - time_delay
    sample_width = 1 if int(raw.data_width) == 0 else 2
    byte_order = "<" if int(raw.byte_order) == 0 else ">"
    probes = [float(value) for value in raw.ch_probe.entries]
    code_per_divs = [float(value) for value in raw.ch_vert_code_per_div.entries]
    return _normalized_waveform(
        revision="V3.0",
        model="Siglent V3.0",
        payload=raw.wave_data,
        enabled=enabled,
        volt_divs=volt_divs,
        vert_offsets=vert_offsets,
        probes=probes,
        wave_length=int(raw.wave_length),
        sample_rate=sample_rate,
        x_origin=x_origin,
        code_per_divs=code_per_divs,
        sample_width=sample_width,
        byte_order=byte_order,
    )


def _normalize_v4(raw: Any) -> SiglentWaveform:
    enabled = [bool(value) for value in raw.ch_on_1_4.entries]
    volt_divs = [_scaled_to_si(node) for node in raw.ch_volt_div_1_4.entries]
    vert_offsets = [_scaled_to_si(node) for node in raw.ch_vert_offset_1_4.entries]
    time_div = _scaled_to_si(raw.time_div)
    time_delay = _scaled_to_si(raw.time_delay)
    sample_rate = _scaled_to_si(raw.sample_rate)
    x_origin = -(time_div * float(raw.hori_div_num) / 2.0) - time_delay
    sample_width = 1 if int(raw.data_width) == 0 else 2
    byte_order = "<" if int(raw.byte_order) == 0 else ">"
    probes = [float(value) for value in raw.ch_probe_1_4.entries]
    code_per_divs = [float(value) for value in raw.ch_vert_code_per_div_1_4.entries]
    return _normalized_waveform(
        revision="V4.0",
        model="Siglent V4.0",
        payload=raw.wave_data,
        enabled=enabled,
        volt_divs=volt_divs,
        vert_offsets=vert_offsets,
        probes=probes,
        wave_length=int(raw.wave_length),
        sample_rate=sample_rate,
        x_origin=x_origin,
        code_per_divs=code_per_divs,
        sample_width=sample_width,
        byte_order=byte_order,
    )


def _normalize_v5(raw: Any) -> SiglentWaveform:
    enabled = [bool(raw.ch1_on), bool(raw.ch2_on), bool(raw.ch3_on), bool(raw.ch4_on)]
    volt_divs = [_scaled_to_si(raw.ch1_volt_div), _scaled_to_si(raw.ch2_volt_div), _scaled_to_si(raw.ch3_volt_div), _scaled_to_si(raw.ch4_volt_div)]
    vert_offsets = [
        _scaled_to_si(raw.ch1_vert_offset),
        _scaled_to_si(raw.ch2_vert_offset),
        _scaled_to_si(raw.ch3_vert_offset),
        _scaled_to_si(raw.ch4_vert_offset),
    ]
    time_div = _scaled_to_si(raw.time_div)
    sample_rate = _scaled_to_si(raw.sample_rate)
    x_origin = -(time_div * 14.0 / 2.0)
    return _normalized_waveform(
        revision="V5.0",
        model="Siglent V5.0",
        payload=raw.wave_data,
        enabled=enabled,
        volt_divs=volt_divs,
        vert_offsets=vert_offsets,
        probes=[1.0, 1.0, 1.0, 1.0],
        wave_length=int(raw.wave_length),
        sample_rate=sample_rate,
        x_origin=x_origin,
        code_per_divs=[25.0, 25.0, 25.0, 25.0],
    )


def _v6_slot(header: Any) -> Optional[int]:
    """Map V6 channel descriptors onto zero-based analog channel slots."""
    index = int(header.channel_index)
    if 1 <= index <= 4:
        return index - 1
    if 0 <= index < 4:
        return index

    label = header.label.strip().upper()
    if label.startswith("CH"):
        try:
            idx = int(label[2:]) - 1
        except ValueError:
            return None
        if 0 <= idx < 4:
            return idx
    return None


def _normalize_v6(raw: Any) -> SiglentWaveform:
    obj = SiglentWaveform()
    header = obj.header
    header.revision = "V6.0"
    header.model = raw.file_header.module or "Siglent"
    header.serial_number = raw.file_header.serial
    header.software_version = raw.file_header.software_version

    analog_found = 0
    for waveform in raw.waveforms:
        wfh = waveform.header
        slot = _v6_slot(wfh)
        if slot is None:
            continue
        if header.channel_data[slot] is not None:
            raise ValueError(
                "Siglent V6.0 file contains multiple waveform records for the same "
                f"analog channel slot ({slot + 1}), which is not yet normalized."
            )
        if int(wfh.data_number) <= 0:
            continue
        if int(wfh.data_bytes) % int(wfh.data_number) != 0:
            raise ValueError(
                "Siglent V6.0 waveform byte count does not divide evenly by its "
                f"point count ({wfh.data_bytes} bytes for {wfh.data_number} points)."
            )

        sample_width = int(wfh.data_bytes) // int(wfh.data_number)
        if sample_width not in (1, 2, 4):
            raise ValueError(
                "Unsupported Siglent V6.0 sample width "
                f"({sample_width} bytes per point) for channel {slot + 1}"
            )

        codes = _decode_integer_codes(waveform.data_raw, sample_width=sample_width, byte_order="<")
        volts = (
            (codes.astype(np.float64) - float(wfh.vert_origin_pos)) * float(wfh.vert_interval)
        ).astype(np.float32)
        x_origin = -float(wfh.hori_origin_pos) * float(wfh.hori_interval)
        x_increment = float(wfh.hori_interval)
        raw_proxy = _raw_proxy_from_codes(codes, sample_width=sample_width)
        _assign_channel(
            header,
            slot,
            wfh.label.strip() or f"CH{slot + 1}",
            volts,
            raw_proxy,
            x_origin=x_origin,
            x_increment=x_increment,
            probe_value=1.0,
            volt_per_division=abs(float(wfh.vert_scale)),
        )
        analog_found += 1

    if analog_found == 0:
        raise ValueError("No supported analog waveform records were found in this Siglent V6.0 capture")

    return obj


def from_file(file_name: str, model_hint: str = "SIGLENT") -> SiglentWaveform:
    """Parse a Siglent waveform `.bin` file and normalize supported revisions."""
    revision, raw = parse_low_level(file_name)
    _ = model_hint  # Reserved for future family-specific overrides.

    if revision == "old":
        raise ValueError(
            "Siglent old-platform files are exposed via the low-level "
            "RigolWFM.siglent_old_platform parser, but `Wfm.from_file()` does "
            "not normalize them because the vendor documentation leaves their "
            "family-specific voltage/time scaling ambiguous."
        )
    if revision == "v0_1":
        return _normalize_v0_1(raw)
    if revision == "v0_2":
        return _normalize_v0_2(raw)
    if revision == "v1":
        return _normalize_v1(raw)
    if revision == "v2":
        return _normalize_v2(raw)
    if revision == "v3":
        return _normalize_v3(raw)
    if revision == "v4":
        return _normalize_v4(raw)
    if revision == "v5":
        return _normalize_v5(raw)
    if revision == "v6":
        return _normalize_v6(raw)
    raise ValueError(f"Unsupported Siglent revision: {revision}")
