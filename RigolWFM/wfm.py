"""
Parse and convert oscilloscope waveform files.

Supports Rigol (DS1000B/C/D/E/Z, DS2000, DS4000, DS6000, MSO5000, MSO5074,
MSO7000/8000, DHO800/DHO1000), Agilent / Keysight (`AGxx` `.bin`), Siglent
(`.bin` waveform revisions), Rohde & Schwarz RTP (`.bin` + `.Wfm.bin`),
Teledyne LeCroy (.trc), Tektronix (.wfm/.isf), and Yokogawa (.wfm) scope
families via ``Wfm.from_file()``.

Example:
    >>> import RigolWFM.wfm as wfm
    >>> waveform = wfm.Wfm.from_file("file_name.wfm")
    >>> description = waveform.describe()
    >>> print(description)

"""

from __future__ import annotations

import os
import os.path
import struct
import sys
import tempfile
import urllib.parse
import wave
from typing import IO, TYPE_CHECKING, Any, Literal

import matplotlib.pyplot as plt
import numpy as np
import numpy.typing as npt
import requests  # type: ignore[import-untyped]

import RigolWFM.channel
import RigolWFM.agilent
import RigolWFM.isf
import RigolWFM.lecroy
import RigolWFM.rohde_schwarz
import RigolWFM.rigol
import RigolWFM.siglent
import RigolWFM.tek
import RigolWFM.yokogawa
import RigolWFM.yokogawa_hdr

if TYPE_CHECKING:
    from matplotlib.figure import Figure

# ---------------------------------------------------------------------------
# Non-Rigol vendor scope-family model-string lists
# ---------------------------------------------------------------------------

# Agilent / Keysight `AGxx` .bin files
Keysight_scopes: list[str] = [
    "Keysight",
    "KEYSIGHT",
    "keysight",
    "Agilent",
    "AGILENT",
    "agilent",
    "agilent_bin",
]

# Siglent `.bin` waveform files
Siglent_scopes: list[str] = [
    "Siglent",
    "SIGLENT",
    "siglent",
    "siglent_bin",
]

Siglent_old_scopes: list[str] = [
    "SiglentOld",
    "SIGLENTOLD",
    "siglentold",
]

# Rohde & Schwarz RTP oscilloscope exports (`.bin` metadata + `.Wfm.bin` payload)
RohdeSchwarz_scopes: list[str] = [
    "RohdeSchwarz",
    "ROHDESCHWARZ",
    "rohdeschwarz",
    "Rohde",
    "ROHDE",
    "rohde",
    "R&S",
    "r&s",
    "rohde_schwarz_bin",
]

# Teledyne LeCroy .trc files (LECROY_1_0 / LECROY_2_3 format)
LeCroy_scopes: list[str] = ["LeCroy", "LECROY", "lecroy", "trc"]

# Tektronix .wfm files (WFM#001 / WFM#002 / WFM#003 formats)
Tek_scopes: list[str] = ["Tek", "TEK", "tektronix", "Tektronix", "tek_wfm"]

# Tektronix .isf files (ISF Internal Save Format)
ISF_scopes: list[str] = ["ISF", "isf", "tek_isf", "TEK_ISF"]

# Yokogawa ASCII-header .wfm files
Yokogawa_scopes: list[str] = ["Yokogawa", "YOKOGAWA", "yokogawa", "yoko", "yokogawa_wfm"]

# Yokogawa two-file .hdr + .wvf pairs
Yokogawa_wvf_scopes: list[str] = ["yokogawa_wvf", "yokogawa_hdr", "Yokogawa_WVF", "YOKOGAWA_WVF"]

_GENERIC_VENDOR_MODELS = {
    *(name.upper() for name in Keysight_scopes),
    *(name.upper() for name in Siglent_scopes),
    *(name.upper() for name in Siglent_old_scopes),
    *(name.upper() for name in RohdeSchwarz_scopes),
    *(name.upper() for name in LeCroy_scopes),
    *(name.upper() for name in Tek_scopes),
    *(name.upper() for name in ISF_scopes),
    *(name.upper() for name in Yokogawa_scopes),
    *(name.upper() for name in Yokogawa_wvf_scopes),
}

