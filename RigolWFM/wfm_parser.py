import argparse

from pprint import pprint

import wfm1000d
import wfm1000e
import wfm1000z
import wfm4000c

def main():
    parser = argparse.ArgumentParser(
        prog='wfm_parse', 
        description='Parse Rigol WFM files.'
        )
    parser.add_argument(
        '-t', 
        choices=('c','d','e','z'), 
        required=True, 
        help='the type of Rigol WFM file'
        )
    parser.add_argument('filename')
    args = parser.parse_args()
    
    if args.t == 'c':
        target = wfm4000c.Wfm4000c.from_file(args.filename)
    elif args.t == 'd':
        target = wfm1000d.Wfm1000d.from_file(args.filename)
    elif args.t == 'e':
        target = wfm1000e.Wfm1000e.from_file(args.filename)
    else:
        target = wfm1000z.Wfm1000z.from_file(args.filename)

    print("Header")
    print("----------")
    print(hex(target.header.magic[0]), hex(target.header.magic[1]))

    print("Header")
    pprint(vars(target.header))
    print()
#     print("time header")
#     pprint(vars(target.header.ch1))
#     print()
#     print("trigger header")
#     pprint(vars(target.data.ch1))


if __name__ == "__main__":
    main()

