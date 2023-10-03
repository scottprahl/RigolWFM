# pylint: disable=invalid-name
# pylint: disable=too-many-instance-attributes
# pylint: disable=raise-missing-from
# pylint: disable=too-many-branches
# pylint: disable=too-many-statements
# pylint: disable=consider-using-f-string
# pylint: disable=consider-using-with

"""
Extract signals or description from Rigol 1000E Oscilloscope waveform file.

Example:
    >>> import RigolWFM.wfm as rigol
    >>> waveform = rigol.Wfm.from_file("file_name.wfm", 'E')
    >>> description = waveform.describe()
    >>> print(description)

"""
import os.path
import tempfile
import urllib.parse
import wave

import matplotlib.pyplot as plt
import numpy as np
import requests

import RigolWFM.wfm1000b
import RigolWFM.wfm1000c
import RigolWFM.wfm1000d
import RigolWFM.wfm1000e
import RigolWFM.wfm1000z
import RigolWFM.wfm2000
import RigolWFM.wfm4000
import RigolWFM.wfm6000
import RigolWFM.channel

# in progress
DS1000B_scopes = ["B", "1000B", "DS1000B",
                  "DS1074B", "DS1104B", "DS1204B"]

# tested
DS1000C_scopes = ["C", "1000C", "DS1000C",
                  "DS1000CD", "DS1000C", "DS1000MD", "DS1000M",
                  "DS1302CA", "DS1202CA", "DS1102CA", "DS1062CA",
                  "DS1042C"]

# tested
DS1000D_scopes = ["D", "1000D", "DS1000D", "DS1102D", "DS1052D"]

# tested
DS1000E_scopes = ["E", "1000E", "DS1000E", "DS1102E", "DS1052E"]

# tested, wonky voltages
DS1000Z_scopes = ["Z", "1000Z", "DS1000Z",
                  "DS1202Z",
                  "DS1054Z", "MSO1054Z",
                  "DS1074Z", "MSO1074Z", "DS1074Z-S",
                  "DS1104Z", "MSO1104Z", "DS1104Z-S"]

# tested
DS2000_scopes = ["2", "2000", "DS2000", "DS2072A",
                 "DS2102A", "MSO2102A", "MSO2102A-S",
                 "DS2202A", "MSO2202A", "MSO2202A-S",
                 "DS2302A", "MSO2302A", "MSO2302A-S"]

# tested
DS4000_scopes = ["4", "4000", "DS4000",
                 "DS4054", "DS4052", "DS4034", "DS4032", "DS4024",
                 "DS4022", "DS4014", "DS4012", "MSO4054", "MSO4052", "MSO4034",
                 "MSO4032", "MSO4024", "MSO4022", "MSO4014", "MSO4012"]

# untested
DS6000_scopes = ["6", "6000", "DS6000",
                 "DS6062", "DS6064", "DS6102", "DS6104"]


def valid_scope_list():
    """List all the oscilloscope types."""
    s = "\nRigol oscilloscope models:\n    "
    s += ", ".join(DS1000C_scopes) + "\n    "
    s += ", ".join(DS1000D_scopes) + "\n    "
    s += ", ".join(DS1000E_scopes) + "\n    "
    s += ", ".join(DS1000Z_scopes) + "\n    "
    s += ", ".join(DS2000_scopes) + "\n    "
    s += ", ".join(DS4000_scopes) + "\n    "
    s += ", ".join(DS6000_scopes) + "\n"
    return s


class Read_WFM_Error(Exception):
    """Generic Read Error."""


class Parse_WFM_Error(Exception):
    """Generic Parse Error."""


class Invalid_URL(Exception):
    """Cannot use this URL.  It must start with https or http."""


class Unknown_Scope_Error(Exception):
    """Not one of the listed Rigol oscilloscopes."""


class Write_WAV_Error(Exception):
    """Something went wrong while writing the .wave file."""


class Channel_Not_In_WFM_Error(Exception):
    """The channel is not in the .wfm file."""


