# Rigol DS1000Z series oscilloscopes waveform library & utilities for Python 3.4

*Important! This library can not calculate correct voltage values from raw data. I could not (yet?) locate all the data necessary to do that in the WFM files. Use --raw parameter to use raw data for plots and CSV files. Any help with file format is welcome!*

*Important! WFM file format differs with firmware versions, 00.04.01.SP2, 00.04.02.SP4 and 00.04.03.SP2 are currently supported, others are untested.*

These scripts are based on the [pyRigolWFM](https://github.com/mabl/pyRigolWFM) by Matthias Blaicher and my reverse engineering of Rigol DS1054Z WFM files.
They include a library for reading DS1000Z WFM files and extracting some basic data from them and a utility for plotting and conversion of the WFM file data to other formats.

The library has been tested with Rigol DS1054Z but hopefully also works with other oscilloscopes from the DS1000Z series.

Additionally an application wfmutil.py is included which provides (See wfmutil.py -h and wfmutil.py <action> -h for parameter descriptions):

 - Printing information about the WFM file
 - Export of WFM data in JSON format
 - Export of WFM data in CSV format
 - Export of WFM data in VCD (Value Change Dump) format
 - Export of WFM data in Atmel Studio 6 stimuli file format  
 - Interactive plotting of the waveform including an FFT (--fft option)(plotting requires scipy, numpy and matplotlib libraries)

## Not supported
 - Voltage calculation from raw data - there is some voltage calculaction code, but it is not functional and produces wrong results except specific cases.
 - Logic analyser (my DS1054Z doesn't have one)
 - Any settings not printed in the following example output are not (yet?) supported
 
## VCD and AS6 stimuli files
As logic analyser is not supported, logic values for VCD and AS6 stimuli files are calculated from raw data of analog channels by simply comparing them to a threshold value (by default 128) common to all the channels (separate threshold values and automatic calculation of threshold values to be done). 
This simple method may not be optimal, but is OK for clean signals.

## Examples

### Information extraction
    % python wfmutil.py info foo.wfm

    General
    =======
    Device model             : DS1054Z
    Firmware version         : 00.04.01.SP2
    Horizontal scale         : 2000000000 ps
    Time delay               : 0 ps
    Sampling rate            : 1.250000e+05 samples/s
    Enabled channels         : [0, 1, 2, 3] (zero-based indexes)
    
    Channel CH1
    ===========
    Label                    : CH1
    Enabled                  : True
    Probe attenuation        : 10.000x
    Y grid scale             : 5.000e+00 V/div
    Y shift                  : 0.000e+00 V
    Y inverted               : False
    Sampling rate            : 1.250e+05 samples/s
    Time delay               : 0.000e+00 s
    No. of recorded samples  : 3000
    
    Channel CH2
    ===========
    Label                    : CH2
    Enabled                  : True
    Probe attenuation        : 10.000x
    Y grid scale             : 2.000e+00 V/div
    Y shift                  : 0.000e+00 V
    Y inverted               : False
    Sampling rate            : 1.250e+05 samples/s
    Time delay               : 0.000e+00 s
    No. of recorded samples  : 3000
    
    Channel CH3
    ===========
    Label                    : CH3
    Enabled                  : True
    Probe attenuation        : 10.000x
    Y grid scale             : 8.400e-01 V/div
    Y shift                  : 0.000e+00 V
    Y inverted               : False
    Sampling rate            : 1.250e+05 samples/s
    Time delay               : 0.000e+00 s
    No. of recorded samples  : 3000
    
    Channel CH4
    ===========
    Label                    : CH4
    Enabled                  : True
    Probe attenuation        : 10.000x
    Y grid scale             : 2.000e-01 V/div
    Y shift                  : 0.000e+00 V
    Y inverted               : False
    Sampling rate            : 1.250e+05 samples/s
    Time delay               : 0.000e+00 s
    No. of recorded samples  : 3000


### CSV export
    % python wfmutil.py csv -r foo.wfm | head
    X,CH1,CH2,CH3,CH4
    -1.20000e-02,89,142,138,95
    -1.19920e-02,89,141,138,95
    -1.19840e-02,89,141,138,95
    -1.19760e-02,89,139,138,95
    -1.19680e-02,89,139,138,95
    -1.19600e-02,89,143,138,95
    -1.19520e-02,89,140,138,95
    -1.19440e-02,89,142,138,95
    -1.19360e-02,89,141,138,95

### AS6 stimuli file export

    % python wfmutil.py stimuli --clkFreq 16000000 --ch1 PIND:0 rs232.wfm | head
    // CPU clock: 16000000 Hz
    // CH1: PIND:0
    #0
    PIND |= 1
    #12844
    PIND &= 254
    #1670
    PIND |= 1
    #1668
    PIND &= 254

### License
    
    Copyright (c) 2013, Matthias Blaicher
    Copyright (c) 2014, Michał Szkutnik
    All rights reserved.

    Redistribution and use in source and binary forms, with or without
    modification, are permitted provided that the following conditions are met: 

    1. Redistributions of source code must retain the above copyright notice, this
      list of conditions and the following disclaimer. 
    2. Redistributions in binary form must reproduce the above copyright notice,
      this list of conditions and the following disclaimer in the documentation
      and/or other materials provided with the distribution. 

    THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
    ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
    WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
    DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
    ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
    (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
    LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
    ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
    (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
    SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
