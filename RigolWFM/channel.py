#pylint: disable=invalid-name
#pylint: disable=too-many-instance-attributes

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
import numpy as np

def best_scale(number):
    """Scale and units for a number with proper prefix"""
    absnr = abs(number)

    if absnr == 0:
        return 1, ''
    elif absnr < 0.99999999e-9:
        return 1e12, 'p'
    elif absnr < 0.99999999e-6:
        return 1e9, 'n'
    elif absnr < 0.99999999e-3:
        return 1e6, 'µ'
    elif absnr < 0.99999999:
        return 1e3, 'm'
    elif absnr < 0.99999999e3:
        return 1, ''
    elif absnr < 0.99999999e6:
        return 1e-3, 'k'
    elif absnr < 0.999999991e9:
        return 1e-6, 'M'
    else:
        return 1e-9, 'G'

def engineering_string(number):
    """Format number with proper prefix"""
    
    scale, prefix = best_scale(number)
    s = "%g %s" % (number * scale, prefix)
    return s

   
def _channel_bytes(enabled_count, data, stride):
    """
    Return right series of bytes for a channel for 1000Z scopes

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
            raw_bytes = np.array(data.raw2 & 0x00FF, dtype=np.uint8)
        else:
            raw_bytes = np.array((data.raw2 & 0xFF00) >> 8, dtype=np.uint8)

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
        self.scope_type = 'default'
        self.channel_number = ch
        self.name = "CH %d" % ch
        self.waveform = w
        self.seconds_per_point = w.header.seconds_per_point
        self.firmware = 'unknown'
        self.unit = 'VOLTS'
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
            self.volt_per_division = channel.volt_per_division
        else:
            self.enabled = False
            self.volt_scale = 1
            self.volt_offset = 0
            self.volt_per_division = 1

        if scope == 'C':
            self.ds1000c(w, ch)
        elif scope == 'E':
            self.ds1000e(w, ch)
        elif scope == 'Z':
            self.ds1000z(w, ch, prior)
        elif scope == '4':
            self.ds4000(w, ch)
        elif scope == '6':
            self.ds6000(w, ch)


    def __str__(self):
        s = "Channel %d\n" % self.channel_number
        s += "    General:\n"
        s += "         Scope = %s\n" % self.scope_type
        s += "      Firmware = %s\n" % self.firmware
        s += "       Enabled = %s\n" % self.enabled
        s += "    Voltage:\n"
        s += "        Scale  = " + \
            engineering_string(self.volt_per_division) + "V/div\n"
        s += "        Offset = " + engineering_string(self.volt_offset) + "V\n"
        s += "      Coupling = %s\n" % self.coupling
        s += "    Time:\n"
        s += "        Scale  = " + \
            engineering_string(self.time_scale) + "s/div\n"
        s += "        offset  = " + engineering_string(self.time_offset) + "s\n"
        s += "        Delta  = " + \
            engineering_string(self.seconds_per_point) + "s/point\n"
        s += "    Data:\n"
        s += "        Points = %d\n" % self.points
        if self.enabled:
            s += "        Raw    = [%9d,%9d,%9d  ... %9d,%9d]\n" % (
                self.raw[0], self.raw[1], self.raw[2], self.raw[-2], self.raw[-1])
            v = [engineering_string(self.volts[i]) +
                 "V" for i in [0, 1, 2, -2, -1]]
            s += "        Volts  = [%9s,%9s,%9s  ... %9s,%9s]\n" % (
                v[0], v[1], v[2], v[-2], v[-1])
            t = [engineering_string(self.times[i]) +
                 "s" for i in [0, 1, 2, -2, -1]]
            s += "        Times  = [%9s,%9s,%9s  ... %9s,%9s]\n" % (
                t[0], t[1], t[2], t[-2], t[-1])
        return s

    def calc_times_and_volts(self):
        """Calculate the times and voltages for this channel."""
        if self.enabled:
            self.volts = self.volt_scale * (127.0 - self.raw) - self.volt_offset
            h = self.points * self.seconds_per_point / 2
            self.times = np.linspace(-h, h, self.points) + self.time_offset

    def ds1000c(self, w, ch):
        """Interpret waveform data for 1000CD series scopes."""
        self.scope_type = '1000C'

        if ch == 1:
            self.time_offset = w.header.ch1_time_offset
            self.time_scale = w.header.ch1_time_scale
            if self.enabled:
                self.points = len(w.data.ch1)
                self.raw = np.array(w.data.ch1)

        if ch == 2:
            self.time_offset = w.header.ch2_time_offset
            self.time_scale = w.header.ch2_time_scale
            if self.enabled:
                self.points = len(w.data.ch2)
                self.raw = np.array(w.data.ch2)

        self.calc_times_and_volts()


    def ds1000e(self, w, ch):
        """Interpret waveform data for 1000D and 1000E series scopes."""

        self.scope_type = '1000E'
        self.roll_stop = w.header.roll_stop

        if ch == 1:
            self.time_offset = w.header.ch1_time_offset
            self.time_scale = w.header.ch1_time_scale
            if self.enabled:
                self.points = len(w.data.ch1)
                self.raw = np.array(w.data.ch1)

        elif ch == 2:
            self.time_offset = w.header.ch2_time_offset
            self.time_scale = w.header.ch2_time_scale
            if self.enabled:
                self.points = len(w.data.ch2)
                self.raw = np.array(w.data.ch2)

        self.calc_times_and_volts()

    def ds1000z(self, w, ch, enabled_count):
        """Interpret waveform for the Rigol DS1000Z series."""

        self.time_scale = w.header.time_scale
        self.time_offset = w.header.time_offset
        self.points = w.header.points
        self.stride = w.header.stride
        self.firmware = w.preheader.firmware_version
        self.scope_type = w.preheader.model_number
        self.probe = w.header.ch[ch-1].probe_value
        self.coupling = w.header.ch[ch-1].coupling.name.upper()
        self.unit = w.header.ch[ch-1].unit

        if self.enabled:
            self.raw = _channel_bytes(enabled_count, w.data, self.stride)

        self.calc_times_and_volts()

    def ds2000(self, w, ch):
        """Interpret waveform for the Rigol DS2000 series."""

        if ch == 1:
            self.raw[0::2] = np.array(w.data.ch1)

        if ch == 2:
            self.raw[1::2] = np.array(w.data.ch2)

        self.calc_times_and_volts()


    def ds4000(self, w, ch):
        """Interpret waveform for the Rigol DS4000 series."""

        self.time_offset = w.header.time_offset
        self.time_scale = w.header.time_scale
        self.points = w.header.points
        self.firmware = w.header.firmware_version
        self.scope_type = w.header.model_number
        self.coupling = w.header.ch[ch-1].coupling.name.upper()

        if self.enabled:
            if ch == 1:
                self.raw = np.array(w.header.raw_1)

            elif ch == 2:
                self.raw = np.array(w.header.raw_2)

            elif ch == 3:
                self.raw = np.array(w.header.raw_3)

            elif ch == 4:
                self.raw = np.array(w.header.raw_4)

        self.calc_times_and_volts()


    def ds6000(self, w, ch):
        """Interpret waveform for the Rigol DS6000 series."""

        self.time_offset = w.header.time_offset
        self.time_scale = w.header.time_scale
        self.points = w.header.points
        self.firmware = w.header.firmware_version
        self.scope_type = w.header.model_number
        self.coupling = w.header.ch[ch-1].coupling.name.upper()
        self.unit = w.header.ch[ch-1].unit

        if self.enabled:
            if ch == 1:
                self.raw = np.array(w.header.raw_1)

            if ch == 2:
                self.raw = np.array(w.header.raw_2)

            if ch == 3:
                self.raw = np.array(w.header.raw_3)

            if ch == 4:
                self.raw = np.array(w.header.raw_4)

        self.calc_times_and_volts()
