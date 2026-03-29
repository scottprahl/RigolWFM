"""
Class structure and methods for an oscilloscope channel.

The idea is to collect all the relevant information from all the Rigol
scope waveforms into a single structure that can be handled in a uniform
and consistent manner.

Specifically this lets one do::

    channel.times   : numpy array of signal times
    channel.volts   : numpy array of signal voltages

or the stringification method to describe a channel::

    print(channel)

"""
from __future__ import annotations

from enum import Enum
from typing import TYPE_CHECKING, Optional

import numpy as np
import numpy.typing as npt

if TYPE_CHECKING:
    from typing import Any

__all__ = ["UnitEnum", "Channel", "best_scale", "engineering_string"]


class UnitEnum(Enum):
    """Enumerated units for scopes without them."""

    w = 0
    a = 1
    v = 2
    u = 3


def best_scale(number: float) -> tuple[float, str]:
    """Scale and units for a number with proper prefix."""
    absnr = abs(number)
    thresholds = [
        (0.99999999e-9, 1e12, "p"),
        (0.99999999e-6, 1e9, "n"),
        (0.99999999e-3, 1e6, "µ"),
        (0.99999999, 1e3, "m"),
        (0.99999999e3, 1, " "),
        (0.99999999e6, 1e-3, "k"),
        (0.999999991e9, 1e-6, "M"),
    ]

    if absnr == 0:
        return 1, " "

    for limit, scale, prefix in thresholds:
        if absnr < limit:
            return scale, prefix

    return 1e-9, "G"


def engineering_string(number: float, n_digits: int) -> str:
    """Format number with proper prefix."""
    scale, prefix = best_scale(number)
    fformat = "%%.%df %%s" % n_digits
    s = fformat % (number * scale, prefix)
    return s


def _channel_bytes(channel_number: int, w: Any) -> npt.NDArray[np.uint8]:
    """
    Return right series of bytes for a channel for 1000Z scopes.

    Waveform points are interleaved stored in memory when two or more
    channels are saved.  This unweaves them.

    Args:
        channel_number: the number of enabled channels before this one
        w:              original waveform object
    Returns
        byte array for specified channel
    """
    offset = 0

    if w.header.stride == 2:  # byte pattern e.g., CH4 CH1 CH4 CH 1
        # use odd bytes when this is the second enabled channel
        if not any(w.header.ch[i].enabled for i in range(channel_number - 1)):
            offset = 1

    elif w.header.stride == 4:  # byte pattern CH4 CH3 CH2 CH1
        offset = 4 - channel_number

    data = np.frombuffer(w.data.raw, dtype=np.uint8)
    raw_bytes = data[offset :: w.header.stride]

    return raw_bytes


def _ds2000_effective_time_offset(w: Any) -> float:
    """Return the trigger-referenced time offset for DS2000 captures."""
    model_number = getattr(w.header, "model_number", "") or ""
    firmware_version = getattr(w.header, "firmware_version", "") or ""

    # The older DS2A captures checked into this repo store a nonzero
    # time_offset even though the saved screenshot shows the trigger
    # marker centered. Newer DS2072A captures use time_offset normally.
    if model_number.startswith("DS2A") and firmware_version == "00.03.00.01.03":
        return 0.0

    return w.header.time_offset


