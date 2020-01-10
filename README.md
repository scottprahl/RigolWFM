# Rigol DS1000E and DS1000Z series oscilloscope waveform library

This is a fork of the work done by Blaicher and Szkutnik to create a command-line utility for converting Rigol waveform files to other formats.  The primary purpose of this fork is to create a module that can be installed via `pip`::

    pip install RigolWFM

Once this is done, one can extract signals from binary Rigol `wfm` files easily::

    import matplotlib.pyplot as plt
    import RigolWFM.wfm as wfm

    t, y = wfm.signals('OneChannelFile.wfm')
    plt.plot(t,y)
    plt.show()

    t, y1, y2 = wfm.signals('TwoChannelFile.wfm')
    plt.plot(t,y)
    plt.show()


## Rigol DS1000E Scopes

The parsing code to read these `.wfm` files from these scopes is written by Blaicher at (pyRigolWFM)[https://github.com/mabl/pyRigolWFM].  The code has been tested by me to work on files from the DS1102E and DS1052E.

## Rigol DS1000Z

The parsing code to read these `.wfm` files from these scopes is written by Szkutnik at (pyRigolWFM)[https://github.com/mabl/pyRigolWFM].  Since I don't have one of these scopes this exact code is currently untested but since I did not touch the parsing code I expect it should still work. Szkutnik does mention

1. the calculated voltage values are wrong
2. the WFM file format can change with firmware.  Only versions 00.04.01.SP2, 00.04.02.SP4 and 00.04.03.SP2 have been tested by Szkutnik with a DS1054Z
3. the logic analyzer functions

## Rigol DS1000C and DS1000D

Unfortunately there is no python code, but in the `doc` directory are C and Matlab codes to parse `.wfm` files for those scopes.  Anyone decides to put together python parses might want consider using (wfm_view)[http://meteleskublesku.cz/wfm_view/] although this was created specifically to reverse engineer the DS1052E.

## License

Copyright (c) 2013, Matthias Blaicher

Copyright (c) 2014, Michał Szkutnik

Copyright (c) 2020, Scott Prahl

All rights reserved.

Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
