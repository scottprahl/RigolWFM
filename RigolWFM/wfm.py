"""
Parse and convert Rigol oscilloscope waveform files.

Supports DS1000B/C/D/E/Z, DS2000, DS4000, DS6000, MSO5000, MSO5074,
MSO7000/8000, and DHO800/DHO1000 scope families via `Wfm.from_file()`.

Example:
    >>> import RigolWFM.wfm as rigol
    >>> waveform = rigol.Wfm.from_file("file_name.wfm")
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
from typing import IO, Any, Literal

import matplotlib.pyplot as plt
import numpy as np
import numpy.typing as npt
import requests  # type: ignore[import-untyped]

import RigolWFM.dho
import RigolWFM.lecroy
import RigolWFM.mso5000
import RigolWFM.mso5074
import RigolWFM.mso7000_8000
import RigolWFM.wfm1000b
import RigolWFM.wfm1000c
import RigolWFM.wfm1000d
import RigolWFM.wfm1000e
import RigolWFM.wfm1000z
import RigolWFM.wfm2000
import RigolWFM.wfm4000
import RigolWFM.wfm6000
import RigolWFM.channel

# in progress
DS1000B_scopes: list[str] = ["B", "1000B", "DS1000B", "DS1074B", "DS1104B", "DS1204B"]

# tested
DS1000C_scopes: list[str] = [
    "C",
    "1000C",
    "DS1000C",
    "DS1000CD",
    "DS1000MD",
    "DS1000M",
    "DS1302CA",
    "DS1202CA",
    "DS1102CA",
    "DS1062CA",
    "DS1042C",
]

# tested
DS1000D_scopes: list[str] = ["D", "1000D", "DS1000D", "DS1102D", "DS1052D"]

# tested
DS1000E_scopes: list[str] = ["E", "1000E", "DS1000E", "DS1102E", "DS1052E"]

# tested, wonky voltages
DS1000Z_scopes: list[str] = [
    "Z",
    "1000Z",
    "DS1000Z",
    "DS1202Z",
    "DS1054Z",
    "MSO1054Z",
    "DS1074Z",
    "MSO1074Z",
    "DS1074Z-S",
    "DS1104Z",
    "MSO1104Z",
    "DS1104Z-S",
]

# tested
DS2000_scopes: list[str] = [
    "2",
    "2000",
    "DS2000",
    "DS2072A",
    "DS2102A",
    "MSO2102A",
    "MSO2102A-S",
    "DS2202A",
    "MSO2202A",
    "MSO2202A-S",
    "DS2302A",
    "MSO2302A",
    "MSO2302A-S",
]

# tested
DS4000_scopes: list[str] = [
    "4",
    "4000",
    "DS4000",
    "DS4054",
    "DS4052",
    "DS4034",
    "DS4032",
    "DS4024",
    "DS4022",
    "DS4014",
    "DS4012",
    "MSO4054",
    "MSO4052",
    "MSO4034",
    "MSO4032",
    "MSO4024",
    "MSO4022",
    "MSO4014",
    "MSO4012",
]

# untested
DS6000_scopes: list[str] = ["6", "6000", "DS6000", "DS6062", "DS6064", "DS6102", "DS6104"]

# example-backed `.bin` support
DS5000_scopes: list[str] = ["5", "5000", "MSO5000"]

# MSO5074 uses a different firmware format (uint8 ADC counts, wrong metadata)
MSO5074_scopes: list[str] = ["5074", "MSO5074"]

# manual-backed `.bin` support
DS7000_scopes: list[str] = ["7", "7000", "DS7000", "MSO7000"]

# manual-backed `.bin` support
DS8000_scopes: list[str] = ["8", "8000", "MSO8000"]

# DHO800/DHO1000 series (.bin and .wfm - format detected by file extension)
DHO1000_scopes: list[str] = [
    "DHO", "DHO800", "DHO1000",
    "DHO804", "DHO812", "DHO814", "DHO824",
    "DHO1072", "DHO1074", "DHO1102", "DHO1202", "DHO1204",
]

# Teledyne LeCroy .trc files (LECROY_2_3 format)
LeCroy_scopes: list[str] = ["LeCroy", "LECROY", "lecroy", "trc"]

_LECROY_MAGIC = b"WAVEDESC"

_SWEEP_NAMES: dict[int, str] = {0: "AUTO", 1: "NORMAL", 2: "SINGLE"}
_COUPLING_NAMES: dict[int, str] = {0: "DC", 1: "LF", 2: "HF", 3: "AC"}
_DS2000_SOURCE_NAMES: dict[int, str] = {
    0: "CH1", 1: "CH2", 2: "EXT", 3: "AC LINE",
    **{4 + i: "D%d" % i for i in range(16)},
}
_DS2000_TRIGGER_MODE_NAMES: dict[int, str] = {
    30: "Edge",
}


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
            hdr = f.read(300)
    except OSError as exc:
        raise FileNotFoundError(filename) from exc

    if len(hdr) < 4:
        raise Parse_WFM_Error(f"File too short to detect model: {filename}")

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
    if magic4 == bytes([0x02, 0x00, 0x00, 0x00]):
        return "DHO"

    # DHO .bin export: RG03
    if hdr[:4] == b"RG03":
        return "DHO"

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

    # LeCroy .trc: "WAVEDESC" marker at byte 0, or after a short SCPI prefix
    if _LECROY_MAGIC in hdr[:64]:
        return "LeCroy"

    raise Parse_WFM_Error(f"Unrecognised file signature {magic4.hex()} in {filename}")


def valid_scope_list() -> str:
    """List all the oscilloscope types."""
    s = "\nRigol oscilloscope models:\n    "
    s += ", ".join(DS1000B_scopes) + "\n    "
    s += ", ".join(DS1000C_scopes) + "\n    "
    s += ", ".join(DS1000D_scopes) + "\n    "
    s += ", ".join(DS1000E_scopes) + "\n    "
    s += ", ".join(DS1000Z_scopes) + "\n    "
    s += ", ".join(DS2000_scopes) + "\n    "
    s += ", ".join(DS4000_scopes) + "\n    "
    s += ", ".join(DS5000_scopes) + "\n    "
    s += ", ".join(MSO5074_scopes) + "\n    "
    s += ", ".join(DS7000_scopes) + "\n    "
    s += ", ".join(DS8000_scopes) + "\n    "
    s += ", ".join(DS6000_scopes) + "\n    "
    s += ", ".join(DHO1000_scopes) + "\n    "
    s += ", ".join(LeCroy_scopes) + "\n"
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


def dho_from_file(file_name: str) -> RigolWFM.dho.DhoWaveform:
    """Backward-compatible wrapper around `RigolWFM.dho.from_file()`."""
    return RigolWFM.dho.from_file(file_name)


def _trig_header_dict(th) -> dict:
    """Extract a KaitaiStruct trigger_header into a plain dict."""
    d: dict = {}
    try:
        d["mode"] = th.mode.name
    except Exception:
        pass
    try:
        d["source"] = th.source.name.upper()
    except Exception:
        pass
    try:
        d["level"] = float(th.level)
    except Exception:
        pass
    try:
        d["sweep"] = _SWEEP_NAMES.get(th.sweep, str(th.sweep))
    except Exception:
        pass
    try:
        d["coupling"] = _COUPLING_NAMES.get(th.coupling, str(th.coupling))
    except Exception:
        pass
    return d


def _describe_trigger_block(d: dict, indent: str = "        ") -> str:
    """Format a trigger info dict as indented text."""
    s = ""
    if "mode" in d:
        s += "%sMode     = %s\n" % (indent, d["mode"])
    if "source" in d:
        s += "%sSource   = %s\n" % (indent, d["source"])
    if "level" in d:
        s += "%sLevel    = %sV\n" % (indent, RigolWFM.channel.engineering_string(d["level"], 2))
    if "sweep" in d:
        s += "%sSweep    = %s\n" % (indent, d["sweep"])
    if "coupling" in d:
        s += "%sCoupling = %s\n" % (indent, d["coupling"])
    return s


def _scaled_ds4000_trigger_levels(level_block: Any, probe_values: list[float]) -> dict[str, float]:
    """Scale a parsed DS4000 trigger-level block into volts."""
    raw_levels = [
        ("CH1", level_block.ch1_level_uv, probe_values[0]),
        ("CH2", level_block.ch2_level_uv, probe_values[1]),
        ("CH3", level_block.ch3_level_uv, probe_values[2]),
        ("CH4", level_block.ch4_level_uv, probe_values[3]),
        ("EXT", level_block.ext_level_uv, 1.0),
    ]
    return {name: raw_uv * 1.0e-6 * scale for name, raw_uv, scale in raw_levels}


def _decode_ds4000_trigger(waveform: Any) -> dict:
    """Best-effort decode of DS4000 trigger metadata from parsed setup fields."""
    setup = getattr(waveform.header, "setup", None)
    if setup is None:
        return {}

    probe_values = [float(channel.probe_value) for channel in waveform.header.ch]

    modern_levels = getattr(setup, "modern_trigger_levels", None)
    modern_mode = getattr(setup, "modern_trigger_mode", None)
    modern_source = getattr(setup, "modern_trigger_source", None)
    if (
        modern_levels is not None
        and hasattr(modern_mode, "name")
        and hasattr(modern_source, "name")
    ):
        input_levels = _scaled_ds4000_trigger_levels(modern_levels, probe_values)
        source = modern_source.name.upper()
        info: dict[str, Any] = {
            "mode": modern_mode.name.capitalize(),
            "source": source,
            "input_levels": input_levels,
        }
        if source in input_levels:
            info["level"] = input_levels[source]
        return info

    legacy_levels = getattr(setup, "legacy_trigger_levels", None)
    if legacy_levels is not None:
        return {"input_levels": _scaled_ds4000_trigger_levels(legacy_levels, probe_values)}

    return {}


def _decode_ds2000_trigger(waveform: Any) -> dict:
    """Best-effort decode of DS2000 trigger metadata from parsed setup fields."""
    setup = getattr(waveform.header, "setup", None)
    if setup is None:
        return {}

    source_primary = getattr(setup, "trigger_source_primary", None)
    source_shadow = getattr(setup, "trigger_source_shadow", None)
    holdoff_ns = int(getattr(setup, "trigger_holdoff_ns", 0) or 0)
    level_block = getattr(setup, "trigger_levels", None)
    if level_block is None:
        return {}

    input_levels = {
        "CH1": level_block.ch1_level_uv * 1.0e-6,
        "CH2": level_block.ch2_level_uv * 1.0e-6,
        "EXT": level_block.ext_level_uv * 1.0e-6,
    }
    has_meaningful_setup = holdoff_ns != 0 or any(level != 0.0 for level in input_levels.values())
    if not has_meaningful_setup:
        return {}

    info: dict[str, Any] = {"input_levels": input_levels}

    try:
        source_code = int(source_primary)
        if source_shadow is not None and source_code == int(source_shadow):
            source_name = _DS2000_SOURCE_NAMES.get(source_code)
            if source_name is not None:
                info["source"] = source_name
                if source_name in input_levels:
                    info["level"] = input_levels[source_name]
    except (TypeError, ValueError):
        pass

    mode_code = getattr(setup, "trigger_mode_code", None)
    try:
        mode_name = _DS2000_TRIGGER_MODE_NAMES.get(int(mode_code))
        if mode_name is not None:
            info["mode"] = mode_name
    except (TypeError, ValueError):
        pass

    return info


class Read_WFM_Error(Exception):
    """Generic Read Error."""


class Parse_WFM_Error(Exception):
    """Generic Parse Error."""


class Invalid_URL(Exception):
    """URL scheme is not http or https."""


class Unknown_Scope_Error(Exception):
    """Not one of the listed Rigol oscilloscopes."""


class Write_WAV_Error(Exception):
    """Something went wrong while writing the .wave file."""


class Channel_Not_In_WFM_Error(Exception):
    """The channel is not in the .wfm file."""


class Wfm:
    """Class with parsed data from a .wfm file."""

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
            model: Rigol Oscilloscope used, e.g., 'E' or 'Z'; defaults to auto-detect
            selected: string of channels to process e.g., '12'
        Returns:
            a wfm object for the file
        """
        # ensure that file exists
        try:
            with open(file_name, "rb"):
                pass
        except OSError as e:
            raise Read_WFM_Error(e) from e

        new_wfm = cls(file_name)
        new_wfm.original_name = file_name
        new_wfm.file_name = file_name
        new_wfm.basename = os.path.basename(file_name)

        # parse the waveform
        auto_model = model.upper() == "AUTO"
        umodel = detect_model(file_name).upper() if auto_model else model.upper()

        if umodel in DS1000B_scopes:
            w = RigolWFM.wfm1000b.Wfm1000b.from_file(file_name)  # type: ignore[attr-defined]
            new_wfm.header_name = "DS1000B"
            new_wfm.trigger_info = {
                "mode": w.header.trigger_mode.name,
                "source": w.header.trigger_source.name.upper(),
            }

        elif umodel in DS1000C_scopes:
            w = RigolWFM.wfm1000c.Wfm1000c.from_file(file_name)  # type: ignore[attr-defined]
            new_wfm.header_name = "DS1000C"
            new_wfm.trigger_info = {
                "mode": w.header.trigger_mode.name,
                "source": w.header.trigger_source.name.upper(),
            }

        elif umodel in DS1000D_scopes:
            w = RigolWFM.wfm1000e.Wfm1000e.from_file(file_name)  # type: ignore[attr-defined]
            w.parser_name = "wfm1000d"
            new_wfm.header_name = "DS1000D"
            _mode = w.header.trigger_mode.name
            if _mode == "alt":
                new_wfm.trigger_info = {
                    "mode": "alt",
                    "trigger1": _trig_header_dict(w.header.trigger1),
                    "trigger2": _trig_header_dict(w.header.trigger2),
                }
            else:
                _d = _trig_header_dict(w.header.trigger1)
                _d["mode"] = _mode
                new_wfm.trigger_info = _d

        elif umodel in DS1000E_scopes:
            w = RigolWFM.wfm1000e.Wfm1000e.from_file(file_name)  # type: ignore[attr-defined]
            new_wfm.header_name = "DS1000E"
            _mode = w.header.trigger_mode.name
            if _mode == "alt":
                new_wfm.trigger_info = {
                    "mode": "alt",
                    "trigger1": _trig_header_dict(w.header.trigger1),
                    "trigger2": _trig_header_dict(w.header.trigger2),
                }
            else:
                _d = _trig_header_dict(w.header.trigger1)
                _d["mode"] = _mode
                new_wfm.trigger_info = _d

        elif umodel in DS1000Z_scopes:
            w = RigolWFM.wfm1000z.Wfm1000z.from_file(file_name)  # type: ignore[attr-defined]
            new_wfm.header_name = w.preheader.model_number

        elif umodel in DS2000_scopes:
            w = RigolWFM.wfm2000.Wfm2000.from_file(file_name)  # type: ignore[attr-defined]
            new_wfm.header_name = "DS2000"
            new_wfm.serial_number = getattr(w.header, "serial_number", w.header.model_number)
            new_wfm.trigger_info = _decode_ds2000_trigger(w)

        elif umodel in DS4000_scopes:
            w = RigolWFM.wfm4000.Wfm4000.from_file(file_name)  # type: ignore[attr-defined]
            new_wfm.header_name = "DS4000"
            new_wfm.serial_number = getattr(w.header, "serial_number", w.header.model_number)
            new_wfm.trigger_info = _decode_ds4000_trigger(w)

        elif umodel in DS5000_scopes:
            w = RigolWFM.mso5000.from_file(file_name)
            new_wfm.header_name = w.header.model_number or "MSO5000"

        elif umodel in MSO5074_scopes:
            w = RigolWFM.mso5074.from_file(file_name)
            new_wfm.header_name = w.header.model_number or "MSO5074"

        elif umodel in DS7000_scopes:
            w = RigolWFM.mso7000_8000.from_file(file_name)
            new_wfm.header_name = w.header.model_number or "MSO7000"

        elif umodel in DS8000_scopes:
            w = RigolWFM.mso7000_8000.from_file(file_name)
            new_wfm.header_name = w.header.model_number or "MSO8000"

        elif umodel in DS6000_scopes:
            w = RigolWFM.wfm6000.Wfm6000.from_file(file_name)  # type: ignore[attr-defined]
            new_wfm.header_name = w.header.model_number

        elif umodel in DHO1000_scopes:
            w = RigolWFM.dho.from_file(file_name)
            fallback = "DHO1000"
            model_hint = w.header.model_number or ""
            if model_hint.upper().startswith(("DHO8", "HDO8")):
                fallback = "DHO800"
            new_wfm.header_name = RigolWFM.dho.family_label(
                model_hint,
                is_bin=RigolWFM.dho.is_bin_file(file_name),
                fallback=fallback,
            )

        elif umodel in LeCroy_scopes:
            w = RigolWFM.lecroy.from_file(file_name)
            new_wfm.header_name = w.header.model_number or "LeCroy"

        else:
            raise Unknown_Scope_Error(f"Unknown Rigol oscilloscope type: '{umodel}'\n{valid_scope_list()}")

        new_wfm.user_name = "auto" if auto_model else model
        pname = getattr(w, "parser_name", type(w).__module__.rsplit(".", 1)[-1])
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
            and file_family not in user_family
            and user_family not in file_family
        ):
            print(
                f"Warning: file reports model '{new_wfm.header_name}' "
                f"but scope type '{model}' was specified.",
                file=sys.stderr,
            )

        # assemble into uniform set of names
        enabled = ""
        for ch_number in range(1, 5):

            ch = RigolWFM.channel.Channel(w, ch_number, pname, selected)

            if not ch.enabled:
                continue

            # keep track of enabled channels for error message
            enabled += str(ch_number)

            # append all enabled channels
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
            model: Rigol Oscilloscope used, e.g., 'E' or 'Z'; defaults to auto-detect
            selected: string of channels to process e.g., '12'
        Returns:
            a wfm object for the file
        """
        u = urllib.parse.urlparse(url)
        scheme = u[0]

        if scheme not in ["http", "https"]:
            raise Invalid_URL(f"URL scheme must be 'http' or 'https', got '{scheme}': {url}")

        try:
            # need a local file for conversion, download url and save as tempfile
            print(f"downloading '{url}'", file=sys.stderr)
            r = requests.get(url, allow_redirects=True, timeout=10)
            r.raise_for_status()

            with tempfile.NamedTemporaryFile(delete=False) as f:
                f.write(r.content)
                working_name = f.name

            try:
                new_wfm = cls.from_file(working_name, model, selected)
                new_wfm.original_name = url
                # extract the simple name
                rawpath = u[2]
                path = urllib.parse.unquote(rawpath)
                new_wfm.basename = os.path.basename(path)
                return new_wfm
            except (Read_WFM_Error, Parse_WFM_Error, Unknown_Scope_Error):
                raise
            except Exception as e:
                raise Parse_WFM_Error(e) from e
            finally:
                os.unlink(working_name)

        except requests.exceptions.RequestException as e:
            raise Read_WFM_Error(f"Failed to download '{url}': {e}") from e

    def describe(self) -> str:
        """Return a string describing the contents of a Rigol wfm file."""
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
        # If source is known and non-analog (EXT, AC LINE, digital), skip entirely.
        # If source is known analog (CH1–CH4), restrict to that channel.
        # If source is unknown, show all enabled analog channels.
        _source = self.trigger_info.get("source", "")
        _CH_SOURCE_MAP = {"CH1": 1, "CH2": 2, "CH3": 3, "CH4": 4}
        _source_ch_num = _CH_SOURCE_MAP.get(_source)  # None if not a recognised analog source
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
                        s += _describe_trigger_block(self.trigger_info["trigger1"], indent="            ")
                    if "trigger2" in self.trigger_info:
                        s += "\n        Trigger 2:\n"
                        s += _describe_trigger_block(self.trigger_info["trigger2"], indent="            ")
                else:
                    s += _describe_trigger_block(self.trigger_info)
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

    def plot(self) -> plt.Figure:
        """Plot the data in oscilloscope style and return the Figure."""
        # Classic Rigol channel colours: CH1=yellow, CH2=cyan, CH3=magenta, CH4=green
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

        # Oscilloscope-style grid: visible but not distracting
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

        # just output the display 100 pts/division
        ch = data_channels[0]
        incr = ch.time_scale / 100
        off = -6 * ch.time_scale
        s += "%ss" % h_prefix
        for ch in data_channels:
            s += ",%s%s" % (v_prefix, ch.unit.name.upper())
        s += ",%e,%e\n" % (off, incr)

        n_pts = min(ch.points for ch in data_channels)
        times = data_channels[0].times
        assert times is not None
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
                ``"auto"``  — each channel's own min/max volts are mapped to ±32767.
                    Preserves waveform shape; absolute voltage information is lost.
                    In LTspice, set Vpeak on the WAV source to the actual peak voltage.
                ``"scope"`` — each channel's ±(4 × V/div) full-scale range is mapped
                    to ±32767.  Zero volts remains at zero.
                    In LTspice, set Vpeak = 4 × V/div.

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
                raise ValueError(
                    f"Channel {num} is not available or not enabled/selected in this waveform."
                )
            channels.append(ch)

        def _scale_channel(ch: Any) -> npt.NDArray[np.int16]:
            assert ch.volts is not None
            v = ch.volts.astype(np.float64)
            if scale == "auto":
                v_min = float(np.min(v))
                v_max = float(np.max(v))
                v_range = v_max - v_min if v_max != v_min else 1.0
                return ((v - v_min) / v_range * 65534 - 32767).astype(np.int16)
            else:  # "scope"
                full_scale = 4.0 * ch.volt_per_division if ch.volt_per_division != 0 else 1.0
                return np.clip(v / full_scale * 32767, -32767, 32767).astype(np.int16)

        scaled = [_scale_channel(ch) for ch in channels]
        n_channels = len(scaled)
        n_pts = min(len(s) for s in scaled)

        if n_channels == 1:
            frames = scaled[0][:n_pts]
        else:
            # Interleave: L R L R ...
            frames = np.empty(n_pts * 2, dtype=np.int16)
            frames[0::2] = scaled[0][:n_pts]
            frames[1::2] = scaled[1][:n_pts]

        # The WAV header stores framerate and byte_rate (framerate × n_channels × sampwidth)
        # as u32 fields.  Cap so both always fit.
        _MAX_WAV_U32 = 2**32 - 1
        sample_rate = int(min(round(1.0 / channels[0].seconds_per_point),
                              _MAX_WAV_U32 // (n_channels * 2)))

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
