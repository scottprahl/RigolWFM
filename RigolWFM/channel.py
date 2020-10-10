#pylint: disable=invalid-name
#pylint: disable=too-many-instance-attributes
#pylint: disable=too-many-return-statements
"""
Class structure and methods for an oscilloscope channel.

The idea is to collect all the relevant information from all the Rigol
scope waveforms into a single structure that can be handled in a uniform
and consistent manner.

Specifically this lets one just use

    channel.times   : numpy array of signal times
    channel.volts   : numpy array of signal voltages

or the stringification method to describe a channel

    print(channel)

"""
from enum import Enum
import numpy as np

class UnitEnum(Enum):
    """Enumerated units for scopes without them."""

    w = 0
    a = 1
    v = 2
    u = 3

def best_scale(number):
    """Scale and units for a number with proper prefix."""
    absnr = abs(number)

    if absnr == 0:
        return 1, ' '
    if absnr < 0.99999999e-9:
        return 1e12, 'p'
    if absnr < 0.99999999e-6:
        return 1e9, 'n'
    if absnr < 0.99999999e-3:
        return 1e6, 'µ'
    if absnr < 0.99999999:
        return 1e3, 'm'
    if absnr < 0.99999999e3:
        return 1, ' '
    if absnr < 0.99999999e6:
        return 1e-3, 'k'
    if absnr < 0.999999991e9:
        return 1e-6, 'M'
    return 1e-9, 'G'

def engineering_string(number, n_digits):
    """Format number with proper prefix."""
    scale, prefix = best_scale(number)
    fformat = "%%.%df %%s" % n_digits
    s = fformat % (number * scale, prefix)
    return s


### maybe replace with something like
#    x0[0::2] = data[offset_1:offset_1+pagesize]
#    x0[1::2] = data[offset_2:offset_2+pagesize]

def _channel_bytes(enabled_count, data, stride):
    """
    Return right series of bytes for a channel for 1000Z scopes.

    Waveform points are interleaved stored in memory when two or more
    channels are enabled:

    Only one channel enabled:
        CH1CH1CH1CH1

    Two channels Enabled:
        CH2CH1CH2CH1

    Three or Four channels enabled:
        CH4CH3CH2CH1

    Args:
        enabled_count: the number of enabled channels before this one
        data:          object containing the raw data structures
    Returns
        byte array for a particular channel
    """
    if stride == 1:
        raw_bytes = np.array(data.raw1, dtype=np.uint8)

    if stride == 2:
        if enabled_count == 0:
            raw_bytes = np.array(np.uint16(data.raw2) & 0x00FF, dtype=np.uint8)
        else:
            raw_bytes = np.array((np.uint16(data.raw2) & 0xFF00) >> 8, dtype=np.uint8)

    if stride == 4:
        if enabled_count == 3:
            raw_bytes = np.array(np.uint32(data.raw4)
                                 & 0x000000FF, dtype=np.uint8)
        elif enabled_count == 2:
            raw_bytes = np.array(
                (np.uint32(data.raw4) & 0x0000FF00) >> 8, dtype=np.uint8)
        elif enabled_count == 1:
            raw_bytes = np.array(
                (np.uint32(data.raw4) & 0x00FF0000) >> 16, dtype=np.uint8)
        else:
            raw_bytes = np.array(
                (np.uint32(data.raw4) & 0xFF000000) >> 24, dtype=np.uint8)

    return raw_bytes


