"""Integration checks for `wfmconvert` sigrok export."""

import zipfile
from pathlib import Path
import tempfile
import shlex
import shutil

import pytest

from tests.cli_helpers import run_command, run_command_failure
from tests.test_isf import _build_isf
from tests.test_lecroy import _build_trc
from tests.test_siglent import _build_siglent_v6
from tests.test_yokogawa import _build_yokogawa_wfm

_ROOT = Path(__file__).resolve().parents[1]
_KEYSIGHT = _ROOT / "tests" / "files" / "bin" / "agilent_1.bin"
_ROHDE = _ROOT / "tests" / "files" / "rs" / "rs_rtp_01.bin"
_STANDARD_5074 = _ROOT / "tests" / "files" / "bin" / "MSO5074-C.bin"


def _quote(path: Path | str) -> str:
    """Shell-quote a path for CLI integration."""
    return shlex.quote(str(path))


def _newer_sigrok_cases(tmp_path: Path) -> list[tuple[str, str]]:
    """Return newer-family sigrok fixtures."""
    siglent = tmp_path / "synthetic_siglent_v6.bin"
    siglent.write_bytes(_build_siglent_v6())

    lecroy = tmp_path / "synthetic_lecroy.trc"
    lecroy.write_bytes(_build_trc(n_pts=4, samples=[0, 1, 2, 3]))

    isf = tmp_path / "synthetic_tek.isf"
    isf.write_bytes(_build_isf(samples=[-10, 0, 10, 20]))

    yokogawa = tmp_path / "synthetic_yokogawa.wfm"
    yokogawa.write_bytes(_build_yokogawa_wfm(raw_samples=[0.0, 1.0, -2.0, 4.0]))

    return [
        ("Keysight", _quote(_KEYSIGHT)),
        ("RohdeSchwarz", _quote(_ROHDE)),
        ("Siglent", _quote(siglent)),
        ("LeCroy", _quote(lecroy)),
        ("ISF", _quote(isf)),
        ("Yokogawa", _quote(yokogawa)),
    ]


def _assert_sigrok_result(scope: str, path: str, output_dir: Path) -> None:
    """Assert sigrok export behavior matches whether `sigrok-cli` is available."""
    command = f"wfmconvert --model {scope} --output-dir {_quote(output_dir)} sigrok {path}"
    expected = output_dir / (Path(shlex.split(path)[0]).stem + ".sr")

    if shutil.which("sigrok-cli"):
        run_command(command)
        assert expected.is_file()
        return

    result = run_command_failure(command)
    assert "sigrok-cli is not installed or not found in PATH." in result.stderr
    assert not expected.exists()


def _read_sigrok_metadata(path: Path) -> str:
    """Return the `metadata` member from a generated sigrok session archive."""
    with zipfile.ZipFile(path) as archive:
        return archive.read("metadata").decode("utf-8")


def test_wfmconvert_sigrok(tmp_path):
    """Verify sigrok export either writes output or reports the missing dependency."""
    cases = [
        ("B", "tests/files/wfm/DS1204B-A.wfm"),
        ("C", "tests/files/wfm/DS1202CA-A.wfm"),
        ("D", "tests/files/wfm/DS1102D-A.wfm"),
        ("E", "tests/files/wfm/DS1102E-A.wfm"),
        ("Z", "tests/files/wfm/MSO1104.wfm"),
        ("Z", "tests/files/wfm/DS1074Z-C.wfm"),
        ("2", "tests/files/wfm/DS2202.wfm"),
        ("4", "tests/files/wfm/DS4022-A.wfm"),
    ]

    for scope, path in cases:
        _assert_sigrok_result(scope, path, tmp_path)
    for scope, path in _newer_sigrok_cases(tmp_path):
        _assert_sigrok_result(scope, path, tmp_path)
    if _STANDARD_5074.is_file():
        _assert_sigrok_result("5", _quote(_STANDARD_5074), tmp_path)


@pytest.mark.skipif(shutil.which("sigrok-cli") is None, reason="sigrok-cli is not installed")
def test_wfmconvert_sigrok_preserves_all_analog_channels(tmp_path):
    """Multi-channel analog exports should preserve every enabled analog channel."""
    run_command(f"wfmconvert --model Z --output-dir {_quote(tmp_path)} sigrok tests/files/wfm/DS1054Z-A.wfm")

    metadata = _read_sigrok_metadata(tmp_path / "DS1054Z-A.sr")
    assert "samplerate=250 MHz" in metadata
    assert "total analog=4" in metadata
    assert "analog1=CH 1 (V)" in metadata
    assert "analog4=CH 4 (V)" in metadata


@pytest.mark.skipif(shutil.which("sigrok-cli") is None, reason="sigrok-cli is not installed")
def test_wfmconvert_sigrok_preserves_logic_only_channels(tmp_path):
    """Logic-only exports should write named probes instead of an empty session."""
    run_command(f"wfmconvert --model Z --output-dir {_quote(tmp_path)} sigrok tests/files/wfm/DS1074Z-C.wfm")

    metadata = _read_sigrok_metadata(tmp_path / "DS1074Z-C.sr")
    assert "total analog=0" in metadata
    assert "total probes=1" in metadata
    assert "probe1=D6" in metadata


@pytest.mark.skipif(
    shutil.which("sigrok-cli") is None or not _STANDARD_5074.is_file(),
    reason="sigrok-cli or MSO5074-C.bin fixture is not available",
)
def test_wfmconvert_sigrok_preserves_rg01_logic_channels(tmp_path):
    """Standard RG01 logic captures should export all eight digital probes."""
    run_command(f"wfmconvert --model 5 --output-dir {_quote(tmp_path)} sigrok {_quote(_STANDARD_5074)}")

    metadata = _read_sigrok_metadata(tmp_path / "MSO5074-C.sr")
    assert "total analog=0" in metadata
    assert "total probes=8" in metadata
    assert "probe1=D0" in metadata
    assert "probe8=D7" in metadata


# Run the tests
if __name__ == "__main__":
    with tempfile.TemporaryDirectory() as tmpdir:
        test_wfmconvert_sigrok(Path(tmpdir))
    print("All tests passed!")
