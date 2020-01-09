#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# pylint: disable=invalid-name
# pylint: disable=eval-used

import collections
import struct
import array
import numpy as np

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


class FormatError(Exception):
    """Definition for malformed/misunderstood waveform format."""

def _parseFile(f, description, leading="<", strict=True):
    """
    Parse a binary file according to the provided description.

    The description is a list of triples, which contain the fieldname, datatype
    and a test condition.
    """

    data = collections.OrderedDict()

    for field, t, test, *optionals in description:
        optionals = optionals[0] if len(optionals) > 0 else {}

        if "if" in optionals:
            _, condition, match = optionals["if"]

            assert condition  in ("==", ">=", "<=", "<", ">", "in", "!=")
            doParse = eval("data[fieldTested] %s match" % condition)
            if not doParse:
                continue


        if t == "nested":
            data[field] = _parseFile(f, test, leading)
        else:
            binary_format = leading+t
            tmp = f.read(struct.calcsize(binary_format))
            value = struct.unpack(binary_format, tmp)[0]
            data[field] = value

            if "transform" in optionals:
                transform = optionals["transform"]
                assert callable(transform)
                data[field] = transform(data[field])

            if test:
                scope, condition, match = test

                assert scope in ("expect", "require")
                assert condition  in ("==", ">=", "<=", "<", ">", "in", "!=")
                matches = eval("value %s match" % condition)

                if not matches and scope == "require":
                    raise FormatError("Field %s %s %s not met, got %s" % (field, condition, match, value))

                if strict and not matches and scope == "expect":
                    raise FormatError("Field %s %s %s not met, got %s" % (field, condition, match, value))

    return data

def decodeNullTerminatedStr(string):
    """Return a python string given a null-terminated C-string."""
    return string.decode('ascii').partition('\x00')[0]

def getRecordLength(enabledChannelsCount):
    """Return number of arrays that will be created."""
    if enabledChannelsCount <= 2:
        return enabledChannelsCount
    return 4

def getCenterValue(channel_scale):
    """Returns an integer needed to calculate voltage for trace?"""
    if abs(channel_scale - 0.5) < 0.001:
        return 125
    if abs(channel_scale - 1) < 0.001:
        return 95
    if abs(channel_scale - 2) < 0.001:
        return 115
    if abs(channel_scale - 10) < 0.001:
        return 125
    return 128

