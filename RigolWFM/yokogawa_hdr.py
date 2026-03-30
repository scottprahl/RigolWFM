"""
Parser for Yokogawa DL/WE-series oscilloscope .hdr companion metadata files.

The Yokogawa DL/WE-series oscilloscopes produce a two-file waveform package:

  <name>.hdr  — **this file**: ASCII text key/value metadata
  <name>.wvf  — companion flat binary sample data

This module parses the .hdr file into a structured :class:`HdrInfo` object
that supplies every parameter needed to read and calibrate the .wvf binary
data (byte order, data layout, per-trace calibration, time axis, etc.).

Typical usage::

    from RigolWFM.yokogawa_hdr import parse_hdr, wvf_byte_offset

    hdr = parse_hdr("capture.hdr")
    print(hdr.model, hdr.endian, hdr.data_format)

    g, t, b = 0, 0, 0                      # group, trace, block indices (0-origin)
    trace = hdr.groups[g].traces[t]
    off = wvf_byte_offset(hdr, g, t, b)    # byte offset into .wvf file
    dtype = hdr.byte_order + trace.v_data_type.numpy_dtype

Calibration:
    volts[i] = v_resolution * raw[i] + v_offset

Time axis (0-origin sample index i):
    t[i] = h_offset + h_resolution * i

References:
    Yokogawa Electric Corporation, IM 707713-61E (WVF File Access Toolkit).
    Yokogawa DL1640 User Manual, Appendix 3.
    Erik Benkler, "wvfread v1.7", Physikalisch-Technische Bundesanstalt, 2011.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class VDataTypeInfo:
    """Decoded vertical data type for one trace (from the VDataType .hdr field)."""
    raw: str        # original token, e.g. "IS2", "IU2", "FS4", "B16"
    byte_num: int   # bytes per ADC sample
    numpy_dtype: str  # endian-neutral numpy dtype string, e.g. "i2", "u2", "f4"
    is_logic: bool  # True for B-type (raw logic bit-fields, e.g. DL750 digital channels)


@dataclass
class TraceInfo:
    """Per-trace metadata within one group."""
    name: str                           = ""
    block_size: int                     = 0      # samples per block
    v_resolution: float                 = 1.0    # volts per ADC count (ScaleA)
    v_offset: float                     = 0.0    # volt offset (ScaleB)
    v_data_type: Optional[VDataTypeInfo] = None
    v_unit: str                         = "V"
    v_plus_over: Optional[int]          = None   # ADC value meaning upper overrange
    v_minus_over: Optional[int]         = None   # ADC value meaning lower overrange
    v_illegal: Optional[int]            = None   # ADC value meaning invalid/hidden sample
    v_max: Optional[int]                = None   # maximum valid ADC value
    v_min: Optional[int]                = None   # minimum valid ADC value
    h_resolution: float                 = 1e-9   # seconds per sample (SamplingInterval)
    h_offset: float                     = 0.0    # time of first sample relative to trigger (s)
    h_unit: str                         = "s"
    dates: list[str]                    = field(default_factory=list)  # one entry per block
    times: list[str]                    = field(default_factory=list)  # one entry per block


@dataclass
class GroupInfo:
    """Per-group metadata (one $Group<N> section)."""
    trace_number: int           = 0
    block_number: int           = 0
    traces: list[TraceInfo]     = field(default_factory=list)


@dataclass
class HdrInfo:
    """Complete parsed contents of a Yokogawa .hdr metadata file."""
    format_version: str         = ""
    model: str                  = ""
    endian: str                 = "Ltl"    # "Big" (Motorola) or "Ltl" (Intel x86)
    data_format: str            = "TRACE"  # "TRACE" or "BLOCK" layout in .wvf
    group_number: int           = 0
    trace_total_number: int     = 0
    data_offset: int            = 0        # leading unused bytes in .wvf
    groups: list[GroupInfo]     = field(default_factory=list)

    @property
    def is_big_endian(self) -> bool:
        """Return True when the .wvf binary data uses big-endian byte order."""
        return self.endian.upper().startswith("B")

    @property
    def byte_order(self) -> str:
        """Numpy / struct byte-order prefix: ``'>'`` (BE) or ``'<'`` (LE)."""
        return ">" if self.is_big_endian else "<"


# ---------------------------------------------------------------------------
# Public entry points
# ---------------------------------------------------------------------------

def parse_hdr(path: str) -> HdrInfo:
    """Parse a Yokogawa .hdr file and return a structured :class:`HdrInfo`.

    Args:
        path: Path to the ``.hdr`` file.

    Returns:
        Populated :class:`HdrInfo` instance.

    Raises:
        FileNotFoundError: If *path* does not exist.
        ValueError:        If a required field is missing or malformed.
    """
    text = Path(path).read_text(encoding="ascii", errors="replace")
    return parse_hdr_text(text)


def parse_hdr_text(text: str) -> HdrInfo:
    """Parse .hdr content already loaded as a string.

    Useful when the text has been fetched from a URL or passed as a JS
    string in a web viewer.

    Args:
        text: Full ASCII contents of the .hdr file.

    Returns:
        Populated :class:`HdrInfo` instance.
    """
    public_raw, group_raws = _split_sections(text.splitlines())
    return _build_info(public_raw, group_raws)


# ---------------------------------------------------------------------------
# Byte-offset calculator
# ---------------------------------------------------------------------------

def wvf_byte_offset(hdr: HdrInfo, group: int, trace: int, block: int) -> int:
    """Return the byte offset of a (group, trace, block) slice in the .wvf file.

    All indices are **0-origin**.

    Args:
        hdr:   Parsed :class:`HdrInfo`.
        group: Group index (0 … GroupNumber-1).
        trace: Trace index within the group (0 … TraceNumber-1).
        block: Block index within the group (0 … BlockNumber-1).

    Returns:
        Byte offset from the start of the .wvf file.

    Raises:
        ValueError: If *hdr.data_format* is not ``"TRACE"`` or ``"BLOCK"``.
    """
    fmt = hdr.data_format.upper()
    off = hdr.data_offset

    if fmt == "TRACE":
        return off + _trace_offset(hdr, group, trace, block)
    if fmt == "BLOCK":
        return off + _block_offset(hdr, group, trace, block)
    raise ValueError(f"Unknown DataFormat: {hdr.data_format!r}")


def _trace_offset(hdr: HdrInfo, tgt_g: int, tgt_t: int, tgt_b: int) -> int:
    """Byte offset for TRACE layout (all blocks of each trace stored together)."""
    off = 0
    for g, grp in enumerate(hdr.groups):
        nb = grp.block_number
        for t, tr in enumerate(grp.traces):
            w = tr.v_data_type.byte_num if tr.v_data_type else 2
            s = tr.block_size
            chunk = s * nb * w
            if g == tgt_g and t == tgt_t:
                return off + tgt_b * s * w
            off += chunk
    raise ValueError(f"(group={tgt_g}, trace={tgt_t}) not found in HdrInfo")


def _block_offset(hdr: HdrInfo, tgt_g: int, tgt_t: int, tgt_b: int) -> int:
    """Byte offset for BLOCK layout (all traces within a block stored together)."""
    off = 0
    for g, grp in enumerate(hdr.groups):
        nb = grp.block_number
        if g < tgt_g:
            for tr in grp.traces:
                w = tr.v_data_type.byte_num if tr.v_data_type else 2
                off += tr.block_size * nb * w
            continue
        for b in range(nb):
            for t, tr in enumerate(grp.traces):
                w = tr.v_data_type.byte_num if tr.v_data_type else 2
                s = tr.block_size
                if b == tgt_b and t == tgt_t:
                    return off
                off += s * w
    raise ValueError(f"(group={tgt_g}, trace={tgt_t}, block={tgt_b}) not found in HdrInfo")


# ---------------------------------------------------------------------------
# Section splitter
# ---------------------------------------------------------------------------

# Stores: key → (original_line_with_leading_spaces, value_after_key)
_SectionDict = dict[str, tuple[str, str]]


def _split_sections(
    lines: list[str],
) -> tuple[_SectionDict, list[_SectionDict]]:
    """Partition .hdr lines into ``$PublicInfo`` and ``$Group<N>`` dicts.

    Each dict maps ``key → (original_line, value_after_key)``.  The original
    line is preserved so column-position alignment (used for VUnit, HUnit, and
    optional numeric fields) can be reproduced exactly.

    ``$PrivateInfo`` and any other sections are silently ignored.
    """
    public: _SectionDict = {}
    groups: list[_SectionDict] = []
    current: Optional[_SectionDict] = None

    for raw_line in lines:
        line = raw_line.rstrip("\r")
        stripped = line.strip()
        if not stripped:
            continue

        if stripped.startswith("$"):
            if stripped == "$PublicInfo":
                current = public
            elif re.match(r"^\$Group\d+$", stripped):
                current = {}
                groups.append(current)
            else:
                current = None      # e.g. $PrivateInfo — skip
            continue

        if current is None:
            continue

        m = re.match(r"(\S+)(.*)", line)
        if not m:
            continue
        key = m.group(1)
        rest = m.group(2).strip()

        # First occurrence wins (duplicates in same section are ignored)
        if key not in current:
            current[key] = (line, rest)

    return public, groups


# ---------------------------------------------------------------------------
# VDataType parsing
# ---------------------------------------------------------------------------

def _parse_vdtype(code: str) -> VDataTypeInfo:
    """Decode one VDataType token string.

    Supported codes (from IM 707713-61E):

    ``IS<n>``  signed integer,   n bytes  (IS1, IS2, IS4)
    ``IU<n>``  unsigned integer, n bytes  (IU1, IU2, IU4)
    ``FS<n>``  IEEE 754 float,   n bytes  (FS4, FS8)
    ``FU<n>``  unsigned float,   n bytes  (treated identically to FS<n>)
    ``B<m>``   logic bit-field,  m bytes  (B2, B4, B8, B16)
    """
    code = code.strip()
    if not code:
        raise ValueError("Empty VDataType code")

    kind = code[0].upper()
    if kind in ("I", "F"):
        if len(code) < 3:
            raise ValueError(f"Malformed VDataType: {code!r}")
        sub = code[1].upper()
        byte_num = int(code[2:])
        if kind == "I":
            base = "i" if sub == "S" else "u"
        else:
            base = "f"
        return VDataTypeInfo(raw=code, byte_num=byte_num, numpy_dtype=f"{base}{byte_num}", is_logic=False)

    if kind == "B":
        byte_num = int(code[1:])
        # B16 = 16-byte / 128-bit words; no native numpy dtype; use void
        numpy_dtype = f"V{byte_num}" if byte_num > 8 else f"u{byte_num}"
        return VDataTypeInfo(raw=code, byte_num=byte_num, numpy_dtype=numpy_dtype, is_logic=True)

    raise ValueError(f"Unknown VDataType code: {code!r}")


# ---------------------------------------------------------------------------
# Column-position helpers  (replicate MATLAB rowpos logic from hdrread.m)
# ---------------------------------------------------------------------------

def _vdtype_col_positions(vdtype_line: str) -> list[int]:
    """Return the starting column index of each VDataType token in *vdtype_line*.

    This mirrors the MATLAB ``rowpos`` array that ``hdrread.m`` uses to
    column-align ``VUnit``, ``HUnit``, and the optional overrange fields.
    """
    return [m.start() for m in re.finditer(r"[IFBifb]\w*", vdtype_line)]


def _col_aligned_values(
    line: Optional[str],
    col_positions: list[int],
    n_traces: int,
) -> list[Optional[str]]:
    """Extract per-trace tokens from *line* by column position.

    For each trace, returns the whitespace-delimited token that starts at
    the same column as the corresponding VDataType token in the VDataType
    line.  Returns ``None`` for traces whose column has no matching token.
    """
    if not line:
        return [None] * n_traces
    tokens: dict[int, str] = {m.start(): m.group() for m in re.finditer(r"\S+", line)}
    return [tokens.get(col) for col in col_positions[:n_traces]]


def _try_int(s: Optional[str]) -> Optional[int]:
    """Parse *s* as int; return ``None`` for ``None``, ``'?'``, or non-numeric."""
    if s is None:
        return None
    try:
        return int(s)
    except (ValueError, TypeError):
        return None


# ---------------------------------------------------------------------------
# Main builder
# ---------------------------------------------------------------------------

def _req(d: _SectionDict, key: str) -> str:
    if key not in d:
        raise ValueError(f".hdr file is missing required field: {key!r}")
    return d[key][1]


def _opt_val(d: _SectionDict, key: str) -> Optional[str]:
    e = d.get(key)
    return e[1] if e else None


def _opt_line(d: _SectionDict, key: str) -> Optional[str]:
    e = d.get(key)
    return e[0] if e else None


def _build_info(public: _SectionDict, group_raws: list[_SectionDict]) -> HdrInfo:
    info = HdrInfo()
    info.format_version     = _req(public, "FormatVersion")
    info.model              = _req(public, "Model")
    info.endian             = _req(public, "Endian")
    info.data_format        = _req(public, "DataFormat")
    info.group_number       = int(_req(public, "GroupNumber"))
    info.trace_total_number = int(_req(public, "TraceTotalNumber"))
    info.data_offset        = int(_req(public, "DataOffset"))

    for g_idx, gd in enumerate(group_raws):
        grp = _build_group(g_idx, gd)
        info.groups.append(grp)

    return info


def _build_group(g_idx: int, gd: _SectionDict) -> GroupInfo:
    """Parse one $Group section dict into a GroupInfo."""
    grp = GroupInfo()
    grp.trace_number = int(_req(gd, "TraceNumber"))
    grp.block_number = int(_req(gd, "BlockNumber"))
    n = grp.trace_number
    nb = grp.block_number
    grp.traces = [TraceInfo() for _ in range(n)]

    _assign_str  (grp.traces, n, _req(gd, "TraceName"),   "name")
    _assign_int  (grp.traces, n, _req(gd, "BlockSize"),   "block_size")
    _assign_float(grp.traces, n, _req(gd, "VResolution"), "v_resolution")
    _assign_float(grp.traces, n, _req(gd, "VOffset"),     "v_offset")

    # --- VDataType: parse codes and capture column positions ---
    vdtype_entry = gd.get("VDataType")
    if not vdtype_entry:
        raise ValueError(f".hdr Group{g_idx + 1} missing VDataType")
    vdtype_line, vdtype_val = vdtype_entry
    col_pos = _vdtype_col_positions(vdtype_line)
    for i, tok in enumerate(vdtype_val.split()[:n]):
        try:
            grp.traces[i].v_data_type = _parse_vdtype(tok)
        except ValueError:
            pass

    # --- Column-aligned string fields ---
    _assign_col_str(grp.traces, n, _opt_line(gd, "VUnit"), col_pos, "VUnit", "v_unit")
    _assign_col_str(grp.traces, n, _opt_line(gd, "HUnit"), col_pos, "HUnit", "h_unit")

    # --- Column-aligned optional integer fields ---
    _assign_col_int(grp.traces, n, _opt_line(gd, "VPlusOverData"),  col_pos, "v_plus_over")
    _assign_col_int(grp.traces, n, _opt_line(gd, "VMinusOverData"), col_pos, "v_minus_over")
    _assign_col_int(grp.traces, n, _opt_line(gd, "VIllegalData"),   col_pos, "v_illegal")
    _assign_col_int(grp.traces, n, _opt_line(gd, "VMaxData"),       col_pos, "v_max")
    _assign_col_int(grp.traces, n, _opt_line(gd, "VMinData"),       col_pos, "v_min")

    # --- HResolution / HOffset ---
    _assign_float(grp.traces, n, _req(gd, "HResolution"), "h_resolution")
    _assign_float(grp.traces, n, _req(gd, "HOffset"),     "h_offset")

    # --- Per-block Date / Time ---
    for tr in grp.traces:
        tr.dates = [""] * nb
        tr.times = [""] * nb

    # Files with 1 block use key "Date" (or occasionally "Date1").
    # Files with >1 blocks use "Date1", "Date2", ...
    # Newer DL750 (v6.22+) may write only "Date" even with multiple blocks.
    for b_idx in range(nb):
        if nb == 1:
            d_key = "Date"  if "Date"  in gd else "Date1"
            t_key = "Time"  if "Time"  in gd else "Time1"
        else:
            d_key = f"Date{b_idx + 1}"
            t_key = f"Time{b_idx + 1}"
            if b_idx == 0 and d_key not in gd:
                d_key = "Date"
            if b_idx == 0 and t_key not in gd:
                t_key = "Time"

        d_val = _opt_val(gd, d_key)
        t_val = _opt_val(gd, t_key)
        if d_val:
            for i, tok in enumerate(d_val.split()[:n]):
                grp.traces[i].dates[b_idx] = tok
        if t_val:
            for i, tok in enumerate(t_val.split()[:n]):
                grp.traces[i].times[b_idx] = tok

    return grp


# ---------------------------------------------------------------------------
# Trace-level assignment helpers (module-level to avoid cell-var-from-loop)
# ---------------------------------------------------------------------------

def _assign_str(traces: list[TraceInfo], n: int, val: str, attr: str) -> None:
    for i, tok in enumerate(val.split()[:n]):
        setattr(traces[i], attr, tok)


def _assign_float(traces: list[TraceInfo], n: int, val: str, attr: str) -> None:
    for i, tok in enumerate(val.split()[:n]):
        setattr(traces[i], attr, float(tok))


def _assign_int(traces: list[TraceInfo], n: int, val: str, attr: str) -> None:
    for i, tok in enumerate(val.split()[:n]):
        setattr(traces[i], attr, int(tok))


def _assign_col_str(
    traces: list[TraceInfo],
    n: int,
    line: Optional[str],
    col_pos: list[int],
    key: str,
    attr: str,
) -> None:
    vals = _col_aligned_values(line, col_pos, n)
    for i, val in enumerate(vals):
        if val and val != key:
            setattr(traces[i], attr, val)


def _assign_col_int(
    traces: list[TraceInfo],
    n: int,
    line: Optional[str],
    col_pos: list[int],
    attr: str,
) -> None:
    vals = _col_aligned_values(line, col_pos, n)
    for i, val in enumerate(vals):
        v = _try_int(val)
        if v is not None:
            setattr(traces[i], attr, v)
