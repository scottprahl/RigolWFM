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

This project is a comprehensive resource for interpreting waveform the proprietary format ``.wmf`` files created by many Rigol oscilloscopes.  Open source (and Rigol's own applications) that can parse/convert Rigol's binary ``.wfm`` files are sadly balkanized: each program tends to support a single oscilloscope group.

This project leverages a domain specific language <https://doc.kaitai.io> to represent the binary files.  Once a binary file has been described in this text format, parsers can be generated for a wide range of languages (C++/STL, C#, Go, Java, JavaScript, Lua, Perl, PHP, Python, and Ruby).  


Installation
---------------

You can install locally using pip::
    
    pip install --user RigolWFM

or ``conda``::

    conda install -c conda-forge RigolWFM

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
| MSO5074     | MSO5074          | ``.bin`` | tested but incomplete, need more examples|
+-------------+------------------+----------+------------------------------------------+
| MSO7000/    | DS7000, MSO7000, | ``.bin`` | tested                                   |
| MSO8000     | MSO8000, DS8000  |          |                                          |
+-------------+------------------+----------+------------------------------------------+
| DHO800/     | DHO800, DHO1000  | ``.bin`` | tested; calibrated float32 samples,      |
| DHO1000     |                  | ``.wfm`` | official format documented in User Guide |
+-------------+------------------+----------+------------------------------------------+

The MSO5074 uses a non-standard firmware layout (uint8 ADC counts, incorrect metadata fields); voltage values are approximated at 1 V/div since no calibration data is embedded in the file.  

Resources
---------

This has been a bit of an adventure.  In the process of nailing down the basic formats, I have gleaned information from a wide range of projects started by others.

* Shein's <https://sourceforge.net/projects/wfmreader>
* Wagenaars's <https://www.mathworks.com/matlabcentral/fileexchange/18999-read-binary-rigol-waveforms>
* Steele's <http://nsweb.tn.tudelft.nl/~gsteele/rigol2dat>
* Blaicher's <https://github.com/mabl/pyRigolWFM>
* Szkutnik's <https://github.com/michal-szkutnik/pyRigolWfm1000Z>
* Cat-Ion's <https://github.com/Cat-Ion/rigol-ds4000-wfm>
* Šolc's <https://www.tablix.org/~avian/blog/archives/2019/08/quick_and_ugly_wfm_data_export_for_rigol_ds2072a/>
* Contributions from <http://www.hakasoft.com.au/wfm_viewer>
* Rigol's documentation of the 1000E, 1000Z, 2000, and 6000 file formats.
* Rigol's documentation of the ``.bin'' formats for the 1000, 5000, and 8000
* Lathe's <https://github.com/Lathe26/WFM_for_Rigol_DHO800_900>


License
-------
    BSD 3-clause -- see the file ``LICENSE`` for details.