# Re-export Rigol scope lists so existing callers that reference e.g.
# ``wfm.DS1000E_scopes`` continue to work without change.
DS1000B_scopes = RigolWFM.rigol.DS1000B_scopes
DS1000C_scopes = RigolWFM.rigol.DS1000C_scopes
DS1000D_scopes = RigolWFM.rigol.DS1000D_scopes
DS1000E_scopes = RigolWFM.rigol.DS1000E_scopes
DS1000Z_scopes = RigolWFM.rigol.DS1000Z_scopes
DS2000_scopes = RigolWFM.rigol.DS2000_scopes
DS4000_scopes = RigolWFM.rigol.DS4000_scopes
DS6000_scopes = RigolWFM.rigol.DS6000_scopes
DS5000_scopes = RigolWFM.rigol.DS5000_scopes
MSO5074_scopes = RigolWFM.rigol.MSO5074_scopes
DS7000_scopes = RigolWFM.rigol.DS7000_scopes
DS8000_scopes = RigolWFM.rigol.DS8000_scopes
DHO1000_scopes = RigolWFM.rigol.DHO1000_scopes

# Re-export Rigol trigger constants so existing callers continue to work.
_DS2000_SOURCE_NAMES = RigolWFM.rigol._DS2000_SOURCE_NAMES  # pylint: disable=protected-access

_LECROY_MAGIC = b"WAVEDESC"
_TEK_MAGIC = b"WFM#"
_ISF_MAGIC = b":CURV"  # matches both ":CURV #" and ":CURVE #"

_CANONICAL_PARSER_NAMES = {
    "rigol_1000b_wfm": "wfm1000b",
    "rigol_1000c_wfm": "wfm1000c",
    "rigol_1000e_wfm": "wfm1000e",
    "rigol_1000z_wfm": "wfm1000z",
    "rigol_2000_wfm": "wfm2000",
    "rigol_4000_wfm": "wfm4000",
    "rigol_6000_wfm": "wfm6000",
    "rigol_mso5000_bin": "bin5000",
    "rigol_7000_8000_bin": "bin7000_8000",
}


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------


class Read_WFM_Error(Exception):
    """Generic Read Error."""


class Parse_WFM_Error(Exception):
    """Generic Parse Error."""


class Invalid_URL(Exception):
    """URL scheme is not http or https."""


class Unknown_Scope_Error(Exception):
    """Not one of the listed oscilloscope models."""


class Write_WAV_Error(Exception):
    """Something went wrong while writing the .wave file."""


class Channel_Not_In_WFM_Error(Exception):
    """The channel is not in the .wfm file."""


# ---------------------------------------------------------------------------
# Autodetect and utility functions
# ---------------------------------------------------------------------------


def detect_model(filename: str) -> str:
    """Detect the oscilloscope model from a waveform file's binary signature.

    Reads a small prefix of the file and uses magic bytes, file size, and
    embedded model strings to identify the scope family.

    Returns a short model string (e.g. ``"E"``, ``"Z"``, ``"5074"``) suitable
    for passing to :meth:`Wfm.from_file`.

    Raises:
        FileNotFoundError: if the file cannot be opened.
        Parse_WFM_Error: if the signature is not recognised.
    """
    try:
        fsize = os.path.getsize(filename)
        with open(filename, "rb") as f:
            hdr = f.read(8192)
    except OSError as exc:
        raise FileNotFoundError(filename) from exc

    return _detect_model_from_header(hdr, fsize, filename)


