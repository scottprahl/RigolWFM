"""Smoke tests for the browser-side `wfmview` assets."""

import io
import json
from pathlib import Path
import re
import shutil
import struct
import subprocess
import zipfile
from typing import cast

import numpy as np
import numpy.typing as npt
import pytest

from tests.mat_helpers import load_simple_mat_v5

_ROOT = Path(__file__).resolve().parents[1]
_INDEX = _ROOT / "wfmview" / "index.html"
_APP = _ROOT / "wfmview" / "app.js"
_SCRIPT_RE = re.compile(r'<script defer src="\./([^"?]+\.js)(?:\?[^"]*)?"></script>')


def _viewer_script_paths() -> list[Path]:
    """Return local JS assets referenced by the viewer index page."""
    text = _INDEX.read_text(encoding="utf-8")
    return [(_ROOT / "wfmview" / match.group(1)) for match in _SCRIPT_RE.finditer(text)]


_EMIT_SCRIPT = _ROOT / "wfmview" / "tests" / "emit.js"


def _emit(what: str) -> subprocess.CompletedProcess:
    """Run the viewer's export emitter and return its captured output.

    The JavaScript that builds these artifacts lives in
    ``wfmview/tests/emit.js``; what belongs on this side is checking that
    NumPy, the MAT reader and ``zipfile`` can read what it wrote.
    """
    return subprocess.run(
        ["node", str(_EMIT_SCRIPT), what],
        check=True,
        capture_output=True,
    )


def _load_npz_arrays(source: io.BytesIO) -> dict[str, npt.NDArray[np.generic]]:
    """Read a viewer-generated NPZ archive into plain NumPy arrays."""
    with np.load(source) as archive:
        return {name: cast(npt.NDArray[np.generic], np.asarray(archive[name])) for name in archive.files}


def test_wfmview_referenced_scripts_exist():
    """Every local script referenced by `index.html` should exist on disk."""
    for path in _viewer_script_paths():
        assert path.exists(), f"Missing viewer script: {path}"


def test_wfmview_open_file_picker_accepts_supported_extensions():
    """The file picker should advertise every supported top-level viewer format."""
    text = _APP.read_text(encoding="utf-8")
    assert "inp.accept = '.wfm,.bin,.trc,.isf';" in text


def test_wfmview_index_mentions_rtp_and_loads_rs_parser():
    """The viewer index should advertise and load the R&S RTP support path."""
    text = _INDEX.read_text(encoding="utf-8")
    assert "Rohde &amp; Schwarz RTP .bin" in text
    assert '<script defer src="./RohdeSchwarzRtpWfmBin.js"></script>' in text


def test_wfmview_index_describes_sr_export_as_sigrok_session_archive():
    """The SR export button text should describe the real `.sr` archive output."""
    text = _INDEX.read_text(encoding="utf-8")
    assert "Sigrok session archive (.sr) for PulseView / sigrok-cli" in text


def test_wfmview_index_describes_npz_and_mat_exports():
    """The export modal should advertise the new MAT and NPZ outputs."""
    text = _INDEX.read_text(encoding="utf-8")
    assert "NumPy archive of arrays" in text
    assert "MATLAB .mat file with numeric arrays for each visible channel" in text


def test_wfmview_export_modal_lists_formats_alphabetically():
    """The export modal should list formats in alphabetical order."""
    text = _INDEX.read_text(encoding="utf-8")
    button_ids = re.findall(r'<button class="exp-btn" id="([^"]+)">', text)
    assert button_ids == [
        "exp-csv",
        "exp-info",
        "exp-mat",
        "exp-npz",
        "exp-png",
        "exp-pwl",
        "exp-sigrok",
        "exp-svg",
        "exp-wav",
    ]


@pytest.mark.skipif(shutil.which("node") is None, reason="node is not installed")
@pytest.mark.parametrize("path", _viewer_script_paths(), ids=lambda path: Path(path).name)
def test_wfmview_javascript_is_syntax_valid(path: Path):
    """Viewer JavaScript assets should pass a Node syntax check."""
    subprocess.run(["node", "--check", str(path)], check=True)


