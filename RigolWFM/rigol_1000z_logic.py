"""Helpers for DS1000Z/MSO-style mixed analog + logic waveform payloads.

The checked-in DS1000Z parser models the raw sample payload as one opaque byte
array because the documented analog `.wfm` format does not describe the logic
analyzer variant.  Local captures used while developing this helper show a
repeatable mixed layout:

* logic-only captures store two interleaved logic byte lanes
* mixed captures with one enabled analog channel store four interleaved lanes
  where lanes 0 and 2 behave like logic bytes and lane 1 behaves like the
  analog trace

This module keeps that interpretation isolated and conservative.  When the byte
pattern does not match the observed logic-capture layout, callers fall back to
the long-standing analog-only path.
"""

from dataclasses import dataclass

import numpy as np
import numpy.typing as npt


@dataclass(frozen=True)
class Rigol1000zSplit:
    """Best-effort split of a Z-series raw payload into analog and logic lanes."""

    analog_lanes: tuple[npt.NDArray[np.uint8], ...]
    logic_lanes: tuple[npt.NDArray[np.uint8], ...]
    inferred_stride: int
    uses_logic_layout: bool

    @property
    def logic_low(self) -> npt.NDArray[np.uint8] | None:
        """Return the first extracted logic byte lane, if present."""
        return self.logic_lanes[0] if self.logic_lanes else None

    @property
    def logic_high(self) -> npt.NDArray[np.uint8] | None:
        """Return the second extracted logic byte lane, if present."""
        return self.logic_lanes[1] if len(self.logic_lanes) > 1 else None

    @property
    def logic_low_mask(self) -> int:
        """Bitwise OR of all bytes in the first logic lane."""
        if self.logic_low is None or self.logic_low.size == 0:
            return 0
        return int(np.bitwise_or.reduce(self.logic_low.astype(np.uint8)))

    @property
    def logic_high_mask(self) -> int:
        """Bitwise OR of all bytes in the second logic lane."""
        if self.logic_high is None or self.logic_high.size == 0:
            return 0
        return int(np.bitwise_or.reduce(self.logic_high.astype(np.uint8)))


def active_bits(values: npt.NDArray[np.uint8]) -> tuple[int, ...]:
    """Return the bit numbers that are ever asserted in a logic byte lane."""
    if values.size == 0:
        return ()

    mask = int(np.bitwise_or.reduce(values.astype(np.uint8)))
    return tuple(bit for bit in range(8) if mask & (1 << bit))


def bit_trace(values: npt.NDArray[np.uint8], bit: int) -> npt.NDArray[np.uint8]:
    """Return a single logic bit as a 0/1 uint8 trace."""
    return ((values >> np.uint8(bit)) & np.uint8(1)).astype(np.uint8)


def observed_bit_traces(split: Rigol1000zSplit) -> dict[str, npt.NDArray[np.uint8]]:
    """Return active logic-bit traces keyed by observed lane/bit labels."""
    traces: dict[str, npt.NDArray[np.uint8]] = {}
    for lane_index, lane in enumerate(split.logic_lanes):
        for bit in active_bits(lane):
            traces[f"L{lane_index}.B{bit}"] = bit_trace(lane, bit)
    return traces


def transition_count(values: npt.NDArray[np.uint8]) -> int:
    """Return the number of sample-to-sample transitions in a byte or bit trace."""
    if values.size < 2:
        return 0
    return int(np.sum(values[1:] != values[:-1]))


def lane_agreement(values_a: npt.NDArray[np.uint8], values_b: npt.NDArray[np.uint8]) -> float:
    """Return the fraction of samples where two lanes have identical bytes."""
    if values_a.size == 0 or values_b.size == 0:
        return 0.0

    count = min(values_a.size, values_b.size)
    return float(np.mean(values_a[:count] == values_b[:count]))


def _transition_positions(values: npt.NDArray[np.uint8]) -> npt.NDArray[np.int64]:
    """Return sample indices where a byte lane changes value."""
    if values.size < 2:
        return np.array([], dtype=np.int64)
    return np.flatnonzero(values[1:] != values[:-1]).astype(np.int64)


