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

A utility to process oscilloscope waveform files
------------------------------------------------

|pypi-badge| |github-badge| |conda-badge| |kaitaistruct| |zenodo-badge|

|license-badge| |test-badge| |docs-badge| |downloads-badge|

This project started as a resource for interpreting the proprietary ``.wfm``
files created by Rigol oscilloscopes.  It now also includes parsers for
Tektronix, LeCroy, Agilent / Keysight, Siglent, and Yokogawa waveform files.
Open source tools that can parse or convert these binary oscilloscope formats
are often balkanized: each program tends to support a single oscilloscope
group.

This project leverages the domain specific language at
<https://doc.kaitai.io> to describe binary files.  Once a format has been
described in this text form, parsers can be generated for a wide range of
languages.

Installation
---------------

You can install locally using pip::
    
    pip install --user RigolWFM

or ``conda``::

    conda install -c conda-forge RigolWFM

or just open <https://scottprahl.github.io/RigolWFM/> and try the web version.

Usage
-----

Once ``RigolWFM`` is installed, you can plot signals from supported waveform
files by::

   import matplotlib.pyplot as plt
   from RigolWFM import Wfm

   filename = 'example.wfm'
   scope = 'DS1000E'

   w = Wfm.from_file(filename)
   w.plot()
   plt.show()

``Wfm.from_file()`` will autodetect the file family for supported formats, so
the same call works for Rigol ``.wfm`` / ``.bin`` files, Tektronix ``.wfm`` /
``.isf`` files, LeCroy ``.trc`` files, Agilent / Keysight ``AGxx`` ``.bin``
files, supported Siglent ``.bin`` revisions, and Yokogawa ``.wfm`` files.


Alternatively, ``wfmconvert`` can be used from the command line.  For example, the following should convert all the DS1000E files in the current directory to the ``.csv`` format::

   prompt> wfmconvert csv *.wfm

If you just wanted to convert channel 1 from a single file to ``.csv`` then::

   prompt> wfmconvert --channel 1 csv DS1102E.wfm

If you wanted to a signal `.wav` file using the second channel waveform (for use with LTspice) then:: 

   prompt> wfmconvert --channel 2 wav *.wfm

If you want to create a ``.wav`` file with channels one and four as signals (and autoscale for use with Audacity or Sigrok Pulseview)::

   prompt> wfmconvert --autoscale --channel 14 wav *.wfm

The project also includes a browser-based viewer at
<https://scottprahl.github.io/RigolWFM/>.  The current web app supports Rigol
``.wfm`` / ``.bin`` files, Tektronix ``.wfm`` / ``.isf`` files, LeCroy
``.trc`` files, Agilent / Keysight ``AGxx`` ``.bin`` files, and supported
Siglent ``.bin`` revisions.

Status
------

There are binary file descriptions and normalized adapters for waveform files
created by the following oscilloscopes.  Most of these work directly through
``Wfm.from_file()``; rows with special limitations are called out in the notes.

+--------------------+------------------+-------------------+-----------------------------------------------+
| Family             | Models           | Format            | Notes                                         |
+====================+==================+===================+===============================================+
| Rigol DS1000B      | DS1074/1104/     | ``.wfm``          | tested                                        |
|                    | 1204B            |                   |                                               |
+--------------------+------------------+-------------------+-----------------------------------------------+
| Rigol DS1000C      | DS1042/1102/     | ``.wfm``          | tested (limited files)                        |
|                    | 1202CA           |                   |                                               |
+--------------------+------------------+-------------------+-----------------------------------------------+
| Rigol DS1000D      | DS1052/1102D     | ``.wfm``          | tested (limited files)                        |
+--------------------+------------------+-------------------+-----------------------------------------------+
| Rigol DS1000E      | DS1052/1102E     | ``.wfm``          | tested                                        |
+--------------------+------------------+-------------------+-----------------------------------------------+
| Rigol DS1000Z      | DS1054Z,         | ``.wfm``          | tested                                        |
|                    | MSO1054Z, etc.   |                   |                                               |
+--------------------+------------------+-------------------+-----------------------------------------------+
| Rigol DS2000       | DS2072A,         | ``.wfm``          | tested                                        |
|                    | MSO2102A, etc.   |                   |                                               |
+--------------------+------------------+-------------------+-----------------------------------------------+
| Rigol DS4000       | DS4012-DS4054,   | ``.wfm``          | tested                                        |
|                    | MSO4012-MSO4054  |                   |                                               |
+--------------------+------------------+-------------------+-----------------------------------------------+
| Rigol DS6000       | DS6062-DS6104    | ``.wfm``          | untested                                      |
+--------------------+------------------+-------------------+-----------------------------------------------+
| Rigol MSO5000      | MSO5354, etc.    | ``.bin``          | tested                                        |
+--------------------+------------------+-------------------+-----------------------------------------------+
| Rigol MSO7000 /    | DS7000, MSO7000, | ``.bin``          | tested                                        |
| MSO8000            | MSO8000, DS8000  |                   |                                               |
+--------------------+------------------+-------------------+-----------------------------------------------+
| Rigol DHO800 /     | DHO800, DHO1000  | ``.bin``          | tested; calibrated float32 samples, official  |
| DHO1000            |                  | ``.wfm``          | ``.bin`` and proprietary ``.wfm`` support     |
+--------------------+------------------+-------------------+-----------------------------------------------+
| Tektronix WFM      | modern DPO/DSA   | ``.wfm``          | supports ``WFM#001``/``WFM#002``/``WFM#003``; |
|                    | families         |                   | legacy ``LLWFM`` also supported               |
+--------------------+------------------+-------------------+-----------------------------------------------+
| Tektronix ISF      | many Tek scopes  | ``.isf``          | tested                                        |
+--------------------+------------------+-------------------+-----------------------------------------------+
| LeCroy             | many WaveRunner/ | ``.trc``          | tested; handles SCPI-prefixed ``WAVEDESC``    |
|                    | WaveSurfer/etc.  |                   | files                                         |
+--------------------+------------------+-------------------+-----------------------------------------------+
| Agilent /          | InfiniiVision /  | ``.bin``          | supports ``AG01``/``AG03``/``AG10`` analog    |
| Keysight           | Infiniium        |                   | captures; low-level parser preserves segments |
|                    |                  |                   | and multi-buffer metadata                     |
+--------------------+------------------+-------------------+-----------------------------------------------+
| Siglent            | documented       | ``.bin``          | supports documented V0.1-V6 revisions; old    |
|                    | ``.bin``         |                   | platform files are detectable via low-level   |
|                    | families         |                   | parsers but not normalized yet                |
+--------------------+------------------+-------------------+-----------------------------------------------+
| Yokogawa           | ASCII-header     | ``.wfm``          | tested single-file import path                |
|                    | waveform exports |                   |                                               |
+--------------------+------------------+-------------------+-----------------------------------------------+

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
* Rigol's documentation of the ``.bin`` formats for the 1000, 5000, and 8000
* Lathe's <https://github.com/Lathe26/WFM_for_Rigol_DHO800_900>
* Nezarati's <https://nezarati.github.io/waveform-viewer/index.html>
* Wavebin's <https://github.com/eyalroz/wavebin> Agilent / Keysight parsers and samples
* Agilent / Keysight ``.bin`` reference readers and programming guides
* Siglent's waveform format PDF and vendor reference parsers
* SMASH toolbox vendor importers for Tektronix, LeCroy, and Yokogawa formats

License
-------
    BSD 3-clause -- see the file ``LICENSE`` for details.
