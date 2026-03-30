"""
Rigol-specific scope lists, trigger helpers, and file-parser dispatch.

This module owns everything that is unique to Rigol oscilloscope families:
the model-string lists used for dispatch, the trigger-metadata helpers, and the
``parse_file()`` entry-point that ``wfm.Wfm.from_file()`` delegates to for all
Rigol families.

Non-Rigol vendors (LeCroy, Tektronix) are handled directly in ``wfm.py``.
"""

from __future__ import annotations

from typing import Any, Optional

import RigolWFM.channel
import RigolWFM.dho
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

# ---------------------------------------------------------------------------
# Scope-family model-string lists
# ---------------------------------------------------------------------------

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
    "DHO",
    "DHO800",
    "DHO1000",
    "DHO804",
    "DHO812",
    "DHO814",
    "DHO824",
    "DHO1072",
    "DHO1074",
    "DHO1102",
    "DHO1202",
    "DHO1204",
]

# Flat list of every Rigol model string, used by detect_model() and valid_scope_list()
ALL_RIGOL_SCOPES: list[list[str]] = [
    DS1000B_scopes,
    DS1000C_scopes,
    DS1000D_scopes,
    DS1000E_scopes,
    DS1000Z_scopes,
    DS2000_scopes,
    DS4000_scopes,
    DS5000_scopes,
    MSO5074_scopes,
    DS7000_scopes,
    DS8000_scopes,
    DS6000_scopes,
    DHO1000_scopes,
]

# ---------------------------------------------------------------------------
# Trigger-metadata helpers (Rigol-specific)
# ---------------------------------------------------------------------------

_SWEEP_NAMES: dict[int, str] = {0: "AUTO", 1: "NORMAL", 2: "SINGLE"}
_COUPLING_NAMES: dict[int, str] = {0: "DC", 1: "LF", 2: "HF", 3: "AC"}
_DS2000_SOURCE_NAMES: dict[int, str] = {
    0: "CH1",
    1: "CH2",
    2: "EXT",
    3: "AC LINE",
    **{4 + i: "D%d" % i for i in range(16)},
}
_DS2000_TRIGGER_MODE_NAMES: dict[int, str] = {
    30: "Edge",
}


def _trig_header_dict(th: Any) -> dict:
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


