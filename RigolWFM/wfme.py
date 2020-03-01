#pylint: disable=invalid-name
#pylint: disable=too-many-instance-attributes
#pylint: disable=unsubscriptable-object
#pylint: disable=too-few-public-methods

"""
Extract signals or description from Rigol 1000E Oscilloscope waveform file.

Use like this::

    import RigolWFM.wfme as wfme

    waveform = wfme.from_file("filename.wfm", '1000E')
    for ch in waveform.channels:
        print(ch)
"""
import tempfile
import traceback
import requests
import matplotlib.pyplot as plt

import RigolWFM.wfm1000d
import RigolWFM.wfm1000e
import RigolWFM.wfm1000z
import RigolWFM.wfm4000
import RigolWFM.wfm6000
import RigolWFM.channel

class Read_WFM_Error(Exception):
    """Generic Read Error."""

class Parse_WFM_Error(Exception):
    """Generic Parse Error."""

class Not_URL_Error(Exception):
    """Not a URL."""

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

        if kind in ['1000c', '1000C']:
            try:
                w = RigolWFM.wfm1000c.Wfm1000c.from_file(filename)
                for ch_number in [1, 2]:
                    ch = RigolWFM.channel.DS1000C(w, ch_number)
                    if ch.enabled:
                        new_wfm.channels.append(ch)
            except Exception as e:
                print(traceback.format_exc())
                raise Parse_WFM_Error("File format is not 1000C.  Sorry.")

        if kind in ['1000e', '1000E']:
            try:
                w = RigolWFM.wfm1000e.Wfm1000e.from_file(filename)
                for ch_number in [1, 2]:
                    ch = RigolWFM.channel.DS1000E(w, ch_number)
                    if ch.enabled:
                        new_wfm.channels.append(ch)
            except Exception as e:
                print(traceback.format_exc())
                raise Parse_WFM_Error("File format is not 1000E.  Sorry.")

        if kind in ['1000z', '1000Z']:
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
                raise Parse_WFM_Error("File format is not 1000Z.  Sorry.")

        if kind == '4000':
            try:
                w = RigolWFM.wfm4000.Wfm4000.from_file(filename)
                for ch_number in [1, 2, 3, 4]:
                    ch = RigolWFM.channel.DS4000(w, ch_number)
                    if ch.enabled:
                        new_wfm.channels.append(ch)

            except Exception as e:
                print(traceback.format_exc())
                raise Parse_WFM_Error("File format is not 4000.  Sorry.")
        return new_wfm

    @classmethod
    def from_url(cls, url, kind):
        """Return an array of channels."""

        if not url.startswith('http://') and not url.startswith('https://'):
            raise Not_URL_Error()

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
