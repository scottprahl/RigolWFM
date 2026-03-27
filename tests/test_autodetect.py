"""Tests for `detect_model()` automatic scope-family detection."""

import pytest

from RigolWFM import wfm


# (filename, expected_model)
# One representative file per detectable family.
_CASES = [
    # DS1000B — magic 0xA5 0xA5 0xA4 0x01
    ("wfm/DS1204B-A.wfm", "B"),
    # DS1000C — magic 0xA1 0xA5 0x00 0x00 (standard) or 0xA5 0xA5 0x00 0x00
    # (variant with 16-byte data padding, size 272+n*pts rather than 256+n*pts)
    ("wfm/DS1202CA-A.wfm", "C"),
    ("wfm/DS1042C-A.wfm", "C"),
    # DS1000D/E — file size disambiguates; DS1102D-A matches the E formula
    # (data at 276) so "E" is returned and the E parser is used for both.
    ("wfm/DS1102D-A.wfm", "E"),
    ("wfm/DS1102E-A.wfm", "E"),
    ("wfm/DS1000E-A.wfm", "E"),
    # DS1000Z — magic 0x01 0xFF 0xFF 0xFF
    ("wfm/DS1054Z-A.wfm", "Z"),
    ("wfm/MSO1104.wfm", "Z"),
    # DS2000 — magic 0xA5 0xA5 0x38 0x00 with model string starting DS2/MSO2
    ("wfm/DS2202.wfm", "2"),
    ("wfm/DS2072A-1.wfm", "2"),
    # DS4000 — same magic as DS2000, model string starting DS4/MSO4
    ("wfm/DS4022-A.wfm", "4"),
    # MSO5000 — magic RG01, wfm_hdr_size == 140
    ("wfm/MSO5000-A.bin", "5"),
    # MSO5074 — magic RG01, wfm_hdr_size == 144
    ("wfm/MSO5074-A.bin", "5074"),
    # DHO800/1000 — magic 0x02 0x00 0x00 0x00 or RG03
    ("wfm/DHO1074.bin", "DHO"),
    ("wfm/DHO824-ch1.bin", "DHO"),
    ("wfm/DHO824-ch1.wfm", "DHO"),
]

@pytest.mark.parametrize("path, expected", _CASES)
def test_detect_model(path, expected):
    """detect_model() returns the correct family for representative files."""
    assert wfm.detect_model(path) == expected


def test_detect_model_missing_file():
    """detect_model() raises FileNotFoundError for a non-existent path."""
    with pytest.raises(FileNotFoundError):
        wfm.detect_model("wfm/does_not_exist.wfm")


@pytest.mark.parametrize(
    "path",
    [
        "wfm/DS1102E-A.wfm",
        "wfm/DS1202Z-E.wfm",
        "wfm/MSO5000-A.bin",
        "wfm/DHO824-ch1.bin",
    ],
)
def test_from_file_auto_matches_detected_model(path):
    """Wfm.from_file() defaults to autodetect and matches explicit parsing."""
    detected = wfm.detect_model(path)
    auto_wave = wfm.Wfm.from_file(path)
    explicit_wave = wfm.Wfm.from_file(path, detected)

    assert auto_wave.user_name == "auto"
    assert auto_wave.parser_name == explicit_wave.parser_name
    assert auto_wave.header_name == explicit_wave.header_name
    assert [ch.channel_number for ch in auto_wave.channels] == [
        ch.channel_number for ch in explicit_wave.channels
    ]
