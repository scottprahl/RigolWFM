Tektronix WFM sample files
==========================

These ``.wfm`` captures are copied unmodified from the Tektronix
``tm_data_types`` repository, where they serve as that project's own test
waveforms:

    https://github.com/tektronix/tm_data_types/tree/main/tests/waveforms

They are the only real (instrument-written) Tektronix ``.wfm`` files in this
test suite; every other Tektronix fixture is synthesised by
``tests/test_tek.py``.  All are ``WFM#003`` little-endian files and all begin
with the ``:`` that ``RigolWFM`` failed to expect before this directory was
added.  ``FF5MhzX100From5Series.wfm`` comes from the ``fastframe``
subdirectory upstream and holds 100 frames.

``tm_data_types`` is distributed under the Apache License, Version 2.0:

    Copyright Tektronix, Inc.

    Licensed under the Apache License, Version 2.0 (the "License"); you may not
    use these files except in compliance with the License.  You may obtain a
    copy of the License at

        http://www.apache.org/licenses/LICENSE-2.0

Expected values used by ``tests/test_tek.py`` were produced by reading these
same files with the ``tm_data_types`` library, so the tests compare this parser
against the vendor's own interpretation rather than against itself.
