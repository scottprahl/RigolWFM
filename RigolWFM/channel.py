#pylint: disable=invalid-name
#pylint: disable=too-many-instance-attributes
#pylint: disable=too-many-return-statements
#pylint: disable=too-many-statements
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


def _channel_bytes(channel_number, w):
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

    if w.header.stride == 2:   # byte pattern CHx CHy
        # use odd bytes when this is the second enabled channel
        if any([w.header.ch[i].enabled for i in range(channel_number-1)]):
            offset = 1

    elif w.header.stride == 4:  # byte pattern CH4 CH3 CH2 CH1
        offset = 4 - channel_number

    data = np.frombuffer(w.data.raw, dtype=np.uint8)
    raw_bytes = data[offset::w.header.stride]

    return raw_bytes


class Channel():
    """Base class for a single channel."""

    def __init__(self, w, channel_number, scope, selected='1234'):
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
        self.name = "CH %d" % channel_number
        self.waveform = w
        self.seconds_per_point = w.header.seconds_per_point
        self.firmware = 'unknown'
        self.unit = UnitEnum.v
        self.points = 0
        self.raw = None
        self.volts = None
        self.times = None
        self.coupling = 'unknown'
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
        chosen = selected.find(str(channel_number)) != -1

        if channel_number <= len(w.header.ch):
            channel = w.header.ch[channel_number-1]
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

        if scope == 'wfm1000c':
            self.ds1000c(w, channel_number)
        elif scope == 'wfm1000d':
            self.ds1000d(w, channel_number)
        elif scope == 'wfm1000e':
            self.ds1000e(w, channel_number)
        elif scope == 'wfm1000z':
            self.ds1000z(w, channel_number)
        elif scope == 'wfm2000':
            self.ds2000(w, channel_number)
        elif scope == 'wfm4000':
            self.ds4000(w, channel_number)
        elif scope == 'wfm6000':
            self.ds6000(w, channel_number)

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

        if self.enabled_and_selected:
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
        if self.enabled_and_selected:
            self.volts = self.y_scale * (127.0 - self.raw) - self.y_offset
            h = self.points * self.seconds_per_point / 2
            self.times = np.linspace(-h, h, self.points) + self.time_offset


    def ds1000c(self, w, channel_number):
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

        self.calc_times_and_volts()


    def ds1000d(self, w, channel_number):
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

        self.calc_times_and_volts()


    def ds1000e(self, w, channel_number):
        """Interpret waveform data for 1000D and 1000E series scopes."""
        self.roll_stop = w.header.roll_stop

        if channel_number == 1:
            self.time_offset = w.header.ch1_time_offset
            self.time_scale = w.header.ch1_time_scale
            if self.enabled_and_selected:
                self.points = len(w.data.ch1)
                self.raw = np.frombuffer(w.data.ch1, dtype=np.uint8)

        elif channel_number == 2:
            self.time_offset = w.header.ch2_time_offset
            self.time_scale = w.header.ch2_time_scale
            if self.enabled_and_selected:
                self.points = len(w.data.ch2)
                self.raw = np.frombuffer(w.data.ch2, dtype=np.uint8)

        self.calc_times_and_volts()

    def ds1000z(self, w, channel_number):
        """Interpret waveform for the Rigol DS1000Z series."""
        self.time_scale = w.header.time_scale
        self.time_offset = w.header.time_offset
        self.points = w.header.points
        self.stride = w.header.stride
        self.firmware = w.preheader.firmware_version
        self.probe = w.header.ch[channel_number-1].probe_value
        self.coupling = w.header.ch[channel_number-1].coupling.name.upper()
        self.y_scale = w.header.ch[channel_number-1].y_scale
        self.y_offset = w.header.ch[channel_number-1].y_offset

        if self.enabled_and_selected:
            self.raw = _channel_bytes(channel_number, w)
            self.points = len(self.raw)

        self.calc_times_and_volts()

    def ds2000(self, w, channel_number):
        """Interpret waveform for the Rigol DS2000 series."""
        self.time_offset = w.header.time_offset
        self.time_scale = w.header.time_scale
        self.points = w.header.storage_depth
        self.firmware = w.header.firmware_version
        self.unit = UnitEnum(w.header.ch[channel_number-1].unit_actual)
        self.coupling = w.header.ch[channel_number-1].coupling.name.upper()
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

        self.calc_times_and_volts()


    def ds4000(self, w, channel_number):
        """Interpret waveform for the Rigol DS4000 series."""
        self.time_offset = w.header.time_offset
        self.time_scale = w.header.time_scale
        self.points = w.header.points
        self.firmware = w.header.firmware_version
        self.coupling = w.header.ch[channel_number-1].coupling.name.upper()
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

        self.calc_times_and_volts()


    def ds6000(self, w, channel_number):
        """Interpret waveform for the Rigol DS6000 series."""
        self.time_offset = w.header.time_offset
        self.time_scale = w.header.time_scale
        self.points = w.header.points
        self.firmware = w.header.firmware_version
        self.coupling = w.header.ch[channel_number-1].coupling.name.upper()
        self.unit = w.header.ch[channel_number-1].unit

        if self.enabled_and_selected:
            if channel_number == 1:
                self.raw = np.array(w.header.raw_1, dtype=np.uint8)

            if channel_number == 2:
                self.raw = np.array(w.header.raw_2, dtype=np.uint8)

            if channel_number == 3:
                self.raw = np.array(w.header.raw_3, dtype=np.uint8)

            if channel_number == 4:
                self.raw = np.array(w.header.raw_4, dtype=np.uint8)

        self.calc_times_and_volts()
