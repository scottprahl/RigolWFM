#!/usr/bin/env python3

"""
Command line utility to convert oscilloscope waveform files.

    Examples::

        prompt> wfmconvert info DS1102E-A.wfm

        prompt> wfmconvert csv DS1102E-A.wfm

        prompt> wfmconvert wav DS1102E-A.wfm
"""

import re
import os
import sys
import shutil
import argparse
import subprocess
import textwrap
from typing import NoReturn

import matplotlib.pyplot as plt

import RigolWFM
import RigolWFM.wfm


def _build_model_aliases() -> dict[str, str]:
    """Return case-insensitive CLI aliases mapped to canonical model names."""
    aliases: dict[str, str] = {"AUTO": "auto"}

    rigol_families = [
        ("B", RigolWFM.wfm.DS1000B_scopes),
        ("C", RigolWFM.wfm.DS1000C_scopes),
        ("D", RigolWFM.wfm.DS1000D_scopes),
        ("E", RigolWFM.wfm.DS1000E_scopes),
        ("Z", RigolWFM.wfm.DS1000Z_scopes),
        ("2", RigolWFM.wfm.DS2000_scopes),
        ("4", RigolWFM.wfm.DS4000_scopes),
        ("5", RigolWFM.wfm.DS5000_scopes),
        ("5074", RigolWFM.wfm.MSO5074_scopes),
        ("6", RigolWFM.wfm.DS6000_scopes),
        ("7", RigolWFM.wfm.DS7000_scopes),
        ("8", RigolWFM.wfm.DS8000_scopes),
        ("DHO", RigolWFM.wfm.DHO1000_scopes),
    ]
    for canonical, family in rigol_families:
        aliases[canonical.upper()] = canonical
        for alias in family:
            aliases[str(alias).upper()] = canonical

    vendor_families = [
        ("Keysight", RigolWFM.wfm.Keysight_scopes),
        ("Siglent", RigolWFM.wfm.Siglent_scopes),
        ("SiglentOld", RigolWFM.wfm.Siglent_old_scopes),
        ("RohdeSchwarz", RigolWFM.wfm.RohdeSchwarz_scopes),
        ("LeCroy", RigolWFM.wfm.LeCroy_scopes),
        ("Tek", RigolWFM.wfm.Tek_scopes),
        ("ISF", RigolWFM.wfm.ISF_scopes),
        ("Yokogawa", RigolWFM.wfm.Yokogawa_scopes),
    ]
    for canonical, family in vendor_families:
        aliases[canonical.upper()] = canonical
        for alias in family:
            aliases[str(alias).upper()] = canonical

    return aliases


_MODEL_ALIASES = _build_model_aliases()
_CANONICAL_MODELS = [
    "auto",
    "B",
    "C",
    "D",
    "E",
    "Z",
    "2",
    "4",
    "5",
    "5074",
    "6",
    "7",
    "8",
    "DHO",
    "Keysight",
    "Siglent",
    "SiglentOld",
    "RohdeSchwarz",
    "LeCroy",
    "Tek",
    "ISF",
    "Yokogawa",
]


def _normalize_model_choice(value: str) -> str:
    """Return a canonical CLI model string or raise argparse.ArgumentTypeError."""
    canonical = _MODEL_ALIASES.get(value.upper())
    if canonical is None:
        raise argparse.ArgumentTypeError(
            "unsupported model '{}'; choose one of {} or any alias listed below".format(
                value, ", ".join(_CANONICAL_MODELS)
            )
        )
    return canonical


def _output_path(infile: str, ext: str, output_dir: str) -> str:
    """Return output path: basename of infile with ext replaced, in output_dir."""
    stem = os.path.splitext(os.path.basename(infile))[0]
    return os.path.join(output_dir, stem + ext)


def info(_args: argparse.Namespace, scope_data: RigolWFM.wfm.Wfm, _infile: str) -> None:
    """Print a text summary describing a waveform file."""
    s = scope_data.describe()
    print(s)


def csv(args: argparse.Namespace, scope_data: RigolWFM.wfm.Wfm, infile: str) -> None:
    """Create a file with comma separated values."""
    csv_name = _output_path(infile, ".csv", args.output_dir)

    if os.path.isfile(csv_name) and not args.force:
        print(f"'{csv_name}' exists, use --force to overwrite")
        return

    s = scope_data.csv()
    with open(csv_name, "wb") as f:
        b = s.encode(encoding="utf-8")
        f.write(b)


def vcsv(args: argparse.Namespace, scope_data: RigolWFM.wfm.Wfm, infile: str) -> None:
    """Create a file with comma separated values (full volts)."""
    csv_name = _output_path(infile, ".csv", args.output_dir)

    if os.path.isfile(csv_name) and not args.force:
        print(f"'{csv_name}' exists, use --force to overwrite")
        return

    s = scope_data.sigrokcsv()
    with open(csv_name, "wb") as f:
        b = s.encode(encoding="utf-8")
        f.write(b)