def describe_trigger_block(d: dict, indent: str = "        ") -> str:
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
    if modern_levels is not None and hasattr(modern_mode, "name") and hasattr(modern_source, "name"):
        input_levels = _scaled_ds4000_trigger_levels(modern_levels, probe_values)
        source = modern_source.name.upper()  # type: ignore[union-attr]
        info: dict[str, Any] = {
            "mode": modern_mode.name.capitalize(),  # type: ignore[union-attr]
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
        source_code = int(source_primary)  # type: ignore[arg-type]
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
        mode_name = _DS2000_TRIGGER_MODE_NAMES.get(int(mode_code))  # type: ignore[arg-type]
        if mode_name is not None:
            info["mode"] = mode_name
    except (TypeError, ValueError):
        pass

    return info


# ---------------------------------------------------------------------------
# Backward-compatible wrapper
# ---------------------------------------------------------------------------


def dho_from_file(file_name: str) -> RigolWFM.dho.DhoWaveform:
    """Backward-compatible wrapper around `RigolWFM.dho.from_file()`."""
    return RigolWFM.dho.from_file(file_name)


# ---------------------------------------------------------------------------
# Unified Rigol parser dispatch
# ---------------------------------------------------------------------------


def parse_file(
    umodel: str,
    file_name: str,
) -> Optional[tuple[Any, str, str, dict]]:
    """Parse a Rigol waveform file and return normalised metadata.

    Args:
        umodel:    Upper-cased model string (as returned by ``detect_model()``
                   or supplied by the user).
        file_name: Path to the waveform file.

    Returns:
        ``(w, header_name, serial_number, trigger_info)`` when *umodel* matches
        a known Rigol family, or ``None`` when it does not (allowing the caller
        to try non-Rigol vendors).
    """
    header_name = ""
    serial_number = ""
    trigger_info: dict = {}

    if umodel in DS1000B_scopes:
        w = RigolWFM.wfm1000b.Wfm1000b.from_file(file_name)  # type: ignore[attr-defined]
        header_name = "DS1000B"
        trigger_info = {
            "mode": w.header.trigger_mode.name,
            "source": w.header.trigger_source.name.upper(),
        }

    elif umodel in DS1000C_scopes:
        w = RigolWFM.wfm1000c.Wfm1000c.from_file(file_name)  # type: ignore[attr-defined]
        header_name = "DS1000C"
        trigger_info = {
            "mode": w.header.trigger_mode.name,
            "source": w.header.trigger_source.name.upper(),
        }

    elif umodel in DS1000D_scopes:
        w = RigolWFM.wfm1000e.Wfm1000e.from_file(file_name)  # type: ignore[attr-defined]
        w.parser_name = "wfm1000d"
        header_name = "DS1000D"
        _mode = w.header.trigger_mode.name
        if _mode == "alt":
            trigger_info = {
                "mode": "alt",
                "trigger1": _trig_header_dict(w.header.trigger1),
                "trigger2": _trig_header_dict(w.header.trigger2),
            }
        else:
            trigger_info = _trig_header_dict(w.header.trigger1)
            trigger_info["mode"] = _mode

    elif umodel in DS1000E_scopes:
        w = RigolWFM.wfm1000e.Wfm1000e.from_file(file_name)  # type: ignore[attr-defined]
        header_name = "DS1000E"
        _mode = w.header.trigger_mode.name
        if _mode == "alt":
            trigger_info = {
                "mode": "alt",
                "trigger1": _trig_header_dict(w.header.trigger1),
                "trigger2": _trig_header_dict(w.header.trigger2),
            }
        else:
            trigger_info = _trig_header_dict(w.header.trigger1)
            trigger_info["mode"] = _mode

    elif umodel in DS1000Z_scopes:
        w = RigolWFM.wfm1000z.Wfm1000z.from_file(file_name)  # type: ignore[attr-defined]
        header_name = w.preheader.model_number

    elif umodel in DS2000_scopes:
        w = RigolWFM.wfm2000.Wfm2000.from_file(file_name)  # type: ignore[attr-defined]
        header_name = "DS2000"
        serial_number = getattr(w.header, "serial_number", w.header.model_number)
        trigger_info = _decode_ds2000_trigger(w)

    elif umodel in DS4000_scopes:
        w = RigolWFM.wfm4000.Wfm4000.from_file(file_name)  # type: ignore[attr-defined]
        header_name = "DS4000"
        serial_number = getattr(w.header, "serial_number", w.header.model_number)
        trigger_info = _decode_ds4000_trigger(w)

    elif umodel in DS5000_scopes:
        w = RigolWFM.mso5000.from_file(file_name)
        header_name = w.header.model_number or "MSO5000"

    elif umodel in MSO5074_scopes:
        w = RigolWFM.mso5074.from_file(file_name)
        header_name = w.header.model_number or "MSO5074"

    elif umodel in DS7000_scopes:
        w = RigolWFM.mso7000_8000.from_file(file_name)
        header_name = w.header.model_number or "MSO7000"

    elif umodel in DS8000_scopes:
        w = RigolWFM.mso7000_8000.from_file(file_name)
        header_name = w.header.model_number or "MSO8000"

    elif umodel in DS6000_scopes:
        w = RigolWFM.wfm6000.Wfm6000.from_file(file_name)  # type: ignore[attr-defined]
        header_name = w.header.model_number

    elif umodel in DHO1000_scopes:
        w = RigolWFM.dho.from_file(file_name)
        fallback = "DHO1000"
        model_hint = w.header.model_number or ""
        if model_hint.upper().startswith(("DHO8", "HDO8")):
            fallback = "DHO800"
        header_name = RigolWFM.dho.family_label(
            model_hint,
            is_bin=RigolWFM.dho.is_bin_file(file_name),
            fallback=fallback,
        )

    else:
        return None

    return w, header_name, serial_number, trigger_info
