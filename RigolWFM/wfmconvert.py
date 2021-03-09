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
        description='Parse Rigol WFM files.',
        formatter_class=argparse.RawTextHelpFormatter,
        epilog=textwrap.dedent('''\
        examples:
            python3 wfmconvert.py E info DS1102E.wfm
            python3 wfmconvert.py E --channel 2 csv DS1102E.wfm
            python3 wfmconvert.py E --channel 12 vcsv DS1102E.wfm
            python3 wfmconvert.py E --channel '1,2,4' wav DS1102E.wfm
        ''')
    )

    parser.add_argument(
        '--force',
        action='store_true',
        help="overwrite existing output files"
    )

    parser.add_argument(
        '--autoscale',
        action='store_true',
        default=False,
        help="autoscale each channel to full range"
    )

    parser.add_argument(
        '--channel',
        type=str,
        default='1',
        help="designate channel(s) to save in .wav file"
    )

    parser.add_argument(
        'model',
        type=str,
        help='the type of scope that created the WFM file' + rigol.valid_scope_list()
    )

    parser.add_argument(
        dest='action',
        choices=['csv', 'info', 'wav', 'vcsv', 'sigrok'],
        help="Action to perform on the WFM file"
    )

    parser.add_argument(
        'infile',
        type=str,
        nargs='+',
        help="Input WFM file"
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
            print("Format does not follow a known format.", file=sys.stderr)
            print("To help development, post report this error\n", file=sys.stderr)
            print("as an issue to https://github.com/scottprahl/RigolWFM\n", file=sys.stderr)
            print(e, file=sys.stderr)
            sys.exit()

if __name__ == "__main__":
    main()