def wav(args: argparse.Namespace, scope_data: RigolWFM.wfm.Wfm, infile: str) -> None:
    """Create an audible .wav file for use in LTspice."""
    wav_name = _output_path(infile, ".wav", args.output_dir)
    if os.path.isfile(wav_name) and not args.force:
        print(f"'{wav_name}' exists, use --force to overwrite")
        return

    channel_digits = [int(c) for c in args.channel]
    if len(channel_digits) > 2:
        print(
            f"wfmconvert error: wav supports at most 2 channels; got --channel {args.channel}.\n"
            "Use --channel 1 for mono or --channel 12 for stereo.",
            file=sys.stderr,
        )
        sys.exit(1)
    channel: int | list[int] = channel_digits[0] if len(channel_digits) == 1 else channel_digits
    try:
        scope_data.wav(wav_name, channel=channel, scale=args.scale)
    except ValueError as e:
        print(f"wfmconvert error: {e}", file=sys.stderr)
        sys.exit(1)


def png(args: argparse.Namespace, scope_data: RigolWFM.wfm.Wfm, infile: str) -> None:
    """Save a PNG plot of the waveform."""
    png_name = _output_path(infile, ".png", args.output_dir)
    if os.path.isfile(png_name) and not args.force:
        print(f"'{png_name}' exists, use --force to overwrite")
        return
    fig = scope_data.plot()
    fig.savefig(png_name, dpi=args.dpi, bbox_inches="tight", facecolor="black")
    plt.close(fig)


def sigrok(args: argparse.Namespace, scope_data: RigolWFM.wfm.Wfm, infile: str) -> bool:
    """Create a Sigrok (.sr) file."""
    sigrok_name = _output_path(infile, ".sr", args.output_dir)

    if os.path.isfile(sigrok_name) and not args.force:
        print(f"'{sigrok_name}' exists, use --force to overwrite", file=sys.stderr)
        return False

    s = scope_data.sigrokcsv()

    # Check if sigrok-cli is installed and accessible
    if not shutil.which("sigrok-cli"):
        print("sigrok-cli is not installed or not found in PATH.", file=sys.stderr)
        print(
            "See https://sigrok.org/wiki/Sigrok-cli for more information.",
            file=sys.stderr,
        )
        return False

    # sigrok-cli reports a warning about /dev/stdin not being a regular file,
    # but the conversion works fine.
    try:
        p = subprocess.run(
            [
                "sigrok-cli",
                "-I",
                "csv:start_line=2:column_formats=t,1a",
                "-i",
                "/dev/stdin",
                "-o",
                sigrok_name,
            ],
            input=s,
            check=True,
            stderr=subprocess.PIPE,
            text=True,
        )
    except subprocess.CalledProcessError as e:
        print(f"sigrok-cli failed with error: {e.stderr}", file=sys.stderr)
        print(
            "See https://sigrok.org/wiki/Sigrok-cli for more information.",
            file=sys.stderr,
        )
        return False
    except Exception as e:
        print(f"An unexpected error occurred: {e}", file=sys.stderr)
        return False

    if p.returncode != 0:
        print(f"sigrok-cli returned non-zero exit code: {p.returncode}", file=sys.stderr)
        print(
            "See https://sigrok.org/wiki/Sigrok-cli for more information.",
            file=sys.stderr,
        )
        return False

    return True


class _WfmParser(argparse.ArgumentParser):
    """ArgumentParser that gives a friendlier error when the action verb is omitted."""

    def error(self, message: str) -> NoReturn:
        if "argument action: invalid choice" in message:
            self.exit(
                2,
                (
                    "wfmconvert error: missing action verb.\n"
                    "Example: wfmconvert info DS1102E.wfm\n"
                    "Run 'wfmconvert --help' for more information.\n"
                ),
            )
        super().error(message)


