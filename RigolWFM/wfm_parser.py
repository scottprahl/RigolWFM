#!/usr/bin/env python3
#pylint: disable=missing-function-docstring
"""
Command line utility to extract signals or description
from a range of Rigol Oscilloscope waveform file.

Use like this::

    wfm_parser.py -a info -t 1000e DS1102E-A.wfm
    wfm_parser.py -a csv -t 1000e DS1102E-A.wfm
"""

import argparse
import RigolWFM.wfm

def main():
    parser = argparse.ArgumentParser(
        prog='wfm_parse',
        description='Parse Rigol WFM files.',
        formatter_class=argparse.RawTextHelpFormatter
    )

    parser.add_argument(
        '-t',
        required=True,
        help='the type of scope that created the WFM file' + RigolWFM.wfm.valid_scope_list()
    )

    parser.add_argument(
        '-a',
        dest = 'action',
        choices=['info', 'csv'],
        required=True,
        help='action to perform'
    )

    parser.add_argument('filename')
    
    args = parser.parse_args()

    try:
        model = args.t
        waveforms = RigolWFM.wfm.Wfm.from_file(args.filename, model)
        action = args.action
        if action == 'csv':
            print(waveforms.csv())
        if action == 'info':
            print(waveforms.describe())
    except Exception as e: 
        print(e)

if __name__ == "__main__":
    main()
