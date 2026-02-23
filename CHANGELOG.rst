Changelog
=========

Unreleased ()
------------------------
*    migrate package metadata and dependencies fully into ``pyproject.toml``
*    switch Makefile workflows to uv-based tooling and shared command wrappers
*    add consistent ``RM``/``RMR`` cleanup variables and remove hardcoded ``rm`` usage
*    update supported Python policy to 3.10 through 3.14 in package metadata and CI
*    update docs and lite dependency ranges, including ``rstcheck[toml,sphinx]``
*    add JupyterLite build/serve/deploy tooling and configuration
*    modernize Read the Docs install/runtime configuration
*    improve docs configuration and project automation/help targets
*    fix badges and default branch references

1.0.0 (2023-10-06)
------------------------
*    fix `wfmconvert --version` so there is no error
*    remove all lfs files in dist.  they're expensive

0.9.9 (2023-10-05)
------------------------
*    don't include large git lfs files!

0.9.8 (2023-10-05)
------------------------
*    no new features, just updating packaging
*    add conda-forge support
*    add zenodo DOI citation support
*    add github action workflows
*    add tests for wfmconvert
*    improve readme

v0.9.7 (2023-08-18)
------------------------
*    include DS1102D test files (Karl Palsson)
*    bump python versions to 3.8 through 3.11
*    add notebook for 1000D files
*    remove unnecessary .rst testing

v0.9.6 (2022-08-26)
------------------------
*    fix DS2072 CH2 wide memory fixes (James Pitts)
*    get html docs building under nbsphinx again

v0.9.5 (2022-03-17)
------------------------
*    use __version__ in __init__.py

v0.9.4 (2021-12-12)
------------------------
*    improve handling of 1000C files
*    add .readthedocs.yaml so docs build correctly

v0.9.3 (2021-11-24)
------------------------
*    processing of E type files is less restrictive
*    use nbsphinx 0.8.5 so docs build
*    improve docs

v0.9.2 (2021-08-06)
------------------------
*    create pure python packaging
*    include wheel file
*    package as python3 only

v0.9.1 (2021-07-28)
------------------------
*    fix for 1204B files with 0x4000 bytes

v0.9.0 (2021-07-25)
------------------------
*    support 1000B scopes
*    automate notebook testing
*    add pypi badges
*    add flake8 testing

v0.8.1 (2021-03-21)
------------------------
*    fixed swapped channels for DS1000Z files (2 channel case only)
*    advise `pip install --user RigolWFM` to avoid permission errors

v0.8.0 (2021-03-20)
------------------------
*    significantly speed parsing of large .wfm files
*    fix bug with selection of channels in DS1000Z files

v0.7.4 (2021-03-14)
------------------------
*    fix version consistency across docs and package metadata

v0.7.3 (2021-03-14)
------------------------
*    fix hyperlinks for colab in docs at https://readthedocs.io

v0.7.2 (2021-03-14)
------------------------
*    fix bug with selecting channels
*    fix bug with autoscaling
*    add links to google colaboratory to documentation
*    describe parameters for a few functions
*    modify message to install RigolWFM when missing

v0.7.1 (2021-03-09)
------------------------
*    add support for selecting channels
*    add autoscaling support for .wav files
*    improve help message for wfmconvert

v0.7.0 (2021-02-14)
------------------------
*    add basic support for DS1000CA files
*    add new model D (untested) out of the E model list

v0.6.7 (2020-10-31)
------------------------
*    add vcsv conversion (just volts, not µV or mV)
*    add support for sigrok exporting (requires sigrok-cli)

v0.6.6 (2020-10-10)
------------------------
*    use probe scaling with DS1000E files

v0.6.5 (2020-08-03)
------------------------
*    fix DS2000 to convert CSV files
*    add more testing to tox

v0.6.4 (2020-05-16)
------------------------
*    fix DS4000 to work with two channels
*    fix DS2000 to work with recent DS2072A firmware
*    add DS2072A test files to repository

v0.6.3 (2020-03-29)
------------------------
*    use sphinx for documentation
*    host docs on https://rigolwfm.readthedocs.io
*    remove unneeded files from pip installation
*    start using tox for testing

v0.6.2 (2020-03-27)
------------------------
*    trying to get console_scripts right

v0.6.1 (2020-03-27)
------------------------
*    use portable install for console_scripts

v0.6.0 (2020-03-26)
------------------------
*    add support for DS2000
*    add command-line utility wfmconvert
*    improve support for DS1000Z
*    fix DS4000
*    add .csv export
*    add .wav export

v0.4.1 (2020-03-01)
------------------------
*    fix requirement for enum by just requiring python > 3.4

v0.4.0 (2020-03-01)
------------------------
*    huge change.  Now using kaitai struct exclusively
*    added support for 1000C, 4000, 6000 .wfm formats
*    much more testing
*    many api changes.

v0.3.0 (2020-01-12)
------------------------
*    fix exception handling, support parsing URLs

v0.2.0 (2020-01-09)
------------------------
*    improve README and package long description metadata

v0.1.3 (2020-01-09)
------------------------
*    fix package classifiers

v0.1.2 (2020-01-09)
------------------------
*    fix URL and other infelicities

v0.1.1 (2020-01-09)
------------------------
*    add missing files needed for release

v0.1.0 (2020-01-09)
------------------------
*    initial commit
