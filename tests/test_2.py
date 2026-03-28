"""Snapshot tests for Rigol 2000-family `wfmconvert info` output."""

import re
import struct
from pathlib import Path

import pytest
import RigolWFM.wfm
import RigolWFM.wfm2000

from tests.cli_helpers import assert_wfmconvert_info_snapshot

_2_INFO_CASES = [
    "DS2072A-1",
    "DS2072A-2",
    "DS2072A-3",
    "DS2072A-4",
    "DS2072A-5",
    "DS2072A-6",
    "DS2072A-7",
    "DS2072A-8",
    "DS2072A-9",
    "DS2000-A",
    "DS2000-B",
]

_2_TXT_CASES = [
    "DS2072A-1",
    "DS2072A-2",
    "DS2072A-3",
    "DS2072A-4",
    "DS2072A-5",
    "DS2072A-6",
    "DS2072A-7",
    "DS2072A-8",
    "DS2072A-9",
]

_WFMINFO_OFFSET = 56
_STORAGE_DEPTH_OFFSET = _WFMINFO_OFFSET + 188
_Z_PT_OFFSET_OFFSET = _WFMINFO_OFFSET + 192
_WFM_LEN_OFFSET = _WFMINFO_OFFSET + 196


def _read_scope_metadata(stem):
    """Return CH1/CH2 metadata extracted from a DS2000 scope text export."""
    text = (Path("tests/files/wfm") / f"{stem}.txt").read_text(encoding="utf-8", errors="ignore")
    metadata = {}
    for channel_number in (1, 2):
        match = re.search(
            (
                rf"CH{channel_number}:(On|Off)\n"
                rf".*?Coupling:(?P<coupling>[^\n]+)\n"
                rf"Invert:(?P<invert>[^\n]+)\n"
                rf"Bandwidth Limit:(?P<bandwidth>[^\n]+)\n"
                rf"Probe Ratio:(?P<probe>[^\n]+)\n"
                rf"Impedance:(?P<impedance>[^\n]+)\n"
                rf"Unit:(?P<unit>[^\n]+)\n"
            ),
            text,
            re.S,
        )
        if match:
            metadata[channel_number] = {
                "enabled": match.group(1) == "On",
                "coupling": match.group("coupling"),
                "invert": match.group("invert") == "On",
                "probe": float(match.group("probe").rstrip("X")),
                "impedance": match.group("impedance"),
                "unit": match.group("unit"),
            }
    return metadata


def _read_scope_trigger_metadata(stem):
    """Return trigger metadata extracted from a DS2000 scope text export."""
    text = (Path("tests/files/wfm") / f"{stem}.txt").read_text(encoding="utf-8", errors="ignore")
    source = re.search(r"Trigger Source:(?P<source>[^\n]+)", text)
    mode = re.search(r"Trigger Mode:(?P<mode>[^\n]+)", text)
    holdoff = re.search(r"Trigger Hold(?:O|o)ff:(?P<holdoff>[0-9eE+\-.]+)s", text)
    levels = {}
    for sidecar_name, internal_name in (("CH1", "CH1"), ("CH2", "CH2"), ("Ext", "EXT")):
        match = re.search(rf"{sidecar_name} Level:(?P<level>[0-9eE+\-.]+)V", text)
        if match:
            levels[internal_name] = float(match.group("level"))

    return {
        "mode": mode.group("mode") if mode else "",
        "source": source.group("source") if source else "",
        "holdoff_s": float(holdoff.group("holdoff")) if holdoff else 0.0,
        "input_levels": levels,
    }


def _patch_u32(data, offset, value):
    """Write a little-endian u32 value into a mutable buffer."""
    struct.pack_into("<I", data, offset, value)


def _expected_ds2000_time_offset(header):
    """Return the trigger-centered time offset for DS2000 captures."""
    if (
        header.model_number.startswith("DS2A")
        and header.firmware_version == "00.03.00.01.03"
    ):
        return 0.0
    return header.time_offset


@pytest.mark.parametrize("stem", _2_INFO_CASES)
def test_wfmconvert_2_info_matches_snapshot(stem):
    """`wfmconvert 2 info` should match the checked-in snapshot output."""
    assert_wfmconvert_info_snapshot("2", stem, "2")


