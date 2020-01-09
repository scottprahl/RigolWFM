# Copyright (c) 2013, Matthias Blaicher
# Copyright (c) 2014, Michał Szkutnik
# Copyright (c) 2020, Scott Prahl
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice, this
#   list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
# ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
# pylint: disable=invalid-name
# pylint: disable=eval-used

"""
Extract signals or description from Rigol Oscilloscope waveform file.

Use like this::

    import RigolWFM.wfm as wfm
    
    signals = wfm.signals("filename.wfm")
    if len(signals) == 2:
        t,v = signals
"""

import RigolWFM.wfm1052
import RigolWFM.wfm1054

import numpy as np

def read_and_parse_file(wfm_filename):
    """Return a scopeData structure."""
    
    model = 0
    
    try:
        f = open(wfm_filename, 'rb')
    except (OSError, IOError):
        print('Unable to open %s for reading.' % wfm_filename)
        return None, None

    try:
        scopeData = RigolWFM.wfm1052.parseRigolWFM(f)
        model = 1052
        
    except RigolWFM.wfm1052.FormatError:
        try:
            scopeData = RigolWFM.wfm1054.parseRigolWFM(f)
            model = 1054
        except RigolWFM.wfm1054.FormatError:
            print("Format is not DS1052 or DS1054 format.  Sorry.")

    f.close()
    return model, scopeData


def signals(wfm_filename):
    """
    Returns the time and voltage signal data from the Rigol wfm file.

    The result will have 0, 2, 3 or 4 elements depending on the scope channels that
    were enabled at the moment the data was captured.

        0: []               # error parsing
        2: [time, voltage]
        3: [time, voltage_channel_1, voltage_channel_2]
        4: [time_channel_1, voltage_channel_1, time_channel_2, voltage_channel_2]

    All the time data is in seconds and the voltage data is in volts.
    """

    model, scopeData = read_and_parse_file(wfm_filename)

    if model==0:
        return []
        
    if scopeData["alternateTrigger"]:
        data = np.zeros(4, dtype=np.array)
        data[0] = np.array(scopeData["channel"][1]["samples"]["time"])
        data[1] = np.array(scopeData["channel"][1]["samples"]["volts"])
        data[2] = np.array(scopeData["channel"][2]["samples"]["time"])
        data[3] = np.array(scopeData["channel"][2]["samples"]["volts"])
        return data

    channels = []
    for channel in range(1, 3):
        if scopeData["channel"][channel]["enabled"]:
            channels.append(channel)

    data = []
    data.append(scopeData["channel"][channels[0]]["samples"]["time"])
    for channel in channels:
        data.append(scopeData["channel"][channel]["samples"]["volts"])

    return data

def describe(wfm_filename):
    """Returns a string describing the contents of a Rigol wfm file."""

    model, scopeData = read_and_parse_file(wfm_filename)

    if model==0:
        desc = ''

    elif model==1052:
        desc = RigolWFM.wfm1052.describeScopeData(scopeData)
        
    elif model==1054:
        desc = RigolWFM.wfm1054.describeScopeData(scopeData)

    return desc
