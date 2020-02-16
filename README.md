# Rigol oscilloscope waveform library

## Background

This project is designed to be a one-stop location for interpreting waveform `.wmf` files from all Rigol scopes.  There are quite a few different Github projects for interacting with Rigol scopes, but most do not deal specifically with the `.wfm` format and if they do, then only one specific scope model.

Initially, I only was interested in parsing DS1000E scope formats and I used the python code written by Blaicher <https://github.com/mabl/pyRigolWFM>.  Later, I noticed that 1000Z files were supported by the work of Szkutnik  <https://github.com/mabl/pyRigolWFM>.  Then, I found the DS1000D Matlab code by Wagenaars <https://www.mathworks.com/matlabcentral/fileexchange/18999-read-binary-rigol-waveforms>.
Eventually, I ran across the work on DS4000 files by Cat-Ion <https://github.com/Cat-Ion/rigol-ds4000-wfm>.

This last project used Kaitai Struct <https://kaitai.io> as a domain specific language to represent the binary files.  Once the binary waveform files are described in the `.ksy` format then parsers can be generated for a wide range of languages (C++/STL, C#, Go, Java, JavaScript, Lua, Perl, PHP, Python, and Ruby).  Moreover, Kaitai Struct has a Web IDE <https://ide.kaitai.io> that allows one to interactively reverse engineer binary file formats.  This is super helpful in the case of the Rigol `.wfm` formats that are undocumented.

There is a bit of work remaining (testing and validation) but at least there are now binary file descriptions for

* 1000C and 1000D
* 1000E
* 1000Z
* 4000C

## Usage

A python module (the old pre-Kaitai Struct version!) can be installed via `pip`::

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

