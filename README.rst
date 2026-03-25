.. |pypi-badge| image:: https://img.shields.io/pypi/v/RigolWFM?color=68CA66
   :target: https://pypi.org/project/RigolWFM/
   :alt: pypi

.. |github-badge| image:: https://img.shields.io/github/v/tag/scottprahl/RigolWFM?label=github&color=68CA66
   :target: https://github.com/scottprahl/RigolWFM
   :alt: github

.. |conda-badge| image:: https://img.shields.io/conda/vn/conda-forge/RigolWFM?label=conda&color=68CA66
   :target: https://github.com/conda-forge/RigolWFM-feedstock
   :alt: conda

.. |kaitaistruct| image:: https://img.shields.io/badge/kaitai-struct-68CA66
   :target: https://ide.kaitai.io
   :alt: kaitai-struct

.. |zenodo-badge| image:: https://zenodo.org/badge/244228290.svg
   :target: https://zenodo.org/badge/latestdoi/244228290
   :alt: doi

.. |license-badge| image:: https://img.shields.io/github/license/scottprahl/RigolWFM?color=68CA66
   :target: https://github.com/scottprahl/RigolWFM/blob/main/LICENSE.txt
   :alt: License

.. |test-badge| image:: https://github.com/scottprahl/RigolWFM/actions/workflows/test.yaml/badge.svg
   :target: https://github.com/scottprahl/RigolWFM/actions/workflows/test.yaml
   :alt: Testing

.. |docs-badge| image:: https://readthedocs.org/projects/rigolwfm/badge?color=68CA66
   :target: https://rigolwfm.readthedocs.io
   :alt: Docs

.. |downloads-badge| image:: https://img.shields.io/pypi/dm/RigolWFM?color=68CA66
   :target: https://pypi.org/project/RigolWFM/
   :alt: Downloads

RigolWFM
=========

by Scott Prahl

A utility to process Rigol oscilloscope ``.wfm`` files
------------------------------------------------------

|pypi-badge| |github-badge| |conda-badge| |kaitaistruct| |zenodo-badge|

|license-badge| |test-badge| |docs-badge| |downloads-badge|

This project is intended to be a comprehensive resource for interpreting waveform ``.wmf`` files created by any Rigol oscilloscope.  Open source (and Rigol's own applications) that parse/convert Rigol's binary ``.wfm`` files are sadly balkanized: each program tends to support a single oscilloscope group and the available efforts are spread across a range of languages.

This project leverages a domain specific language (kaitai struct) to represent the binary files.  Once a binary file has been described in this text format, parsers can be generated for a wide range of languages (C++/STL, C#, Go, Java, JavaScript, Lua, Perl, PHP, Python, and Ruby).  

Documentation can be found at <https://RigolWFM.readthedocs.io>

Installation
---------------

You can install locally using pip::
    
    pip install --user RigolWFM

or ``conda``::

    conda install -c conda-forge RigolWFM

or use immediately by clicking the Google Colaboratory button below

.. image:: https://colab.research.google.com/assets/colab-badge.svg
  :target: https://colab.research.google.com/github/scottprahl/RigolWFM/blob/main
  :alt: Colab

or `analyze your files using the kaitai struct IDE <https://ide.kaitai.io>`_ (you will need to manually upload the appropriate `.ksy` file and your `.wfm` to the IDE).  This allows one to interactively reverse engineer binary file formats directly in your browser.  This is super helpful for those Rigol ``.wfm`` formats that are undocumented or not parsing correctly.


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

Status
------

There are binary file descriptions for waveform files created by the following scopes:

+-------------+------------------+----------+------------------------------------------+
| Family      | Models           | Format   | Notes                                    |
+=============+==================+==========+==========================================+
| DS1000B     | DS1074/1104/     | ``.wfm`` | tested                                   |
|             | 1204B            |          |                                          |
+-------------+------------------+----------+------------------------------------------+
| DS1000C     | DS1042/1102/     | ``.wfm`` | tested (limited files)                   |
|             | 1202CA           |          |                                          |
+-------------+------------------+----------+------------------------------------------+
| DS1000D     | DS1052/1102D     | ``.wfm`` | tested (limited files)                   |
+-------------+------------------+----------+------------------------------------------+
| DS1000E     | DS1052/1102E     | ``.wfm`` | tested                                   |
+-------------+------------------+----------+------------------------------------------+
| DS1000Z     | DS1054Z,         | ``.wfm`` | tested                                   |
|             | MSO1054Z, etc.   |          |                                          |
+-------------+------------------+----------+------------------------------------------+
| DS2000      | DS2072A,         | ``.wfm`` | tested                                   |
|             | MSO2102A, etc.   |          |                                          |
+-------------+------------------+----------+------------------------------------------+
| DS4000      | DS4012–DS4054,   | ``.wfm`` | tested                                   |
|             | MSO4012–MSO4054  |          |                                          |
+-------------+------------------+----------+------------------------------------------+
| DS6000      | DS6062–DS6104    | ``.wfm`` | untested                                 |
+-------------+------------------+----------+------------------------------------------+
| MSO5000     | MSO5354, etc.    | ``.bin`` | tested                                   |
+-------------+------------------+----------+------------------------------------------+
| MSO5074     | MSO5074          | ``.bin`` | tested; voltage values approximate       |
|             |                  |          | (no calibration data in file)            |
+-------------+------------------+----------+------------------------------------------+
| MSO7000/    | DS7000, MSO7000, | ``.bin`` | tested                                   |
| MSO8000     | MSO8000, DS8000  |          |                                          |
+-------------+------------------+----------+------------------------------------------+
| DHO800/     | DHO800, DHO1000  | ``.bin`` | tested; calibrated float32 samples,      |
| DHO1000     |                  | ``.wfm`` | official format documented in User Guide |
+-------------+------------------+----------+------------------------------------------+

DHO Series Notes
~~~~~~~~~~~~~~~~

DHO800 and DHO1000 series oscilloscopes export waveforms in two formats:

* ``.bin`` — official format documented in the User Guide (§19.2.4); stores calibrated
  float32 voltage samples; works identically across all DHO variants.
* ``.wfm`` — proprietary undocumented format; reverse-engineered for both DHO1000
  and DHO800.  The DHO800 uses a different block type (5 vs 9), a 10× larger scale
  divisor, and interleaves all enabled channels in a single data section.

Both formats support up to 4 simultaneous channels.

MSO5000/7000/8000 Series Notes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

These scopes export waveforms as ``.bin`` files.  The MSO5074 uses a non-standard
firmware layout (uint8 ADC counts, incorrect metadata fields); voltage values are
approximated at 1 V/div since no calibration data is embedded in the file.

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


License
-------
    BSD 3-clause -- see the file ``LICENSE`` for details.