def parseRigolWFM(f, strict=True):
    """
    Parse a file object which has opened a Rigol WFM file in read-binary
    mode (rb).

    The parser has been developed based on reverse engineering RIGOL DS1054Z WFM files
    and is far from complete!

    The result of the parsing is a nested dictionary containing all relevant data.

    """

    # # # #
    # First read in all the known fields and data of the waveform file. It is
    # interpreted later on.


    chan_header = (
        ("enabled", "?", None),
        ("unknown1", "7s", None),
        ("scale", "f", None),
        ("shift", "f", None),
        ("inverted", "?", None),
        ("unknown2", "11s", None),
    )

    chan_header2 = (
        ("unknown1", "3s", None),
        ("enabled", "?", None),
        ("unknown2", "7s", None),
        ("inverted", "?", None),
        ("unknown3", "10s", None),
        ("probeAttenTimesRange", "q", None),
        ("unknown4", "16s", None),
        ("label", "4s", None, {"transform": decodeNullTerminatedStr}),
        ("unknown5", "10s", None),
    )

    wfm_header = (
        ("unknown1", "H", ("require", "==", 0xFF01)),
        ("unknown2", "6s", None),

        ("model", "20s", None, {"transform": decodeNullTerminatedStr}),
        ("fwVersion", "20s", None, {"transform": decodeNullTerminatedStr}),
        ("unknown3", "16s", None),

        ("scaleD", "q", None),
        ("timeDelay", "q", None),
        ("unknown4", "40s", None),
        ("smpRate", "f", ("require", ">=", 0), {"transform": lambda x: x * 1e9}),

        ("channel1", "nested", chan_header),

        ("channel2", "nested", chan_header),

        ("channel3", "nested", chan_header),

        ("channel4", "nested", chan_header),

        ("unknown5", "1759s", None),
        ("unknown5.1", "40s", None, {"if": ("fwVersion", "==", "00.04.02.SP4")}),
        ("unknown5.1", "55s", None, {"if": ("fwVersion", "==", "00.04.03.SP2")}),

        ("channel4_head2", "nested", chan_header2),
        ("channel3_head2", "nested", chan_header2),
        ("channel2_head2", "nested", chan_header2),
        ("channel1_head2", "nested", chan_header2),

        ("unknown6", "475s", None),

        ("ch1Range", "L", ("require", ">=", 0)),
        ("ch2Range", "L", ("require", ">=", 0)),
        ("ch3Range", "L", ("require", ">=", 0)),
        ("ch4Range", "L", ("require", ">=", 0)),

        ("ch1Shift", "q", None),
        ("ch2Shift", "q", None),
        ("ch3Shift", "q", None),
        ("ch4Shift", "q", None),

        ("unknown7", "248s", None, {"if" : ("fwVersion", "!=", "00.04.01.SP2")}),
        ("unknown7", "244s", None, {"if" : ("fwVersion", "==", "00.04.01.SP2")}),

        ("sampleCount", "L", ("require", ">=", 0)),

        ("unknown8", "148s", None, {"if" : ("fwVersion", "!=", "00.04.01.SP2")}),
        ("unknown8", "152s", None, {"if" : ("fwVersion", "==", "00.04.01.SP2")}),
    )

    fileHdr = _parseFile(f, wfm_header, strict=strict)

    # Add some simple access helpers for the repeating fields
    fileHdr["channels"] = (fileHdr["channel1"], fileHdr["channel2"], fileHdr["channel3"], fileHdr["channel4"])
    fileHdr["channels2"] = (fileHdr["channel1_head2"], fileHdr["channel2_head2"], fileHdr["channel3_head2"], fileHdr["channel4_head2"])
    for  channel in range(4):
        fileHdr["channels2"][channel]["integerRange"] = fileHdr["ch{0}Range".format(channel+1)]
        fileHdr["channels2"][channel]["integerShift"] = fileHdr["ch{0}Shift".format(channel+1)]

    # Read in the sample data from the scope
    fileHdr["enabledChannels"] = [x for x in range(4) if fileHdr["channels"][x]['enabled']]
    fileHdr["enabledChannelsCount"] = len(fileHdr["enabledChannels"])

    recordLength = getRecordLength(fileHdr["enabledChannelsCount"])
    nBytes = fileHdr["sampleCount"] * struct.calcsize("B") * recordLength
    sampleData = array.array('B')
    sampleData.fromfile(f, nBytes)
    # Channel samples are interleaved and are stored in descending channel number order
    # Depending on number of enabled channels 1, 2 or 4 samples are stored for each clock tick
    if fileHdr["enabledChannelsCount"] == 1:
        channelOffsets = [0]
    elif fileHdr["enabledChannelsCount"] == 2:
        channelOffsets = [1, 0]
    else: # 3 or 4 channels
        channelOffsets = [3 - x for x in fileHdr["enabledChannels"]]
    for channel in fileHdr["enabledChannels"]:
        fileHdr["channels"][channel]['data'] = sampleData[channelOffsets.pop()::recordLength]

    # # # # # # # # # # # #
    # Interpret all the results to mean something useful.

    scopeData = dict()

    scopeData['model'] = fileHdr['model']
    scopeData['fwVersion'] = fileHdr['fwVersion']
    scopeData['scaleD'] = fileHdr['scaleD']
    scopeData['timeDelay'] = fileHdr['timeDelay']
    scopeData["samplerate"] = fileHdr["smpRate"]
    scopeData["timeScale"] = 1./scopeData["samplerate"]
    scopeData['enabledChannels'] = fileHdr['enabledChannels']
    scopeData['enabledChannelsCount'] = fileHdr['enabledChannelsCount']

    scopeData["channel"] = dict()
    for channel in range(4):
        channelDict = dict()
        channelDict["enabled"] = fileHdr["channels"][channel]["enabled"]

        channelDict["label"] = fileHdr["channels2"][channel]["label"]

        channelDict["channelName"] = "CH" + str(channel+1)

        if channelDict["enabled"]:

            channelDict["probeAttenuation"] = float(fileHdr["channels2"][channel]["probeAttenTimesRange"]) / fileHdr["channels2"][channel]["integerRange"] / 1000.

            channelDict["scale"] = fileHdr["channels"][channel]["scale"]

            channelDict["inverted"] = fileHdr["channels"][channel]["inverted"]

            channelDict["shift"] = fileHdr["channels"][channel]["shift"]

            # Calculate the sample data

            channelDict["samples"] = {'raw' : fileHdr["channels"][channel]['data']}

            channelDict["samples"]["volts"] = [((x-getCenterValue(channelDict["scale"]))/20.)*channelDict["scale"]  - channelDict["shift"] for x in channelDict["samples"]["raw"]]

            samples = len(channelDict["samples"]["raw"])
            channelDict["nsamples"] = samples

            channelDict["samplerate"] = fileHdr["smpRate"]
            channelDict["timeScale"] = 1./channelDict["samplerate"]
            channelDict["timeDelay"] = 1e-12 * fileHdr["timeDelay"]

            channelDict["samples"]["time"] = [
                (t - samples/2) * channelDict["timeScale"] + channelDict["timeDelay"]
                                for t in range(samples)]

        # Save channel data to the overall scope data
        scopeData["channel"][channel+1] = channelDict

    #pprint.pprint(scopeData)
    return scopeData




