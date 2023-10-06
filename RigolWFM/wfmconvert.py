#!/usr/bin/env python3

# pylint: disable=invalid-name
# pylint: disable=missing-function-docstring
# pylint: disable=unused-argument
# pylint: disable=consider-using-f-string

"""
Command line utility to convert Rigol .wfm files.

    Examples::

        prompt> wfmconvert E info DS1102E-A.wfm

        prompt> wfmconvert E csv DS1102E-A.wfm

        prompt> wfmconvert E wav DS1102E-A.wfm
"""

import re
import os
import sys
import shutil
import argparse
import subprocess
import textwrap

import RigolWFM
import RigolWFM.wfm


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
    """Create an audible .wav file for use in LTspice."""
    wav_name = os.path.splitext(infile)[0] + '.wav'
    if os.path.isfile(wav_name) and not args.force:
        print("'%s' exists, use --force to overwrite" % wav_name)
        return

    scope_data.wav(wav_name, autoscale=args.autoscale)


def sigrok(args, scope_data, infile):
    """Create a Sigrok (.sr) file."""
    sigrok_name = os.path.splitext(infile)[0] + '.sr'

    if os.path.isfile(sigrok_name) and not args.force:
        print(f"'{sigrok_name}' exists, use --force to overwrite", file=sys.stderr)
        return False

    s = scope_data.sigrokcsv()

    # Check if sigrok-cli is installed and accessible
    if not shutil.which("sigrok-cli"):
        print("sigrok-cli is not installed or not found in PATH.", file=sys.stderr)
        print("See https://sigrok.org/wiki/Sigrok-cli for more information.", file=sys.stderr)
        return False

    # sigrok-cli reports a warning about /dev/stdin not being a regular file,
    # but the conversion works fine.
    try:
        p = subprocess.run(
            ['sigrok-cli', '-I', 'csv:start_line=2:column_formats=t,1a',
             '-i', '/dev/stdin', '-o', sigrok_name],
            input=s,
            check=True,
            stderr=subprocess.PIPE,
            text=True)
    except subprocess.CalledProcessError as e:
        print(f"sigrok-cli failed with error: {e.stderr}", file=sys.stderr)
        print("See https://sigrok.org/wiki/Sigrok-cli for more information.", file=sys.stderr)
        return False
    except Exception as e:
        print(f"An unexpected error occurred: {e}", file=sys.stderr)
        return False

    if p.returncode != 0:
        print(f"sigrok-cli returned non-zero exit code: {p.returncode}", file=sys.stderr)
        print("See https://sigrok.org/wiki/Sigrok-cli for more information.", file=sys.stderr)
        return False

    return True

def main():
    """Parse console command line arguments."""
    parser = argparse.ArgumentParser(
        prog='wfmconvert',
        description='Convert Rigol WFM files to another format.',
        formatter_class=argparse.RawTextHelpFormatter,
        epilog=textwrap.dedent("""\
        examples:
            wfmconvert E info DS1102E.wfm
            wfmconvert --channel 2 E csv DS1102E.wfm
            wfmconvert --channel 124 E vcsv DS1102E.wfm
            wfmconvert --channel 34 --autoscale E wav DS1102E.wfm
        """) + RigolWFM.wfm.valid_scope_list()
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
        choices=['B', 'C', 'D', 'E', 'Z', '2', '4', '6'],
        help='oscilloscope model.  See list below.'
    )

    parser.add_argument(
        '--version',
        action='version',
        version='%(prog)s {version}'.format(version=RigolWFM.__version__)
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
    good = re.sub(r'[^1234]', '', args.channel)

    # remove duplicates keeping order
    selected = "".join(dict.fromkeys(good))

    if len(selected) == 0:
        print('\nwfmconvert error')
        print('No valid channels were passed after --channel')
        print('Channels are identified by number and must be a combination of 1, 2, 3, or 4')
        print('You used "--channel %s"' % args.channel)
        sys.exit()

    if len(selected) > 4:
        print('\nwfmconvert error')
        print('Only 1-2 channel (monophonic) or 3-4 channels (stereo) ', end='')
        print('can be used when creating a .wav file')
        print('You used "--channel %s"' % args.channel)
        sys.exit()

    actionMap = {"info": info, "csv": csv, "wav": wav, "vcsv": vcsv, "sigrok": sigrok}

    for filename in args.infile:
        try:
            scope_data = RigolWFM.wfm.Wfm.from_file(filename, args.model, selected)
            actionMap[args.action](args, scope_data, filename)

        except RigolWFM.wfm.Parse_WFM_Error as e:
            print("File contents do not follow the format for", end='', file=sys.stderr)
            print("for the Rigol Oscilloscope Model %s." % args.model, file=sys.stderr)
            print("To help with development, please report this error\n", file=sys.stderr)
            print("as an issue to https://github.com/scottprahl/RigolWFM\n", file=sys.stderr)
            print(e, file=sys.stderr)
            sys.exit()


if __name__ == "__main__":
    main()
