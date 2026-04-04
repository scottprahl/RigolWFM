"""Tests for best-effort DS1000Z/MSO-style logic-lane extraction."""

from pathlib import Path
from typing import Any

import numpy as np
import pytest

import RigolWFM.rigol_1000z_logic
import RigolWFM.wfm
import RigolWFM.rigol_1000z_wfm

_Rigol1000zWfm: Any = RigolWFM.rigol_1000z_wfm.Rigol1000zWfm  # type: ignore[attr-defined]


def _interleave(*lanes: np.ndarray) -> bytes:
    """Return byte-wise interleaving of equally sized uint8 lanes."""
    assert lanes
    count = len(lanes[0])
    assert all(len(lane) == count for lane in lanes)
    raw = np.empty(count * len(lanes), dtype=np.uint8)
    for index, lane in enumerate(lanes):
        raw[index:: len(lanes)] = lane
    return raw.tobytes()


def test_split_raw_payload_detects_logic_only_capture():
    """Two sparse interleaved bitmask lanes should be treated as logic bytes."""
    logic_a = np.array([0, 64, 0, 64, 64, 0], dtype=np.uint8)
    logic_b = np.array([0, 64, 64, 0, 64, 0], dtype=np.uint8)

    split = RigolWFM.rigol_1000z_logic.split_raw_payload(_interleave(logic_a, logic_b), analog_channels=0)

    assert split.uses_logic_layout
    assert split.inferred_stride == 2
    assert split.analog_lanes == ()
    np.testing.assert_array_equal(split.logic_low, logic_a)
    np.testing.assert_array_equal(split.logic_high, logic_b)
    assert split.logic_low_mask == 0x40
    assert split.logic_high_mask == 0x40


def test_split_raw_payload_detects_mixed_analog_logic_capture():
    """A four-lane mixed payload should expose analog lane 1 and logic lanes 0/2."""
    logic_low = np.array([0, 64, 64, 0, 64, 0], dtype=np.uint8)
    analog_a = np.array([115, 116, 115, 116, 115, 116], dtype=np.uint8)
    logic_high = np.array([0, 64, 0, 64, 64, 0], dtype=np.uint8)
    analog_b = np.array([116, 115, 116, 115, 116, 115], dtype=np.uint8)

    split = RigolWFM.rigol_1000z_logic.split_raw_payload(
        _interleave(logic_low, analog_a, logic_high, analog_b),
        analog_channels=1,
    )

    assert split.uses_logic_layout
    assert split.inferred_stride == 4
    assert len(split.analog_lanes) == 1
    np.testing.assert_array_equal(split.analog_lanes[0], analog_a)
    np.testing.assert_array_equal(split.logic_low, logic_low)
    np.testing.assert_array_equal(split.logic_high, logic_high)
    assert split.logic_low_mask == 0x40
    assert split.logic_high_mask == 0x40


def test_named_digital_traces_collapse_mirrored_low_byte_lanes():
    """Near-identical observed lanes should map to one set of D0-D7 names."""
    logic_a = np.array([0, 0, 64, 64, 0, 0, 64, 64], dtype=np.uint8)
    logic_b = np.array([0, 0, 64, 64, 0, 0, 64, 64], dtype=np.uint8)
    split = RigolWFM.rigol_1000z_logic.split_raw_payload(_interleave(logic_a, logic_b), analog_channels=0)

    traces, mapping = RigolWFM.rigol_1000z_logic.named_digital_traces(split)

    assert mapping == "mirrored D7-D0 byte lanes"
    assert list(traces) == ["D6"]
    np.testing.assert_array_equal(traces["D6"], np.array([0, 0, 1, 1, 0, 0, 1, 1], dtype=np.uint8))


def test_named_digital_traces_map_distinct_second_lane_to_d8_d15():
    """Independent second-lane bits should map into the upper digital byte."""
    split = RigolWFM.rigol_1000z_logic.Rigol1000zSplit(
        analog_lanes=(),
        logic_lanes=(
            np.array([0, 2, 2, 0, 0, 2], dtype=np.uint8),
            np.array([0, 0, 8, 8, 0, 0], dtype=np.uint8),
        ),
        inferred_stride=2,
        uses_logic_layout=True,
    )

    traces, mapping = RigolWFM.rigol_1000z_logic.named_digital_traces(split)

    assert mapping == "D7-D0 + D15-D8 byte lanes"
    assert list(traces) == ["D1", "D11"]
    np.testing.assert_array_equal(traces["D1"], np.array([0, 1, 1, 0, 0, 1], dtype=np.uint8))
    np.testing.assert_array_equal(traces["D11"], np.array([0, 0, 1, 1, 0, 0], dtype=np.uint8))


_LOCAL_TEST1 = Path("tests/files/wfm/DS1074Z-C.wfm")
_LOCAL_TEST3 = Path("tests/files/wfm/DS1074Z-D.wfm")
_CHECKED_IN_LOGIC_ONLY = Path("tests/files/wfm/DS1074Z-C.wfm")
_skip_no_local_logic_samples = pytest.mark.skipif(
    not (_LOCAL_TEST1.exists() and _LOCAL_TEST3.exists()),
    reason="Local DS1000Z logic sample files are not present in the repo root",
)


