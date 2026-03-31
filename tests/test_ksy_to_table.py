"""Tests for the `scripts/ksy_to_table.py` helper."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "ksy_to_table.py"


def _run_script(*args: str) -> subprocess.CompletedProcess[str]:
    """Run the schema-table script and capture its output."""
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )


def test_rst_output_preserves_schema_doc_and_includes_types_and_enums():
    """RST output should keep the top-level schema doc and summarize types/enums."""
    result = _run_script("ksy/agilent_agxx_bin.ksy")

    assert result.returncode == 0, result.stderr
    assert "Agilent / Keysight AGxx Binary Format" in result.stdout
    assert "Metadata" in result.stdout
    assert "Top-Level Sequence" in result.stdout
    assert "File layout::" in result.stdout
    assert "Sources used for this KSY binary format:" in result.stdout
    assert "Type: waveform_header" in result.stdout
    assert "Enum: unit_enum" in result.stdout
    assert "repeat-expr=file_header.n_waveforms" in result.stdout


def test_rst_output_includes_parameters_and_size_eos():
    """reStructuredText output should render top-level params and size-eos fields."""
    result = _run_script("ksy/yokogawa_dl_we_wvf.ksy")

    assert result.returncode == 0, result.stderr
    assert "Yokogawa" in result.stdout
    assert "Parameters" in result.stdout
    assert "len_leading_unused" in result.stdout
    assert "samples_raw" in result.stdout
    assert "size=eos" in result.stdout


def test_script_can_write_output_file(tmp_path: Path):
    """The CLI should support writing rendered output to a file."""
    output_path = tmp_path / "rohde.rst"
    result = _run_script(
        "--output",
        str(output_path),
        "ksy/rohde_schwarz_rtp_wfm_bin.ksy",
    )

    assert result.returncode == 0, result.stderr
    assert output_path.exists()
    assert "Rohde & Schwarz RTP WFM.BIN Binary Format" in output_path.read_text(encoding="utf-8")