def describeScopeData(scopeData):
    """
    Returns a human-readable string representation of a scope data dictionary.
    """
    def describeDict(d, description, ljust=0):
        tmp = ""
        for item, desc in description:
            if item in d:
                tmp = tmp + "%s: %s\n" % (desc[0].ljust(ljust), desc[1] % d[item])
        return tmp

    def header(header_name, sep='='):
        return "\n%s\n%s\n" % (header_name, sep*len(header_name))

    headerDsc = (
        ('model', ("Device model", "%s")),
        ('fwVersion', ("Firmware version", "%s")),
        ('scaleD', ("Horizontal scale", "%d ps")),
        ('timeDelay', ("Time delay", "%d ps")),
        ('samplerate', ("Sampling rate", "%e samples/s")),
        ('enabledChannels', ("Enabled channels", "%s (zero-based indexes)")),
        )

    channelDsc = (
        ('label', ("Label", "%s")),
        ('enabled', ("Enabled", "%s")),
        ('probeAttenuation', ("Probe attenuation", "%.3fx")),
        ('scale', ("Y grid scale", "%0.3e V/div")),
        ('shift', ("Y shift", "%0.3e V")),
        ('inverted', ("Y inverted", "%s")),
        ('timeDiv', ("Time grid scale", "%0.3e s/div")),
        ('samplerate', ("Sampling rate", "%0.3e samples/s")),
        ('timeDelay', ("Time delay", "%0.3e s")),
        ('nsamples', ("No. of recorded samples", "%i")),
        )

    tmp = ""

    tmp = tmp + header("General")
    tmp = tmp + describeDict(scopeData, headerDsc, ljust=25)

    for i in range(4):
        channelDict = scopeData["channel"][i+1]

        tmp = tmp + header("Channel %s" % channelDict["channelName"])
        tmp = tmp + describeDict(channelDict, channelDsc, ljust=25)

    return tmp


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

    data = []

    try:
        f = open(wfm_filename, 'rb')
    except (OSError, IOError):
        print('Unable to open %s for reading.' % wfm_filename)
        return data

    try:
        scopeData = parseRigolWFM(f)
    except FormatError:
        print("Format does not follow the known file format.")
        return data

    f.close()

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

    data.append(scopeData["channel"][channels[0]]["samples"]["time"])
    for channel in channels:
        data.append(scopeData["channel"][channel]["samples"]["volts"])

    return data

def describe(wfm_filename):
    """Returns a string describing the contents of a Rigol wfm file."""

    try:
        f = open(wfm_filename, 'rb')
    except (OSError, IOError):
        print('Unable to open %s for reading.' % wfm_filename)
        return ''

    try:
        scopeData = parseRigolWFM(f)
    except FormatError:
        print("Format does not follow the known file format.")
        return ''

    desc = describeScopeData(scopeData)
    f.close()
    return desc
