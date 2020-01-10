# Rigol DS1000E and DS1000Z series oscilloscope waveform library

This is a fork of the work done by Blaicher and Szkutnik to create a command-line utility for converting Rigol waveform files to other formats.  The primary purpose of this fork is to create a module that can be installed via `pip`::

    pip install RigolWFM

Once this is done, one can extract signals from binary Rigol `.wfm` files easily::

    import matplotlib.pyplot as plt
    import RigolWFM.wfm as wfm

    t, y = wfm.signals('OneChannelFile.wfm')
    plt.plot(t,y)
    plt.show()

    t, y1, y2 = wfm.signals('TwoChannelFile.wfm')
    plt.plot(t,y)
    plt.show()


## Rigol DS1000E Scopes

The parsing code to read these `.wfm` files from these scopes is written by Blaicher <https://github.com/mabl/pyRigolWFM>.  The code has been tested by me to work on files from the DS1102E and DS1052E.

## Rigol DS1000Z

The parsing code to read these `.wfm` files from these scopes is written by Szkutnik  <https://github.com/mabl/pyRigolWFM>.  Since I don't have one of these scopes this exact code is currently untested, but it may still work. Szkutnik does warn

1. the calculated voltage values are wrong
2. the WFM file format can change with firmware.  Only versions 00.04.01.SP2, 00.04.02.SP4 and 00.04.03.SP2 have been tested by Szkutnik with a DS1054Z
3. the logic analyzer functions

## Rigol DS1000C and DS1000D

Unfortunately there is no python code, but in the `doc` directory are C and Matlab codes to parse `.wfm` files for those scopes.  Anyone who decides to write a python parser might want consider using `wfm_view` at <http://meteleskublesku.cz/wfm_view/> (although this was created specifically to reverse engineer the DS1052E).
