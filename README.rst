
Parsing binary .wfm files created by Rigol scopes
=================================================

Usage
-----

The RigolWFM package can be installed via `pip`::

.. code-block::

   pip install RigolWFM


Once this is done, one can extract signals from binary Rigol ``.wfm`` files by:

.. code-block::

   import matplotlib.pyplot as plt
   import RigolWFM.wfm as rigol

   filename = 'example.wfm'
   scope = 'DS1000E'

   w = rigol.Wfm.from_file(filename, scope)
   w.plot()
   plt.show()


Alternatively, ``wfmconvert`` can be used from the command line.  For example, the following should convert all the DS1000E files in the current directory to the ``.csv`` format:

.. code-block::

   prompt> wfmconvert 1000E csv *.wfm


More extensive documentation can be found here


* Basics https://github.com/scottprahl/RigolWFM/blob/master/doc/0-Basics.ipynb
* DS1000E https://github.com/scottprahl/RigolWFM/blob/master/doc/1-DS1000E-Waveforms.ipynb
* DS1000Z https://github.com/scottprahl/RigolWFM/blob/master/doc/1-DS1000Z-Waveforms.ipynb
* DS2000 https://github.com/scottprahl/RigolWFM/blob/master/doc/1-DS2000-Waveforms.ipynb
* DS4000 https://github.com/scottprahl/RigolWFM/blob/master/doc/1-DS4000-Waveforms.ipynb

Background
----------

This project is should be a one-stop location for interpreting waveform ``.wmf`` files from any Rigol scopes.  Programs that parse Rigol's binary ``.wfm`` files are sadly balkanized: each project tends to support a single scope model and the available efforts are spread across a range of languages.

Most seem to avoid do not deal specifically with the ``.wfm`` format and if they do, then only one specific scope model is supported.

Initially, I too, was only interested in a single scope format (DS1102E) and I successfully used the python parser written by Blaicher https://github.com/mabl/pyRigolWFM.  Later, I realized that DS1000Z files were parsed by Szkutnik  https://github.com/michal-szkutnik/pyRigolWfm1000Z and added support for these scopes.  Eventually, I ran across the work on DS4000 files by Cat-Ion https://github.com/Cat-Ion/rigol-ds4000-wfm.

This last project leveraged Kaitai Struct https://kaitai.io as a domain specific language to represent the binary files.  Once a binary file has been described in the ``.ksy`` format, parsers can be generated for a wide range of languages (C++/STL, C#, Go, Java, JavaScript, Lua, Perl, PHP, Python, and Ruby).  Moreover, Kaitai Struct has a Web IDE https://ide.kaitai.io that allows one to interactively reverse engineer binary file formats.  This is super helpful for those Rigol ``.wfm`` formats that are undocumented.

Status
------

There is a bit of work remaining (testing, validation, repackaging) but at least there are now binary file descriptions for ``.wfm`` files for the following scopes:


* DS1000C untested
* DS1000E tested
* DS1000Z tested, but with wonky voltage offsets
* DS2000 tested
* DS4000 tested
* DS6000 untested

Resources
---------

This has been a bit of an adventure.  In the process of nailing down the basic formats, I have gleaned information from a wide range of projects started by others.


* Shein's Pascal program https://sourceforge.net/projects/wfmreader
* Wagenaars's Matlab script https://www.mathworks.com/matlabcentral/fileexchange/18999-read-binary-rigol-waveforms
* Steele's C program http://nsweb.tn.tudelft.nl/~gsteele/rigol2dat
* Blaicher's python code https://github.com/mabl/pyRigolWFM
* Szkutnik's python code https://github.com/michal-szkutnik/pyRigolWfm1000Z
* Cat-Ion's python code https://github.com/Cat-Ion/rigol-ds4000-wfm
* Šolc's python code https://www.tablix.org/~avian/blog/archives/2019/08/quick_and_ugly_wfm_data_export_for_rigol_ds2072a/
* Contributions from http://www.hakasoft.com.au/wfm_viewer
* A LabView program I got from Rigol support
* Rigol's documentation of the 1000E, 1000Z, 2000, and 6000 file formats.

License
-------

Copyright (c) 2020, Scott Prahl
All rights reserved.

Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:


#. 
   Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.

#. 
   Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