def _detect_model_from_header(hdr: bytes, fsize: int, filename_hint: str = "") -> str:
    """Detect the oscilloscope model from a file header and filename hint."""
    basename_hint = os.path.basename(filename_hint)
    suffix = os.path.splitext(basename_hint)[1].lower()
    allow_bin_like = suffix in ("", ".bin")
    allow_wfm_like = suffix in ("", ".wfm")
    display_name = filename_hint or "<buffer>"

    if len(hdr) < 4:
        raise Parse_WFM_Error(f"File too short to detect model: {display_name}")

    magic4 = hdr[:4]

    # DS1000B: a5 a5 a4 01
    if magic4 == bytes([0xA5, 0xA5, 0xA4, 0x01]):
        return "B"

    # DS1000C: first byte 0xA1, bytes 1-3 = a5 00 00
    if magic4 == bytes([0xA1, 0xA5, 0x00, 0x00]):
        return "C"

    # DS1000Z (and MSO1000Z): 01 ff ff ff
    if magic4 == bytes([0x01, 0xFF, 0xFF, 0xFF]):
        return "Z"

    # DHO proprietary .wfm: 02 00 00 00
    if magic4 == bytes([0x02, 0x00, 0x00, 0x00]) and allow_wfm_like:
        return "DHO"

    # DHO .bin export: RG03
    if hdr[:4] == b"RG03":
        return "DHO"

    # Agilent / Keysight `.bin`: AG01 / AG03 / AG10
    if hdr[:2] == b"AG":
        try:
            version = int(hdr[2:4].decode("ascii"))
        except ValueError:
            version = -1
        if version in (1, 3, 10):
            return "Keysight"

    # Siglent `.bin`: documented old platform and V0.1-V6 waveform families
    if allow_bin_like:
        try:
            siglent_revision = RigolWFM.siglent.detect_revision_from_bytes(hdr, fsize)
        except ValueError:
            siglent_revision = ""
        if siglent_revision:
            return "SiglentOld" if siglent_revision == "old" else "Siglent"

    # Rohde & Schwarz RTP exports: XML `.bin` metadata with companion `.Wfm.bin` payload
    if allow_bin_like and hdr.startswith(b"<?xml") and b"<Database" in hdr and b'SaveItemType="Data"' in hdr:
        return "RohdeSchwarz"

    # RG01: MSO5000, MSO5074, MSO7000, MSO8000
    if hdr[:4] == b"RG01":
        if len(hdr) >= 16:
            wfm_hdr_size = struct.unpack("<I", hdr[12:16])[0]
            if wfm_hdr_size == 144:
                return "5074"
            if wfm_hdr_size == 128:
                # MSO7000 vs MSO8000: read frame_string at file offset 100
                # (12-byte file header + 88 bytes into waveform header)
                try:
                    frame = hdr[100:124].split(b"\x00")[0].decode("ascii")
                    if frame.upper().startswith("MSO8") or frame.upper().startswith("DS8"):
                        return "8"
                except Exception:
                    pass
                return "7"
        return "5"

    # DS2000/4000/6000: a5 a5 38 00, model string at offset 4
    if magic4 == bytes([0xA5, 0xA5, 0x38, 0x00]):
        try:
            model_str = hdr[4:24].split(b"\x00")[0].decode("ascii")
            if model_str.startswith("DS4") or model_str.startswith("MSO4"):
                return "4"
            if model_str.startswith("DS6") or model_str.startswith("MSO6"):
                return "6"
        except Exception:
            pass
        return "2"

    # DS1000C/D/E: a5 a5 00 00
    # Distinguish by comparing file size to expected data offsets.
    # DS1000D uses the wfm1000e parser (data at 276), so genuine D files match
    # the E formula.  The 272-byte formula arises only for DS1000C files whose
    # first byte is 0xA5 instead of the usual 0xA1: those files include a
    # 16-byte padding block before the samples (256 + 16 + n*pts = 272 + n*pts).
    if magic4 == bytes([0xA5, 0xA5, 0x00, 0x00]):
        try:
            pts = struct.unpack("<I", hdr[28:32])[0]
            ch1_en = bool(hdr[49])
            ch2_en = bool(hdr[73])
            n_ch = int(ch1_en) + int(ch2_en)
            if pts > 0 and n_ch > 0:
                if fsize == 256 + n_ch * pts:
                    return "C"
                if fsize == 272 + n_ch * pts:
                    return "C"
                if fsize == 276 + n_ch * pts:
                    return "E"
        except Exception:
            pass
        return "E"  # most common default for this magic

    # Yokogawa single-file .wfm: ASCII header with NR_PT/XIN/YMU/YOF fields
    if all(token in hdr for token in (b"NR_PT:", b"PT_O:", b"XIN:", b"YMU:", b"YOF:", b"BYT:")):
        return "Yokogawa"

    # Yokogawa two-file .hdr + .wvf: ASCII text with $PublicInfo section
    if b"$PublicInfo" in hdr:
        return "yokogawa_wvf"

    # Tektronix legacy .wfm: "LLWFM" marker in the opening bytes
    if b"LLWFM" in hdr[:8]:
        return "Tek"

    # Tektronix .wfm: byte_order word at 0 (0x0F0F LE or 0xF0F0 BE), version "WFM#" at offset 2
    if hdr[0] in (0x0F, 0xF0) and hdr[1] in (0x0F, 0xF0) and hdr[2:6] == _TEK_MAGIC:
        return "Tek"

    # Tektronix .isf: ASCII header containing ":CURV " or ":CURVE " followed by '#'
    if _ISF_MAGIC in hdr:
        return "ISF"

    # LeCroy .trc: "WAVEDESC" marker at byte 0, or after a SCPI / transport prefix
    if _LECROY_MAGIC in hdr:
        return "LeCroy"

    raise Parse_WFM_Error(f"Unrecognised file signature {magic4.hex()} in {display_name}")


