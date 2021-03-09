#!/usr/bin/env python3

#pylint: disable=invalid-name
#pylint: disable=missing-function-docstring
#pylint: disable=unused-argument
"""
Command line utility to convert Rigol .wfm files.

Use like this::

    wfmconvert E info DS1102E-A.wfm
    wfmconvert E csv DS1102E-A.wfm
    wfmconvert E wav DS1102E-A.wfm
"""

import re
import os
import sys
import argparse
import subprocess
import textwrap

import RigolWFM.wfm as rigol

def info(args, scope_data, infile):
    """Create a string that describes content of .wfm file."""
    s = scope_data.describe()
    print(s)

def csv(args, scope_data, infile):
    """Create a file with comma separated values."""
    csv_name = os.path.splitext(infile)[0] + '.csv'

    if os.path.isfile(csv_name) and not args.force:
        print("'%s' exists, use --force to overwrite" % csv_name)
        return

    s = scope_data.csv()
    with open(csv_name, 'wb') as f:
        b = s.encode(encoding='utf-8')
        f.write(b)

def vcsv(args, scope_data, infile):
    """Create a file with comma separated values (full volts)."""
    csv_name = os.path.splitext(infile)[0] + '.csv'

    if os.path.isfile(csv_name) and not args.force:
        print("'%s' exists, use --force to overwrite" % csv_name)
        return

    s = scope_data.sigrokcsv()
    with open(csv_name, 'wb') as f:
        b = s.encode(encoding='utf-8')
        f.write(b)

def wav(args, scope_data, infile):
    """Create an audible .wav file for use in LTSpice."""
    wav_name = os.path.splitext(infile)[0] + '.wav'
    if os.path.isfile(wav_name) and not args.force:
        print("'%s' exists, use --force to overwrite" % wav_name)
        return

    scope_data.wav(wav_name, channel=args.channel)

def sigrok(args, scope_data, infile):
    """Create a Sigrok (.sr) file."""
    sigrok_name = os.path.splitext(infile)[0] + '.sr'

    if os.path.isfile(sigrok_name) and not args.force:
        print("'%s' exists, use --force to overwrite" % sigrok_name)
        return

    s = scope_data.sigrokcsv()
    # sigrok-cli reports a warning about /dev/stdin not being a regular file,
    # but the conversion works fine.
    p = subprocess.run(
        ['sigrok-cli', '-I', 'csv:start_line=2:column_formats=t,1a',
         '-i', '/dev/stdin', '-o', sigrok_name],
        input=s.encode(encoding='utf-8'),
        check=True)
    if p.returncode != 0:
        print("sigrok-cli failed")

def main():
    """Parse console command line arguments."""
    parser = argparse.ArgumentParser(
        prog='wfmconvert',
        description='Convert Rigol WFM files to another format.',
        formatter_class=argparse.RawTextHelpFormatter,
        epilog=textwrap.dedent("""\
        examples:
            wfmconvert.py E info DS1102E.wfm
            wfmconvert.py --channel 2 E csv DS1102E.wfm
            wfmconvert.py --channel 12 E vcsv DS1102E.wfm
            wfmconvert.py --channel 124 --autoscale E wav DS1102E.wfm
        """) + rigol.valid_scope_list()
    )

    parser.add_argument(
        '--force',
        action='store_true',
        default=False,
        help="overwrite existing output files"
    )

    parser.add_argument(
        '--autoscale',
        action='store_true',
        default=False,
        help=textwrap.dedent("""\
        autoscale each channel to full range.  Used when creating
        .wav files so signal goes from 0-255.
        """)
    )

    parser.add_argument(
        '--channel',
        type=str,
        default='1234',
        help=textwrap.dedent("""\
        select channel(s) to process.  `--channel 1` outputs only contents of
        the first channel.  `--channel 34` outputs contents of channels 3 and 4. 
        The default is `--channel 1234`.
        """)
    )

    parser.add_argument(
        'model',
        type=str,
        choices=['C', 'D', 'E', 'Z', '2', '4', '6'],
        help='oscilloscope model.  See list below.' 
    )

    parser.add_argument(
        dest='action',
        choices=['csv', 'info', 'wav', 'vcsv', 'sigrok'],
        help=textwrap.dedent("""\
        csv:    convert to a file with comma separated values
        info:   show the various scope settings for a .wfm file
        wav:    convert to a WAV sound format file for use with Audacity
                or Sigrok Pulseview. If a single channel is specified then
                the .wav file can be used with LTspice.
        vcsv:   convert to a file with comma separated values with raw voltages
        sigrok: convert to a sigrok file
        """)
    )

    parser.add_argument(
        'infile',
        type=str,
        nargs='+',
        help="the WFM file to be converted"
    )

    args = parser.parse_args()

    # strip anything that is not a possible channel number
    selected = re.sub(r'[^1234]', '', args.channel)

    actionMap = {"info": info, "csv": csv, "wav": wav, "vcsv": vcsv, "sigrok": sigrok}

    for filename in args.infile:
        try:
            scope_data = rigol.Wfm.from_file(filename, args.model, selected)
            actionMap[args.action](args, scope_data, filename)

        except rigol.Parse_WFM_Error as e:
            print("File contents do not follow a known format.", file=sys.stderr)
            print("To help development, please report this error\n", file=sys.stderr)
            print("as an issue to https://github.com/scottprahl/RigolWFM\n", file=sys.stderr)
            print(e, file=sys.stderr)
            sys.exit()

if __name__ == "__main__":
    main()
