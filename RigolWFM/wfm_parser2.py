import argparse
import wfme

def main():
    parser = argparse.ArgumentParser(
        prog='wfm_parse',
        description='Parse Rigol WFM files.'
    )
    parser.add_argument(
        '-t',
        choices=('c', 'd', 'e', 'z'),
        required=True,
        help='the type of Rigol WFM file'
    )
    parser.add_argument('filename')
    args = parser.parse_args()
    
    channels = wfme.parse(args.filename)
    for ch in channels:
        print(ch)


if __name__ == "__main__":
    main()
