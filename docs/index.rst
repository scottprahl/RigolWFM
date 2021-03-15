RigolWFM: a utility to process Rigol oscilloscope `.wfm` files
==============================================================

.. image:: https://mybinder.org/badge_logo.svg
   :target: https://mybinder.org/v2/gh/scottprahl/RigolWFM/master?filepath=docs

.. image:: https://colab.research.google.com/assets/colab-badge.svg
   :target: https://colab.research.google.com/github/scottprahl/RigolWFM/blob/master

.. image:: https://img.shields.io/badge/kaitai-struct-green.svg
   :target: https://ide.kaitai.io

.. image:: https://img.shields.io/badge/nbviewer-docs-yellow.svg
   :target: https://nbviewer.jupyter.org/github/scottprahl/RigolWFM/tree/master/docs

.. image:: https://img.shields.io/badge/readthedocs-latest-blue.svg
   :target: https://RigolWFM.readthedocs.io

__________

This project is intended to be a comprehensive resource for interpreting waveform ``.wmf`` files created by any Rigol oscilloscope.  The open source (and Rigol's own applications) that parse/convert Rigol's binary ``.wfm`` files are sadly balkanized: each program tends to support a single oscilloscope group and the available efforts are spread across a range of languages.

This project leverages a domain specific language (kaitai struct) to represent the binary files.  Once a binary file has been described in this text format, parsers can be generated for a wide range of languages (C++/STL, C#, Go, Java, JavaScript, Lua, Perl, PHP, Python, and Ruby).  

Kaitai Struct <https://kaitai.io> also has a slick web IDE <https://ide.kaitai.io> that allows one to interactively reverse engineer binary file formats directly in your browser.  This is super helpful for those Rigol ``.wfm`` formats that are undocumented.


Links
=====
.. toctree::
   :maxdepth: 3
   :titlesonly:
   
   readme
   0-Basics.ipynb
   1-DS1000C-Waveforms.ipynb
   1-DS1000E-Waveforms.ipynb
   1-DS1000Z-Waveforms.ipynb
   1-DS2000-Waveforms.ipynb
   1-DS4000-Waveforms.ipynb

   RigolWFM

   changelog