@pytest.mark.parametrize("stem", _2_INFO_CASES)
def test_ds2000_time_grid_matches_sample_period(stem):
    """Adjacent DS2000 timestamps should match the reported sample period."""
    waveform = RigolWFM.wfm.Wfm.from_file(f"tests/files/wfm/{stem}.wfm", "2")
    for channel in waveform.channels:
        if channel.enabled:
            assert channel.times[1] - channel.times[0] == pytest.approx(
                channel.seconds_per_point
            )


@pytest.mark.parametrize("stem", ["DS2000-A", "DS2000-B"])
def test_ds2000_legacy_trigger_is_centered(stem):
    """Older DS2A captures should place the trigger at time zero."""
    waveform = RigolWFM.wfm.Wfm.from_file(f"tests/files/wfm/{stem}.wfm", "2")
    for channel in waveform.channels:
        if channel.enabled:
            assert channel.time_offset == pytest.approx(0.0)
            assert channel.times[channel.points // 2] == pytest.approx(
                0.0, abs=channel.seconds_per_point
            )


def test_ds2072a_nonzero_time_offset_is_preserved():
    """Newer DS2072A captures should keep their stored nonzero offsets."""
    waveform = RigolWFM.wfm.Wfm.from_file("tests/files/wfm/DS2072A-5.wfm", "2")
    channel = next(ch for ch in waveform.channels if ch.enabled)
    assert channel.time_offset == pytest.approx(4.48e-6)


@pytest.mark.parametrize("stem", _2_INFO_CASES)
def test_ds2000_serial_number_is_exposed(stem):
    """The serial-like DS2000 header string should be surfaced separately."""
    waveform = RigolWFM.wfm.Wfm.from_file(f"tests/files/wfm/{stem}.wfm", "2")
    assert waveform.serial_number.startswith("DS2")


@pytest.mark.parametrize("stem", _2_TXT_CASES)
def test_ds2000_parser_matches_scope_metadata(stem):
    """Low-level DS2000 metadata should match the sidecar scope export."""
    waveform = RigolWFM.wfm2000.Wfm2000.from_file(f"tests/files/wfm/{stem}.wfm")
    metadata = _read_scope_metadata(stem)

    impedance_map = {"50": "ohm_50", "1M": "ohm_1meg"}
    unit_map = {"W": 0, "A": 1, "V": 2, "U": 3}

    for channel_number, expected in metadata.items():
        channel = waveform.header.ch[channel_number - 1]
        assert channel.enabled == expected["enabled"]
        assert channel.coupling.name.upper() == expected["coupling"]
        assert channel.inverted == expected["invert"]
        assert channel.probe_value == pytest.approx(expected["probe"])
        assert channel.probe_impedance.name == impedance_map[expected["impedance"]]
        assert channel.unit_actual == unit_map[expected["unit"]]


@pytest.mark.parametrize("stem", _2_TXT_CASES)
def test_ds2000_setup_trigger_matches_scope_export(stem):
    """DS2072A setup fields should match the sidecar trigger settings."""
    waveform = RigolWFM.wfm2000.Wfm2000.from_file(f"tests/files/wfm/{stem}.wfm")
    expected = _read_scope_trigger_metadata(stem)
    setup = waveform.header.setup
    levels = setup.trigger_levels

    assert int(setup.trigger_source_primary) == int(setup.trigger_source_shadow)
    assert RigolWFM.wfm._DS2000_SOURCE_NAMES[int(setup.trigger_source_primary)] == expected["source"]
    assert setup.trigger_holdoff_ns * 1.0e-9 == pytest.approx(expected["holdoff_s"])
    assert levels.ch1_level_uv * 1.0e-6 == pytest.approx(expected["input_levels"]["CH1"])
    assert levels.ch2_level_uv * 1.0e-6 == pytest.approx(expected["input_levels"]["CH2"])
    assert levels.ext_level_uv * 1.0e-6 == pytest.approx(expected["input_levels"]["EXT"])


@pytest.mark.parametrize("stem", _2_TXT_CASES)
def test_ds2000_trigger_info_uses_setup_metadata(stem):
    """High-level DS2000 trigger info should come from the setup block."""
    waveform = RigolWFM.wfm.Wfm.from_file(f"tests/files/wfm/{stem}.wfm", "2")
    expected = _read_scope_trigger_metadata(stem)

    assert waveform.trigger_info["mode"] == expected["mode"]
    assert waveform.trigger_info["source"] == expected["source"]
    assert waveform.trigger_info["level"] == pytest.approx(
        expected["input_levels"].get(expected["source"], 0.0)
    )


