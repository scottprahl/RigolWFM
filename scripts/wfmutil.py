#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse
import re
import sys
from io import TextIOWrapper

import wfm

# Copyright (c) 2014, Michał Szkutnik
# Copyright (c) 2013, Matthias Blaicher
# All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met: 
# 
# 1. Redistributions of source code must retain the above copyright notice, this
# list of conditions and the following disclaimer.
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

def PortPin(arg):
    regexp = re.compile("^(\w+):(\d)$");
    mo = regexp.match(arg);
    if mo:
        port = mo.group(1)
        bitNo = int(mo.group(2))
        if bitNo >= 8:
            raise argparse.ArgumentTypeError("%d is not a valid port pin number, should be in range 0..7" % (bitNo))
        else:
            return (port, bitNo)
    else:
        raise argparse.ArgumentTypeError("%s is not a valid port pin specifier, use: <PORTNAME>:<PIN_NUMBER>" % arg)


def info(args, scopeData, outfile):
    scopeDataDsc = wfm.describeScopeData(scopeData)
    print(scopeDataDsc, file=outfile)


def csv(args, scopeData, outfile):
    nsamples = 0
    channels = []
    dataSrc = "raw" if args.raw else "volts"
    dataFmt = "%d" if args.raw else "%0.2e"
    unit    = "NoUnit" if args.raw else "Volt"

    if not args.raw:
        print("warning: Voltage computation code is currently giving WRONG results, please do not rely on the calculated values until code is improved.", file=sys.stderr)

    for channel in scopeData["enabledChannels"]:
        nsamples = max(nsamples, scopeData["channel"][channel+1]["nsamples"])
        channels.append(channel+1)

    def csvWrite(fields, dest):
        print(",".join(fields), file=dest)

    # Print first line with column source description
    if args.header != 'none':
        fields = []
        if not args.notime:
            fields.append("X")
        for channel in channels:
            fields.append(scopeData["channel"][channel]["channelName"])
        csvWrite(fields, outfile)


        if args.header == 'rigol':
            # Print second line with column unit description
            secondLineFields = []
            if not args.notime:
                secondLineFields.append("Second")
            secondLineFields.extend([unit] * len(channels))
            csvWrite(secondLineFields, outfile)

    for i in range(nsamples):
        fields = []
        if not args.notime:
            fields.append("%0.5e" % scopeData["channel"][channel]["samples"]["time"][i])
        for channel in channels:
            sampleDict = scopeData["channel"][channel]["samples"]
            fields.append(dataFmt % sampleDict[dataSrc][i])
        csvWrite(fields, outfile)


def plot(args, scopeData, outfile):
    import numpy as np
    import matplotlib.pyplot as plt
    import scipy
    import scipy.fftpack

    if not args.raw:
        print("warning: Voltage computation code is currently giving WRONG results, please do not rely on the calculated values until code is improved.", file=sys.stderr)

    dataSrc = "raw" if args.raw else "volts"

    sigplot = plt.subplot(211 if args.fft else 111)

    for i in scopeData["enabledChannels"]:
        plt.plot(scopeData["channel"][i + 1]["samples"]["time"],
                 scopeData["channel"][i + 1]["samples"][dataSrc], label=scopeData["channel"][i + 1]["label"])

    if not args.nolegend:
        plotpos = sigplot.get_position()
        sigplot.set_position([plotpos.x0, plotpos.y0, plotpos.width * 0.9, plotpos.height])
        sigplot.legend(loc='center left', bbox_to_anchor=(1, 0.5))

    plt.grid()
    plt.ylabel("Raw value" if args.raw else "Voltage [V]")

    plt.title("Waveform")
    plt.xlabel("Time [s]")

    if args.fft:
        plt.subplot(212)
        for i in scopeData["enabledChannels"]:
            channelDict = scopeData["channel"][i + 1]
            signal = np.array(channelDict["samples"][dataSrc])
            fft = np.abs(np.fft.fftshift(scipy.fft(signal)))
            freqs = np.fft.fftshift(scipy.fftpack.fftfreq(signal.size, scopeData["timeScale"]))
            plt.plot(freqs, 20 * np.log10(fft))

        plt.grid()
        plt.title("FFT")
        plt.ylabel("Magnitude [dB]")
        plt.xlabel("Frequency [Hz]")

    plt.show()


