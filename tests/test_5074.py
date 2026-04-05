"""Tests for standard MSO5074 RG01 captures handled by the MSO5000-family parser."""

from pathlib import Path

import numpy as np
import pytest
import RigolWFM.mso5000
import RigolWFM.wfm

from tests.cli_helpers import assert_wfmconvert_info_snapshot_file

_STANDARD_5074 = Path("tests/files/bin/MSO5074-C.bin")
_MALFORMED_5074 = [
    Path("tests/files/bin/MSO5074-A.bin"),
    Path("tests/files/bin/MSO5074-B.bin"),
]
_skip_no_standard_5074 = pytest.mark.skipif(
    not _STANDARD_5074.is_file(),
    reason="Standard MSO5074-C.bin fixture is not checked into the repo.",
)


@_skip_no_standard_5074
def test_wfmconvert_5074_info_matches_snapshot():
    """`wfmconvert 5074 info` should describe standard RG01 logic captures."""
    assert_wfmconvert_info_snapshot_file("5074", _STANDARD_5074, "5074", "MSO5074-C")


@_skip_no_standard_5074
def test_mso5000_adapter_decodes_standard_mso5074_logic_record():
    """The normal MSO5000 adapter should decode the checked-in MSO5074 logic record."""
    waveform = RigolWFM.mso5000.from_file(str(_STANDARD_5074))

    assert waveform.header.model == "MSO5074"
    assert waveform.header.points == 500_000
    assert waveform.header.seconds_per_point == pytest.approx(9.999999717180685e-10)
    assert waveform.header.x_origin == pytest.approx(0.00024930799294908823)
    assert [channel.enabled for channel in waveform.header.ch] == [False] * 4
    assert waveform.logic_mapping == "LA D7-D0"
    assert list(waveform.logic_channels) == [f"D{i}" for i in range(8)]

    np.testing.assert_array_equal(np.unique(waveform.logic_channels["D2"]), np.array([0, 1], dtype=np.uint8))
    np.testing.assert_array_equal(np.unique(waveform.logic_channels["D6"]), np.array([0], dtype=np.uint8))


@_skip_no_standard_5074
def test_wfm_from_file_accepts_5074_alias_but_uses_bin5000_parser():
    """The `5074` alias should route to the normal RG01/5000 parser."""
    alias_waveform = RigolWFM.wfm.Wfm.from_file(str(_STANDARD_5074), "5074")
    family_waveform = RigolWFM.wfm.Wfm.from_file(str(_STANDARD_5074), "5")

    assert alias_waveform.parser_name == family_waveform.parser_name == "bin5000"
    assert alias_waveform.header_name == family_waveform.header_name == "MSO5074"
    assert not alias_waveform.channels
    assert list(alias_waveform.logic_channels) == [f"D{i}" for i in range(8)]
    assert alias_waveform.logic_mapping == "LA D7-D0"
    assert alias_waveform.logic_times is not None
    assert len(alias_waveform.logic_times) == 500_000

    description = alias_waveform.describe()
    assert "Parser Model = bin5000" in description
    assert "Mapping      = LA D7-D0" in description
    assert "Traces       = [D0, D1, D2, D3, D4, D5, D6, D7]" in description


@pytest.mark.parametrize("path", _MALFORMED_5074)
def test_malformed_5074_concatenated_exports_are_rejected(path: Path):
    """Broken concatenated MSO5074 exports should fail with a clear error."""
    with pytest.raises(ValueError, match="Unsupported malformed MSO5074 concatenated RG01 export"):
        RigolWFM.mso5000.from_file(str(path))
