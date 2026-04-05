"""Tests for `detect_model()` automatic scope-family detection."""

from pathlib import Path

import pytest

from RigolWFM import wfm
from tests.test_siglent import _build_siglent_v6
from tests.test_tek import _build_tek_wfm

_ROOT = Path(__file__).resolve().parents[1]
_RS_DIR = _ROOT / "tests" / "files" / "rs"
_ROHDE = _RS_DIR / "rs_rtp_01.bin"
_STANDARD_5074 = _ROOT / "tests" / "files" / "bin" / "MSO5074-C.bin"

# (filename, expected_model)
# One representative file per detectable family.
_CASES = [
    # DS1000B — magic 0xA5 0xA5 0xA4 0x01
    ("tests/files/wfm/DS1204B-A.wfm", "B"),
    # DS1000C — magic 0xA1 0xA5 0x00 0x00 (standard) or 0xA5 0xA5 0x00 0x00
    # (variant with 16-byte data padding, size 272+n*pts rather than 256+n*pts)
    ("tests/files/wfm/DS1202CA-A.wfm", "C"),
    ("tests/files/wfm/DS1042C-A.wfm", "C"),
    # DS1000D/E — file size disambiguates; DS1102D-A matches the E formula
    # (data at 276) so "E" is returned and the E parser is used for both.
    ("tests/files/wfm/DS1102D-A.wfm", "E"),
    ("tests/files/wfm/DS1102E-A.wfm", "E"),
    ("tests/files/wfm/DS1000E-A.wfm", "E"),
    # DS1000Z — magic 0x01 0xFF 0xFF 0xFF
    ("tests/files/wfm/DS1054Z-A.wfm", "Z"),
    ("tests/files/wfm/MSO1104.wfm", "Z"),
    # DS2000 — magic 0xA5 0xA5 0x38 0x00 with model string starting DS2/MSO2
    ("tests/files/wfm/DS2202.wfm", "2"),
    ("tests/files/wfm/DS2072A-1.wfm", "2"),
    # DS4000 — same magic as DS2000, model string starting DS4/MSO4
    ("tests/files/wfm/DS4022-A.wfm", "4"),
    # MSO5000-family RG01 analog export
    ("tests/files/bin/MSO5000-A.bin", "5"),
    # DHO800/1000 — magic 0x02 0x00 0x00 0x00 or RG03
    ("tests/files/bin/DHO1074.bin", "DHO"),
    ("tests/files/bin/DHO824-ch1.bin", "DHO"),
    ("tests/files/wfm/DHO824-ch1.wfm", "DHO"),
    # Agilent / Keysight `.bin` — AG01 / AG03 / AG10
    ("tests/files/bin/agilent_1.bin", "Keysight"),
    # Rohde & Schwarz RTP `.bin` metadata with companion `.Wfm.bin` payload
    ("tests/files/rs/rs_rtp_01.bin", "RohdeSchwarz"),
]

if _STANDARD_5074.is_file():
    _CASES.append(("tests/files/bin/MSO5074-C.bin", "5"))


@pytest.mark.parametrize("path, expected", _CASES)
def test_detect_model(path, expected):
    """detect_model() returns the correct family for representative files."""
    assert wfm.detect_model(path) == expected


def test_detect_model_missing_file():
    """detect_model() raises FileNotFoundError for a non-existent path."""
    with pytest.raises(FileNotFoundError):
        wfm.detect_model("tests/files/wfm/does_not_exist.wfm")