def json(args, scopeData, outfile):
    import json
    import array

    print("warning: Voltage computation code is currently giving WRONG results, please do not rely on the calculated values until code is improved.", file=sys.stderr)

    class ArrayEncoder(json.JSONEncoder):
        def default(self, obj):
            if isinstance(obj, array.array):
                return tuple(obj)
            return json.JSONEncoder.default(self, obj)

    print(json.dumps(scopeData, cls=ArrayEncoder, indent=4, separators=(',', ': ')), file=outfile)


def vcd(args, scopeData, outfile):
    if scopeData["enabledChannelsCount"] > 0:
        def stringSection(name, value="", seperator=' '):
            return '$%(name)s%(seperator)s%(value)s%(seperator)s$end' % {'name': name, 'value': value,
                                                                         'seperator': seperator}

        print(stringSection("timescale", "%d ns" % (round(1e9 / (scopeData["samplerate"])))), file=outfile)
        print(stringSection("scope", "module logic"), file=outfile)

        def channelToSymbol(c):
            assert c >= 0 & c < 16
            return chr(ord('a') + c)

        for channel in scopeData["enabledChannels"]:
            print(stringSection("var", "wire 1 %s D%02i" % (channelToSymbol(channel), channel + 1)), file=outfile)

        print(stringSection("upscope"), file=outfile)
        print(stringSection("enddefinitions"), file=outfile)

        lastState = dict([(x, -1) for x in scopeData["enabledChannels"]])
        currState = {}
        for pos in range(scopeData['channel'][scopeData["enabledChannels"][0] + 1]['nsamples']):
            changedChannels = []
            for channel in scopeData["enabledChannels"]:
                currState[channel] = 1 if scopeData['channel'][channel + 1]['samples']['raw'][pos] > args.threshold else 0
                if currState[channel] != lastState[channel]:
                    changedChannels.append(channel)
                    lastState[channel] = currState[channel]
            if len(changedChannels) > 0:
                print('#%i ' % pos, file=outfile)
                for changedChannel in changedChannels:
                    print('%i%s' % (currState[changedChannel], channelToSymbol(changedChannel)), file=outfile)
    else:
        print("error: No channels enabled in WFM file", file=sys.stderr)

