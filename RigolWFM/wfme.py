#pylint: disable=invalid-name
#pylint: disable=too-many-instance-attributes

"""
Extract signals or description from Rigol 1000E Oscilloscope waveform file.

Use like this::

    import RigolWFM.wfme as wfme

    channels = wfme.parse("filename.wfm")
    for ch in channels:
        print(ch)
"""

import tempfile
import requests
import numpy as np

import RigolWFM.wfm1000e
import RigolWFM.wfm1000z
import RigolWFM.wfm4000
import RigolWFM.wfm6000


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

    def __init__(self):
        self.channel_number = 1
        self.enabled = False
        self.volts_per_division = 1  # V/div
        self.volts_offset = 0        # V
        self.time_scale = 1          # s/div
        self.seconds_per_point = 0.1    # s/point
        self.time_offset = 0         # s
        self.points = 0
        self.raw = None

    def __str__(self):
        s = "Channel %d\n" % self.channel_number
        s += "    Enabled:   %s\n" % self.enabled
        s += "    Voltage:\n"
        s += "        Scale  = " + engineering_string(self.volts_per_division) + "V/div\n"
        s += "        Offset = " + engineering_string(self.volts_offset) + "V\n"
        s += "    Time:\n"
        s += "        Scale  = " + engineering_string(self.time_scale) + "s/div\n"
        s += "        Delay  = " + engineering_string(self.time_offset) + "s\n"
        s += "        Delta  = " + engineering_string(self.seconds_per_point) + "s/point\n"
        s += "    Data:\n"
        s += "        Points = %d\n" % self.points
        if self.enabled:
            s += "        Raw    = [%9d,%9d,%9d  ... %9d,%9d]\n" % (
                self.raw[0], self.raw[1], self.raw[2], self.raw[-2], self.raw[-1])
            v = [engineering_string(self.volts[i])+"V" for i in [0,1,2,-2,-1]]
            s += "        Volts  = [%9s,%9s,%9s  ... %9s,%9s]\n" % (v[0],v[1],v[2],v[3],v[4])
            t = [engineering_string(self.times[i])+"s" for i in [0,1,2,-2,-1]]
            s += "        Times  = [%9s,%9s,%9s  ... %9s,%9s]\n" % (t[0],t[1],t[2],t[3],t[4])
        return s


class ChannelE(Channel):
    """Base class for a single channel from 1000E series scopes."""

    def __init__(self, w, ch=1):
        super().__init__()
        self.channel_number = ch
        self.seconds_per_point = w.header.seconds_per_point

        if ch == 1:
            self.enabled = w.header.ch1.enabled
            self.volts_per_division = w.header.ch1_volts_per_division
            self.volts_offset = w.header.ch1_volts_offset
            self.time_offset = w.header.ch1_time_delay
            self.time_scale = w.header.ch1_time_scale
            self.points = w.header.ch1_points
            if self.enabled:
                self.raw = np.array(w.data.ch1)
                self.volts = self.volts_per_division * (5.0 - self.raw/25.0) - self.volts_offset
                self.times  = np.arange(self.points) * self.seconds_per_point

                
        elif ch == 2:
            self.enabled = w.header.ch2.enabled
            self.volts_per_division = w.header.ch2_volts_per_division
            self.volts_offset = w.header.ch2_volts_offset
            self.time_offset = w.header.ch2_time_delay
            self.time_scale = w.header.ch2_time_scale
            self.points = w.header.ch2_points
            if self.enabled:
                self.raw = np.array(w.data.ch2)
                self.volts = self.volts_per_division * (5.0 - self.raw/25.0) - self.volts_offset
                self.times  = np.arange(self.points) * self.seconds_per_point