@pytest.mark.parametrize("stem", ["DS2000-A", "DS2000-B"])
def test_ds2000_legacy_captures_do_not_report_setup_trigger(stem):
    """Older DS2A captures should not invent trigger metadata from zeroed setup bytes."""
    waveform = RigolWFM.wfm.Wfm.from_file(f"tests/files/wfm/{stem}.wfm", "2")
    assert waveform.trigger_info == {}


def test_ds2000_windowed_data_uses_effective_length_and_offset(tmp_path):
    """Windowed non-interwoven DS2000 data should honor `z_pt_offset` and `wfm_len`."""
    source = Path("tests/files/wfm/DS2000-A.wfm")
    original = RigolWFM.wfm2000.Wfm2000.from_file(str(source))
    data = bytearray(source.read_bytes())
    z_pt_offset = 100
    wfm_len = 700

    _patch_u32(data, _Z_PT_OFFSET_OFFSET, z_pt_offset)
    _patch_u32(data, _WFM_LEN_OFFSET, wfm_len)

    path = tmp_path / "windowed-ds2000.wfm"
    path.write_bytes(data)

    patched = RigolWFM.wfm2000.Wfm2000.from_file(str(path))
    assert patched.header.points == wfm_len
    assert len(patched.header.raw_1) == wfm_len
    assert len(patched.header.raw_2) == wfm_len
    assert patched.header.raw_1[0] == original.header.raw_1[z_pt_offset]
    assert patched.header.raw_2[0] == original.header.raw_2[z_pt_offset]

    waveform = RigolWFM.wfm.Wfm.from_file(str(path), "2")
    channel = waveform.channels[0]
    expected_start = (
        _expected_ds2000_time_offset(original.header)
        - original.header.storage_depth * original.header.seconds_per_point / 2
        + z_pt_offset * original.header.seconds_per_point
    )
    assert channel.points == wfm_len
    assert channel.raw[0] == original.header.raw_1[z_pt_offset]
    assert channel.times[0] == pytest.approx(expected_start)
    assert channel.times[1] - channel.times[0] == pytest.approx(
        original.header.seconds_per_point
    )


def test_ds2000_interwoven_data_uses_effective_half_windows(tmp_path):
    """Interwoven DS2000 data should read half windows and interleave them."""
    source = Path("tests/files/wfm/DS2072A-6.wfm")
    original = RigolWFM.wfm2000.Wfm2000.from_file(str(source))
    data = bytearray(source.read_bytes())
    z_pt_offset = 50
    wfm_len = 1400

    _patch_u32(data, _STORAGE_DEPTH_OFFSET, original.header.storage_depth)
    _patch_u32(data, _Z_PT_OFFSET_OFFSET, z_pt_offset)
    _patch_u32(data, _WFM_LEN_OFFSET, wfm_len)

    path = tmp_path / "windowed-ds2072a-6.wfm"
    path.write_bytes(data)

    patched = RigolWFM.wfm2000.Wfm2000.from_file(str(path))
    assert patched.header.points == wfm_len
    assert len(patched.header.raw_1) == wfm_len // 2
    assert len(patched.header.raw_2) == wfm_len // 2
    assert patched.header.raw_1[0] == original.header.raw_1[z_pt_offset]
    assert patched.header.raw_2[0] == original.header.raw_2[z_pt_offset]

    waveform = RigolWFM.wfm.Wfm.from_file(str(path), "2")
    channel = next(ch for ch in waveform.channels if ch.enabled)
    expected_start = (
        _expected_ds2000_time_offset(original.header)
        - original.header.storage_depth * original.header.seconds_per_point / 2
        + z_pt_offset * original.header.seconds_per_point
    )
    assert channel.points == wfm_len
    assert channel.raw[0] == original.header.raw_1[z_pt_offset]
    assert channel.raw[1] == original.header.raw_2[z_pt_offset]
    assert channel.times[0] == pytest.approx(expected_start)
    assert channel.times[1] - channel.times[0] == pytest.approx(
        original.header.seconds_per_point
    )
