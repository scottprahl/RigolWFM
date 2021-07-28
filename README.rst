RigolWFM: a utility to process Rigol oscilloscope `.wfm` files
==============================================================

.. image:: https://colab.research.google.com/assets/colab-badge.svg
   :target: https://colab.research.google.com/github/scottprahl/RigolWFM/blob/master

.. image:: https://img.shields.io/pypi/v/RigolWFM.svg
   :target: https://pypi.org/project/RigolWFM/

.. image:: https://img.shields.io/badge/kaitai-struct-green.svg
   :target: https://ide.kaitai.io

.. image:: https://img.shields.io/badge/readthedocs-latest-blue.svg
   :target: https://RigolWFM.readthedocs.io

.. image:: https://img.shields.io/badge/github-code-green.svg
   :target: https://github.com/scottprahl/RigolWFM

.. image:: https://img.shields.io/badge/BSD-license-yellow.svg
   :target: https://github.com/scottprahl/RigolWFM/blob/master/LICENSE

__________

This project is intended to be a comprehensive resource for interpreting waveform ``.wmf`` files created by any Rigol oscilloscope.  Open source (and Rigol's own applications) that parse/convert Rigol's binary ``.wfm`` files are sadly balkanized: each program tends to support a single oscilloscope group and the available efforts are spread across a range of languages.

This project leverages a domain specific language (kaitai struct) to represent the binary files.  Once a binary file has been described in this text format, parsers can be generated for a wide range of languages (C++/STL, C#, Go, Java, JavaScript, Lua, Perl, PHP, Python, and Ruby).  

Using RigolWFM
---------------

1. You can install locally using pip::
    
    pip install --user RigolWFM

2. or `run this code in the cloud using Google Collaboratory <https://colab.research.google.com/github/scottprahl/RigolWFM/blob/master>`_ by selecting the Jupyter notebook that interests you.

3. or `analyze your files using the kaitai struct IDE <https://ide.kaitai.io>`_ (you will need to manually upload the appropriate `.ksy` file and your `.wfm` to the IDE).  This allows one to interactively reverse engineer binary file formats directly in your browser.  This is super helpful for those Rigol ``.wfm`` formats that are undocumented or not parsing correctly.


Usage
-----

Once ``RigolWFM`` is installed, you can plot the signals from binary Rigol ``.wfm`` files by::

   import matplotlib.pyplot as plt
   import RigolWFM.wfm as rigol

   filename = 'example.wfm'
   scope = 'DS1000E'

   w = rigol.Wfm.from_file(filename, scope)
   w.plot()
   plt.show()


Alternatively, ``wfmconvert`` can be used from the command line.  For example, the following should convert all the DS1000E files in the current directory to the ``.csv`` format::

   prompt> wfmconvert E csv *.wfm

If you just wanted to convert channel 1 from a single file to ``.csv`` then::

   prompt> wfmconvert --channel 1 E csv DS1102E.wfm

If you wanted to a signal `.wav` file using the second channel waveform (for use with LTspice) then:: 

   prompt> wfmconvert --channel 2 E wav *.wfm

If you want to create a ``.wav`` file with channels one and four as signals (and autoscale for use with Audacity or Sigrok Pulseview)::

   prompt> wfmconvert --autoscale --channel 14 E wav *.wfm

More extensive documentation can be found at <https://RigolWFM.readthedocs.io>

Status
------

There is a bit of work remaining (testing, validation, repackaging) but there are binary file descriptions for ``.wfm`` files created by the following scopes:

* DS1000B tested 
* DS1000C tested (one file only)
* DS1000E tested
* DS1000Z tested, but with wonky voltage offsets
* DS2000 tested
* DS4000 tested
* DS6000 untested

Resources
---------

This has been a bit of an adventure.  In the process of nailing down the basic formats, I have gleaned information from a wide range of projects started by others.


* Shein's Pascal program <https://sourceforge.net/projects/wfmreader>
* Wagenaars's Matlab script <https://www.mathworks.com/matlabcentral/fileexchange/18999-read-binary-rigol-waveforms>
* Steele's C program <http://nsweb.tn.tudelft.nl/~gsteele/rigol2dat>
* Blaicher's python code <https://github.com/mabl/pyRigolWFM>
* Szkutnik's python code <https://github.com/michal-szkutnik/pyRigolWfm1000Z>
* Cat-Ion's python code <https://github.com/Cat-Ion/rigol-ds4000-wfm>
* Šolc's python code <https://www.tablix.org/~avian/blog/archives/2019/08/quick_and_ugly_wfm_data_export_for_rigol_ds2072a/>
* Contributions from <http://www.hakasoft.com.au/wfm_viewer>
* A LabView program I got from Rigol support
* Rigol's documentation of the 1000E, 1000Z, 2000, and 6000 file formats.


Source code repository
-------------------------------------------

    <https://github.com/scottprahl/RigolWFM>

License
-------
    BSD 3-clause -- see the file ``LICENSE`` for details.
