"""Adapter layer for Rigol MSO5074 binary waveform exports.

The MSO5074 firmware writes a non-standard variant of the MSO5000 `.bin`
format with several bugs:

  * The waveform header is 144 bytes (not the standard 140).
  * Nearly all metadata fields contain wrong/default values:
      file_size      = 4168 (always)
      n_waveforms    = 1 (always, even for multi-channel captures)
      n_pts          = 1000 (always)
      x_increment    = 1e-12 (always)
      buffer_size    = 4000 (always)
      bytes_per_point = 4 (always, but data is actually uint8)
      waveform_label = "" (always empty)
  * Sample data is raw uint8 ADC counts, not calibrated float32 volts.
  * Multi-channel captures are stored as concatenated RG01 blocks in a single
    file.  The channel order matches the physical channel order (CH1 first).

This adapter corrects for all of the above.  Voltage values are expressed in
approximate volts using a default 1 V/div scale because the file contains no
calibration coefficients.
"""

from __future__ import annotations

import struct
import warnings
import numpy as np

from RigolWFM.mso5000 import (
    ChannelHeader,
    Mso5000Waveform,
    _model_from_frame,
)

# Each RG01 block starts with these four magic bytes.
_RG01_MAGIC = b"RG01"

# Every MSO5074 block has a fixed overhead before sample data:
#   12 bytes file header  +  144 bytes waveform header  +  12 bytes data header
_BLOCK_OVERHEAD = 168

# Waveform-header field offsets relative to the start of the waveform header.
_WH_HEADER_SIZE = 0
_WH_X_DISPLAY_RANGE = 20  # f4
_WH_X_ORIGIN = 40  # f8
_WH_Y_UNITS = 52  # u4
_WH_FRAME_STRING = 88  # 24-byte ASCII string
_WH_WAVEFORM_LABEL = 112  # 16-byte ASCII string

# Default voltage scale applied when no calibration data is available.
_ADC_MIDPOINT = 127.0  # midpoint of the 8-bit unsigned ADC range
_COUNTS_PER_VOLT = 25.0  # approximate ADC counts per volt (1 V/div, 25 cts/div)


def _find_block_offsets(data: bytes) -> list[int]:
    """Return byte offsets of all RG01 magic markers in *data*."""
    offsets: list[int] = []
    pos = 0
    while True:
        idx = data.find(_RG01_MAGIC, pos)
        if idx == -1:
            break
        offsets.append(idx)
        pos = idx + 1
    return offsets


def _parse_waveform_header(data: bytes, block_offset: int) -> dict[str, object]:
    """Return a dict of waveform-header fields for the block at *block_offset*."""
    wh = block_offset + 12  # skip the 12-byte file header
    header_size = struct.unpack_from("<I", data, wh + _WH_HEADER_SIZE)[0]
    x_display_range = struct.unpack_from("<f", data, wh + _WH_X_DISPLAY_RANGE)[0]
    x_origin = struct.unpack_from("<d", data, wh + _WH_X_ORIGIN)[0]
    y_units = struct.unpack_from("<I", data, wh + _WH_Y_UNITS)[0]
    frame_string = (
        data[wh + _WH_FRAME_STRING : wh + _WH_FRAME_STRING + 24].rstrip(b"\x00").decode("ascii", errors="replace")
    )
    waveform_label = (
        data[wh + _WH_WAVEFORM_LABEL : wh + _WH_WAVEFORM_LABEL + 16].rstrip(b"\x00").decode("ascii", errors="replace")
    )
    return {
        "header_size": header_size,
        "x_display_range": x_display_range,
        "x_origin": x_origin,
        "y_units": y_units,
        "frame_string": frame_string,
        "waveform_label": waveform_label,
    }


def from_file(file_name: str) -> Mso5000Waveform:
    """Parse a Rigol MSO5074 `.bin` file and normalize it for `Wfm.from_file()`.

    The MSO5074 firmware stores nearly all metadata fields incorrectly.  This
    function recovers what it can (x_display_range, frame string) and derives
    the rest (actual sample count, x_increment) from the file layout itself.
    Voltage values are approximate: 1 V/div with 25 ADC counts per division.
    """
    with open(file_name, "rb") as fh:
        raw_bytes = fh.read()

    if not raw_bytes.startswith(b"RG"):
        raise ValueError(f"Not a Rigol binary file: {file_name}")

    warnings.warn(
        "MSO5074 voltage values are approximate (1 V/div, no calibration data in file).",
        UserWarning,
        stacklevel=2,
    )

    offsets = _find_block_offsets(raw_bytes)
    if not offsets:
        raise ValueError(f"No RG01 blocks found in {file_name}")

    obj = Mso5000Waveform()
    header = obj.header
    header.cookie = raw_bytes[0:2].decode("ascii")
    header.version = raw_bytes[2:4].decode("ascii")
    header.n_waveforms = len(offsets)
    header.ch = [ChannelHeader(f"CH{i + 1}", enabled=False) for i in range(4)]

    for slot, block_off in enumerate(offsets[:4]):
        wh_fields = _parse_waveform_header(raw_bytes, block_off)

        data_start = block_off + _BLOCK_OVERHEAD
        data_end = offsets[slot + 1] if (slot + 1) < len(offsets) else len(raw_bytes)

        samples = np.frombuffer(raw_bytes[data_start:data_end], dtype=np.uint8).copy()
        actual_n_pts = len(samples)
        if actual_n_pts == 0:
            continue

        # Derive x_increment from x_display_range — the only reliable timing field.
        x_display_range = float(wh_fields["x_display_range"])  # type: ignore[arg-type]
        if x_display_range > 0.0 and actual_n_pts > 1:
            x_increment = x_display_range / actual_n_pts
        else:
            x_increment = 1e-9 / max(actual_n_pts, 1)

        if header.n_pts == 0:
            header.n_pts = actual_n_pts
            header.x_increment = x_increment
            header.x_origin = float(wh_fields["x_origin"])  # type: ignore[arg-type]
            header.x_display_range = x_display_range
            header.model = _model_from_frame(str(wh_fields["frame_string"]))

        # Convert raw uint8 ADC counts to approximate volts.
        # No calibration coefficients are present in the file.
        volts = (samples.astype(np.float64) - _ADC_MIDPOINT) / _COUNTS_PER_VOLT

        ch_name = str(wh_fields["waveform_label"]) or f"CH{slot + 1}"
        channel = ChannelHeader(ch_name, enabled=True, unit_code=1)  # 1 = V
        channel.volt_per_division = 1.0

        header.ch[slot] = channel
        header.channel_data[slot] = volts
        header.raw_data[slot] = samples

    return obj
