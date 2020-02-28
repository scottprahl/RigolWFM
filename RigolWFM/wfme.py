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
import tempfile
import requests
import numpy as np
import matplotlib.pyplot as plt
import traceback

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

    def __init__(self, w, ch):
        self.scope_type = 'default'
        self.channel_number = ch
        self.waveform = w
        self.seconds_per_point = w.header.seconds_per_point
        self.enabled = False
        self.points = 0
        self.raw = None
        self.volts = None
        self.times = None

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
            v = [engineering_string(self.volts[i])+"V" for i in [0, 1, 2, -2, -1]]
            s += "        Volts  = [%9s,%9s,%9s  ... %9s,%9s]\n" % (v[0], v[1], v[2], v[-2], v[-1])
            t = [engineering_string(self.times[i])+"s" for i in [0, 1, 2, -2, -1]]
            s += "        Times  = [%9s,%9s,%9s  ... %9s,%9s]\n" % (t[0], t[1], t[2], t[-2], t[-1])
        return s


class ChannelE(Channel):
    """Base class for a single channel from 1000E series scopes."""

    def __init__(self, w, ch):
        super().__init__(w, ch)
        self.scope_type = '1000E'
        self.roll_stop = w.header.roll_stop
        
        if ch == 1:
            self.enabled = w.header.ch1.enabled
            self.volts_per_division = w.header.ch1_volts_per_division
            self.volt_scale = w.header.ch1_volts_scale
            self.volts_offset = w.header.ch1_volts_offset
            self.time_offset = w.header.ch1_time_delay
            self.time_scale = w.header.ch1_time_scale
            if self.enabled:
                self.points = len(w.data.ch1)
                self.raw = np.array(w.data.ch1)

        if ch == 2:
            self.enabled = w.header.ch2.enabled
            self.volts_per_division = w.header.ch2_volts_per_division
            self.volt_scale = w.header.ch2_volts_scale
            self.volts_offset = w.header.ch2_volts_offset
            self.time_offset = w.header.ch2_time_delay
            self.time_scale = w.header.ch2_time_scale
            if self.enabled:
                self.points = len(w.data.ch2)
                self.raw = np.array(w.data.ch2)

        if self.enabled:
            self.volts = self.volt_scale * (127.0 - self.raw) - self.volts_offset
            half = self.points * self.seconds_per_point / 2
            self.times = np.linspace(-half,half,self.points) + self.time_offset


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
            raw_bytes = np.array(data.raw1, dtype=np.uint8)

        if self.stride == 2:
            if enabled_count == 0:
                raw_bytes = np.array(data.raw2 & 0x00FF, dtype=np.uint8)
            else:
                raw_bytes = np.array((data.raw2 & 0xFF00) >> 8, dtype=np.uint8)

        if self.stride == 4:
            if enabled_count == 3:
                raw_bytes = np.array(np.uint32(data.raw4) & 0x000000FF, dtype=np.uint8)
            elif enabled_count == 2:
                raw_bytes = np.array((np.uint32(data.raw4) & 0x0000FF00) >> 8, dtype=np.uint8)
            elif enabled_count == 1:
                raw_bytes = np.array((np.uint32(data.raw4) & 0x00FF0000) >> 16, dtype=np.uint8)
            else:
                raw_bytes = np.array((np.uint32(data.raw4) & 0xFF000000) >> 24, dtype=np.uint8)

        return raw_bytes

    def __init__(self, w, ch, enabled_count):
        super().__init__(w, ch)
        self.scope_type = '1000Z'
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
        if ch == 4:
            self.enabled = w.header.ch4.enabled
            self.probe = w.header.ch4.probe_value
            self.volts_per_division = w.header.ch4.scale
            self.volts_offset = w.header.ch4.shift

        if self.enabled:
            self.volts_scale = self.volts_per_division / 25.0
            self.raw = self.channel_bytes(enabled_count, w.data)
            self.volts = self.volts_scale * (self.raw - 127.0) + self.volts_offset
            half = self.points * self.seconds_per_point / 2
            self.times = np.linspace(-half,half,self.points) + self.time_offset