def _model_in_family(model: str, family: list[str]) -> bool:
    """Return True when model matches one of the aliases in family."""
    upper = model.upper()
    return any(upper == alias.upper() for alias in family)


def _default_download_suffix(model: str, header: bytes) -> str:
    """Return a usable file suffix for a downloaded waveform."""
    if _model_in_family(model, Keysight_scopes):
        return ".bin"
    if _model_in_family(model, Siglent_scopes) or _model_in_family(model, Siglent_old_scopes):
        return ".bin"
    if _model_in_family(model, RohdeSchwarz_scopes):
        return ".bin"
    if _model_in_family(model, LeCroy_scopes):
        return ".trc"
    if _model_in_family(model, ISF_scopes):
        return ".isf"
    if _model_in_family(model, Tek_scopes):
        return ".wfm"
    if _model_in_family(model, Yokogawa_scopes):
        return ".wfm"
    if _model_in_family(model, DHO1000_scopes):
        return ".bin" if header.startswith(b"RG03") else ".wfm"
    if (
        _model_in_family(model, DS5000_scopes)
        or _model_in_family(model, MSO5074_scopes)
        or _model_in_family(model, DS7000_scopes)
        or _model_in_family(model, DS8000_scopes)
    ):
        return ".bin"
    return ".wfm"


def _rohde_schwarz_payload_url(url: str) -> str:
    """Return the companion `.Wfm.bin` URL for an RTP metadata URL."""
    parsed = urllib.parse.urlparse(url)
    path = parsed.path
    if path.lower().endswith(".wfm.bin") or not path.lower().endswith(".bin"):
        raise Parse_WFM_Error(f"Cannot derive a Rohde & Schwarz companion payload URL from '{url}'")
    return parsed._replace(path=path[:-4] + ".Wfm.bin").geturl()


def valid_scope_list() -> str:
    """List all supported oscilloscope model strings."""
    s = "\nRigol oscilloscope models:\n    "
    s += "\n    ".join(", ".join(family) for family in RigolWFM.rigol.ALL_RIGOL_SCOPES)
    s += "\n    "
    s += ", ".join(Keysight_scopes) + "\n    "
    s += ", ".join(Siglent_scopes) + "\n    "
    s += ", ".join(Siglent_old_scopes) + "\n    "
    s += ", ".join(RohdeSchwarz_scopes) + "\n    "
    s += ", ".join(LeCroy_scopes) + "\n    "
    s += ", ".join(Tek_scopes) + "\n    "
    s += ", ".join(ISF_scopes) + "\n"
    s += "    " + ", ".join(Yokogawa_scopes) + "\n"
    s += "    " + ", ".join(Yokogawa_wvf_scopes) + "\n"
    return s


def _scope_family(name: str) -> str:
    """Return the alphabetic prefix of a scope name (e.g. 'MSO' from 'MSO5074').

    Used to detect obvious model mismatches between user-supplied model codes
    and the model string embedded in the file.  Single-character aliases (B, C,
    D, E, Z) and purely-numeric codes ('2', '5074') are intentionally short and
    can never be compared reliably, so callers should skip the warning when
    len(_scope_family(umodel)) <= 1.
    """
    head = name.upper().split("(", 1)[0].strip()
    head = head.split(None, 1)[0] if head else ""
    return "".join(c for c in head if c.isalpha())


# Backward-compatible convenience wrapper
def dho_from_file(file_name: str) -> Any:
    """Backward-compatible wrapper around `RigolWFM.dho.from_file()`."""
    return RigolWFM.rigol.dho_from_file(file_name)


# ---------------------------------------------------------------------------
# Main Wfm class
# ---------------------------------------------------------------------------


