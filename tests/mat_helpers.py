"""Small MATLAB v5 reader for the repo's numeric-only export tests."""

from pathlib import Path
import struct

import numpy as np


def _pad8(length: int) -> int:
    """Return the trailing padding needed for an 8-byte MAT alignment."""
    return (-length) % 8


def load_simple_mat_v5(source: bytes | bytearray | str | Path) -> dict[str, np.ndarray]:
    """Load the repo's simple numeric-only MATLAB v5 files into NumPy arrays."""
    if isinstance(source, (str, Path)):
        payload = Path(source).read_bytes()
    else:
        payload = bytes(source)

    if len(payload) < 128:
        raise ValueError("MAT payload is too short.")
    if payload[126:128] != b"IM":
        raise ValueError("Only little-endian MATLAB v5 files are supported.")

    out: dict[str, np.ndarray] = {}
    offset = 128
    while offset + 8 <= len(payload):
        data_type, size = struct.unpack_from("<II", payload, offset)
        offset += 8
        if data_type == 0 and size == 0:
            break
        if data_type != 14:
            raise ValueError(f"Unexpected MAT element type {data_type}; expected miMATRIX.")

        matrix = payload[offset : offset + size]
        offset += size + _pad8(size)

        inner = 0

        def _read_element(expected_type: int) -> bytes:
            nonlocal inner
            elem_type, elem_size = struct.unpack_from("<II", matrix, inner)
            inner += 8
            if elem_type != expected_type:
                raise ValueError(f"Unexpected MAT subelement type {elem_type}; expected {expected_type}.")
            data = matrix[inner : inner + elem_size]
            inner += elem_size + _pad8(elem_size)
            return data

        _flags = _read_element(6)
        dims_raw = _read_element(5)
        dims = struct.unpack("<" + ("i" * (len(dims_raw) // 4)), dims_raw)
        name = _read_element(1).decode("ascii")

        real_type, real_size = struct.unpack_from("<II", matrix, inner)
        inner += 8
        real = matrix[inner : inner + real_size]

        if real_type == 9:
            array = np.frombuffer(real, dtype="<f8").copy()
        elif real_type == 2:
            array = np.frombuffer(real, dtype=np.uint8).copy()
        else:
            raise ValueError(f"Unsupported MAT real data type {real_type}.")

        if not dims:
            out[name] = array
            continue

        shape = tuple(int(dim) for dim in dims)
        array = array.reshape(shape, order="F")
        if array.shape == (1, 1):
            array = array.reshape(1)
        elif len(array.shape) == 2 and array.shape[1] == 1:
            array = array[:, 0]
        out[name] = array

    return out
