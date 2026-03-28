"""Snapshot tests for Rigol 4000-family `wfmconvert info` output."""

from pathlib import Path

import pytest
import RigolWFM.wfm

from tests.cli_helpers import assert_wfmconvert_info_snapshot

_4_INFO_CASES = [
    "DS4022-A",
    "DS4022-B",
    "DS4024-A",
    "DS4024-B",
]
_DS4024_SIDE_CAR_CASES = ["DS4024-A", "DS4024-B"]


def _parse_ds4024_sidecar(stem: str) -> dict:
    """Parse the checked-in DS4024 text export into a compact reference dict."""
    sidecar = Path("tests/files/wfm") / f"{stem}.txt"
    info: dict[str, object] = {"levels": {}}
    with sidecar.open(encoding="utf-8") as handle:
        for raw_line in handle:
            line = raw_line.strip()
            if line.startswith("Time Offset:"):
                info["time_offset"] = float(line.split(":", 1)[1].removesuffix("s"))
            elif line.startswith("Trigger Mode:"):
                info["mode"] = line.split(":", 1)[1]
            elif line.startswith("Trigger Source:"):
                info["source"] = line.split(":", 1)[1]
            elif line.startswith("CH") and " Level:" in line:
                name, value = line.split(" Level:", 1)
                levels = info["levels"]
                assert isinstance(levels, dict)
                levels[name] = float(value.removesuffix("V"))
            elif line.startswith("Ext Level:"):
                levels = info["levels"]
                assert isinstance(levels, dict)
                levels["EXT"] = float(line.split(":", 1)[1].removesuffix("V"))
    return info


@pytest.mark.parametrize("stem", _4_INFO_CASES)
def test_wfmconvert_4_info_matches_snapshot(stem):
    """`wfmconvert 4 info` should match the checked-in snapshot output."""
    assert_wfmconvert_info_snapshot("4", stem, "4")


@pytest.mark.parametrize("stem", _4_INFO_CASES)
def test_ds4000_time_grid_matches_sample_period(stem):
    """Adjacent DS4000 timestamps should match the reported sample period."""
    waveform = RigolWFM.wfm.Wfm.from_file(f"tests/files/wfm/{stem}.wfm", "4")
    for channel in waveform.channels:
        if channel.enabled:
            assert channel.times[1] - channel.times[0] == pytest.approx(
                channel.seconds_per_point
            )


@pytest.mark.parametrize("stem", _DS4024_SIDE_CAR_CASES)
def test_ds4024_time_offset_matches_sidecar(stem):
    """DS4024 time offsets should match the reference text exports."""
    reference = _parse_ds4024_sidecar(stem)
    waveform = RigolWFM.wfm.Wfm.from_file(f"tests/files/wfm/{stem}.wfm", "4")
    for channel in waveform.channels:
        if channel.enabled:
            assert channel.time_offset == pytest.approx(reference["time_offset"])


@pytest.mark.parametrize("stem", _DS4024_SIDE_CAR_CASES)
def test_ds4024_trigger_matches_sidecar(stem):
    """DS4024 trigger mode/source/levels should match the reference text exports."""
    reference = _parse_ds4024_sidecar(stem)
    waveform = RigolWFM.wfm.Wfm.from_file(f"tests/files/wfm/{stem}.wfm", "4")

    assert waveform.header_name == "DS4000"
    assert waveform.serial_number == "DS4A200500078"
    assert waveform.trigger_info["mode"] == reference["mode"]
    assert waveform.trigger_info["source"] == reference["source"]

    source = reference["source"]
    levels = reference["levels"]
    assert isinstance(source, str)
    assert isinstance(levels, dict)
    assert waveform.trigger_info["level"] == pytest.approx(levels[source])

    input_levels = waveform.trigger_info["input_levels"]
    for name, value in levels.items():
        assert input_levels[name] == pytest.approx(value)