class Channel():
    """Base class for a single channel."""

    def __init__(self, w, ch, scope, prior):
        """
        Initialize a Channel Object.

        Args:
            w: Wfm object
            ch: 1,2,3,4
            scope: string describing scope
            prior: number of channels that came before
        Returns:
            Channel object
        """
        self.channel_number = ch
        self.name = "CH %d" % ch
        self.waveform = w
        self.seconds_per_point = w.header.seconds_per_point
        self.firmware = 'unknown'
        self.unit = 'V'
        self.points = 0
        self.raw = None
        self.volts = None
        self.times = None
        self.coupling = 'unknown'
        self.roll_stop = 0
        self.time_offset = 0
        self.time_scale = 1

        if ch <= len(w.header.ch):
            channel = w.header.ch[ch-1]
            self.enabled = channel.enabled
            self.volt_scale = channel.volt_scale
            self.volt_offset = channel.volt_offset
            self.y_scale = channel.volt_scale
            self.y_offset = channel.volt_offset
            self.volt_per_division = channel.volt_per_division
            self.probe_value = channel.probe_value
            self.unit = channel.unit
            self.inverted = channel.inverted
        else:
            self.enabled = False
            self.volt_scale = 1
            self.volt_offset = 0
            self.y_scale = 1
            self.y_offset = 0
            self.volt_per_division = 1
            self.probe_value = 1
            self.unit = UnitEnum.v
            self.inverted = False

        if scope == 'wfm1000c':
            self.ds1000c(w, ch)
        elif scope == 'wfm1000e':
            self.ds1000e(w, ch)
        elif scope == 'wfm1000z':
            self.ds1000z(w, ch, prior)
        elif scope == 'wfm2000':
            self.ds2000(w, ch)
        elif scope == 'wfm4000':
            self.ds4000(w, ch)
        elif scope == 'wfm6000':
            self.ds6000(w, ch)


    def __str__(self):
        """Describe this channel."""
        s = "     Channel %d:\n" % self.channel_number
        s += "         Coupling = %8s\n" % self.coupling.rjust(7, ' ')
        s += "            Scale = %10sV/div\n" % engineering_string(self.volt_per_division, 2)
        s += "           Offset = %10sV\n" % engineering_string(self.volt_offset, 2)
        s += "            Probe = %7gX\n" % self.probe_value
        s += "         Inverted = %8s\n\n" % self.inverted
        s += "        Time Base = %10ss/div\n" % engineering_string(self.time_scale, 3)
        s += "           Offset = %10ss\n" % engineering_string(self.time_offset, 3)
        s += "            Delta = %10ss/point\n" % engineering_string(self.seconds_per_point, 3)
        s += "           Points = %8d\n\n" % self.points
        if self.enabled:
            s += "         Count    = [%9d,%9d,%9d  ... %9d,%9d]\n" % (
                1, 2, 3, self.points-1, self.points)
            s += "           Raw    = [%9d,%9d,%9d  ... %9d,%9d]\n" % (
                self.raw[0], self.raw[1], self.raw[2], self.raw[-2], self.raw[-1])
            t = [engineering_string(self.times[i], 3) +
                 "s" for i in [0, 1, 2, -2, -1]]
            s += "           Times  = [%9s,%9s,%9s  ... %9s,%9s]\n" % (
                t[0], t[1], t[2], t[-2], t[-1])
            v = [engineering_string(self.volts[i], 2) +
                 "V" for i in [0, 1, 2, -2, -1]]
            s += "           Volts  = [%9s,%9s,%9s  ... %9s,%9s]\n" % (
                v[0], v[1], v[2], v[-2], v[-1])
        return s

    def calc_times_and_volts(self):
        """Calculate the times and voltages for this channel."""
        if self.enabled:
            self.volts = self.y_scale * (127.0 - self.raw) - self.y_offset
            h = self.points * self.seconds_per_point / 2
            self.times = np.linspace(-h, h, self.points) + self.time_offset


    def ds1000c(self, w, ch):
        """Interpret waveform data for 1000CD series scopes."""
        if ch == 1:
            self.time_offset = w.header.ch1_time_offset
            self.time_scale = w.header.ch1_time_scale
            if self.enabled:
                self.points = len(w.data.ch1)
                self.raw = np.array(w.data.ch1, dtype=np.uint8)

        if ch == 2:
            self.time_offset = w.header.ch2_time_offset
            self.time_scale = w.header.ch2_time_scale
            if self.enabled:
                self.points = len(w.data.ch2)
                self.raw = np.array(w.data.ch2, dtype=np.uint8)

        self.calc_times_and_volts()


    def ds1000e(self, w, ch):
        """Interpret waveform data for 1000D and 1000E series scopes."""
        self.roll_stop = w.header.roll_stop

        if ch == 1:
            self.time_offset = w.header.ch1_time_offset
            self.time_scale = w.header.ch1_time_scale
            if self.enabled:
                self.points = len(w.data.ch1)
                self.raw = np.array(w.data.ch1, dtype=np.uint8)

        elif ch == 2:
            self.time_offset = w.header.ch2_time_offset
            self.time_scale = w.header.ch2_time_scale
            if self.enabled:
                self.points = len(w.data.ch2)
                self.raw = np.array(w.data.ch2, dtype=np.uint8)

        self.calc_times_and_volts()
