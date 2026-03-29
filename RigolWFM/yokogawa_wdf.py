"""
Convert Yokogawa DL850/DL850V .WDF files to .hdr + .wvf pairs.

**Status: Not implemented.**

The DL850 WDF format is a proprietary binary format whose structure is not
publicly documented.  Yokogawa's only published interface is ``DL850.dll``,
a Windows-only shared library described in IM B8074XP-01EN.  Because that
DLL is Windows-only and not redistributable, this module currently raises
:exc:`NotImplementedError` for all operations.

If the binary layout of ``.WDF`` files is ever reverse-engineered or
officially documented, this module is the intended home for a
platform-independent parser and the ``.hdr`` + ``.wvf`` writer.

Output format goal
------------------
The target ``.hdr`` / ``.wvf`` pair follows the WVF File Access Toolkit
format (IM 707713-61E), which is already parsed by ``yokogawa_wvf.ksy``::

    $PublicInfo
    FormatVersion 1.11
    Model DL850
    Endian Ltl
    DataFormat TRACE
    GroupNumber 1
    TraceTotalNumber <N>
    DataOffset 0

    $Group1
    TraceNumber <N>
    BlockNumber <B>

    TraceName    CH1 CH2 ...
    BlockSize    <S> <S> ...
    VResolution  <r> <r> ...
    VOffset      <o> <o> ...
    VDataType    IS2 IS2 ...
    VUnit        V   V   ...
    ...

The ``.wvf`` file contains raw little-endian 16-bit samples (IS2/IU2 per
trace) in TRACE layout (all history blocks of each trace written
contiguously), with no leading padding (DataOffset = 0).

References:
    Yokogawa Electric Corporation, "Model DL850/DL850V WDF File Access
    Library User's Manual", IM B8074XP-01EN, 1st Edition, 2010.
"""
from __future__ import annotations

from typing import Optional


def wdf_to_wvf(
    wdf_path: str,
    output_dir: Optional[str] = None,
    block_index: Optional[int] = None,
) -> tuple[str, str]:
    """Convert a Yokogawa DL850 ``.WDF`` file to a ``.hdr`` + ``.wvf`` pair.

    Args:
        wdf_path:    Path to the input ``.WDF`` file.
        output_dir:  Directory for the output files.  Defaults to the same
                     directory as the input file.
        block_index: When given, export only this single history block
                     (0-origin, where 0 = earliest capture).  By default
                     all history blocks are exported.

    Returns:
        ``(hdr_path, wvf_path)`` — paths to the two output files.

    Raises:
        NotImplementedError: Always.  The WDF binary format is not
            publicly documented and cannot be parsed without
            ``DL850.dll`` (a Windows-only, non-redistributable library).
    """
    raise NotImplementedError(
        "WDF parsing is not implemented: the Yokogawa DL850 WDF binary "
        "format is proprietary and undocumented.  Use the DOS/Windows "
        "utility supplied by Yokogawa to convert .WDF files to .hdr + .wvf "
        "pairs, then open the .wvf file with this library."
    )
