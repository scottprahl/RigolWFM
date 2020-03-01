#pylint: disable=invalid-name
#pylint: disable=too-many-instance-attributes
#pylint: disable=unsubscriptable-object
#pylint: disable=too-few-public-methods

"""
Extract signals or description from Rigol 1000E Oscilloscope waveform file.

Use like this::

    import RigolWFM.wfme as wfme

    channels = wfme.parse("filename.wfm", '1000E')
    for ch in channels:
        print(ch)
"""
import numpy as np


def engineering_string(number):
    """Format number with proper prefix"""
    absnr = abs(number)

    if absnr == 0:
        engr_str = '%g ' % (number / 1e-12)
    elif absnr < 0.99999999e-9:
        engr_str = '%g p' % (number / 1e-12)
    elif absnr < 0.99999999e-6:
        engr_str = '%g n' % (number / 1e-9)
    elif absnr < 0.99999999e-3:
        engr_str = '%g µ' % (number / 1e-6)
    elif absnr < 0.99999999:
        engr_str = '%g m' % (number / 1e-3)
    elif absnr < 0.99999999e3:
        engr_str = '%g ' % (number)
    elif absnr < 0.99999999e6:
        engr_str = '%g k' % (number / 1e3)
    elif absnr < 0.999999991e9:
        engr_str = '%g M' % (number / 1e6)
    else:
        engr_str = '%g G' % (number / 1e9)
    return engr_str


class Channel():
    """Base class for a single channel."""

    def __init__(self, w, ch):
        self.scope_type = 'default'
        self.channel_number = ch
        self.name = "CH %d" % ch
        self.waveform = w
        self.seconds_per_point = w.header.seconds_per_point
        channel = w.header.ch[ch-1]
        self.enabled = channel.enabled
        self.volt_scale = channel.volt_scale
        self.volt_offset = channel.volt_offset
        self.volt_per_division = channel.volt_per_division
        self.firmware = 'unknown'
        self.points = 0
        self.raw = None
        self.volts = None
        self.times = None
        self.coupling = 'unknown'
        self.roll_stop = 0
        self.time_offset = 0
        self.time_scale = 1

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
        s += "        Delay  = " + engineering_string(self.time_offset) + "s\n"
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


class DS1000C(Channel):
    """Base class for a single channel from 1000CD series scopes."""

    def __init__(self, w, ch):
        super().__init__(w, ch)
        self.scope_type = '1000C'

        if ch == 1:
            self.time_offset = w.header.ch1_time_delay
            self.time_scale = w.header.ch1_time_scale
            if self.enabled:
                self.points = len(w.data.ch1)
                self.raw = np.array(w.data.ch1)

        if ch == 2:
            self.time_offset = w.header.ch2_time_delay
            self.time_scale = w.header.ch2_time_scale
            if self.enabled:
                self.points = len(w.data.ch2)
                self.raw = np.array(w.data.ch2)

        if self.enabled:
            self.volts = self.volt_scale * \
                (127.0 - self.raw) - self.volt_offset
            half = self.points * self.seconds_per_point / 2
            self.times = np.linspace(-half, half,
                                     self.points) + self.time_offset


class DS1000E(Channel):
    """Base class for a single channel from 1000E series scopes."""

    def __init__(self, w, ch):
        super().__init__(w, ch)
        self.scope_type = '1000E'
        self.roll_stop = w.header.roll_stop

        if ch == 1:
            self.time_offset = w.header.ch1_time_delay
            self.time_scale = w.header.ch1_time_scale
            if self.enabled:
                self.points = len(w.data.ch1)
                self.raw = np.array(w.data.ch1)

        if ch == 2:
            self.time_offset = w.header.ch2_time_delay
            self.time_scale = w.header.ch2_time_scale
            if self.enabled:
                self.points = len(w.data.ch2)
                self.raw = np.array(w.data.ch2)

        if self.enabled:
            self.volts = self.volt_scale * \
                (127.0 - self.raw) - self.volt_offset
            half = self.points * self.seconds_per_point / 2
            self.times = np.linspace(-half, half,
                                     self.points) + self.time_offset


class DS1000Z(Channel):
    """Base class for a single channel from 1000Z series scopes."""

    def channel_bytes(self, enabled_count, data):
        """
        Return right series of bytes for a channel.

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

        if self.stride == 1:
            raw_bytes = np.array(data.raw1, dtype=np.uint8)

        if self.stride == 2:
            if enabled_count == 0:
                raw_bytes = np.array(data.raw2 & 0x00FF, dtype=np.uint8)
            else:
                raw_bytes = np.array((data.raw2 & 0xFF00) >> 8, dtype=np.uint8)

        if self.stride == 4:
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

    def __init__(self, w, ch, enabled_count):
        super().__init__(w, ch)
        self.time_scale = w.header.seconds_per_division
        self.time_offset = w.header.time_offset
        self.points = w.header.points
        self.stride = w.header.stride
        self.firmware = w.preheader.firmware_version
        self.scope_type = w.preheader.model_number
        self.probe = w.header.ch[ch-1].probe_value
        self.coupling = w.header.ch[ch-1].coupling.name.upper()

        if self.enabled:
            self.raw = self.channel_bytes(enabled_count, w.data)
            self.volts = self.volt_scale * \
                (self.raw - 127.0) + self.volt_offset
            half = self.points * self.seconds_per_point / 2.0
            self.times = np.linspace(-half, half,
                                     self.points) + self.time_offset


class DS4000(Channel):
    """Base class for a single channel from 4000 series scopes."""

    def __init__(self, w, ch):
        super().__init__(w, ch)
        self.time_offset = w.header.time_delay
        self.time_scale = w.header.time_scale
        self.points = w.header.points
        self.firmware = w.header.firmware_version
        self.scope_type = w.header.model_number
        self.coupling = w.header.ch[ch-1].coupling.name.upper()

        if self.enabled:
            if ch == 1:
                self.raw = np.array(w.header.raw_1)

            if ch == 2:
                self.raw = np.array(w.header.raw_2)

            if ch == 3:
                self.raw = np.array(w.header.raw_3)

            if ch == 4:
                self.raw = np.array(w.header.raw_4)

            self.volts = self.volt_scale * \
                (self.raw - 127.0) - self.volt_offset
            half = self.points * self.seconds_per_point / 2
            self.times = np.linspace(-half, half,
                                     self.points) + self.time_offset
