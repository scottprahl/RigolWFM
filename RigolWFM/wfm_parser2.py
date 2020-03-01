#pylint: disable=missing-function-docstring
"""
Command line utility to extract signals or description
from a range of Rigol Oscilloscope waveform file.

Use like this::

    import RigolWFM.wfme as wfme

    waveform = wfme.from_file("filename.wfm", '1000E')
    for ch in waveform.channels:
        print(ch)
"""

import argparse
import RigolWFM.wfme


def main():
    parser = argparse.ArgumentParser(
        prog='wfm_parse',
        description='Parse Rigol WFM files.'
    )
    parser.add_argument(
        '-t',
        choices=('1000c', '1000e', '1000z', '4000', '6000'),
        required=True,
        help='the type of Rigol WFM file'
    )
    parser.add_argument('filename')
    args = parser.parse_args()

    waveforms = RigolWFM.wfme.Wfm.from_file(args.filename, kind=args.t)
    print(waveforms.describe())
    description = waveforms.describe()
    print(description)


if __name__ == "__main__":
    main()
