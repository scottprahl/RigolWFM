"""Integration checks for core `wfmconvert` output modes."""

from pathlib import Path
import shlex
import shutil
from types import SimpleNamespace
import sys

import numpy as np
import pytest

import RigolWFM.channel
import RigolWFM.wfm
import RigolWFM.wfmconvert
from tests.cli_helpers import run_command, run_command_failure, run_command_result
from tests.test_isf import _build_isf
from tests.test_lecroy import _build_trc
from tests.test_siglent import _build_siglent_v6
from tests.test_yokogawa import _build_yokogawa_wfm

_ROOT = Path(__file__).resolve().parents[1]
_KEYSIGHT = _ROOT / "tests" / "files" / "bin" / "agilent_1.bin"
_ROHDE = _ROOT / "tests" / "files" / "rs" / "rs_rtp_01.bin"
_STANDARD_5074 = _ROOT / "tests" / "files" / "bin" / "MSO5074-C.bin"


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
    if _STANDARD_5074.is_file():
        run_command("wfmconvert --model 5074 info tests/files/bin/MSO5074-C.bin")
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
    n_rows = len(lines) - 2
    expected_start = float(times[0] * h_scale)
    expected_increment = float(((times[n_rows - 1] - times[0]) / (n_rows - 1)) * h_scale) if n_rows > 1 else 0.0

    assert start == pytest.approx(expected_start)
    assert increment == pytest.approx(expected_increment)

    sample_rows = sorted({0, 1, 2, n_rows // 2, n_rows - 2, n_rows - 1})
    for idx in sample_rows:
        if idx < 0:
            continue
        exported_time = float(lines[2 + idx].split(",")[0])
        expected_time = start + idx * increment
        assert exported_time == pytest.approx(expected_time, rel=1e-12, abs=1e-15)


def test_csv_time_axis_ignores_small_in_memory_roundoff():
    """CSV X values should follow the declared linear Start/Increment grid."""
    waveform = RigolWFM.wfm.Wfm.from_file("tests/files/wfm/DS1102E-A.wfm", "E")
    h_scale, _, _, _ = waveform.best_scaling()
    times = waveform.channels[0].times
    assert times is not None

    noisy_times = times.copy()
    idx = 123
    noisy_times[idx] += waveform.channels[0].seconds_per_point * 1e-3
    waveform.channels[0].times = noisy_times

    lines = waveform.csv().splitlines()
    metadata = lines[1].split(",")
    start = float(metadata[-2])
    increment = float(metadata[-1])
    exported_time = float(lines[2 + idx].split(",")[0])
    expected_time = start + idx * increment

    assert exported_time == pytest.approx(expected_time, rel=1e-12, abs=1e-15)
    assert abs(exported_time - float(noisy_times[idx] * h_scale)) > abs(increment) * 1e-4


def test_csv_exports_logic_only_waveforms():
    """Logic-only captures should export named digital traces as 0/1 CSV columns."""
    waveform = RigolWFM.wfm.Wfm.from_file("tests/files/wfm/DS1074Z-C.wfm", "Z")
    h_scale, _, _, _ = waveform.best_scaling()

    lines = waveform.csv().splitlines()
    assert lines[0].split(",") == ["X", "D6", "Start", "Increment"]
    assert lines[1].split(",")[1] == "STATE"

    metadata = lines[1].split(",")
    start = float(metadata[-2])
    increment = float(metadata[-1])

    assert waveform.logic_times is not None
    assert start == pytest.approx(float(waveform.logic_times[0] * h_scale))
    expected_increment = float((waveform.logic_times[1] - waveform.logic_times[0]) * h_scale)
    assert increment == pytest.approx(expected_increment)

    sample_rows = [line.split(",") for line in lines[2:20]]
    assert {row[1] for row in sample_rows} <= {"0", "1"}


def test_csv_exports_mixed_analog_and_digital_columns():
    """Digital traces should appear after analog traces and stay integer formatted."""
    waveform = RigolWFM.wfm.Wfm("synthetic.csv")
    waveform.channels = [
        SimpleNamespace(
            name="CH1",
            enabled_and_selected=True,
            times=np.array([0.0, 1.0e-6, 2.0e-6], dtype=np.float64),
            volts=np.array([0.25, -0.5, 0.75], dtype=np.float64),
            points=3,
            unit=RigolWFM.channel.UnitEnum.v,
            volt_per_division=1.0e-3,
            time_scale=1.0e-6,
        )
    ]
    waveform.logic_channels = {"D6": np.array([0, 1, 0], dtype=np.uint8)}
    waveform.logic_times = np.array([0.0, 1.0e-6, 2.0e-6], dtype=np.float64)
    waveform.logic_seconds_per_point = 1.0e-6

    lines = waveform.csv().splitlines()

    assert lines[0].split(",") == ["X", "CH1", "D6", "Start", "Increment"]
    assert lines[1].split(",")[1:3] == ["mV", "STATE"]

    row0 = lines[2].split(",")
    row1 = lines[3].split(",")
    assert row0[2] == "0"
    assert row1[2] == "1"
    assert row0[1] == "250.00"
    assert row1[1] == "-500.00"


def test_wfmconvert_csv_writes_logic_columns(tmp_path):
    """CLI CSV export should include parsed digital channels for logic-only fixtures."""
    run_command(f"wfmconvert --model Z --output-dir {shlex.quote(str(tmp_path))} csv tests/files/wfm/DS1074Z-C.wfm")

    lines = (tmp_path / "DS1074Z-C.csv").read_text(encoding="utf-8").splitlines()
    assert lines[0].split(",") == ["X", "D6", "Start", "Increment"]
    assert lines[1].split(",")[1] == "STATE"


def test_sigrokcsv_exports_logic_only_waveforms():
    """Logic-only captures should export named digital traces for sigrok staging."""
    waveform = RigolWFM.wfm.Wfm.from_file("tests/files/wfm/DS1074Z-C.wfm", "Z")

    lines = waveform.sigrokcsv().splitlines()
    assert lines[0].split(",") == ["X", "D6"]

    sample_rows = [line.split(",") for line in lines[1:20]]
    assert {row[1] for row in sample_rows} <= {"0", "1"}


def test_sigrokcsv_exports_mixed_analog_and_digital_columns():
    """Sigrok staging CSV should preserve full analog precision and digital columns."""
    waveform = RigolWFM.wfm.Wfm("synthetic.sigrok")
    waveform.channels = [
        SimpleNamespace(
            name="CH1",
            enabled_and_selected=True,
            times=np.array([0.0, 1.0e-6, 2.0e-6], dtype=np.float64),
            volts=np.array([0.123456789, -0.5, 0.75], dtype=np.float64),
            points=3,
            unit=RigolWFM.channel.UnitEnum.v,
            volt_per_division=1.0,
            time_scale=1.0e-6,
        )
    ]
    waveform.logic_channels = {"D6": np.array([0, 1, 0], dtype=np.uint8)}
    waveform.logic_times = np.array([0.0, 1.0e-6, 2.0e-6], dtype=np.float64)
    waveform.logic_seconds_per_point = 1.0e-6

    lines = waveform.sigrokcsv().splitlines()

    assert lines[0].split(",") == ["X", "CH1 (V)", "D6"]
    row1 = lines[2].split(",")
    assert float(row1[0]) == pytest.approx(1.0e-6, rel=1e-12, abs=1e-18)
    assert float(row1[1]) == pytest.approx(-0.5, rel=1e-12, abs=1e-18)
    assert row1[2] == "1"
    assert "0.123456789" in lines[1]


def test_sigrokcsv_preserves_high_resolution_time_axis():
    """Fast-sampled captures should keep adjacent timestamps distinguishable."""
    waveform = RigolWFM.wfm.Wfm.from_file("tests/files/wfm/DS1054Z-A.wfm", "Z")
    assert waveform.channels
    assert waveform.channels[0].times is not None

    actual_increment = float(waveform.channels[0].times[1] - waveform.channels[0].times[0])
    lines = waveform.sigrokcsv().splitlines()
    exported_increment = float(lines[2].split(",")[0]) - float(lines[1].split(",")[0])

    assert exported_increment == pytest.approx(actual_increment, rel=1e-12, abs=1e-18)


def test_sigrok_input_format_covers_all_exported_series():
    """Sigrok import options should describe every exported analog and logic column."""
    waveform = RigolWFM.wfm.Wfm("synthetic.sigrok")
    waveform.channels = [
        SimpleNamespace(
            name="CH1",
            enabled_and_selected=True,
            times=np.array([0.0, 1.0e-6], dtype=np.float64),
            volts=np.array([0.1, 0.2], dtype=np.float64),
            points=2,
            unit=RigolWFM.channel.UnitEnum.v,
            volt_per_division=1.0,
            time_scale=1.0e-6,
        ),
        SimpleNamespace(
            name="CH2",
            enabled_and_selected=True,
            times=np.array([0.0, 1.0e-6], dtype=np.float64),
            volts=np.array([0.3, 0.4], dtype=np.float64),
            points=2,
            unit=RigolWFM.channel.UnitEnum.v,
            volt_per_division=1.0,
            time_scale=1.0e-6,
        ),
    ]
    waveform.logic_channels = {
        "D0": np.array([0, 1], dtype=np.uint8),
        "D1": np.array([1, 0], dtype=np.uint8),
    }
    waveform.logic_times = np.array([0.0, 1.0e-6], dtype=np.float64)
    waveform.logic_seconds_per_point = 1.0e-6

    assert (
        RigolWFM.wfmconvert._sigrok_csv_input_format(waveform)
        == "csv:start_line=1:header=true:samplerate=1000000:column_formats=t,2a,2l"
    )


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