class ChannelZ(Channel):
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
            bytes = np.array(data.raw1, dtype=np.uint8)
            
        if self.stride == 2:
            if enabled_count == 0:
                bytes = np.array(data.raw2 & 0x00FF, dtype=np.uint8)
            else:
                bytes = np.array((data.raw2 & 0xFF00) >> 8, dtype=np.uint8)
            
        if self.stride == 4:
            if enabled_count == 3:
                bytes = np.array(np.uint32(data.raw4) & 0x000000FF, dtype=np.uint8)
            elif enabled_count == 2:
                bytes = np.array((np.uint32(data.raw4) & 0x0000FF00) >> 8, dtype=np.uint8)
            elif enabled_count == 1:
                bytes = np.array((np.uint32(data.raw4) & 0x00FF0000) >> 16, dtype=np.uint8)
            else:
                bytes = np.array((np.uint32(data.raw4) & 0xFF000000) >> 24, dtype=np.uint8)
        
        return bytes
            
    def __init__(self, w, ch, enabled_count):
        super().__init__()
        self.channel_number = ch
        self.seconds_per_point = w.header.seconds_per_point
        self.time_scale = w.header.seconds_per_division
        self.time_offset = w.header.time_offset
        self.points = w.header.points
        self.stride = w.header.stride
        
        if ch == 1:
            self.enabled = w.header.ch1.enabled
            self.probe = w.header.ch1.probe_value
            self.volts_per_division = w.header.ch1.scale
            self.volts_offset = w.header.ch1.shift
        if ch == 2:
            self.enabled = w.header.ch2.enabled
            self.probe = w.header.ch2.probe_value
            self.volts_per_division = w.header.ch2.scale
            self.volts_offset = w.header.ch2.shift
        if ch == 3:
            self.enabled = w.header.ch3.enabled
            self.probe = w.header.ch3.probe_value
            self.volts_per_division = w.header.ch3.scale
            self.volts_offset = w.header.ch3.shift
        elif ch == 4:
            self.enabled = w.header.ch4.enabled
            self.probe = w.header.ch4.probe_value
            self.volts_per_division = w.header.ch4.scale
            self.volts_offset = w.header.ch4.shift

        if self.enabled:
            self.raw = self.channel_bytes(enabled_count, w.data)
            self.volts = self.volts_per_division/25.0 * (self.raw - 127.0) - self.volts_offset
            self.times  = np.arange(self.points) * self.seconds_per_point - self.time_scale

class Channel4(Channel):
    """Base class for a single channel from 4000 series scopes."""

    def __init__(self, w, ch=1):
        super().__init__()
        self.channel_number = ch
        self.seconds_per_point = w.header.seconds_per_point
        self.time_offset = w.header.time_delay
        self.time_scale = w.header.time_scale
        self.points = w.header.points

        if ch == 1:
            self.enabled = w.header.enabled.channel_1
            self.volts_per_division = w.header.channel[0].volts_per_division
            self.volts_offset = w.header.channel[0].volts_offset
            if self.enabled:
                self.raw = np.array(w.data.channel_1)
                self.volts = self.volts_per_division * (5.0 - self.raw/25.0) - self.volts_offset
                self.times  = np.arange(self.points) * self.seconds_per_point

        elif ch == 2:
            self.enabled = w.header.enabled.channel_2
            self.volts_per_division = w.header.channel[1].volts_per_division
            self.volts_offset = w.header.channel[1].volts_offset
            if self.enabled:
                self.raw = np.array(w.data.channel_2)
                self.volts = self.volts_per_division * (5.0 - self.raw/25.0) - self.volts_offset
                self.times  = np.arange(self.points) * self.seconds_per_point


class ReadWFMError(Exception):
    """Generic Read Error."""


class ParseWFMError(Exception):
    """Generic Parse Error."""


def parse(wfm_filename, kind='1000E'):
    """Return a list of channels."""


    if kind == '1000e' or kind == '1000E':
        channels = [None, None]
        try:
            w = RigolWFM.wfm1000e.Wfm1000e.from_file(wfm_filename)
            channels = [ChannelE(w, i) for i in [1,2]]
            return channels

        except:
            raise ParseWFMError("File format is not 1000E.  Sorry.")

    if kind == '1000z' or kind == '1000Z':
        enabled_channels = 0
        channels = [None, None, None, None]
        try:
            w = RigolWFM.wfm1000z.Wfm1000z.from_file(wfm_filename)
            for i in range(4):
                channels[i] = ChannelZ(w, i+1, enabled_channels)
                if channels[i].enabled:
                    enabled_channels += 1
        except:
            raise ParseWFMError("File format is not 1000Z.  Sorry.")

    if kind == '4000':
        enabled_channels = 0
        channels = [None, None, None, None]
        try:
            w = RigolWFM.wfm4000.Wfm4000.from_file(wfm_filename)
            for i in range(4):
                channels[i] = Channel4(w, i+1)
                if channels[i].enabled:
                    enabled_channels += 1
        except:
            raise ParseWFMError("File format is not 4000.  Sorry.")

    return channels