@pytest.mark.skipif(shutil.which("node") is None, reason="node is not installed")
def test_wfmview_npz_export_builds_real_mixed_archive():
    """Viewer NPZ export should write real NumPy arrays for mixed traces."""
    result = _emit("npz")

    arrays = _load_npz_arrays(io.BytesIO(result.stdout))
    assert set(arrays) == {"time", "start", "increment", "CH1", "D6"}
    assert arrays["CH1"].dtype == np.dtype(np.float64)
    assert arrays["D6"].dtype == np.dtype(np.uint8)
    assert arrays["CH1"].tolist() == pytest.approx([0.25, -0.5, 0.75])
    assert arrays["D6"].tolist() == [0, 1, 0]
    assert arrays["start"][0] == pytest.approx(0.0)
    assert arrays["increment"][0] == pytest.approx(1.0e-6)


@pytest.mark.skipif(shutil.which("node") is None, reason="node is not installed")
def test_wfmview_mat_export_builds_real_mixed_file():
    """Viewer MAT export should write MATLAB arrays for mixed traces."""
    result = _emit("mat")

    arrays = load_simple_mat_v5(result.stdout)
    assert set(arrays) == {"time", "start", "increment", "CH1", "D6"}
    assert arrays["CH1"].tolist() == pytest.approx([0.25, -0.5, 0.75])
    assert arrays["D6"].tolist() == pytest.approx([0.0, 1.0, 0.0])
    assert arrays["start"][0] == pytest.approx(0.0)
    assert arrays["increment"][0] == pytest.approx(1.0e-6)


@pytest.mark.skipif(shutil.which("node") is None, reason="node is not installed")
def test_wfmview_npz_and_mat_exports_download_expected_files():
    """The NPZ and MAT export actions should download the right file types."""
    result = _emit("downloads")

    captures = json.loads(result.stdout)

    assert captures[0]["filename"] == "scope-shot.npz"
    assert captures[0]["mime"] == "application/zip"
    assert captures[0]["bytes"] == [80, 75, 3, 4]

    assert captures[1]["filename"] == "scope-shot.mat"
    assert captures[1]["mime"] == "application/octet-stream"
    assert captures[1]["bytes"] == [77, 65, 84, 76]


@pytest.mark.skipif(shutil.which("node") is None, reason="node is not installed")
def test_wfmview_sigrok_export_builds_real_mixed_session_archive():
    """Viewer SR export should build a real sigrok session for mixed traces."""
    result = _emit("sigrok-mixed")

    with zipfile.ZipFile(io.BytesIO(result.stdout)) as archive:
        assert archive.namelist() == ["version", "metadata", "logic-1-1", "analog-1-2-1"]
        assert archive.read("version") == b"2"

        metadata = archive.read("metadata").decode("utf-8")
        assert "capturefile=logic-1" in metadata
        assert "total probes=1" in metadata
        assert "samplerate=1 MHz" in metadata
        assert "total analog=1" in metadata
        assert "probe1=D6" in metadata
        assert "analog2=CH1 (V)" in metadata
        assert "unitsize=1" in metadata

        logic = archive.read("logic-1-1")
        assert logic == bytes([0, 1, 0])

        analog = archive.read("analog-1-2-1")
        assert struct.unpack("<fff", analog) == pytest.approx((0.25, -0.5, 0.75), rel=1e-7, abs=1e-7)


@pytest.mark.skipif(shutil.which("node") is None, reason="node is not installed")
def test_wfmview_sigrok_export_builds_real_logic_only_session_archive():
    """Viewer SR export should write logic-only captures as named probes."""
    result = _emit("sigrok-logic")

    with zipfile.ZipFile(io.BytesIO(result.stdout)) as archive:
        assert archive.namelist() == ["version", "metadata", "logic-1-1"]

        metadata = archive.read("metadata").decode("utf-8")
        assert "capturefile=logic-1" in metadata
        assert "total probes=1" in metadata
        assert "samplerate=1 kHz" in metadata
        assert "total analog=0" in metadata
        assert "probe1=D6" in metadata
        assert "unitsize=1" in metadata

        logic = archive.read("logic-1-1")
        assert logic == bytes([0, 1, 1])