class Wfm():
    """Class with parsed data from a .wfm file."""

    def __init__(self, file_name):
        """Initialize a Wfm object from a file."""
        self.channels = []
        self.original_name = file_name
        self.file_name = file_name
        self.basename = file_name
        self.firmware = 'unknown'

        # there are multiple possible scope names
        # 1. user_name   - the name passed to the program
        # 2. header_name - the name found in the header of the file
        # 3. parser_name - the name of parser used
        self.user_name = 'unknown'
        self.parser_name = 'unknown'
        self.header_name = 'unknown'

    @classmethod
    def from_file(cls, file_name, model, selected='1234'):
        """
        Create Wfm object from a file.

        Args:
            file_name: name of file
            model: Rigol Oscilloscope used, e.g., 'E' or 'Z'
            selected: string of channels to process e.g., '12'
        Returns:
            a wfm object for the file
        """
        # ensure that file exists
        try:
            f = open(file_name, 'rb')
            f.close()
        except IOError as e:
            raise Read_WFM_Error(e)

        new_wfm = cls(file_name)
        new_wfm.original_name = file_name
        new_wfm.file_name = file_name
        new_wfm.basename = os.path.basename(file_name)

        # parse the waveform
        umodel = model.upper()

        if umodel in DS1000B_scopes:
            w = RigolWFM.wfm1000b.Wfm1000b.from_file(file_name)
            new_wfm.header_name = 'DS1000B'

        elif umodel in DS1000C_scopes:
            w = RigolWFM.wfm1000c.Wfm1000c.from_file(file_name)
            new_wfm.header_name = 'DS1000C'

        elif umodel in DS1000D_scopes:
            w = RigolWFM.wfm1000d.Wfm1000d.from_file(file_name)
            new_wfm.header_name = 'DS1000D'

        elif umodel in DS1000E_scopes:
            w = RigolWFM.wfm1000e.Wfm1000e.from_file(file_name)
            new_wfm.header_name = 'DS1000E'

        elif umodel in DS1000Z_scopes:
            w = RigolWFM.wfm1000z.Wfm1000z.from_file(file_name)
            new_wfm.header_name = w.preheader.model_number

        elif umodel in DS2000_scopes:
            w = RigolWFM.wfm2000.Wfm2000.from_file(file_name)
            new_wfm.header_name = 'DS2000'

        elif umodel in DS4000_scopes:
            w = RigolWFM.wfm4000.Wfm4000.from_file(file_name)
            new_wfm.header_name = w.header.model_number

        elif umodel in DS6000_scopes:
            w = RigolWFM.wfm6000.Wfm6000.from_file(file_name)
            new_wfm.header_name = w.header.model_number

        else:
            print("Unknown Rigol oscilloscope type: '%s'" % umodel)
            print(valid_scope_list())
            return new_wfm

        new_wfm.user_name = model
        pname = str(w).split(".")[1]
        new_wfm.parser_name = pname

        # assemble into uniform set of names
        enabled = ''
        for ch_number in range(1, 5):

            ch = RigolWFM.channel.Channel(w, ch_number, pname, selected)

            if not ch.enabled:
                continue

            # keep track of enabled channels for error message
            enabled += str(ch_number)

            # append all enabled channels
            new_wfm.channels.append(ch)

        if len(new_wfm.channels) == 0:
            print("Sorry! No channels in the waveform are both selected and enabled")
            print("    User selected channels = '%s'" % selected)
            print("    Scope enabled channels = '%s'" % enabled)
            print()
        else:
            new_wfm.firmware = new_wfm.channels[0].firmware

        return new_wfm

    @classmethod
    def from_url(cls, url, model, selected='1234'):
        """
        Return a waveform object given a URL.

        This is a bit complicated because the parser must have a local file
        to work with.  The process is to download the file to a temporary
        location and then process that file.  There is a lot that can go
        wrong - bad url, bad download, or an error parsing the file.

        Args:
            url: location of the file
            model: Rigol Oscilloscope used, e.g., 'E' or 'Z'
            selected: string of channels to process e.g., '12'
        Returns:
            a wfm object for the file
        """
        u = urllib.parse.urlparse(url)
        scheme = u[0]

        if scheme not in ['http', 'https']:
            raise Invalid_URL()

        try:
            # need a local file for conversion, download url and save as tempfile
            print("downloading '%s'" % url)
            r = requests.get(url, allow_redirects=True, timeout=10)
            r.raise_for_status()

            if not r.ok:
                error_string = "Downloading URL '%s' failed: '%s'" % (
                    url, r.reason)
                raise Read_WFM_Error(error_string)

            f = tempfile.NamedTemporaryFile()
            f.write(r.content)
            f.seek(0)
            working_name = f.name

            try:
                new_wfm = cls.from_file(working_name, model, selected)
                new_wfm.original_name = url
                # extract the simple name
                rawpath = u[2]
                path = urllib.parse.unquote(rawpath)
                new_wfm.basename = os.path.basename(path)
                return new_wfm
            except Exception as e:
                raise Parse_WFM_Error(e)

        except r.exceptions.RequestException as e:
            raise Parse_WFM_Error(e)

    def describe(self):
        """Return a string describing the contents of a Rigol wfm file."""
        s = "    General:\n"
        s += '        File Model   = %s\n' % self.parser_name
        s += "        User Model   = %s\n" % self.user_name
        s += '        Parser Model = %s\n' % self.parser_name
        s += "        Firmware     = %s\n" % self.firmware
        s += '        Filename     = %s\n' % self.basename
        s += '        Channels     = ['

        first = True
        for ch in self.channels:
            if not first:
                s += ', '
            s += '%s' % ch.channel_number
            first = False
        s += ']\n\n'

        for ch in self.channels:
            s += str(ch)
            s += "\n"
        return s

    def best_scaling(self):
        """Return appropriate scaling for plot."""
        v_scale = 1e-12
        v_prefix = ''
        h_scale = 1e-12
        h_prefix = ''
        for ch in self.channels:
            v, p = RigolWFM.channel.best_scale(ch.volt_per_division)
            if v > v_scale:
                v_scale = v
                v_prefix = p
            h, p = RigolWFM.channel.best_scale(ch.time_scale)
            if h > h_scale:
                h_scale = h
                h_prefix = p
        return h_scale, h_prefix, v_scale, v_prefix

    def plot(self):
        """Plot the data."""
        h_scale, h_prefix, v_scale, v_prefix = self.best_scaling()
        colors = ['red', 'blue', 'orange', 'magenta']

        for i, ch in enumerate(self.channels):
            plt.plot(ch.times * h_scale, ch.volts * v_scale,
                     label=ch.name, color=colors[i])

        plt.xlabel("Time (%ss)" % h_prefix)
        plt.ylabel("Voltage (%sV)" % v_prefix)
        plt.title(self.basename)
        plt.legend(loc='upper right')

    def csv(self):
        """Return a string of comma separated values."""
        if len(self.channels) == 0:
            return ''

        h_scale, h_prefix, v_scale, v_prefix = self.best_scaling()

        s = 'X'
        for ch in self.channels:
            s += ",%s" % ch.name
        s += ",Start,Increment\n"

        # just output the display 100 pts/division
        ch = self.channels[0]
        incr = ch.time_scale / 100
        off = -6 * ch.time_scale
        s += '%ss' % h_prefix
        for ch in self.channels:
            s += ",%s%s" % (v_prefix, ch.unit.name.upper())
        s += ",%e,%e\n" % (off, incr)

        for i in range(self.channels[0].points):
            s += "%.6f" % (ch.times[i] * h_scale)
            for ch in self.channels:
                s += ",%.2f" % (ch.volts[i] * v_scale)
            s += "\n"
        return s

    def sigrokcsv(self):
        """Return a string of comma separated values for sigrok."""
        if len(self.channels) == 0:
            return ''

        s = 'X'
        for ch in self.channels:
            s += ",%s (%s)" % (ch.name, ch.unit.name.upper())
        s += "\n"

        ch = self.channels[0]
        for i in range(self.channels[0].points):
            s += "%.8f" % (ch.times[i])
            for ch in self.channels:
                s += ",%.2f" % (ch.volts[i])
            s += "\n"
        return s

    def wav(self, wav_filename, autoscale=False):
        """Save data as a WAV file for use with LTspice or Sigrok."""
        n_channels = len(self.channels)
        channel_length = self.channels[0].points
        total_len = channel_length * n_channels

        out = np.empty((total_len,), dtype=np.uint8, order='C')

        # channels are interleaved e.g., 123123123
        for i, ch in enumerate(self.channels):
            if autoscale:
                amin = np.min(ch.raw)
                amax = max(np.max(ch.raw), amin + 1)  # avoid division by zero
                scale = 250 / (amax - amin) * 0.95
                out[i::n_channels] = np.int8((ch.raw - amin) * scale)
            else:
                out[i::n_channels] = ch.raw

        sample_rate = 1.0 / self.channels[0].seconds_per_point

        wavef = wave.open(wav_filename, 'wb')
        wavef.setnchannels(n_channels)  # 1 = mono, 2 = stereo
        wavef.setsampwidth(1)
        wavef.setframerate(sample_rate)
        wavef.setcomptype('NONE', '')
        wavef.setnframes(channel_length)

        wavef.writeframes(out)
        wavef.close()
