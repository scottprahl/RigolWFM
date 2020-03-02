#pylint: disable=invalid-name
#pylint: disable=too-many-instance-attributes
#pylint: disable=unsubscriptable-object
#pylint: disable=too-few-public-methods

"""
Extract signals or description from Rigol 1000E Oscilloscope waveform file.

Use like this::

    import RigolWFM.wfm as wfm

    waveform = wfm.from_file("filename.wfm", '1000E')
    for ch in waveform.channels:
        print(ch)
"""
import tempfile
import traceback
import requests
import matplotlib.pyplot as plt

import RigolWFM.wfm1000c
import RigolWFM.wfm1000e
import RigolWFM.wfm1000z
import RigolWFM.wfm4000
import RigolWFM.wfm6000
import RigolWFM.channel

# not implemented
#DS1000B_scopes = ["B", "1000B", "DS1000B",
#                  "DS1074B", "DS1104B", "DS1204B"]

# untested
DS1000C_scopes = ["C", "1000C", "DS1000C",
                  "DS1000CD", "DS1000C", "DS1000MD", "DS1000M",
                  "DS1302CA", "DS1202CA", "DS1102CA", "DS1062CA"]

# tested
DS1000E_scopes = ["E", "1000E", "DS1000E",
                  "D", "1000D", "DS1000D",
                  "DS1000E", "DS1102E", "DS1052E", "DS1102D", "DS1052D"]

# tested, wonky voltages
DS1000Z_scopes = ["Z", "1000Z", "DS1000Z",
                  "DS1202Z", "DS1074Z", "DS1104Z", "DS1074Z-S",
                  "DS1104Z-S", "MSO1054Z", "DS1054Z",
                  "MSO1074Z", "MSO1104Z", "DS1104Z"]

# tested
DS4000_scopes = ["4", "4000", "DS4000",
                 "DS4054", "DS4052", "DS4034", "DS4032", "DS4024",
                 "DS4022", "DS4014", "DS4012", "MSO4054", "MSO4052", "MSO4034",
                 "MSO4032", "MSO4024", "MSO4022", "MSO4014", "MSO4012"]

#untested
DS6000_scopes = ["6", "6000", "DS6000",
                 "DS6062", "DS6064", "DS6102", "DS6104"]

def valid_scope_list():
    """List all the oscilloscope types."""
    s = "\nValid types are:\n"
    s += ", ".join(DS1000C_scopes) + "\n"
    s += ", ".join(DS1000E_scopes) + "\n"
    s += ", ".join(DS1000Z_scopes) + "\n"
    s += ", ".join(DS4000_scopes) + "\n"
    s += ", ".join(DS6000_scopes) + "\n"
    return s

class Read_WFM_Error(Exception):
    """Generic Read Error."""

class Parse_WFM_Error(Exception):
    """Generic Parse Error."""

class Invalid_URL(Exception):
    """Cannot use this URL.  It must start with https:// or http://"""

class Unknown_Scope_Error(Exception):
    """Not one of the listed Rigol oscilloscopes."""