def stimuli(args, scopeData, outfile):
    if scopeData["enabledChannelsCount"] > 0:
        timeScale = scopeData['timeScale']
        lastState = dict([(x, -1) for x in scopeData["enabledChannels"]])
        lastPos = 0
        channelMapping = {0: args.ch1, 1: args.ch2, 2: args.ch3, 3: args.ch4}
        mappedChannels = [channel for channel in scopeData["enabledChannels"] if channelMapping[channel]]
        if len(mappedChannels) > 0:
            currState = {}
            print("// CPU clock: %d Hz" % args.clkFreq, file=outfile)
            for channel in mappedChannels:
                print("// CH%d: %s:%d" % (channel + 1, channelMapping[channel][0], channelMapping[channel][1]), file=outfile)
            for pos in range(scopeData['channel'][scopeData["enabledChannels"][0] + 1]['nsamples']):
                changedChannels = []
                for channel in mappedChannels:
                    currState[channel] = 1 if scopeData['channel'][channel + 1]['samples']['raw'][pos] > args.threshold else 0
                    if currState[channel] != lastState[channel]:
                        changedChannels.append(channel)
                        lastState[channel] = currState[channel]
                if len(changedChannels) > 0:
                    print('#%i' % ((pos - lastPos) * timeScale / (1. / args.clkFreq)), file=outfile)
                    lastPos = pos
                    for changedChannel in changedChannels:
                        bitEnabled = currState[changedChannel]
                        channelPort = channelMapping[changedChannel][0]
                        channelBit = channelMapping[changedChannel][1]
                        print("%s %s %d" % (channelPort, "|=" if bitEnabled else "&=",
                                            (1 << channelBit) if bitEnabled else (255 - (1 << channelBit))), file=outfile)
        else:
            print("error: No channels mapped to port pins or mapped channels not enabled in WFM file", file=sys.stderr)
    else:
        print("error: No channels enabled in WFM file", file=sys.stderr)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Rigol DS1000Z series WFM file reader')
    infileparser = argparse.ArgumentParser(add_help=False)
    infileparser.add_argument('infile', type=argparse.FileType('rb'), help="Input WFM file")
    infileparser.add_argument('outfile', type=argparse.FileType('wb'), default=sys.stdout, nargs='?', help="Output file, defaults to stdout")
    infileparser.add_argument('--forgiving', action='store_false', help="Lazier file parsing")
    subparsers = parser.add_subparsers(dest='action', help="Action to perform on the WFM file")
    subparsers.required=True
    infoParser = subparsers.add_parser('info', parents=[infileparser], help="Print information about the file")
    csvParser = subparsers.add_parser('csv', parents=[infileparser], help="Generate CSV representation of voltages or raw values")
    csvParser.add_argument('-r', '--raw', action='store_true', help='Use raw values instead of voltages')
    csvParser.add_argument('-t', '--notime', action='store_true', help='Do not include time in the output')
    csvParser.add_argument('-d', '--header', type=str, default='normal', choices=['none', 'std', 'rigol'], help='Type of header; std is a standard single-line header, rigol is a two-line header following format produced by the oscilloscope, none is no header')
    plotParser = subparsers.add_parser('plot', parents=[infileparser], help="Plot voltage or raw values with optional FFT")
    plotParser.add_argument('-r', '--raw', action='store_true', help='Use raw values instead of voltages')
    plotParser.add_argument('-l', '--nolegend', action='store_true', help='Do not display legend')
    plotParser.add_argument('-f', '--fft', action='store_true', help='Display FFT')
    jsonParser = subparsers.add_parser('json', parents=[infileparser], help="Generate JSON representation")
    vcdParser = subparsers.add_parser('vcd', parents=[infileparser], help="Generate VCD (Value Change Dump) representation")
    vcdParser.add_argument('-s', '--threshold', type=int, default=128, required=False, help='Logic level treshold value')
    stimuliParser = subparsers.add_parser('stimuli', parents=[infileparser],
                                          help='Generate Atmel Studio 6 stimuli file')
    stimuliParser.add_argument('--ch1', type=PortPin, required=False, help='I/O Register bit to map CH1 to. Format: <REG>:<BIT>, where REG is register name or address and BIT is bit number (zero-based), e.g. PIND:0')
    stimuliParser.add_argument('--ch2', type=PortPin, required=False, help='I/O Register bit to map CH2 to.')
    stimuliParser.add_argument('--ch3', type=PortPin, required=False, help='I/O Register bit to map CH3 to.')
    stimuliParser.add_argument('--ch4', type=PortPin, required=False, help='I/O Register bit to map CH4 to.')
    stimuliParser.add_argument('-s', '--threshold', type=int, default=128, required=False, help='Logic level treshold value')
    stimuliParser.add_argument('--clkFreq', type=int, required=True, help="Simulated AVR uC clock frequency in Hz")

    actionMap = {
                    "info": info,
                    "csv": csv,
                    "plot": plot,
                    "json": json,
                    "vcd": vcd,
                    "stimuli": stimuli
                }

    args = parser.parse_args()

    try:
        with args.infile as f:
            scopeData = wfm.parseRigolWFM(f, args.forgiving)
        if isinstance(args.outfile, TextIOWrapper):
            outputFile = args.outfile
        else:
            outputFile = TextIOWrapper(args.outfile, encoding="ascii")
        actionMap[args.action](args, scopeData, outputFile)
        outputFile.close()
    except wfm.FormatError as e:
        print("Format does not follow the known file format. Try the --forgiving option.", file=sys.stderr)
        print("If you'd like to help development, please report this error:\n", file=sys.stderr)
        print(e, file=sys.stderr)
        sys.exit()

