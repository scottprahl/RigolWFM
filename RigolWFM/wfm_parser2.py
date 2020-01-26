import argparse
import wfme

def main():
    parser = argparse.ArgumentParser(
        prog='wfm_parse',
        description='Parse Rigol WFM files.'
    )
    parser.add_argument(
        '-t',
        choices=('4000c', '1000d', '1000e', '1000z'),
        required=True,
        help='the type of Rigol WFM file'
    )
    parser.add_argument('filename')
    args = parser.parse_args()
    
    channels = wfme.parse(args.filename, kind=args.t)
    for ch in channels:
        print(ch)


if __name__ == "__main__":
    main()