class Wfm:
    """Class with parsed data from a waveform file."""

    channels: list[RigolWFM.channel.Channel]
    original_name: str
    file_name: str
    basename: str
    firmware: str
    user_name: str
    parser_name: str
    header_name: str
    serial_number: str

    def __init__(self, file_name: str) -> None:
        """Initialize a Wfm object from a file."""
        self.channels = []
        self.original_name = file_name
        self.file_name = file_name
        self.basename = file_name
        self.firmware = "unknown"

        # there are multiple possible scope names
        # 1. user_name   - the name passed to the program
        # 2. header_name - the name found in the header of the file
        # 3. parser_name - the name of parser used
        self.user_name = "unknown"
        self.parser_name = "unknown"
        self.header_name = "unknown"
        self.serial_number = ""
        self.trigger_info: dict = {}

    @classmethod
    def from_file(cls, file_name: str, model: str = "auto", selected: str = "1234") -> Wfm:
        """
        Create Wfm object from a file.

        Args:
            file_name: name of file
            model: oscilloscope family, e.g. 'E', 'Z', 'LeCroy', 'Tek'; defaults to auto-detect
            selected: string of channels to process e.g., '12'
        Returns:
            a Wfm object for the file
        """
        try:
            with open(file_name, "rb"):
                pass
        except OSError as e:
            raise Read_WFM_Error(e) from e

        new_wfm = cls(file_name)
        new_wfm.original_name = file_name
        new_wfm.file_name = file_name
        new_wfm.basename = os.path.basename(file_name)

        auto_model = model.upper() == "AUTO"
        umodel = detect_model(file_name).upper() if auto_model else model.upper()

        # --- Rigol families ---
        rigol_result = RigolWFM.rigol.parse_file(umodel, file_name)
        if rigol_result is not None:
            w, new_wfm.header_name, new_wfm.serial_number, new_wfm.trigger_info = rigol_result

        # --- Agilent / Keysight `.bin` ---
        elif _model_in_family(umodel, Keysight_scopes):
            w = RigolWFM.agilent.from_file(file_name)
            new_wfm.header_name = w.header.model or "Keysight"
            new_wfm.serial_number = w.header.serial_number

        # --- Siglent `.bin` waveform files ---
        elif _model_in_family(umodel, Siglent_scopes) or _model_in_family(umodel, Siglent_old_scopes):
            w = RigolWFM.siglent.from_file(file_name, umodel)
            new_wfm.header_name = w.header.model or "Siglent"
            new_wfm.serial_number = getattr(w.header, "serial_number", "")

        # --- Rohde & Schwarz RTP `.bin` metadata files ---
        elif _model_in_family(umodel, RohdeSchwarz_scopes):
            w = RigolWFM.rohde_schwarz.from_file(file_name)
            new_wfm.header_name = w.header.model or "Rohde & Schwarz"
            new_wfm.serial_number = getattr(w.header, "serial_number", "")

        # --- LeCroy ---
        elif _model_in_family(umodel, LeCroy_scopes):
            w = RigolWFM.lecroy.from_file(file_name)
            new_wfm.header_name = w.header.model_number or "LeCroy"

        # --- Tektronix .wfm ---
        elif _model_in_family(umodel, Tek_scopes):
            w = RigolWFM.tek.from_file(file_name)
            new_wfm.header_name = w.header.model or "Tektronix"

        # --- Tektronix .isf ---
        elif _model_in_family(umodel, ISF_scopes):
            w = RigolWFM.isf.from_file(file_name)
            new_wfm.header_name = w.header.model or "Tektronix ISF"

        # --- Yokogawa .wfm ---
        elif _model_in_family(umodel, Yokogawa_scopes):
            w = RigolWFM.yokogawa.from_file(file_name)
            new_wfm.header_name = w.header.model or "Yokogawa"

        # --- Yokogawa .hdr + .wvf ---
        elif _model_in_family(umodel, Yokogawa_wvf_scopes):
            w = RigolWFM.yokogawa_hdr.from_hdr_file(file_name)
            new_wfm.header_name = w.header.model or "Yokogawa"

        else:
            raise Unknown_Scope_Error(f"Unknown oscilloscope type: '{umodel}'\n{valid_scope_list()}")

        new_wfm.user_name = "auto" if auto_model else model
        pname = getattr(w, "parser_name", type(w).__module__.rsplit(".", 1)[-1])
        pname = _CANONICAL_PARSER_NAMES.get(pname, pname)
        new_wfm.parser_name = pname

        # Warn when the model embedded in the file clearly disagrees with the
        # user-supplied model.  Single-character aliases (B, C, D, E, Z) and
        # purely-numeric codes ('2', '5074') are intentionally short and cannot
        # be compared reliably, so skip the check for them.
        file_family = _scope_family(new_wfm.header_name)
        user_family = "" if auto_model else _scope_family(umodel)
        if (
            file_family
            and len(user_family) > 1
            and umodel not in _GENERIC_VENDOR_MODELS
            and file_family not in user_family
            and user_family not in file_family
        ):
            print(
                f"Warning: file reports model '{new_wfm.header_name}' " f"but scope type '{model}' was specified.",
                file=sys.stderr,
            )

        enabled = ""
        for ch_number in range(1, 5):
            ch = RigolWFM.channel.Channel(w, ch_number, pname, selected)

            if not ch.enabled:
                continue

            enabled += str(ch_number)
            new_wfm.channels.append(ch)

        if len(new_wfm.channels) == 0:
            print("Sorry! No channels in the waveform are both selected and enabled", file=sys.stderr)
            print(f"    User selected channels = '{selected}'", file=sys.stderr)
            print(f"    Scope enabled channels = '{enabled}'", file=sys.stderr)
            print(file=sys.stderr)
        else:
            new_wfm.firmware = new_wfm.channels[0].firmware

        return new_wfm

    @classmethod
    def from_url(cls, url: str, model: str = "auto", selected: str = "1234") -> Wfm:
        """
        Return a waveform object given a URL.

        This is a bit complicated because the parser must have a local file
        to work with.  The process is to download the file to a temporary
        location and then process that file.  There is a lot that can go
        wrong - bad url, bad download, or an error parsing the file.

        Args:
            url: location of the file
            model: oscilloscope family, e.g. 'E' or 'Z'; defaults to auto-detect
            selected: string of channels to process e.g., '12'
        Returns:
            a Wfm object for the file
        """
        u = urllib.parse.urlparse(url)
        scheme = u[0]

        if scheme not in ["http", "https"]:
            raise Invalid_URL(f"URL scheme must be 'http' or 'https', got '{scheme}': {url}")

        try:
            print(f"downloading '{url}'", file=sys.stderr)
            r = requests.get(url, allow_redirects=True, timeout=10)
            r.raise_for_status()
            payload = r.content
            path = urllib.parse.unquote(u.path)
            basename = os.path.basename(path)
            auto_model = model.upper() == "AUTO"
            resolved_model = (
                _detect_model_from_header(payload[:8192], len(payload), basename or path or url)
                if auto_model
                else model
            )

            if not basename:
                basename = "downloaded_waveform"
            if not os.path.splitext(basename)[1]:
                basename += _default_download_suffix(resolved_model, payload[:8192])

            with tempfile.TemporaryDirectory() as tmpdir:
                working_name = os.path.join(tmpdir, basename)
                with open(working_name, "wb") as handle:
                    handle.write(payload)

                if _model_in_family(resolved_model, RohdeSchwarz_scopes):
                    payload_url = _rohde_schwarz_payload_url(url)
                    print(f"downloading '{payload_url}'", file=sys.stderr)
                    payload_response = requests.get(payload_url, allow_redirects=True, timeout=10)
                    payload_response.raise_for_status()
                    local_payload = os.path.splitext(working_name)[0] + ".Wfm.bin"
                    with open(local_payload, "wb") as handle:
                        handle.write(payload_response.content)

                try:
                    model_choice = "auto" if auto_model else model
                    new_wfm = cls.from_file(working_name, model_choice, selected)
                    new_wfm.original_name = url
                    new_wfm.basename = os.path.basename(path) or basename
                    return new_wfm
                except (Read_WFM_Error, Parse_WFM_Error, Unknown_Scope_Error):
                    raise
                except Exception as e:
                    raise Parse_WFM_Error(e) from e

        except requests.exceptions.RequestException as e:
            raise Read_WFM_Error(f"Failed to download '{url}': {e}") from e

    def describe(self) -> str:
        """Return a string describing the contents of the waveform file."""
        s = "    General:\n"
        s += "        File Model   = %s\n" % self.header_name
        if self.serial_number:
            s += "        Serial Number = %s\n" % self.serial_number
        s += "        User Model   = %s\n" % self.user_name
        s += "        Parser Model = %s\n" % self.parser_name
        s += "        Firmware     = %s\n" % self.firmware
        s += "        Filename     = %s\n" % self.basename
        s += "        Channels     = ["

        first = True
        for ch in self.channels:
            if not first:
                s += ", "
            s += "%s" % ch.channel_number
            first = False
        s += "]\n\n"

        # Compute derived trigger levels: voltage at t=0 for relevant analog channels.
        _source = self.trigger_info.get("source", "")
        _CH_SOURCE_MAP = {"CH1": 1, "CH2": 2, "CH3": 3, "CH4": 4}
        _source_ch_num = _CH_SOURCE_MAP.get(_source)
        _known_non_analog = bool(_source) and _source_ch_num is None

        derived_levels: dict[int, float] = {}
        if not _known_non_analog:
            for ch in self.channels:
                if _source_ch_num is not None and ch.channel_number != _source_ch_num:
                    continue
                if ch.enabled_and_selected and ch.times is not None and ch.volts is not None and len(ch.times) > 0:
                    idx = int(np.argmin(np.abs(ch.times)))
                    derived_levels[ch.channel_number] = float(ch.volts[idx])

        if self.trigger_info or derived_levels:
            s += "    Trigger:\n"
            if self.trigger_info:
                if self.trigger_info.get("mode") == "alt":
                    s += "        Mode     = alt\n"
                    if "trigger1" in self.trigger_info:
                        s += "\n        Trigger 1:\n"
                        s += RigolWFM.rigol.describe_trigger_block(self.trigger_info["trigger1"], indent="            ")
                    if "trigger2" in self.trigger_info:
                        s += "\n        Trigger 2:\n"
                        s += RigolWFM.rigol.describe_trigger_block(self.trigger_info["trigger2"], indent="            ")
                else:
                    s += RigolWFM.rigol.describe_trigger_block(self.trigger_info)
            show_ch_label = _source_ch_num is None
            for ch_num, level in sorted(derived_levels.items()):
                label = "Derived Level (CH%d)" % ch_num if show_ch_label else "Derived Level    "
                s += "        %s = %sV\n" % (label, RigolWFM.channel.engineering_string(level, 2))
            s += "\n"

        for ch in self.channels:
            s += str(ch)
            s += "\n"
        return s

    def best_scaling(self) -> tuple[float, str, float, str]:
        """Return appropriate scaling for plot."""
        v_scale = 1e-12
        v_prefix = ""
        h_scale = 1e-12
        h_prefix = ""
        for ch in self.channels:
            v, p = RigolWFM.channel.best_scale(ch.volt_per_division)
            if v > v_scale:
                v_scale = v
                v_prefix = p
            h, p = RigolWFM.channel.best_scale(ch.time_scale)
            if h > h_scale:
                h_scale = h
                h_prefix = p
        return h_scale, h_prefix, v_scale, v_prefix

    def plot(self) -> Figure:
        """Plot the data in oscilloscope style and return the Figure."""
        _CH_COLORS = ["#FFFF00", "#00FFFF", "#FF00FF", "#00FF00"]

        h_scale, h_prefix, v_scale, v_prefix = self.best_scaling()

        fig, ax = plt.subplots(figsize=(10, 6), facecolor="black")
        ax.set_facecolor("black")

        for i, ch in enumerate(self.channels):
            ax.plot(
                ch.times * h_scale,  # type: ignore[operator]
                ch.volts * v_scale,  # type: ignore[operator]
                label=ch.name,
                color=_CH_COLORS[i % 4],
                linewidth=0.8,
            )

        ax.set_xlabel("Time (%ss)" % h_prefix, color="white")
        ax.set_ylabel("Voltage (%sV)" % v_prefix, color="white")
        ax.set_title(self.basename, color="white")
        ax.legend(loc="upper right", facecolor="black", edgecolor="#555555", labelcolor="white")

        ax.grid(True, which="major", color="#2a2a2a", linewidth=0.8, linestyle="-")
        ax.minorticks_on()
        ax.grid(True, which="minor", color="#1a1a1a", linewidth=0.4, linestyle=":")

        ax.tick_params(colors="white", which="both")
        for spine in ax.spines.values():
            spine.set_edgecolor("#444444")

        fig.tight_layout()
        return fig

    def csv(self) -> str:
        """Return a string of comma separated values."""
        data_channels = [ch for ch in self.channels if ch.enabled_and_selected]
        if not data_channels:
            return ""

        h_scale, h_prefix, v_scale, v_prefix = self.best_scaling()

        s = "X"
        for ch in data_channels:
            s += ",%s" % ch.name
        s += ",Start,Increment\n"

        ch = data_channels[0]
        times = data_channels[0].times
        assert times is not None
        incr = (times[1] - times[0]) * h_scale if len(times) > 1 else 0.0
        off = times[0] * h_scale
        s += "%ss" % h_prefix
        for ch in data_channels:
            s += ",%s%s" % (v_prefix, ch.unit.name.upper())
        s += ",%e,%e\n" % (off, incr)

        n_pts = min(ch.points for ch in data_channels)
        for i in range(n_pts):
            s += "%.6f" % (times[i] * h_scale)
            for ch in data_channels:
                assert ch.volts is not None
                s += ",%.2f" % (ch.volts[i] * v_scale)
            s += "\n"
        return s

    def sigrokcsv(self) -> str:
        """Return a string of comma separated values for sigrok."""
        data_channels = [ch for ch in self.channels if ch.enabled_and_selected]
        if not data_channels:
            return ""

        s = "X"
        for ch in data_channels:
            s += ",%s (%s)" % (ch.name, ch.unit.name.upper())
        s += "\n"

        n_pts = min(ch.points for ch in data_channels)
        times = data_channels[0].times
        assert times is not None
        for i in range(n_pts):
            s += "%.8f" % (times[i])
            for ch in data_channels:
                assert ch.volts is not None
                s += ",%.2f" % (ch.volts[i])
            s += "\n"
        return s

    def wav(
        self,
        filename: str | os.PathLike[str] | IO[bytes],
        *,
        channel: int | list[int] = 1,
        scale: Literal["auto", "scope"] = "auto",
    ) -> None:
        """Save one or two channels as a signed 16-bit WAV file.

        Args:
            filename: Destination path (str or PathLike) or a writable binary file-like object.
            channel: Channel number(s) to export.  Pass a single int for mono output,
                or a list of two ints for stereo output.  Each channel must be enabled
                and selected.  In LTspice, the first channel is addressed as ``chan=0``
                and the second as ``chan=1``.
            scale: How to map voltages to the ±32767 integer range.
                ``"auto"`` maps each channel's own min/max volts to ±32767.
                This preserves waveform shape, but absolute voltage information is
                lost. In LTspice, set ``Vpeak`` on the WAV source to the actual
                peak voltage.

                ``"scope"`` maps each channel's ±(4 × V/div) full-scale range to
                ±32767 while keeping zero volts at zero. In LTspice, set
                ``Vpeak = 4 × V/div``.

        Raises:
            ValueError: If more than two channels are requested, or if any requested
                channel is not found, not enabled, or not selected.
        """
        channel_list = [channel] if isinstance(channel, int) else list(channel)
        if len(channel_list) > 2:
            raise ValueError(f"WAV files support at most 2 channels; {len(channel_list)} requested.")

        channels = []
        for num in channel_list:
            ch = next(
                (c for c in self.channels if c.channel_number == num and c.enabled_and_selected),
                None,
            )
            if ch is None:
                raise ValueError(f"Channel {num} is not available or not enabled/selected in this waveform.")
            channels.append(ch)

        def _scale_channel(ch: Any) -> npt.NDArray[np.int16]:
            assert ch.volts is not None
            v = ch.volts.astype(np.float64)
            if scale == "auto":
                v_min = float(np.min(v))
                v_max = float(np.max(v))
                v_range = v_max - v_min if v_max != v_min else 1.0
                return ((v - v_min) / v_range * 65534 - 32767).astype(np.int16)
            # "scope"
            full_scale = 4.0 * ch.volt_per_division if ch.volt_per_division != 0 else 1.0
            return np.clip(v / full_scale * 32767, -32767, 32767).astype(np.int16)

        scaled = [_scale_channel(ch) for ch in channels]
        n_channels = len(scaled)
        n_pts = min(len(s) for s in scaled)

        if n_channels == 1:
            frames = scaled[0][:n_pts]
        else:
            frames = np.empty(n_pts * 2, dtype=np.int16)
            frames[0::2] = scaled[0][:n_pts]
            frames[1::2] = scaled[1][:n_pts]

        _MAX_WAV_U32 = 2**32 - 1
        sample_rate = int(min(round(1.0 / channels[0].seconds_per_point), _MAX_WAV_U32 // (n_channels * 2)))

        wavef = wave.Wave_write(filename)  # type: ignore[arg-type]
        try:
            wavef.setnchannels(n_channels)
            wavef.setsampwidth(2)
            wavef.setframerate(sample_rate)
            wavef.setcomptype("NONE", "")
            wavef.setnframes(n_pts)
            wavef.writeframes(frames.tobytes())
        finally:
            wavef.close()
