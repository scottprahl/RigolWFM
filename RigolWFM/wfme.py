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

import wfm1000e


def engineering_string(number):
    """Format number with proper prefix"""
    absnr = abs(number)

    if absnr == 0:
        engr_str = '%g ' % (number / 1e-12)
    elif absnr < 1e-9:
        engr_str = '%g p' % (number / 1e-12)
    elif absnr < 1e-6:
        engr_str = '%g n' % (number / 1e-9)
    elif absnr < 1e-3:
        engr_str = '%g µ' % (number / 1e-6)
    elif absnr < 1:
        engr_str = '%g m' % (number / 1e-3)
    elif absnr < 1e3:
        engr_str = '%g ' % (number)
    elif absnr < 1e6:
        engr_str = '%g k' % (number / 1e3)
    elif absnr < 1e9:
        engr_str = '%g M' % (number / 1e6)
    else:
        engr_str = '%g G' % (number / 1e9)
    return engr_str


class Channel():
    """Base class for a single channel."""

    def __init__(self):
        self.channel_number = 1
        self.enabled = False
        self.volt_scale = 1    # s/div
        self.volt_offset = 0   # s
        self.time_scale = 1    # s/div
        self.time_delta = 0.1  # s
        self.time_offset = 0   # s
        self.points = 0
        self.raw = None

    def __str__(self):
        s = "Channel %d\n" % self.channel_number
        s += "    Enabled: %s\n" % self.enabled
        s += "    Voltage:\n"
        s += "        Scale  = " + engineering_string(self.volt_scale) + "V/div\n"
        s += "        Offset = " + engineering_string(self.volt_offset) + "V\n"
        s += "    Time:\n"
        s += "        Scale  = " + engineering_string(self.time_scale) + "s/div\n"
        s += "        Delay  = " + engineering_string(self.time_offset) + "s\n"
        s += "        Delta  = " + engineering_string(self.time_delta) + "s/point\n"
        s += "    Raw volts:\n"
        s += "        Points = %d\n" % self.points
        if self.enabled:
            s += "        Raw   = [%d,%d,%d,...,%d,%d]\n" % (
                self.raw[0], self.raw[1], self.raw[2], self.raw[-2], self.raw[-1])
            v = [engineering_string(self.volts[i])+"V" for i in [0,1,2,-2,-1]]
            s += "        Volts  = [%s,%s,%s,...,%s,%s]\n" % (v[0],v[1],v[2],v[3],v[4])
        return s


class ChannelE(Channel):
    """Base class for a single channel from 1000E series scopes."""

    def __init__(self, w, ch=1):
        super().__init__()
        if ch == 1:
            self.channel_number = 1
            self.enabled = w.header.ch1.enabled
            self.volt_scale = w.header.ch1_volt_scale
            self.volt_offset = w.header.ch1_volt_shift/25
            self.time_delta = 1/w.header.sample_rate
            self.time_offset = w.header.ch1_time_delay
            self.time_scale = w.header.ch1_time_scale
            self.points = w.header.ch1_points
            if self.enabled:
                self.raw =np.array(w.data.ch1)
                self.volts = self.volt_scale * self.raw/55 - self.volt_offset
                
        elif ch == 2:
            self.channel_number = 2
            self.enabled = w.header.ch2.enabled
            self.volt_scale = w.header.ch2_volt_scale
            self.volt_offset = w.header.ch2_volt_shift/25
            self.time_delta = 1/w.header.sample_rate
            self.time_offset = w.header.ch2_time_delay
            self.time_scale = w.header.ch2_time_scale
            self.points = w.header.ch2_points
            if self.enabled:
                self.raw = np.array(w.data.ch2)
                self.volts = self.volt_scale * self.raw / 55- self.volt_offset


class ReadWFMError(Exception):
    """Generic Read Error."""


class ParseWFMError(Exception):
    """Generic Parse Error."""


def parse(wfm_filename):
    """Return a list of channels."""

    channels = [None, None]

    try:
        w = wfm1000e.Wfm1000e.from_file(wfm_filename)
        channels = [ChannelE(w, i) for i in [1,2]]
        return channels

    except:
        raise ParseWFMError("File format is not 1000E.  Sorry.")

    return channels