class Channel:
    """Base class for a single channel."""

    channel_number: int
    name: str
    waveform: Any
    seconds_per_point: float
    firmware: str
    unit: UnitEnum
    points: int
    raw: Optional[npt.NDArray[np.uint8]]
    volts: Optional[npt.NDArray[np.float64]]
    times: Optional[npt.NDArray[np.float64]]
    coupling: str
    roll_stop: int
    time_offset: float
    time_scale: float
    enabled: bool
    enabled_and_selected: bool
    volt_scale: float
    volt_offset: float
    y_scale: float
    y_offset: float
    volt_per_division: float
    probe_value: float
    inverted: bool

    def __init__(self, w: Any, channel_number: int, scope: str, selected: str = "1234") -> None:
        """
        Initialize a Channel Object.

        Args:
            w: Wfm object
            channel_number: 1, 2, 3, or 4
            scope: string describing scope
            selected: string with channels chosen by user
        Returns:
            Channel object
        """
        self.channel_number = channel_number
        self.name = f"CH {channel_number}"
        self.waveform = w
        self.seconds_per_point = w.header.seconds_per_point
        self.firmware = "unknown"
        self.unit = UnitEnum.v
        self.points = 0
        self.raw = None
        self.volts = None
        self.times = None
        self.coupling = "unknown"
        self.roll_stop = 0
        self.time_offset = 0
        self.time_scale = 1
        self.enabled = False
        self.enabled_and_selected = False
        self.volt_scale = 1
        self.volt_offset = 0
        self.y_scale = 1
        self.y_offset = 0
        self.volt_per_division = 1
        self.probe_value = 1
        self.inverted = False

        # determine if this channel is one of those chosen by user
        chosen = str(channel_number) in selected

        if channel_number <= len(w.header.ch):
            channel = w.header.ch[channel_number - 1]
            self.enabled = channel.enabled
            self.enabled_and_selected = channel.enabled and chosen
            self.volt_scale = channel.volt_scale
            self.volt_offset = channel.volt_offset
            self.y_scale = channel.volt_scale
            self.y_offset = channel.volt_offset
            self.volt_per_division = channel.volt_per_division
            self.probe_value = channel.probe_value
            self.unit = channel.unit
            self.inverted = channel.inverted

        if scope == "wfm1000z":
            # DS1000Z files have per-channel slots for all four analog channels,
            # but two-channel models can leave non-zero junk in the unused CH3/CH4
            # slot flags.  Trust the header bitmask instead of each slot's
            # enabled_val when deciding which channels are really present.
            enabled_flags = (
                bool(getattr(w.header, "ch1_enabled", False)),
                bool(getattr(w.header, "ch2_enabled", False)),
                bool(getattr(w.header, "ch3_enabled", False)),
                bool(getattr(w.header, "ch4_enabled", False)),
            )
            self.enabled = enabled_flags[channel_number - 1]
            self.enabled_and_selected = self.enabled and chosen

        if scope == "wfm6000":
            # DS6000 files carry a dedicated channel marker in WfmInfoStru and
            # document a zero waveform offset as "no saved data".  Use that
            # pair instead of the per-channel vertical settings when deciding
            # whether a trace is actually present in the file.
            enabled_flags = (
                bool(getattr(w.header.enabled, "channel_1", False)) and w.header.channel_offset[0] != 0,
                bool(getattr(w.header.enabled, "channel_2", False)) and w.header.channel_offset[1] != 0,
                bool(getattr(w.header.enabled, "channel_3", False)) and w.header.channel_offset[2] != 0,
                bool(getattr(w.header.enabled, "channel_4", False)) and w.header.channel_offset[3] != 0,
            )
            self.enabled = enabled_flags[channel_number - 1]
            self.enabled_and_selected = self.enabled and chosen

        if scope == "wfm1000b":
            self.y_offset += 1.12 * channel.volt_per_division
            self.ds1000b(w, channel_number)
        elif scope == "wfm1000c":
            self.ds1000c(w, channel_number)
        elif scope == "wfm1000d":
            self.ds1000d(w, channel_number)
        elif scope == "wfm1000e":
            self.ds1000e(w, channel_number)
        elif scope == "wfm1000z":
            self.ds1000z(w, channel_number)
        elif scope == "wfm2000":
            self.ds2000(w, channel_number)
        elif scope == "wfm4000":
            self.ds4000(w, channel_number)
        elif scope == "wfm6000":
            self.ds6000(w, channel_number)
        elif scope == "bin5000":
            self.bin5000(w, channel_number)
        elif scope == "bin7000_8000":
            self.bin7000_8000(w, channel_number)
        elif scope == "dho1000":
            self.dho1000(w, channel_number)
        elif scope == "lecroy_trc":
            self.lecroy(w, channel_number)
        elif scope == "agilent_bin":
            self.agilent(w, channel_number)
        elif scope == "tek_wfm":
            self.tek(w, channel_number)
        elif scope == "tek_isf":
            self.tek(w, channel_number)
        elif scope == "yokogawa_wfm":
            self.yokogawa(w, channel_number)

    def __str__(self) -> str:
        """Describe this channel."""
        s = "     Channel %d:\n" % self.channel_number
        s += "         Coupling = %8s\n" % self.coupling.rjust(7, " ")
        s += "            Scale = %10sV/div\n" % engineering_string(
            self.volt_per_division, 2
        )
        s += "           Offset = %10sV\n" % engineering_string(self.volt_offset, 2)
        s += "            Probe = %7gX\n" % self.probe_value
        s += "         Inverted = %8s\n\n" % self.inverted
        s += "        Time Base = %10ss/div\n" % engineering_string(self.time_scale, 3)
        s += "           Offset = %10ss\n" % engineering_string(self.time_offset, 3)
        s += "            Delta = %10ss/point\n" % engineering_string(
            self.seconds_per_point, 3
        )
        s += "           Points = %8d\n\n" % self.points

        if self.enabled_and_selected and self.points >= 5:
            assert self.raw is not None
            assert self.times is not None
            assert self.volts is not None
            format_str = "         Count    = [%9d,%9d,%9d  ... %9d,%9d]\n"
            s += format_str % (1, 2, 3, self.points - 1, self.points)
            format_str = "           Raw    = [%9d,%9d,%9d  ... %9d,%9d]\n"
            s += format_str % (
                self.raw[0],
                self.raw[1],
                self.raw[2],
                self.raw[-2],
                self.raw[-1],
            )
            t = [engineering_string(self.times[i], 3) + "s" for i in [0, 1, 2, -2, -1]]
            format_str = "           Times  = [%9s,%9s,%9s  ... %9s,%9s]\n"
            s += format_str % (t[0], t[1], t[2], t[-2], t[-1])
            v = [engineering_string(self.volts[i], 2) + "V" for i in [0, 1, 2, -2, -1]]
            format_str = "           Volts  = [%9s,%9s,%9s  ... %9s,%9s]\n"
            s += format_str % (v[0], v[1], v[2], v[-2], v[-1])
        return s

    def calc_times_and_volts(
        self,
        sample_aligned: bool = False,
        memory_depth_points: Optional[int] = None,
        midpoint: float = 127.0,
    ) -> None:
        """Calculate the times and voltages for this channel."""
        if self.enabled_and_selected:
            # The midpoint maps an ADC count to zero volts (before offset).
            # Most Rigol families use 127 (midpoint of 0–255).
            # DS1000C/D use 125, matching the Delphi reference parser and
            # confirmed by comparing derived trigger levels to stored offsets.
            assert self.raw is not None
            self.volts = (self.y_scale * (midpoint - self.raw) - self.y_offset).astype(np.float64)
            if sample_aligned:
                depth_points = self.points
                if memory_depth_points is not None:
                    depth_points = memory_depth_points
                start = self.time_offset - depth_points * self.seconds_per_point / 2
                self.times = (start + np.arange(self.points) * self.seconds_per_point).astype(np.float64)
            else:
                h = self.points * self.seconds_per_point / 2
                self.times = (np.linspace(-h, h, self.points) + self.time_offset).astype(np.float64)

    def ds1000b(self, w: Any, channel_number: int) -> None:
        """Interpret waveform data for 1000B series scopes."""
        self.time_scale = 1.0e-12 * w.header.time_scale
        self.time_offset = 1.0e-12 * w.header.time_offset
        self.coupling = "AC"
        if channel_number == 1:
            if self.enabled_and_selected:
                if (w.header.coupling_ch12 & 0xC0) == 0xC0:
                    self.coupling = "DC"
                self.points = w.header.len_ch1
                self.raw = np.frombuffer(w.header.ch1, dtype=np.uint8)

        if channel_number == 2:
            if self.enabled_and_selected:
                if (w.header.coupling_ch12 & 0x0C) == 0x0C:
                    self.coupling = "DC"
                self.points = w.header.len_ch2
                self.raw = np.frombuffer(w.header.ch2, dtype=np.uint8)

        if channel_number == 3:
            if self.enabled_and_selected:
                if (w.header.coupling_ch34 & 0xC0) == 0xC0:
                    self.coupling = "DC"
                self.points = w.header.len_ch3
                self.raw = np.frombuffer(w.header.ch3, dtype=np.uint8)

        if channel_number == 4:
            if self.enabled_and_selected:
                if (w.header.coupling_ch34 & 0x0C) == 0x0C:
                    self.coupling = "DC"
                self.points = w.header.len_ch4
                self.raw = np.frombuffer(w.header.ch4, dtype=np.uint8)

        self.calc_times_and_volts()

    def ds1000c(self, w: Any, channel_number: int) -> None:
        """Interpret waveform data for 1000CD series scopes."""
        self.time_scale = 1.0e-12 * w.header.time_scale
        self.time_offset = 1.0e-12 * w.header.time_offset
        if channel_number == 1:
            if self.enabled_and_selected:
                self.points = len(w.data.ch1)
                self.raw = np.frombuffer(w.data.ch1, dtype=np.uint8)

        if channel_number == 2:
            if self.enabled_and_selected:
                self.points = len(w.data.ch2)
                self.raw = np.frombuffer(w.data.ch2, dtype=np.uint8)

        self.calc_times_and_volts(midpoint=125.0)

    def ds1000d(self, w: Any, channel_number: int) -> None:
        """Interpret waveform data for 1000D series scopes (uses wfm1000e parser).

        DS1000D firmware stores scale_measured already probe-corrected, so the
        probe_value factor that wfm1000e bakes into volt_scale must be divided out.
        """
        self.roll_stop = w.header.roll_stop
        # Remove the probe factor that wfm1000e includes in volt_scale/volt_offset.
        if self.probe_value != 0:
            self.y_scale /= self.probe_value
            self.y_offset /= self.probe_value
        memory_depth_points = None

        if channel_number == 1:
            self.time_offset = w.header.ch1_time_offset
            self.time_scale = w.header.ch1_time_scale
            if self.enabled_and_selected:
                self.points = len(w.data.ch1)
                self.raw = np.frombuffer(w.data.ch1, dtype=np.uint8)
                memory_depth_points = w.header.ch1_memory_depth

        elif channel_number == 2:
            self.time_offset = w.header.ch2_time_offset
            self.time_scale = w.header.ch2_time_scale
            if self.enabled_and_selected:
                self.points = len(w.data.ch2)
                self.raw = np.frombuffer(w.data.ch2, dtype=np.uint8)
                memory_depth_points = w.header.ch2_memory_depth

        self.calc_times_and_volts(
            sample_aligned=True,
            memory_depth_points=memory_depth_points,
            midpoint=125.0,
        )

    def ds1000e(self, w: Any, channel_number: int) -> None:
        """Interpret waveform data for 1000D and 1000E series scopes."""
        self.roll_stop = w.header.roll_stop
        memory_depth_points = None

        if channel_number == 1:
            self.time_offset = w.header.ch1_time_offset
            self.time_scale = w.header.ch1_time_scale
            if self.enabled_and_selected:
                self.points = len(w.data.ch1)
                self.raw = np.frombuffer(w.data.ch1, dtype=np.uint8)
                memory_depth_points = w.header.ch1_memory_depth

        elif channel_number == 2:
            self.time_offset = w.header.ch2_time_offset
            self.time_scale = w.header.ch2_time_scale
            if self.enabled_and_selected:
                self.points = len(w.data.ch2)
                self.raw = np.frombuffer(w.data.ch2, dtype=np.uint8)
                memory_depth_points = w.header.ch2_memory_depth

        self.calc_times_and_volts(
            sample_aligned=True,
            memory_depth_points=memory_depth_points,
            midpoint=125.0,
        )

    def ds1000z(self, w: Any, channel_number: int) -> None:
        """Interpret waveform for the Rigol DS1000Z series."""
        self.time_scale = w.header.time_scale
        self.time_offset = w.header.time_offset
        self.points = w.header.points
        self.firmware = w.preheader.firmware_version
        self.probe_value = w.header.ch[channel_number - 1].probe_value
        self.coupling = w.header.ch[channel_number - 1].coupling.name.upper()
        self.y_scale = w.header.ch[channel_number - 1].y_scale
        self.y_offset = w.header.ch[channel_number - 1].y_offset

        if self.enabled_and_selected:
            self.raw = _channel_bytes(channel_number, w)
            self.points = len(self.raw)

        self.calc_times_and_volts(sample_aligned=True)

    def ds2000(self, w: Any, channel_number: int) -> None:
        """Interpret waveform for the Rigol DS2000 series."""
        self.time_offset = (
            _ds2000_effective_time_offset(w)
            + w.header.z_pt_offset * w.header.seconds_per_point
        )
        self.time_scale = w.header.time_scale
        self.points = w.header.points
        self.firmware = w.header.firmware_version
        self.unit = UnitEnum(w.header.ch[channel_number - 1].unit_actual)
        self.coupling = w.header.ch[channel_number - 1].coupling.name.upper()
        # DS2000/4000/6000 ADC convention: higher count = higher voltage (normal polarity).
        # The formula in calc_times_and_volts() is y_scale*(127-raw)-y_offset, so negating
        # volt_scale flips the subtraction to (raw-127), giving the correct sign.
        # Contrast with DS1000E/B/C/D which store inverted ADC data (higher count = lower
        # voltage), where y_scale = +volt_scale is correct without a sign flip.
        self.y_scale = -self.volt_scale
        self.y_offset = self.volt_offset

        if self.enabled_and_selected and not w.header.enabled.interwoven:
            if channel_number == 1:
                self.raw = np.frombuffer(w.header.raw_1, dtype=np.uint8)

            if channel_number == 2:
                self.raw = np.frombuffer(w.header.raw_2, dtype=np.uint8)

            if channel_number == 3:
                self.raw = np.frombuffer(w.header.raw_3, dtype=np.uint8)

            if channel_number == 4:
                self.raw = np.frombuffer(w.header.raw_4, dtype=np.uint8)

        elif self.enabled_and_selected and w.header.enabled.interwoven:
            # 'Interwoven' wave captures use the memory available to all channels
            # to sample at a higher resolution.  This means if CH1 is disabled
            # CH2 will use the memory from CH1.
            raw_a = np.frombuffer(w.header.raw_1, dtype=np.uint8)
            raw_b = np.frombuffer(w.header.raw_2, dtype=np.uint8)
            self.raw = np.empty((len(raw_a) + len(raw_b),), dtype=np.uint8)
            self.raw[0::2] = raw_a
            self.raw[1::2] = raw_b

        if self.enabled_and_selected:
            assert self.raw is not None
            self.points = len(self.raw)

        self.calc_times_and_volts(
            sample_aligned=True,
            memory_depth_points=w.header.storage_depth,
        )

    def ds4000(self, w: Any, channel_number: int) -> None:
        """Interpret waveform for the Rigol DS4000 series."""
        self.time_offset = w.header.time_offset
        self.time_scale = w.header.time_scale
        self.points = w.header.points
        self.firmware = w.header.firmware_version
        self.coupling = w.header.ch[channel_number - 1].coupling.name.upper()
        # See ds2000() for the ADC polarity sign convention.
        self.y_scale = -self.volt_scale
        self.y_offset = self.volt_offset

        if self.enabled_and_selected:
            if channel_number == 1:
                self.raw = np.frombuffer(w.header.raw_1, dtype=np.uint8)

            if channel_number == 2:
                self.raw = np.frombuffer(w.header.raw_2, dtype=np.uint8)

            if channel_number == 3:
                self.raw = np.frombuffer(w.header.raw_3, dtype=np.uint8)

            if channel_number == 4:
                self.raw = np.frombuffer(w.header.raw_4, dtype=np.uint8)

        self.calc_times_and_volts(
            sample_aligned=True,
            memory_depth_points=w.header.mem_depth,
        )

    def ds6000(self, w: Any, channel_number: int) -> None:
        """Interpret waveform for the Rigol DS6000 series."""
        self.time_offset = (
            w.header.time_offset
            + w.header.z_pt_offset * w.header.seconds_per_point
        )
        self.time_scale = w.header.time_scale
        self.points = w.header.points
        self.firmware = w.header.firmware_version
        self.coupling = w.header.ch[channel_number - 1].coupling.name.upper()
        self.unit = w.header.ch[channel_number - 1].unit
        # See ds2000() for the ADC polarity sign convention.
        self.y_scale = -self.volt_scale
        self.y_offset = self.volt_offset

        if self.enabled_and_selected:
            if channel_number == 1:
                self.raw = np.frombuffer(w.header.raw_1, dtype=np.uint8)

            if channel_number == 2:
                self.raw = np.frombuffer(w.header.raw_2, dtype=np.uint8)

            if channel_number == 3:
                self.raw = np.frombuffer(w.header.raw_3, dtype=np.uint8)

            if channel_number == 4:
                self.raw = np.frombuffer(w.header.raw_4, dtype=np.uint8)

            assert self.raw is not None
            self.points = len(self.raw)

        self.calc_times_and_volts(
            sample_aligned=True,
            memory_depth_points=w.header.storage_depth,
        )

    def bin5000(self, w: Any, channel_number: int) -> None:
        """Interpret normalized waveform data for Rigol MSO5000 `.bin` files."""
        self.time_scale = w.header.time_scale
        self.time_offset = w.header.time_offset
        self.points = w.header.points
        self.firmware = w.header.firmware_version

        idx = channel_number - 1
        ch_data = w.header.channel_data[idx] if idx < len(w.header.channel_data) else None
        if ch_data is not None and self.enabled_and_selected:
            self.volts = ch_data.astype(np.float64)
            raw_data = getattr(w.header, "raw_data", None)
            if isinstance(raw_data, list):
                raw8 = raw_data[idx] if idx < len(raw_data) else None
            else:
                raw8 = None

            if raw8 is None:
                raw8 = np.full(self.volts.shape, 127, dtype=np.uint8)

            self.raw = raw8
            self.points = len(self.volts)
            self.times = -w.header.x_origin + np.arange(self.points) * w.header.x_increment

    def bin7000_8000(self, w: Any, channel_number: int) -> None:
        """Interpret normalized waveform data for Rigol 7000/8000 `.bin` files."""
        self.bin5000(w, channel_number)

    def dho1000(self, w: Any, channel_number: int) -> None:
        """Interpret normalized waveform data for the Rigol DHO800/DHO1000 series."""
        self.time_scale = w.header.time_scale
        self.time_offset = 0.0
        self.points = w.header.points
        self.firmware = w.header.firmware_version

        idx = channel_number - 1
        ch_data = w.header.channel_data[idx] if idx < len(w.header.channel_data) else None
        if ch_data is not None and self.enabled_and_selected:
            self.volts = ch_data.astype(np.float64)
            raw_data = getattr(w.header, "raw_data", None)
            if isinstance(raw_data, list):
                raw16 = raw_data[idx] if idx < len(raw_data) else None
            else:
                raw16 = None

            if raw16 is None:
                raw16 = np.clip(
                    (self.volts * 1000 + 32768).astype(np.int32), 0, 65535
                ).astype(np.uint16)
            self.raw = (raw16 >> 8).astype(np.uint8)
            self.points = len(self.volts)
            t0 = w.header.x_origin
            self.times = t0 + np.arange(self.points) * w.header.x_increment

    def lecroy(self, w: Any, channel_number: int) -> None:
        """Interpret normalized waveform data for a LeCroy .trc file."""
        self.time_scale = w.header.time_scale
        self.time_offset = 0.0
        self.points = w.header.points
        self.firmware = w.header.firmware_version

        idx = channel_number - 1
        ch_data = w.header.channel_data[idx] if idx < len(w.header.channel_data) else None
        if ch_data is not None and self.enabled_and_selected:
            self.volts = ch_data.astype(np.float64)

            raw_data = getattr(w.header, "raw_data", None)
            raw8 = raw_data[idx] if isinstance(raw_data, list) and idx < len(raw_data) else None
            if raw8 is None:
                raw8 = np.full(self.volts.shape, 127, dtype=np.uint8)

            self.raw = raw8
            self.points = len(self.volts)
            t0 = w.header.x_origin
            self.times = t0 + np.arange(self.points) * w.header.x_increment

    def agilent(self, w: Any, channel_number: int) -> None:
        """Interpret normalized waveform data for an Agilent/Keysight `.bin` file."""
        self.time_scale = w.header.time_scale
        self.time_offset = 0.0
        self.points = w.header.points
        self.firmware = w.header.firmware_version

        idx = channel_number - 1
        ch_data = w.header.channel_data[idx] if idx < len(w.header.channel_data) else None
        if ch_data is not None and self.enabled_and_selected:
            self.volts = ch_data.astype(np.float64)

            raw_data = getattr(w.header, "raw_data", None)
            raw8 = raw_data[idx] if isinstance(raw_data, list) and idx < len(raw_data) else None
            if raw8 is None:
                raw8 = np.full(self.volts.shape, 127, dtype=np.uint8)

            self.raw = raw8
            self.points = len(self.volts)
            t0 = w.header.x_origin
            self.times = t0 + np.arange(self.points) * w.header.x_increment

    def tek(self, w: Any, channel_number: int) -> None:
        """Interpret normalized waveform data for a Tektronix .wfm file."""
        self.time_scale = w.header.time_scale
        self.time_offset = 0.0
        self.points = w.header.points
        self.firmware = w.header.firmware_version

        idx = channel_number - 1
        ch_data = w.header.channel_data[idx] if idx < len(w.header.channel_data) else None
        if ch_data is not None and self.enabled_and_selected:
            self.volts = ch_data.astype(np.float64)

            raw_data = getattr(w.header, "raw_data", None)
            raw8 = raw_data[idx] if isinstance(raw_data, list) and idx < len(raw_data) else None
            if raw8 is None:
                raw8 = np.full(self.volts.shape, 127, dtype=np.uint8)

            self.raw = raw8
            self.points = len(self.volts)
            t0 = w.header.x_origin
            self.times = t0 + np.arange(self.points) * w.header.x_increment

    def yokogawa(self, w: Any, channel_number: int) -> None:
        """Interpret normalized waveform data for a Yokogawa .wfm file."""
        self.time_scale = w.header.time_scale
        self.time_offset = 0.0
        self.points = w.header.points
        self.firmware = w.header.firmware_version

        idx = channel_number - 1
        ch_data = w.header.channel_data[idx] if idx < len(w.header.channel_data) else None
        if ch_data is not None and self.enabled_and_selected:
            self.volts = ch_data.astype(np.float64)

            raw_data = getattr(w.header, "raw_data", None)
            raw8 = raw_data[idx] if isinstance(raw_data, list) and idx < len(raw_data) else None
            if raw8 is None:
                raw8 = np.full(self.volts.shape, 127, dtype=np.uint8)

            self.raw = raw8
            self.points = len(self.volts)
            t0 = w.header.x_origin
            self.times = t0 + np.arange(self.points) * w.header.x_increment