def main() -> None:
    """Parse console command line arguments."""
    parser = _WfmParser(
        prog="wfmconvert",
        description="Convert oscilloscope waveform files to another format.",
        formatter_class=argparse.RawTextHelpFormatter,
        epilog=textwrap.dedent("""\
        examples:
            wfmconvert info DS1102E.wfm
            wfmconvert csv DS1102E.wfm
            wfmconvert png DS1102E.wfm
            wfmconvert --output-dir /tmp csv *.wfm
            wfmconvert --channel 2 csv DS1102E.wfm
            wfmconvert --channel 124 vcsv DS1102E.wfm
            wfmconvert --channel 3 --scale scope wav DS1102E.wfm
            wfmconvert --channel 12 wav DS1102E.wfm
            wfmconvert --model C info DS1042C-A.wfm
        """) + RigolWFM.wfm.valid_scope_list(),
    )

    parser.add_argument(
        "--model",
        type=_normalize_model_choice,
        default="auto",
        metavar="MODEL",
        help=(
            "oscilloscope model family (default: auto-detect from file). "
            "Canonical values include {}. Aliases listed below are also accepted."
        ).format(", ".join(_CANONICAL_MODELS)),
    )

    parser.add_argument(
        "--output-dir",
        metavar="DIR",
        default=".",
        help="directory for output files (default: current working directory)",
    )

    parser.add_argument(
        "--force",
        action="store_true",
        default=False,
        help="overwrite existing output files",
    )

    parser.add_argument(
        "--dpi",
        type=int,
        default=300,
        help="resolution in dots per inch for PNG output (default: 300)",
    )

    parser.add_argument(
        "--scale",
        choices=["auto", "scope"],
        default="auto",
        help=textwrap.dedent("""\
        voltage scaling for WAV output (default: auto).
          auto:  signal min/max → ±32767.  Waveform shape is preserved;
                 set Vpeak on the LTspice WAV source to the actual peak voltage.
          scope: scope ±(4×V/div) range → ±32767.  Zero volts stays at zero;
                 set Vpeak = 4×V/div in LTspice.
        """),
    )

    parser.add_argument(
        "--channel",
        type=str,
        default="1234",
        help=textwrap.dedent("""\
        select channel(s) to process.  `--channel 1` outputs only contents of
        the first channel.  `--channel 34` outputs contents of channels 3 and 4.
        The default is `--channel 1234`.
        """),
    )

    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s {version}".format(version=RigolWFM.__version__),
    )

    parser.add_argument(
        dest="action",
        choices=["csv", "info", "png", "wav", "vcsv", "sigrok"],
        help=textwrap.dedent("""\
        csv:    convert to a file with comma separated values
        info:   show the various scope settings for a waveform file
        png:    save a waveform plot as a PNG image (use --dpi to set resolution)
        wav:    convert to a WAV sound format file for use with Audacity
                or Sigrok Pulseview. If a single channel is specified then
                the .wav file can be used with LTspice.
        vcsv:   convert to a file with comma separated values with raw voltages
        sigrok: convert to a sigrok file
        """),
    )

    parser.add_argument("infile", type=str, nargs="+", help="the waveform file(s) to be converted")

    args = parser.parse_args()

    if not os.path.isdir(args.output_dir):
        print(f"wfmconvert error: output directory '{args.output_dir}' does not exist", file=sys.stderr)
        sys.exit(1)

    # strip anything that is not a possible channel number
    good = re.sub(r"[^1234]", "", args.channel)

    # remove duplicates keeping order
    selected = "".join(dict.fromkeys(good))

    if len(selected) == 0:
        print("\nwfmconvert error")
        print("No valid channels were passed after --channel")
        print("Channels are identified by number and must be a combination of 1, 2, 3, or 4")
        print(f'You used "--channel {args.channel}"')
        sys.exit(1)

    actionMap = {"info": info, "csv": csv, "png": png, "wav": wav, "vcsv": vcsv, "sigrok": sigrok}

    for filename in args.infile:
        try:
            model = args.model
            if model == "auto":
                model = RigolWFM.wfm.detect_model(filename)
                print(f"Detected model: {model}", file=sys.stderr)

            scope_data = RigolWFM.wfm.Wfm.from_file(filename, model, selected)
            result = actionMap[args.action](args, scope_data, filename)
            if result is False:
                sys.exit(1)

        except FileNotFoundError:
            print(f"wfmconvert error: file not found: '{filename}'", file=sys.stderr)
            sys.exit(1)

        except RigolWFM.wfm.Read_WFM_Error as e:
            if isinstance(e.__cause__, FileNotFoundError):
                print(f"wfmconvert error: file not found: '{filename}'", file=sys.stderr)
            else:
                print(f"wfmconvert error: could not read '{filename}': {e}", file=sys.stderr)
            sys.exit(1)

        except RigolWFM.wfm.Unknown_Scope_Error as e:
            print(e, file=sys.stderr)
            sys.exit(1)

        except (RigolWFM.wfm.Parse_WFM_Error, ValueError) as e:
            if args.model == "auto":
                print(f"Could not detect or parse the scope model for '{filename}'.", file=sys.stderr)
            else:
                print(
                    f"File contents do not follow the selected oscilloscope model format '{args.model}'.",
                    file=sys.stderr,
                )
            print("To help with development, please report this error", file=sys.stderr)
            print("as an issue to https://github.com/scottprahl/RigolWFM\n", file=sys.stderr)
            print(e, file=sys.stderr)
            sys.exit(1)


if __name__ == "__main__":
    main()
