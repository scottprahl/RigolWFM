"""Integration checks for core `wfmconvert` output modes."""

from __future__ import annotations

from pathlib import Path
import shlex
import shutil
import sys

import pytest

import RigolWFM.wfm
from tests.cli_helpers import run_command, run_command_failure, run_command_result
from tests.test_isf import _build_isf
from tests.test_lecroy import _build_trc
from tests.test_siglent import _build_siglent_v6
from tests.test_yokogawa import _build_yokogawa_wfm

_ROOT = Path(__file__).resolve().parents[1]
_KEYSIGHT = _ROOT / "tests" / "files" / "bin" / "agilent_1.bin"
_ROHDE = _ROOT / "tests" / "files" / "rs" / "rs_rtp_01.bin"


_LEGACY_INFO = [
    ("B", "tests/files/wfm/DS1204B-A.wfm"),
    ("C", "tests/files/wfm/DS1202CA-A.wfm"),
    ("D", "tests/files/wfm/DS1102D-A.wfm"),
    ("E", "tests/files/wfm/DS1102E-A.wfm"),
    ("Z", "tests/files/wfm/MSO1104.wfm"),
    ("2", "tests/files/wfm/DS2202.wfm"),
    ("4", "tests/files/wfm/DS4022-A.wfm"),
]

_BIN_INFO = [
    ("5", "tests/files/bin/MSO5000-A.bin"),
    ("5074", "tests/files/bin/MSO5074-A.bin"),
    ("DHO", "tests/files/bin/DHO1074.bin"),
    ("DHO", "tests/files/bin/DHO824-ch1.bin"),
]


def _quote(path: Path | str) -> str:
    """Shell-quote a path for the CLI integration helpers."""
    return shlex.quote(str(path))


def _newer_family_cases(tmp_path: Path) -> list[tuple[str, str]]:
    """Return representative newer-family CLI fixtures."""
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


def _assert_sigrok_conversion(scope: str, path: str, output_dir: Path) -> None:
    """Assert sigrok conversion succeeds with output or fails with a clear error."""
    command = f"wfmconvert --model {scope} --output-dir {shlex.quote(str(output_dir))} sigrok {path}"
    expected = output_dir / (Path(shlex.split(path)[0]).stem + ".sr")

    if shutil.which("sigrok-cli"):
        run_command(command)
        assert expected.is_file()
        return

    result = run_command_failure(command)
    assert "sigrok-cli is not installed or not found in PATH." in result.stderr
    assert not expected.exists()


def test_wfmconvert_info(tmp_path):
    """Verify `info` conversion succeeds for representative scopes."""
    for scope, path in _LEGACY_INFO + _BIN_INFO:
        run_command(f"wfmconvert --model {scope} info {path}")
    for scope, path in _newer_family_cases(tmp_path):
        run_command(f"wfmconvert --model {scope} info {path}")


def test_wfmconvert_csv(tmp_path):
    """Verify CSV export succeeds for representative scopes."""
    for scope, path in _LEGACY_INFO + _BIN_INFO:
        run_command(f"wfmconvert --model {scope} --output-dir {tmp_path} csv {path}")
    for scope, path in _newer_family_cases(tmp_path):
        run_command(f"wfmconvert --model {scope} --output-dir {shlex.quote(str(tmp_path))} csv {path}")


def test_wfmconvert_wav(tmp_path):
    """Verify WAV export succeeds for representative scopes."""
    for scope, path in _LEGACY_INFO + _BIN_INFO:
        run_command(f"wfmconvert --model {scope} --channel 1 --output-dir {tmp_path} wav {path}")
    for scope, path in _newer_family_cases(tmp_path):
        run_command(f"wfmconvert --model {scope} --channel 1 --output-dir {shlex.quote(str(tmp_path))} wav {path}")


def test_wfmconvert_vcsv(tmp_path):
    """Verify VCSV export succeeds for representative scopes."""
    for scope, path in _LEGACY_INFO + _BIN_INFO:
        run_command(f"wfmconvert --model {scope} --output-dir {tmp_path} vcsv {path}")
    for scope, path in _newer_family_cases(tmp_path):
        run_command(f"wfmconvert --model {scope} --output-dir {shlex.quote(str(tmp_path))} vcsv {path}")


def test_wfmconvert_sigrok(tmp_path):
    """Verify sigrok export either writes output or reports the missing dependency."""
    for scope, path in _LEGACY_INFO + _BIN_INFO:
        _assert_sigrok_conversion(scope, path, tmp_path)
    for scope, path in _newer_family_cases(tmp_path):
        _assert_sigrok_conversion(scope, path, tmp_path)


def test_wfmconvert_model_aliases():
    """Representative aliases should be accepted case-insensitively."""
    run_command(f"wfmconvert --model keysight info {_quote(_KEYSIGHT)}")
    run_command(f"wfmconvert --model rohde info {_quote(_ROHDE)}")


@pytest.mark.parametrize(
    "path",
    [
        "tests/files/wfm/DS1102E-A.wfm",
        "tests/files/wfm/DS2202.wfm",
        str(_ROHDE),
    ],
)
def test_csv_metadata_matches_exported_time_axis(path):
    """CSV `Start` and `Increment` metadata should match the exported X axis."""
    waveform = RigolWFM.wfm.Wfm.from_file(path)
    h_scale, _, _, _ = waveform.best_scaling()
    lines = waveform.csv().splitlines()
    metadata = lines[1].split(",")
    start = float(metadata[-2])
    increment = float(metadata[-1])

    times = waveform.channels[0].times
    assert times is not None
    expected_start = float(times[0] * h_scale)
    expected_increment = float((times[1] - times[0]) * h_scale) if len(times) > 1 else 0.0

    assert start == pytest.approx(expected_start)
    assert increment == pytest.approx(expected_increment)
    assert float(lines[2].split(",")[0]) == pytest.approx(expected_start, rel=0.0, abs=1e-6)


def test_wfmconvert_missing_file_reports_clean_error():
    """Explicit-model read failures should not escape as Python tracebacks."""
    result = run_command_failure("wfmconvert --model E info tests/files/wfm/does_not_exist.wfm")
    assert "wfmconvert error: file not found" in result.stderr
    assert "Traceback" not in result.stderr


def test_wfmconvert_sigrok_missing_dependency_fails_cleanly(tmp_path):
    """Missing `sigrok-cli` should produce a non-zero exit code and no output file."""
    if shutil.which("sigrok-cli") is None:
        pytest.skip("sigrok-cli is already absent in this environment")

    command = (
        f"PATH=/nonexistent {shlex.quote(sys.executable)} -m RigolWFM.wfmconvert "
        f"--model E --force --output-dir {shlex.quote(str(tmp_path))} "
        "sigrok tests/files/wfm/DS1102E-A.wfm"
    )
    result = run_command_result(command)

    assert result.returncode != 0
    assert "sigrok-cli is not installed or not found in PATH." in result.stderr
    assert not (tmp_path / "DS1102E-A.sr").exists()
