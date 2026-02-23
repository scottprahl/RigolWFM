"""Helpers for invoking CLI commands in integration-style tests."""

import subprocess


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