def _transition_count(values: np.ndarray) -> int:
    """Return the number of byte-to-byte value transitions in a lane."""
    return int(np.sum(values[1:] != values[:-1]))


def _run_states_and_lengths(values: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Return alternating logic states plus their run lengths."""
    edges = np.flatnonzero(values[1:] != values[:-1]) + 1
    states = np.concatenate(([values[0]], values[edges]))
    lengths = np.diff(np.concatenate(([0], edges, [len(values)])))
    return states.astype(np.uint8), lengths.astype(np.int64)


def test_checked_in_z_logic_only_fixture_exposes_observed_logic_traces():
    """The checked-in DS1074Z logic-only fixture should map to named digital traces."""
    waveform = RigolWFM.wfm.Wfm.from_file(str(_CHECKED_IN_LOGIC_ONLY), "Z")

    assert waveform.channels == []
    assert waveform.firmware == "00.04.05.SP2"
    assert waveform.logic_split is not None
    assert waveform.logic_split.uses_logic_layout
    assert waveform.logic_mapping == "mirrored D7-D0 byte lanes"
    assert list(waveform.logic_channels) == ["D6"]
    assert list(waveform.logic_observed_channels) == ["L0.B6", "L1.B6"]
    assert waveform.logic_times is not None
    assert len(waveform.logic_times) == len(waveform.logic_channels["D6"])
    np.testing.assert_array_equal(np.unique(waveform.logic_channels["D6"]), np.array([0, 1], dtype=np.uint8))

    description = waveform.describe()
    assert "Logic:" in description
    assert "Mapping      = mirrored D7-D0 byte lanes" in description
    assert "Traces       = [D6]" in description
    assert "Observed     = [L0.B6, L1.B6]" in description


@_skip_no_local_logic_samples
def test_local_z_logic_samples_extract_sparse_logic_lanes():
    """The local DS1074Z logic samples should expose the same active bit and edges."""
    logic_only = _Rigol1000zWfm.from_file(str(_LOCAL_TEST1))
    mixed = _Rigol1000zWfm.from_file(str(_LOCAL_TEST3))

    split_logic = RigolWFM.rigol_1000z_logic.split_raw_payload(logic_only.data.raw, analog_channels=0)
    split_mixed = RigolWFM.rigol_1000z_logic.split_raw_payload(mixed.data.raw, analog_channels=1)

    assert split_logic.uses_logic_layout
    assert split_mixed.uses_logic_layout
    assert split_logic.logic_low_mask == 0x40
    assert split_logic.logic_high_mask == 0x40
    assert split_mixed.logic_low_mask == 0x40
    assert split_mixed.logic_high_mask == 0x40
    assert _transition_count(split_logic.logic_low) == _transition_count(split_mixed.logic_low)
    assert _transition_count(split_logic.logic_high) == _transition_count(split_mixed.logic_high)


@_skip_no_local_logic_samples
def test_local_z_logic_samples_expose_matching_observed_trace_labels():
    """The local logic-only and mixed captures should expose the same D6 event sequence."""
    logic_only = RigolWFM.wfm.Wfm.from_file(str(_LOCAL_TEST1), "Z")
    mixed = RigolWFM.wfm.Wfm.from_file(str(_LOCAL_TEST3), "Z")

    assert logic_only.logic_mapping == "mirrored D7-D0 byte lanes"
    assert mixed.logic_mapping == "mirrored D7-D0 byte lanes"
    assert list(logic_only.logic_channels) == ["D6"]
    assert list(mixed.logic_channels) == ["D6"]
    assert _transition_count(logic_only.logic_channels["D6"]) == _transition_count(mixed.logic_channels["D6"])

    logic_states, logic_lengths = _run_states_and_lengths(logic_only.logic_channels["D6"])
    mixed_states, mixed_lengths = _run_states_and_lengths(mixed.logic_channels["D6"])

    np.testing.assert_array_equal(logic_states, mixed_states)
    assert len(logic_lengths) == len(mixed_lengths)


@_skip_no_local_logic_samples
def test_local_z_mixed_capture_uses_single_analog_lane_for_ch1():
    """The mixed local sample should no longer expose the whole interleaved payload as CH1."""
    waveform = RigolWFM.wfm.Wfm.from_file(str(_LOCAL_TEST3), "Z")
    split_mixed = RigolWFM.rigol_1000z_logic.split_raw_payload(
        _Rigol1000zWfm.from_file(str(_LOCAL_TEST3)).data.raw,
        analog_channels=1,
    )

    assert len(waveform.channels) == 1
    assert waveform.channels[0].raw is not None
    assert split_mixed.analog_lanes
    assert len(waveform.channels[0].raw) == len(split_mixed.analog_lanes[0])
