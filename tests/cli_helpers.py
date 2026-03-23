"""Helpers for invoking CLI commands in integration-style tests."""

import subprocess
from pathlib import Path


def run_command(command):
    """Run a shell command and assert that it exits successfully."""
    result = subprocess.run(
        command,
        shell=True,
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    assert result.returncode == 0, result.stderr


def run_command_stdout(command):
    """Run a shell command, assert success, and return normalized stdout."""
    result = subprocess.run(
        command,
        shell=True,
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    return result.stdout.replace("\r\n", "\n")


def assert_command_matches_file(command, expected_path):
    """Assert that command stdout matches the checked-in expected text."""
    actual = run_command_stdout(command).rstrip("\n")
    expected = (
        Path(expected_path)
        .read_text(encoding="utf-8")
        .replace("\r\n", "\n")
        .rstrip("\n")
    )
    assert actual == expected


def assert_wfmconvert_info_snapshot(scope, stem, family):
    """Assert that `wfmconvert <scope> info` matches a checked-in snapshot."""
    expected = Path(__file__).resolve().parent / "expected_info" / family / f"{stem}.txt"
    command = f"wfmconvert {scope} info wfm/{stem}.wfm"
    assert_command_matches_file(command, expected)
