"""Helpers for invoking CLI commands in integration-style tests."""

import shlex
import shutil
import subprocess
import sys
from pathlib import Path

_UV = shutil.which("uv")


def wfmconvert_command(arguments: str = "") -> str:
    """Build a shell-safe `wfmconvert` command using the active `uv` environment."""
    if _UV is not None:
        base = f"{shlex.quote(_UV)} run python -m RigolWFM.wfmconvert"
    else:
        executable = getattr(sys, "_base_executable", sys.executable)
        base = f"{shlex.quote(executable)} -m RigolWFM.wfmconvert"

    stripped = arguments.strip()
    return f"{base} {stripped}" if stripped else base


def _resolve_command(command: str) -> str:
    """Rewrite local console-script invocations to use the current interpreter."""
    stripped = command.lstrip()
    if stripped == "wfmconvert" or stripped.startswith("wfmconvert "):
        suffix = stripped[len("wfmconvert") :]
        return wfmconvert_command(suffix)
    return command


def run_command_result(command):
    """Run a shell command and return the completed process."""
    return subprocess.run(
        _resolve_command(command),
        shell=True,
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )


def run_command(command):
    """Run a shell command and assert that it exits successfully."""
    result = run_command_result(command)
    assert result.returncode == 0, result.stderr


def run_command_stdout(command):
    """Run a shell command, assert success, and return normalized stdout."""
    result = run_command_result(command)
    assert result.returncode == 0, result.stderr
    return result.stdout.replace("\r\n", "\n")


def run_command_failure(command):
    """Run a shell command and assert that it exits with a non-zero code."""
    result = run_command_result(command)
    assert result.returncode != 0
    return result


def assert_command_matches_file(command, expected_path):
    """Assert that command stdout matches the checked-in expected text."""
    actual = run_command_stdout(command).rstrip("\n")
    expected = Path(expected_path).read_text(encoding="utf-8").replace("\r\n", "\n").rstrip("\n")
    assert actual == expected


def assert_wfmconvert_info_snapshot(scope, stem, family):
    """Assert that `wfmconvert --model <scope> info` matches a checked-in snapshot."""
    expected = Path(__file__).resolve().parent / "expected_info" / family / f"{stem}.txt"
    command = f"wfmconvert --model {scope} info tests/files/wfm/{stem}.wfm"
    assert_command_matches_file(command, expected)


def assert_wfmconvert_info_snapshot_file(scope, infile, family, stem):
    """Assert that `wfmconvert --model <scope> info <infile>` matches a snapshot."""
    expected = Path(__file__).resolve().parent / "expected_info" / family / f"{stem}.txt"
    command = f"wfmconvert --model {scope} info {infile}"
    assert_command_matches_file(command, expected)