#        if self.enabled:
#            self.volts *= self.probe_value

    def ds1000z(self, w, ch, enabled_count):
        """Interpret waveform for the Rigol DS1000Z series."""
        self.time_scale = w.header.time_scale
        self.time_offset = w.header.time_offset
        self.points = w.header.points
        self.stride = w.header.stride
        self.firmware = w.preheader.firmware_version
        self.probe = w.header.ch[ch-1].probe_value
        self.coupling = w.header.ch[ch-1].coupling.name.upper()
        self.y_scale = w.header.ch[ch-1].y_scale
        self.y_offset = w.header.ch[ch-1].y_offset

        if self.enabled:
            self.raw = _channel_bytes(enabled_count, w.data, self.stride)

        self.calc_times_and_volts()

    def ds2000(self, w, ch):
        """Interpret waveform for the Rigol DS2000 series."""
        self.time_offset = w.header.time_offset
        self.time_scale = w.header.time_scale
        self.points = w.header.storage_depth
        self.firmware = w.header.firmware_version
        self.unit = UnitEnum(w.header.ch[ch-1].unit_actual)
        self.coupling = w.header.ch[ch-1].coupling.name.upper()
        self.y_scale = -self.volt_scale
        self.y_offset = self.volt_offset

        if self.enabled:
            if ch == 1:
                self.raw = np.array(w.header.raw_1, dtype=np.uint8)

            if ch == 2:
                self.raw = np.array(w.header.raw_2, dtype=np.uint8)

            if ch == 3:
                self.raw = np.array(w.header.raw_3, dtype=np.uint8)

            if ch == 4:
                self.raw = np.array(w.header.raw_4, dtype=np.uint8)

        self.calc_times_and_volts()


    def ds4000(self, w, ch):
        """Interpret waveform for the Rigol DS4000 series."""
        self.time_offset = w.header.time_offset
        self.time_scale = w.header.time_scale
        self.points = w.header.points
        self.firmware = w.header.firmware_version
        self.coupling = w.header.ch[ch-1].coupling.name.upper()
        self.y_scale = -self.volt_scale
        self.y_offset = self.volt_offset

        if self.enabled:
            if ch == 1:
                self.raw = np.array(w.header.raw_1, dtype=np.uint8)

            elif ch == 2:
                self.raw = np.array(w.header.raw_2, dtype=np.uint8)

            elif ch == 3:
                self.raw = np.array(w.header.raw_3, dtype=np.uint8)

            elif ch == 4:
                self.raw = np.array(w.header.raw_4, dtype=np.uint8)

        self.calc_times_and_volts()


    def ds6000(self, w, ch):
        """Interpret waveform for the Rigol DS6000 series."""
        self.time_offset = w.header.time_offset
        self.time_scale = w.header.time_scale
        self.points = w.header.points
        self.firmware = w.header.firmware_version
        self.coupling = w.header.ch[ch-1].coupling.name.upper()
        self.unit = w.header.ch[ch-1].unit

        if self.enabled:
            if ch == 1:
                self.raw = np.array(w.header.raw_1, dtype=np.uint8)

            if ch == 2:
                self.raw = np.array(w.header.raw_2, dtype=np.uint8)

            if ch == 3:
                self.raw = np.array(w.header.raw_3, dtype=np.uint8)

            if ch == 4:
                self.raw = np.array(w.header.raw_4, dtype=np.uint8)

        self.calc_times_and_volts()