@pytest.mark.parametrize(
    "path",
    [
        "tests/files/wfm/DS1102E-A.wfm",
        "tests/files/wfm/DS1202Z-E.wfm",
        "tests/files/bin/MSO5000-A.bin",
        "tests/files/bin/DHO824-ch1.bin",
        "tests/files/bin/agilent_1.bin",
        "tests/files/rs/rs_rtp_01.bin",
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
    assert [ch.channel_number for ch in auto_wave.channels] == [ch.channel_number for ch in explicit_wave.channels]


def test_from_url_auto_matches_detected_model(monkeypatch):
    """Wfm.from_url() defaults to autodetect and matches explicit parsing."""
    path = "tests/files/wfm/DS1102E-A.wfm"
    with open(path, "rb") as handle:
        content = handle.read()

    class DummyResponse:  # pylint: disable=too-few-public-methods
        """Minimal requests response stand-in for unit tests."""

        def __init__(self, payload):
            self.content = payload

        def raise_for_status(self):
            """Pretend the HTTP request succeeded."""

    def fake_get(url, allow_redirects=True, timeout=10):
        """Return local waveform bytes without performing network I/O."""
        assert url == "https://example.test/DS1102E-A.wfm"
        assert allow_redirects is True
        assert timeout == 10
        return DummyResponse(content)

    monkeypatch.setattr(wfm.requests, "get", fake_get)

    auto_wave = wfm.Wfm.from_url("https://example.test/DS1102E-A.wfm")
    explicit_wave = wfm.Wfm.from_file(path, "E")

    assert auto_wave.user_name == "auto"
    assert auto_wave.parser_name == explicit_wave.parser_name
    assert auto_wave.header_name == explicit_wave.header_name
    assert auto_wave.basename == "DS1102E-A.wfm"
    assert [ch.channel_number for ch in auto_wave.channels] == [ch.channel_number for ch in explicit_wave.channels]


def test_from_url_auto_matches_detected_model_for_siglent(monkeypatch, tmp_path):
    """`from_url(auto)` should preserve enough context for Siglent `.bin` files."""
    path = tmp_path / "synthetic_siglent_v6.bin"
    path.write_bytes(_build_siglent_v6())
    content = path.read_bytes()

    class DummyResponse:  # pylint: disable=too-few-public-methods
        """Minimal requests response stand-in for unit tests."""

        def __init__(self, payload):
            self.content = payload

        def raise_for_status(self):
            """Pretend the HTTP request succeeded."""

    def fake_get(url, allow_redirects=True, timeout=10):
        """Return local waveform bytes without performing network I/O."""
        assert url == "https://example.test/synthetic_siglent_v6.bin"
        assert allow_redirects is True
        assert timeout == 10
        return DummyResponse(content)

    monkeypatch.setattr(wfm.requests, "get", fake_get)

    auto_wave = wfm.Wfm.from_url("https://example.test/synthetic_siglent_v6.bin")
    explicit_wave = wfm.Wfm.from_file(str(path), "Siglent")

    assert auto_wave.user_name == "auto"
    assert auto_wave.parser_name == explicit_wave.parser_name
    assert auto_wave.header_name == explicit_wave.header_name
    assert auto_wave.basename == "synthetic_siglent_v6.bin"
    assert [ch.channel_number for ch in auto_wave.channels] == [ch.channel_number for ch in explicit_wave.channels]


def test_from_url_auto_matches_detected_model_for_rohde_schwarz(monkeypatch):
    """`from_url(auto)` should fetch the companion R&S payload when needed."""
    root = _RS_DIR
    metadata = (root / "rs_rtp_01.bin").read_bytes()
    payload = (root / "rs_rtp_01.Wfm.bin").read_bytes()

    class DummyResponse:  # pylint: disable=too-few-public-methods
        """Minimal requests response stand-in for unit tests."""

        def __init__(self, body):
            self.content = body

        def raise_for_status(self):
            """Pretend the HTTP request succeeded."""

    def fake_get(url, allow_redirects=True, timeout=10):
        """Return local waveform bytes without performing network I/O."""
        assert allow_redirects is True
        assert timeout == 10
        if url == "https://example.test/rs_rtp_01.bin":
            return DummyResponse(metadata)
        if url == "https://example.test/rs_rtp_01.Wfm.bin":
            return DummyResponse(payload)
        raise AssertionError(f"Unexpected URL requested: {url}")

    monkeypatch.setattr(wfm.requests, "get", fake_get)

    auto_wave = wfm.Wfm.from_url("https://example.test/rs_rtp_01.bin")
    explicit_wave = wfm.Wfm.from_file(str(root / "rs_rtp_01.bin"), "RohdeSchwarz")

    assert auto_wave.user_name == "auto"
    assert auto_wave.parser_name == explicit_wave.parser_name
    assert auto_wave.header_name == explicit_wave.header_name
    assert auto_wave.basename == "rs_rtp_01.bin"
    assert [ch.channel_number for ch in auto_wave.channels] == [ch.channel_number for ch in explicit_wave.channels]


def test_from_file_accepts_documented_vendor_aliases(tmp_path):
    """Explicit `model=` aliases advertised by `valid_scope_list()` should work."""
    tek_path = tmp_path / "synthetic_tek.wfm"
    tek_path.write_bytes(_build_tek_wfm(version="WFM#002", samples=[-10, 0, 10]))

    cases = [
        ("tests/files/bin/agilent_1.bin", "agilent_bin", "Keysight"),
        (str(_ROHDE), "rohde_schwarz_bin", "RohdeSchwarz"),
        (str(tek_path), "Tektronix", "Tek"),
        (str(tek_path), "tek_wfm", "Tek"),
    ]

    for path, alias, canonical in cases:
        alias_wave = wfm.Wfm.from_file(path, alias)
        canonical_wave = wfm.Wfm.from_file(path, canonical)

        assert alias_wave.user_name == alias
        assert alias_wave.parser_name == canonical_wave.parser_name
        assert alias_wave.header_name == canonical_wave.header_name
        assert [ch.channel_number for ch in alias_wave.channels] == [
            ch.channel_number for ch in canonical_wave.channels
        ]