def looks_like_mirrored_low_byte(
    values_a: npt.NDArray[np.uint8],
    values_b: npt.NDArray[np.uint8],
) -> bool:
    """Return True when two observed byte lanes behave like mirrored D7-D0 data.

    The local DS1074Z/MSO captures under study expose two logic-looking lanes
    whose active bits and edge positions match almost perfectly.  That pattern
    looks more like a duplicated low-byte stream than two independent
    `D7-D0` / `D15-D8` byte arrays.
    """
    bits_a = active_bits(values_a)
    bits_b = active_bits(values_b)
    if not bits_a or bits_a != bits_b:
        return False

    if lane_agreement(values_a, values_b) < 0.9999:
        return False

    transitions_a = _transition_positions(values_a)
    transitions_b = _transition_positions(values_b)
    if len(transitions_a) == 0 or len(transitions_a) != len(transitions_b):
        return False

    deltas = np.abs(transitions_a - transitions_b)
    return bool(np.max(deltas) <= 1 and np.mean(deltas) <= 0.5)


def named_digital_traces(split: Rigol1000zSplit) -> tuple[dict[str, npt.NDArray[np.uint8]], str]:
    """Return named digital traces plus a short description of the mapping."""
    if not split.logic_lanes:
        return {}, ""

    if len(split.logic_lanes) >= 2 and looks_like_mirrored_low_byte(split.logic_lanes[0], split.logic_lanes[1]):
        traces = {f"D{bit}": bit_trace(split.logic_lanes[0], bit) for bit in active_bits(split.logic_lanes[0])}
        return traces, "mirrored D7-D0 byte lanes"

    traces = {f"D{bit}": bit_trace(split.logic_lanes[0], bit) for bit in active_bits(split.logic_lanes[0])}
    if len(split.logic_lanes) >= 2:
        for bit in active_bits(split.logic_lanes[1]):
            traces[f"D{8 + bit}"] = bit_trace(split.logic_lanes[1], bit)
        return traces, "D7-D0 + D15-D8 byte lanes"

    return traces, "single D7-D0 byte lane"


def _looks_like_single_bit_logic(values: npt.NDArray[np.uint8]) -> bool:
    """Return True for byte lanes that behave like sparse logic bitmasks.

    This heuristic intentionally targets the captures currently under study:
    one or a few active logic lines produce a very small set of byte values,
    typically zero plus one or more single-bit masks.
    """
    if values.size == 0:
        return False

    unique = np.unique(values)
    if unique.size > 8:
        return False

    return all(value == 0 or (int(value) & (int(value) - 1)) == 0 for value in unique)


def split_raw_payload(
    raw_bytes: bytes | bytearray | memoryview | npt.NDArray[np.uint8], analog_channels: int
) -> Rigol1000zSplit:
    """Return a best-effort split of a DS1000Z raw payload.

    Args:
        raw_bytes: Raw bytes from the `.wfm` payload.
        analog_channels: Number of enabled analog channels from the header mask.

    Returns:
        A :class:`Rigol1000zSplit`.  When the layout does not look like one of
        the observed logic-analyzer variants, ``uses_logic_layout`` is False and
        ``analog_lanes`` / ``logic_lanes`` are empty so callers can fall back
        to the legacy analog-only extraction path.
    """
    raw = np.frombuffer(raw_bytes, dtype=np.uint8) if not isinstance(raw_bytes, np.ndarray) else raw_bytes

    if analog_channels == 0 and raw.size % 2 == 0:
        logic_a = raw[0::2].copy()
        logic_b = raw[1::2].copy()
        if _looks_like_single_bit_logic(logic_a) and _looks_like_single_bit_logic(logic_b):
            return Rigol1000zSplit(
                analog_lanes=(), logic_lanes=(logic_a, logic_b), inferred_stride=2, uses_logic_layout=True
            )

    if analog_channels == 1 and raw.size % 4 == 0:
        lanes = tuple(raw[index::4].copy() for index in range(4))
        if _looks_like_single_bit_logic(lanes[0]) and _looks_like_single_bit_logic(lanes[2]):
            return Rigol1000zSplit(
                analog_lanes=(lanes[1],),
                logic_lanes=(lanes[0], lanes[2]),
                inferred_stride=4,
                uses_logic_layout=True,
            )

    return Rigol1000zSplit(
        analog_lanes=(), logic_lanes=(), inferred_stride=max(analog_channels, 1), uses_logic_layout=False
    )