class Wfm():
    """Class with parsed data from a .wfm file."""
    def __init__(self, filename, kind):
        self.channels = []
        self.file_name = filename
        self.kind = kind

    @classmethod
    def from_file(cls, filename, kind):
        """Create Wfm object from a file."""

        new_wfm = cls(filename, kind)

        # ensure that file exists
        try:
            f = open(filename, 'rb')
            f.close()
        except IOError as e:
            raise Read_WFM_Error(e)

        ukind = kind.upper()
        if ukind in DS1000C_scopes:
            try:
                w = RigolWFM.wfm1000c.Wfm1000c.from_file(filename)
                for ch_number in [1, 2]:
                    ch = RigolWFM.channel.DS1000C(w, ch_number)
                    if ch.enabled:
                        new_wfm.channels.append(ch)
            except Exception as e:
                print(traceback.format_exc())
                raise Parse_WFM_Error("Failed to parse as DS1000C format. Sorry.")

        elif ukind in DS1000E_scopes:
            try:
                w = RigolWFM.wfm1000e.Wfm1000e.from_file(filename)
                for ch_number in [1, 2]:
                    ch = RigolWFM.channel.DS1000E(w, ch_number)
                    if ch.enabled:
                        new_wfm.channels.append(ch)
            except Exception as e:
                print(traceback.format_exc())
                raise Parse_WFM_Error("Failed to parse as DS1000E format. Sorry.")

        elif ukind in DS1000Z_scopes:
            enabled_channels = 0
            try:
                w = RigolWFM.wfm1000z.Wfm1000z.from_file(filename)
                for ch_number in [1, 2, 3, 4]:
                    ch = RigolWFM.channel.DS1000Z(w, ch_number, enabled_channels)
                    if ch.enabled:
                        new_wfm.channels.append(ch)
                        enabled_channels += 1

            except Exception as e:
                print(traceback.format_exc())
                raise Parse_WFM_Error("Failed to parse as DS1000Z format. Sorry.")

        elif ukind in DS4000_scopes:
            try:
                w = RigolWFM.wfm4000.Wfm4000.from_file(filename)
                for ch_number in [1, 2, 3, 4]:
                    ch = RigolWFM.channel.DS4000(w, ch_number)
                    if ch.enabled:
                        new_wfm.channels.append(ch)

            except Exception as e:
                print(traceback.format_exc())
                raise Parse_WFM_Error("Failed to parse as DS4000 format. Sorry.")

        elif ukind in DS6000_scopes:
            try:
                w = RigolWFM.wfm6000.Wfm6000.from_file(filename)
                for ch_number in [1, 2, 3, 4]:
                    ch = RigolWFM.channel.DS4000(w, ch_number)
                    if ch.enabled:
                        new_wfm.channels.append(ch)

            except Exception as e:
                print(traceback.format_exc())
                raise Parse_WFM_Error("Failed to parse as DS6000 format. Sorry.")

        else:
            print("Unknown Rigol oscilloscope type: '%s'" % ukind)
            print(valid_scope_list())

        return new_wfm

    @classmethod
    def from_url(cls, url, kind):
        """Return an array of channels."""

        if not url.startswith('http://') and not url.startswith('https://'):
            raise Invalid_URL()

        try:
            # need a local file for conversion, download url and save as tempfile
            print("downloading '%s'" % url)
            r = requests.get(url, allow_redirects=True)
            if not r.ok:
                error_string = "Downloading URL '%s' failed: '%s'" % (url, r.reason)
                raise Read_WFM_Error(error_string)

            f = tempfile.NamedTemporaryFile()
            f.write(r.content)
            f.seek(0)
            working_filename = f.name

            try:
                new_cls = cls.from_file(working_filename, kind)
                new_cls.file_name = url
                return new_cls
            except Exception as e:
                raise Parse_WFM_Error(e)

        except Exception as e:
            raise Parse_WFM_Error(e)

    def describe(self):
        """Returns a string describing the contents of a Rigol wfm file."""
        s = ''
        for ch in self.channels:
            s += str(ch)
        return s


    def plot(self):
        """Plots the data."""
        for ch in self.channels:
            plt.plot(ch.times, ch.volts, label=ch.name)

        plt.xlabel("Time (s)")
        plt.ylabel("Volts (V)")
        plt.title(self.file_name)
        plt.legend(loc='upper right')

    def csv(self):
        """Return a string of comma separated values"""

        if len(self.channels) == 0:
            return ''

        s = 'X'
        for ch in self.channels:
            s += ",%s" % ch.name
        s += "\n"
        
        s += 'SECONDS'
        for ch in self.channels:
            s += ",%s" % ch.unit
        s += "\n"

        for i in range(self.channels[0].points):
            s += "%e" % ch.times[i]
            for ch in self.channels:
                s += ",%e" % ch.volts[i]
            s += "\n"
        return s
