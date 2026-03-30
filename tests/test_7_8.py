"""Synthetic tests for Rigol 7000/8000 `.bin` waveform parsing."""

import struct
from pathlib import Path

import numpy as np
import pytest
import RigolWFM.mso7000_8000
import RigolWFM.wfm

import RigolWFM.rigol_7000_8000_bin


def _padded_ascii(text, size):
    """Return a null-padded ASCII field of exactly `size` bytes."""
    raw = text.encode("ascii")
    return raw[:size] + b"\x00" * max(size - len(raw), 0)


def _waveform_record(label, model, values, dt, xorigin):
    """Build one synthetic 7000/8000 waveform record."""
    values = np.asarray(values, dtype="<f4")
    header = struct.pack(
        "<IIIII f d d d II 16s 16s 24s 16s",
        128,
        1,
        1,
        len(values),
        0,
        float(len(values) * dt),
        -xorigin,
        dt,
        xorigin,
        2,
        1,
        _padded_ascii("2026-03-24", 16),
        _padded_ascii("12:00:00", 16),
        _padded_ascii(f"{model}:TEST0001", 24),
        _padded_ascii(label, 16),
    )
    data = values.tobytes()
    data_header = struct.pack("<IHHI", 12, 1, 4, len(data))
    return header + data_header + data


def _write_synthetic_bin(path, model, logic=False):
    """Write a synthetic UltraVision `.bin` file to `path`."""
    ch1 = np.array([0.0, 0.5, 1.0, 0.5], dtype=np.float32)
    ch2 = np.array([1.0, 0.0, -1.0, 0.0], dtype=np.float32)
    dt = 2.5e-9
    xorigin = 7.5e-9

    records = [
        _waveform_record("CH1", model, ch1, dt, xorigin),
        _waveform_record("CH2", model, ch2, dt, xorigin),
    ]

    if logic:
        header = struct.pack(
            "<IIIII f d d d II 16s 16s 24s 16s",
            128,
            6,
            1,
            4,
            0,
            float(4 * dt),
            -xorigin,
            dt,
            xorigin,
            2,
            3,
            _padded_ascii("2026-03-24", 16),
            _padded_ascii("12:00:00", 16),
            _padded_ascii(f"{model}:TEST0001", 24),
            _padded_ascii("LA1", 16),
        )
        data = bytes([0, 1, 0, 1])
        records.append(header + struct.pack("<IHHI", 12, 6, 1, len(data)) + data)

    payload = b"".join(records)
    file_header = struct.pack("<2s2sII", b"RG", b"01", 12 + len(payload), len(records))
    path.write_bytes(file_header + payload)
    return dt, xorigin


@pytest.mark.parametrize(
    "_family, model",
    [("7000", "MSO7034"), ("8000", "MSO8204")],
)
def test_bin7000_8000_low_level_parser_reads_synthetic_file(tmp_path, _family, model):
    """The shared parser should honor the documented 128-byte header layout."""
    path = Path(tmp_path) / f"{model}.bin"
    dt, xorigin = _write_synthetic_bin(path, model)

    waveform = RigolWFM.rigol_7000_8000_bin.Rigol70008000Bin.from_file(str(path))

    assert waveform.file_header.cookie == b"RG"
    assert waveform.file_header.version == "01"
    assert waveform.file_header.n_waveforms == 2
    assert waveform.waveforms[0].wfm_header.header_size == 128
    assert waveform.waveforms[0].wfm_header.n_pts == 4
    assert waveform.waveforms[0].wfm_header.x_increment == pytest.approx(dt)
    assert waveform.waveforms[0].wfm_header.x_origin == pytest.approx(xorigin)
    assert waveform.waveforms[0].data_header.header_size == 12
    assert waveform.waveforms[0].data_header.bytes_per_point == 4
    assert waveform.waveforms[0].data_header.buffer_size == 16


@pytest.mark.parametrize(
    "family, model",
    [("7000", "MSO7034"), ("8000", "MSO8204")],
)
def test_wfm_from_file_supports_shared_7000_8000_adapter(tmp_path, family, model):
    """The normalized adapter should expose calibrated channels and timing."""
    path = Path(tmp_path) / f"{model}.bin"
    dt, xorigin = _write_synthetic_bin(path, model)

    waveform = RigolWFM.wfm.Wfm.from_file(str(path), family)

    assert waveform.header_name == model
    assert waveform.parser_name == "bin7000_8000"
    assert len(waveform.channels) == 2
    assert waveform.channels[0].times[0] == pytest.approx(-xorigin)
    assert waveform.channels[0].times[1] - waveform.channels[0].times[0] == pytest.approx(dt)
    assert waveform.channels[0].volts[:4] == pytest.approx([0.0, 0.5, 1.0, 0.5])
    assert waveform.channels[1].volts[:4] == pytest.approx([1.0, 0.0, -1.0, 0.0])


@pytest.mark.parametrize("model", ["MSO7034", "MSO8204"])
def test_mso7000_8000_rejects_logic_records_for_now(tmp_path, model):
    """Logic records should fail fast until we have fixtures for them."""
    path = Path(tmp_path) / f"{model}-logic.bin"
    _write_synthetic_bin(path, model, logic=True)

    with pytest.raises(ValueError, match="logic waveform record"):
        RigolWFM.mso7000_8000.from_file(str(path))
