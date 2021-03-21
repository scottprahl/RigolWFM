RigolWFM: a utility to process Rigol oscilloscope `.wfm` files
==============================================================

.. image:: https://colab.research.google.com/assets/colab-badge.svg
   :target: https://colab.research.google.com/github/scottprahl/RigolWFM/blob/master

.. image:: https://img.shields.io/badge/kaitai-struct-green.svg
   :target: https://ide.kaitai.io

.. image:: https://img.shields.io/badge/readthedocs-latest-blue.svg
   :target: https://RigolWFM.readthedocs.io

.. image:: https://img.shields.io/badge/github-code-green.svg
   :target: https://github.com/scottprahl/RigolWFM

.. image:: https://img.shields.io/badge/BSD-license-yellow.svg
   :target: https://github.com/scottprahl/RigolWFM/blob/master/LICENSE

__________

This project is intended to be a comprehensive resource for interpreting waveform ``.wmf`` files created by any Rigol oscilloscope.  The open source (and Rigol's own applications) that parse/convert Rigol's binary ``.wfm`` files are sadly balkanized: each program tends to support a single oscilloscope group and the available efforts are spread across a range of languages.

This project leverages a domain specific language (kaitai struct) to represent the binary files.  Once a binary file has been described in this text format, parsers can be generated for a wide range of languages (C++/STL, C#, Go, Java, JavaScript, Lua, Perl, PHP, Python, and Ruby).  


Using RigolWFM
---------------

1. You can install locally using pip::
    
    pip install --user RigolWFM

2. or `run this code in the cloud using Google Collaboratory <https://colab.research.google.com/github/scottprahl/RigolWFM/blob/master>`_ by selecting the Jupyter notebook that interests you.

3. or `analyze your files using the kaitai struct IDE <https://ide.kaitai.io>`_ (you will need to manually upload the appropriate `.ksy` file and your `.wfm` to the IDE).  This allows one to interactively reverse engineer binary file formats directly in your browser.  This is super helpful for those Rigol ``.wfm`` formats that are undocumented or not parsing correctly.

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