class Channel4(Channel):
    """Base class for a single channel from 4000 series scopes."""

    def __init__(self, w, ch):
        super().__init__(w, ch)
        self.time_offset = w.header.time_delay
        self.time_scale = w.header.time_scale
        self.points = w.header.points
        self.enable = False

        if ch == 1:
            self.enabled = w.header.enabled.channel_1
            self.volts_per_division = w.header.channel[0].volts_per_division
            self.volts_offset = w.header.channel[0].volts_offset
            self.volts_scale = w.header.channel[0].volts_scale
            if self.enabled:
                self.raw = np.array(w.header.raw_1)

        if ch == 2:
            self.enabled = w.header.enabled.channel_2
            self.volts_per_division = w.header.channel[1].volts_per_division
            self.volts_offset = w.header.channel[1].volts_offset
            self.volts_scale = w.header.channel[1].volts_scale
            if self.enabled:
                self.raw = np.array(w.header.raw_2)

        if ch == 3:
            self.enabled = w.header.enabled.channel_3
            self.volts_per_division = w.header.channel[2].volts_per_division
            self.volts_offset = w.header.channel[2].volts_offset
            self.volts_scale = w.header.channel[2].volts_scale
            if self.enabled:
                self.raw = np.array(w.header.raw_3)

        if ch == 4:
            self.enabled = w.header.enabled.channel_4
            self.volts_per_division = w.header.channel[3].volts_per_division
            self.volts_offset = w.header.channel[3].volts_offset
            self.volts_scale = w.header.channel[3].volts_scale
            if self.enabled:
                self.raw = np.array(w.header.raw_4)

        if self.enabled:
            self.volts = self.volts_scale * (self.raw - 127.0) - self.volts_offset
            half = self.points * self.seconds_per_point / 2
            self.times = np.linspace(-half,half,self.points) + self.time_offset

class Read_WFM_Error(Exception):
    """Generic Read Error."""


class Parse_WFM_Error(Exception):
    """Generic Parse Error."""


def parse(wfm_filename, kind):
    """Return a list of channels."""

    enabled_channels = 0
    channels = []
    
    if kind in ['1000e', '1000E']:
        try:
            w = RigolWFM.wfm1000e.Wfm1000e.from_file(wfm_filename)
            for ch_number in [1, 2]:
                ch = ChannelE(w, ch_number)
                if ch.enabled:
                    channels.append(ch)
        except Exception as e:
            print(traceback.format_exc())
            raise Parse_WFM_Error("File format is not 1000E.  Sorry.")

    if kind in ['1000z', '1000Z']:
        try:
            w = RigolWFM.wfm1000z.Wfm1000z.from_file(wfm_filename)
            for ch_number in [1, 2, 3, 4]:
                ch = ChannelZ(w, ch_number, enabled_channels)
                if ch.enabled:
                    channels.append(ch)
                    enabled_channels += 1
                    
        except Exception as e:
            print(traceback.format_exc())
            raise Parse_WFM_Error("File format is not 1000Z.  Sorry.")

    if kind == '4000':
        try:
            w = RigolWFM.wfm4000.Wfm4000.from_file(wfm_filename)
            for ch_number in [1, 2, 3, 4]:
                ch = Channel4(w, ch_number)
                if ch.enabled:
                    channels.append(ch)

        except Exception as e:
            print(traceback.format_exc())
            raise Parse_WFM_Error("File format is not 4000.  Sorry.")

    return channels

def read_and_parse_file(wfm_filename, kind):
    """Return an array of channels."""

    try:
        print("working on %s" % wfm_filename)
        if wfm_filename.startswith('http://') or wfm_filename.startswith('https://'):
            # need a local file for conversion, download url and save as tempfile
            print("downloading file")
            r = requests.get(wfm_filename, allow_redirects=True)
            if not r.ok:
                error_string = "Downloading URL '%s' failed: '%s'" % (wfm_filename, r.reason)
                raise Read_WFM_Error(error_string)

            f = tempfile.NamedTemporaryFile()
            f.write(r.content)
            f.seek(0)
            working_filename = f.name

        else:
            try:
                f = open(wfm_filename, 'rb')
                f.close()
                working_filename = wfm_filename
            except IOError as e:
                raise Read_WFM_Error(e)
        try:
            channels = parse(working_filename, kind)
        except Exception as e: 
            raise Parse_WFM_Error(e)

    except Read_WFM_Error as e:
        print(e)
        return []

    except Parse_WFM_Error as e:
        print(e)
        return []

    return channels


def describe(wfm_filename, kind):
    """Returns a string describing the contents of a Rigol wfm file."""

    channels = read_and_parse_file(wfm_filename, kind)
    s = ''
    for ch in channels:
        s += str(ch)
    return s

def plot(wfm_filename, kind):
    """Plots the data."""

    channels = read_and_parse_file(wfm_filename, kind)

    for ch in channels:
        plt.plot(ch.times, ch.volts)
