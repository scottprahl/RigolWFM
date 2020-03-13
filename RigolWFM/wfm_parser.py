#!/usr/bin/env python3
#pylint: disable=missing-function-docstring
"""
Command line utility to extract signals or description
from a range of Rigol Oscilloscope waveform file.

Use like this::

    wfm_parser.py --model 1000E info DS1102E-A.wfm
    wfm_parser.py --model 1000E csv  DS1102E-A.wfm DS1102E-A.csv
    wfm_parser.py --model 1000E wav  DS1102E-A.wfm DS1102E-A.wav

"""
import sys
import argparse
import RigolWFM.wfm as rigol
            
def info(args, scope_data, info_file_name):
    s = scope_data.describe()
    if info_file_name is None:
        print(s)
    else:
        with open(info_file_name, 'wb') as f:
            b = s.encode(encoding='utf-8')
            f.write(b)

def csv(args, scope_data, csv_file_name):
    s = scope_data.csv()
    if csv_file_name is None:
        print(s)
    else:
        with open(csv_file_name, 'wb') as f:
            b = s.encode(encoding='utf-8')
            f.write(b)

def wav(args, scope_data, outfile):
    scope_data.wav(1, outfile)

def main():

    parser = argparse.ArgumentParser(
        prog='wfm_parse',
        description='Parse Rigol WFM files.',
        formatter_class=argparse.RawTextHelpFormatter
    )

    parser.add_argument(
        '-m',
        '--model',
        type=str,
        required=True,
        help='the type of scope that created the WFM file' + rigol.valid_scope_list()
    )

    infile_parser = argparse.ArgumentParser(add_help=False)
    infile_parser.add_argument('infile', type=str, help="Input WFM file")
    infile_parser.add_argument('outfile', type=str, default=None, nargs='?', help="Output file, defaults to stdout")
#    infile_parser.add_argument('--minimal', action='store_false', help="Just scale and time")

    subparsers = parser.add_subparsers(dest='action', help="Action to perform on the WFM file")
    subparsers.required = True
    info_parser = subparsers.add_parser('info', parents=[infile_parser], help="Print information about the file")
    csv_parser = subparsers.add_parser('csv', parents=[infile_parser], help="Generate CSV representation of voltages or raw values")
#    csv_parser.add_argument('-r', '--raw', action='store_true', help='Use raw values instead of voltages')
#    csv_parser.add_argument('-t', '--notime', action='store_true', help='Do not include time in the output')
#    csv_parser.add_argument('-d', '--header', type=str, default='normal', choices=['none', 'std', 'rigol'], help='Type of header; std is a standard single-line header, rigol is a two-line header following format produced by the oscilloscope, none is no header')
    ltspice_parser = subparsers.add_parser('wav', parents=[infile_parser], help="Generate WAV file for input to ltspice")

    args = parser.parse_args()

    actionMap = {
                    "info": info,
                    "csv": csv,
                    "wav": wav,
                }

    try:
        scope_data = rigol.Wfm.from_file_name(args.infile, args.model)
        actionMap[args.action](args, scope_data, args.outfile)
        
    except rigol.Parse_WFM_Error as e:
        print("Format does not follow the known file format. Try the --forgiving option.", file=sys.stderr)
        print("If you'd like to help development, please report this error:\n", file=sys.stderr)
        print(e, file=sys.stderr)
        sys.exit()
if __name__ == "__main__":
    main()
