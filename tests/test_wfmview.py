"""Smoke tests for the browser-side `wfmview` assets."""

import io
import json
from pathlib import Path
import re
import shutil
import struct
import subprocess
import textwrap
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
def test_wfmview_rohde_schwarz_helpers_execute_under_node():
    """Selected R&S helper functions should execute correctly in a stubbed DOM."""
    script = textwrap.dedent(f"""
        const fs = require('fs');
        const vm = require('vm');

        function makeClassList() {{
            return {{
                add() {{}},
                remove() {{}},
                toggle() {{}},
                contains() {{ return false; }},
            }};
        }}

        function makeElement() {{
            return {{
                checked: false,
                disabled: false,
                innerHTML: '',
                textContent: '',
                value: '',
                dataset: {{}},
                style: {{}},
                classList: makeClassList(),
                addEventListener() {{}},
                removeEventListener() {{}},
                appendChild() {{}},
                removeChild() {{}},
                setAttribute() {{}},
                getAttribute() {{ return null; }},
                getContext() {{
                    return {{
                        fillRect() {{}},
                        beginPath() {{}},
                        moveTo() {{}},
                        lineTo() {{}},
                        stroke() {{}},
                        fillText() {{}},
                        measureText() {{ return {{ width: 0 }}; }},
                        save() {{}},
                        restore() {{}},
                        clearRect() {{}},
                        arc() {{}},
                        closePath() {{}},
                        setLineDash() {{}},
                    }};
                }},
                getBoundingClientRect() {{
                    return {{ left: 0, top: 0, right: 800, bottom: 480, width: 800, height: 480 }};
                }},
                closest() {{ return null; }},
                click() {{}},
                width: 800,
                height: 480,
                offsetWidth: 800,
                offsetHeight: 480,
                clientWidth: 800,
                clientHeight: 480,
            }};
        }}

        global.document = {{
            getElementById() {{ return makeElement(); }},
            createElement() {{ return makeElement(); }},
            addEventListener() {{}},
            removeEventListener() {{}},
            body: {{
                classList: makeClassList(),
                appendChild() {{}},
                removeChild() {{}},
            }},
        }};
        global.window = {{
            addEventListener() {{}},
            removeEventListener() {{}},
            innerHeight: 800,
            URL: {{
                createObjectURL() {{ return 'blob:test'; }},
                revokeObjectURL() {{}},
            }},
        }};
        global.FileReader = function FileReader() {{}};

        vm.runInThisContext(fs.readFileSync({json.dumps(str(_APP))}, 'utf8'), {{ filename: 'app.js' }});

        const fileMap = buildSelectedFileMap([
            {{ name: 'singleChan.bin' }},
            {{ name: 'singleChan.Wfm.bin' }},
        ]);
        if (!shouldSkipRohdeSchwarzPayload({{ name: 'singleChan.Wfm.bin' }}, fileMap)) {{
            throw new Error('Expected companion payload to be skipped when metadata is selected.');
        }}
        if (shouldSkipRohdeSchwarzPayload({{ name: 'orphan.Wfm.bin' }}, {{}})) {{
            throw new Error('Unexpected skip for an orphan payload file.');
        }}
        if (rohdeSchwarzPayloadLookupName('singleChan.bin') !== 'singlechan.wfm.bin') {{
            throw new Error('Unexpected companion lookup name.');
        }}

        const xml = new TextEncoder().encode('<?xml version="1.0"?><Database SaveItemType="Data"></Database>');
        if (!looksLikeRohdeSchwarzMetadata(xml.buffer, 'singleChan.bin')) {{
            throw new Error('Failed to recognize R&S metadata.');
        }}
        if (looksLikeRohdeSchwarzMetadata(xml.buffer, 'singleChan.Wfm.bin')) {{
            throw new Error('Payload files must not be treated as metadata.');
        }}
        """)

    subprocess.run(["node", "-e", script], check=True, text=True)


@pytest.mark.skipif(shutil.which("node") is None, reason="node is not installed")
def test_wfmview_csv_export_matches_python_digital_format():
    """Viewer CSV export should emit STATE columns and integer digital samples."""
    script = textwrap.dedent(f"""
        const fs = require('fs');
        const vm = require('vm');

        function makeClassList() {{
            return {{
                add() {{}},
                remove() {{}},
                toggle() {{}},
                contains() {{ return false; }},
            }};
        }}

        function makeElement() {{
            return {{
                checked: false,
                disabled: false,
                innerHTML: '',
                textContent: '',
                value: '',
                dataset: {{}},
                style: {{}},
                classList: makeClassList(),
                addEventListener() {{}},
                removeEventListener() {{}},
                appendChild() {{}},
                removeChild() {{}},
                setAttribute() {{}},
                getAttribute() {{ return null; }},
                getContext() {{
                    return {{
                        fillRect() {{}},
                        beginPath() {{}},
                        moveTo() {{}},
                        lineTo() {{}},
                        stroke() {{}},
                        fillText() {{}},
                        measureText() {{ return {{ width: 0 }}; }},
                        save() {{}},
                        restore() {{}},
                        clearRect() {{}},
                        arc() {{}},
                        closePath() {{}},
                        setLineDash() {{}},
                    }};
                }},
                getBoundingClientRect() {{
                    return {{ left: 0, top: 0, right: 800, bottom: 480, width: 800, height: 480 }};
                }},
                closest() {{ return null; }},
                click() {{}},
                width: 800,
                height: 480,
                offsetWidth: 800,
                offsetHeight: 480,
                clientWidth: 800,
                clientHeight: 480,
            }};
        }}

        global.document = {{
            getElementById() {{ return makeElement(); }},
            createElement() {{ return makeElement(); }},
            addEventListener() {{}},
            removeEventListener() {{}},
            body: {{
                classList: makeClassList(),
                appendChild() {{}},
                removeChild() {{}},
            }},
        }};
        global.window = {{
            addEventListener() {{}},
            removeEventListener() {{}},
            innerHeight: 800,
            URL: {{
                createObjectURL() {{ return 'blob:test'; }},
                revokeObjectURL() {{}},
            }},
        }};
        global.FileReader = function FileReader() {{}};

        vm.runInThisContext(fs.readFileSync({json.dumps(str(_APP))}, 'utf8'), {{ filename: 'app.js' }});

        const mixedEntry = {{
            result: {{
                channels: [
                    {{
                        name: 'CH1',
                        times: Float64Array.from([0, 1e-6, 2e-6]),
                        volts: Float64Array.from([0.25, -0.5, 0.75]),
                        voltPerDiv: 1e-3,
                        timeScale: 1e-6,
                    }},
                    {{
                        name: 'D6',
                        kind: 'digital',
                        times: Float64Array.from([0, 1e-6, 2e-6]),
                        volts: Float64Array.from([0, 1, 0]),
                        voltPerDiv: 0.25,
                        timeScale: 1e-6,
                    }},
                ],
            }},
            channelEnabled: [true, true],
        }};
        const mixedLines = buildExportCSVText(mixedEntry).split('\\n');
        if (mixedLines[0] !== 'X,CH1,D6,Start,Increment') {{
            throw new Error('Mixed CSV header should include the digital channel.');
        }}
        if (mixedLines[1] !== 'µs,mV,STATE,0,1') {{
            throw new Error('Mixed CSV units row should match the Python digital export shape.');
        }}
        if (mixedLines[2] !== '0,250.00,0' || mixedLines[3] !== '1,-500.00,1') {{
            throw new Error('Mixed CSV data rows should keep analog decimals and digital 0/1 values.');
        }}

        const logicEntry = {{
            result: {{
                channels: [
                    {{
                        name: 'D6',
                        kind: 'digital',
                        times: Float64Array.from([0.001, 0.002, 0.003]),
                        volts: Float64Array.from([0, 1, 1]),
                        voltPerDiv: 0.25,
                        timeScale: 0.001,
                    }},
                ],
            }},
            channelEnabled: [true],
        }};
        const logicLines = buildExportCSVText(logicEntry).split('\\n');
        if (logicLines[0] !== 'X,D6,Start,Increment') {{
            throw new Error('Logic-only CSV header should include the digital trace name.');
        }}
        if (logicLines[1] !== 'ms,STATE,1,1') {{
            throw new Error('Logic-only CSV should export STATE units and linear metadata.');
        }}
        if (logicLines[2] !== '1,0' || logicLines[3] !== '2,1') {{
            throw new Error('Logic-only CSV rows should contain integer digital samples.');
        }}
        """)

    subprocess.run(["node", "-e", script], check=True, text=True)


@pytest.mark.skipif(shutil.which("node") is None, reason="node is not installed")
def test_wfmview_npz_export_builds_real_mixed_archive():
    """Viewer NPZ export should write real NumPy arrays for mixed traces."""
    script = textwrap.dedent(f"""
        const fs = require('fs');
        const vm = require('vm');

        function makeClassList() {{
            return {{
                add() {{}},
                remove() {{}},
                toggle() {{}},
                contains() {{ return false; }},
            }};
        }}

        function makeElement() {{
            return {{
                checked: false,
                disabled: false,
                innerHTML: '',
                textContent: '',
                value: '',
                dataset: {{}},
                style: {{}},
                classList: makeClassList(),
                addEventListener() {{}},
                removeEventListener() {{}},
                appendChild() {{}},
                removeChild() {{}},
                setAttribute() {{}},
                getAttribute() {{ return null; }},
                getContext() {{
                    return {{
                        fillRect() {{}},
                        beginPath() {{}},
                        moveTo() {{}},
                        lineTo() {{}},
                        stroke() {{}},
                        fillText() {{}},
                        measureText() {{ return {{ width: 0 }}; }},
                        save() {{}},
                        restore() {{}},
                        clearRect() {{}},
                        arc() {{}},
                        closePath() {{}},
                        setLineDash() {{}},
                    }};
                }},
                getBoundingClientRect() {{
                    return {{ left: 0, top: 0, right: 800, bottom: 480, width: 800, height: 480 }};
                }},
                closest() {{ return null; }},
                click() {{}},
                width: 800,
                height: 480,
                offsetWidth: 800,
                offsetHeight: 480,
                clientWidth: 800,
                clientHeight: 480,
            }};
        }}

        global.document = {{
            getElementById() {{ return makeElement(); }},
            createElement() {{ return makeElement(); }},
            addEventListener() {{}},
            removeEventListener() {{}},
            body: {{
                classList: makeClassList(),
                appendChild() {{}},
                removeChild() {{}},
            }},
        }};
        global.window = {{
            addEventListener() {{}},
            removeEventListener() {{}},
            innerHeight: 800,
            URL: {{
                createObjectURL() {{ return 'blob:test'; }},
                revokeObjectURL() {{}},
            }},
        }};
        global.FileReader = function FileReader() {{}};

        vm.runInThisContext(fs.readFileSync({json.dumps(str(_APP))}, 'utf8'), {{ filename: 'app.js' }});

        const entry = {{
            result: {{
                channels: [
                    {{
                        name: 'CH1',
                        times: Float64Array.from([0, 1e-6, 2e-6]),
                        volts: Float64Array.from([0.25, -0.5, 0.75]),
                        voltPerDiv: 1e-3,
                        timeScale: 1e-6,
                    }},
                    {{
                        name: 'D6',
                        kind: 'digital',
                        times: Float64Array.from([0, 1e-6, 2e-6]),
                        volts: Float64Array.from([0, 1, 0]),
                        voltPerDiv: 0.25,
                        timeScale: 1e-6,
                    }},
                ],
            }},
            channelEnabled: [true, true],
        }};

        const archive = buildExportNPZArchive(entry);
        if (!archive) {{
            throw new Error('Expected mixed entry to produce an NPZ archive.');
        }}
        process.stdout.write(Buffer.from(archive));
        """)

    result = subprocess.run(["node", "-e", script], check=True, stdout=subprocess.PIPE)
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
    script = textwrap.dedent(f"""
        const fs = require('fs');
        const vm = require('vm');

        function makeClassList() {{
            return {{
                add() {{}},
                remove() {{}},
                toggle() {{}},
                contains() {{ return false; }},
            }};
        }}

        function makeElement() {{
            return {{
                checked: false,
                disabled: false,
                innerHTML: '',
                textContent: '',
                value: '',
                dataset: {{}},
                style: {{}},
                classList: makeClassList(),
                addEventListener() {{}},
                removeEventListener() {{}},
                appendChild() {{}},
                removeChild() {{}},
                setAttribute() {{}},
                getAttribute() {{ return null; }},
                getContext() {{
                    return {{
                        fillRect() {{}},
                        beginPath() {{}},
                        moveTo() {{}},
                        lineTo() {{}},
                        stroke() {{}},
                        fillText() {{}},
                        measureText() {{ return {{ width: 0 }}; }},
                        save() {{}},
                        restore() {{}},
                        clearRect() {{}},
                        arc() {{}},
                        closePath() {{}},
                        setLineDash() {{}},
                    }};
                }},
                getBoundingClientRect() {{
                    return {{ left: 0, top: 0, right: 800, bottom: 480, width: 800, height: 480 }};
                }},
                closest() {{ return null; }},
                click() {{}},
                width: 800,
                height: 480,
                offsetWidth: 800,
                offsetHeight: 480,
                clientWidth: 800,
                clientHeight: 480,
            }};
        }}

        global.document = {{
            getElementById() {{ return makeElement(); }},
            createElement() {{ return makeElement(); }},
            addEventListener() {{}},
            removeEventListener() {{}},
            body: {{
                classList: makeClassList(),
                appendChild() {{}},
                removeChild() {{}},
            }},
        }};
        global.window = {{
            addEventListener() {{}},
            removeEventListener() {{}},
            innerHeight: 800,
            URL: {{
                createObjectURL() {{ return 'blob:test'; }},
                revokeObjectURL() {{}},
            }},
        }};
        global.FileReader = function FileReader() {{}};

        vm.runInThisContext(fs.readFileSync({json.dumps(str(_APP))}, 'utf8'), {{ filename: 'app.js' }});

        const entry = {{
            result: {{
                channels: [
                    {{
                        name: 'CH1',
                        times: Float64Array.from([0, 1e-6, 2e-6]),
                        volts: Float64Array.from([0.25, -0.5, 0.75]),
                        voltPerDiv: 1e-3,
                        timeScale: 1e-6,
                    }},
                    {{
                        name: 'D6',
                        kind: 'digital',
                        times: Float64Array.from([0, 1e-6, 2e-6]),
                        volts: Float64Array.from([0, 1, 0]),
                        voltPerDiv: 0.25,
                        timeScale: 1e-6,
                    }},
                ],
            }},
            channelEnabled: [true, true],
        }};

        const payload = buildExportMATPayload(entry);
        if (!payload) {{
            throw new Error('Expected mixed entry to produce a MAT file.');
        }}
        process.stdout.write(Buffer.from(payload));
        """)

    result = subprocess.run(["node", "-e", script], check=True, stdout=subprocess.PIPE)
    arrays = load_simple_mat_v5(result.stdout)
    assert set(arrays) == {"time", "start", "increment", "CH1", "D6"}
    assert arrays["CH1"].tolist() == pytest.approx([0.25, -0.5, 0.75])
    assert arrays["D6"].tolist() == pytest.approx([0.0, 1.0, 0.0])
    assert arrays["start"][0] == pytest.approx(0.0)
    assert arrays["increment"][0] == pytest.approx(1.0e-6)


@pytest.mark.skipif(shutil.which("node") is None, reason="node is not installed")
def test_wfmview_npz_and_mat_exports_download_expected_files():
    """The NPZ and MAT export actions should download the right file types."""
    script = textwrap.dedent(f"""
        const fs = require('fs');
        const vm = require('vm');

        function makeClassList() {{
            return {{
                add() {{}},
                remove() {{}},
                toggle() {{}},
                contains() {{ return false; }},
            }};
        }}

        function makeElement() {{
            return {{
                checked: false,
                disabled: false,
                innerHTML: '',
                textContent: '',
                value: '',
                dataset: {{}},
                style: {{}},
                classList: makeClassList(),
                addEventListener() {{}},
                removeEventListener() {{}},
                appendChild() {{}},
                removeChild() {{}},
                setAttribute() {{}},
                getAttribute() {{ return null; }},
                getContext() {{
                    return {{
                        fillRect() {{}},
                        beginPath() {{}},
                        moveTo() {{}},
                        lineTo() {{}},
                        stroke() {{}},
                        fillText() {{}},
                        measureText() {{ return {{ width: 0 }}; }},
                        save() {{}},
                        restore() {{}},
                        clearRect() {{}},
                        arc() {{}},
                        closePath() {{}},
                        setLineDash() {{}},
                    }};
                }},
                getBoundingClientRect() {{
                    return {{ left: 0, top: 0, right: 800, bottom: 480, width: 800, height: 480 }};
                }},
                closest() {{ return null; }},
                click() {{}},
                width: 800,
                height: 480,
                offsetWidth: 800,
                offsetHeight: 480,
                clientWidth: 800,
                clientHeight: 480,
            }};
        }}

        global.document = {{
            getElementById() {{ return makeElement(); }},
            createElement() {{ return makeElement(); }},
            addEventListener() {{}},
            removeEventListener() {{}},
            body: {{
                classList: makeClassList(),
                appendChild() {{}},
                removeChild() {{}},
            }},
        }};
        global.window = {{
            addEventListener() {{}},
            removeEventListener() {{}},
            innerHeight: 800,
            URL: {{
                createObjectURL() {{ return 'blob:test'; }},
                revokeObjectURL() {{}},
            }},
        }};
        global.FileReader = function FileReader() {{}};

        vm.runInThisContext(fs.readFileSync({json.dumps(str(_APP))}, 'utf8'), {{ filename: 'app.js' }});

        loadedFiles = [{{
            id: 'file-1',
            stem: 'scope-shot',
            filename: 'scope-shot.wfm',
            result: {{
                channels: [
                    {{
                        name: 'CH1',
                        times: Float64Array.from([0, 1e-6]),
                        volts: Float64Array.from([0.1, 0.2]),
                        voltPerDiv: 1e-3,
                        timeScale: 1e-6,
                    }},
                    {{
                        name: 'D6',
                        kind: 'digital',
                        times: Float64Array.from([0, 1e-6]),
                        volts: Float64Array.from([0, 1]),
                        voltPerDiv: 0.25,
                        timeScale: 1e-6,
                    }},
                ],
            }},
            channelEnabled: [true, true],
        }}];
        activeFileId = 'file-1';
        currentFilename = 'scope-shot';

        const captures = [];
        triggerDownload = function(data, filename, mime) {{
            captures.push({{ filename, mime, bytes: Array.from(data.slice(0, 4)) }});
        }};

        doExportNPZ();
        doExportMAT();
        process.stdout.write(JSON.stringify(captures));
        """)

    result = subprocess.run(["node", "-e", script], check=True, stdout=subprocess.PIPE, text=True)
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
    script = textwrap.dedent(f"""
        const fs = require('fs');
        const vm = require('vm');

        function makeClassList() {{
            return {{
                add() {{}},
                remove() {{}},
                toggle() {{}},
                contains() {{ return false; }},
            }};
        }}

        function makeElement() {{
            return {{
                checked: false,
                disabled: false,
                innerHTML: '',
                textContent: '',
                value: '',
                dataset: {{}},
                style: {{}},
                classList: makeClassList(),
                addEventListener() {{}},
                removeEventListener() {{}},
                appendChild() {{}},
                removeChild() {{}},
                setAttribute() {{}},
                getAttribute() {{ return null; }},
                getContext() {{
                    return {{
                        fillRect() {{}},
                        beginPath() {{}},
                        moveTo() {{}},
                        lineTo() {{}},
                        stroke() {{}},
                        fillText() {{}},
                        measureText() {{ return {{ width: 0 }}; }},
                        save() {{}},
                        restore() {{}},
                        clearRect() {{}},
                        arc() {{}},
                        closePath() {{}},
                        setLineDash() {{}},
                    }};
                }},
                getBoundingClientRect() {{
                    return {{ left: 0, top: 0, right: 800, bottom: 480, width: 800, height: 480 }};
                }},
                closest() {{ return null; }},
                click() {{}},
                width: 800,
                height: 480,
                offsetWidth: 800,
                offsetHeight: 480,
                clientWidth: 800,
                clientHeight: 480,
            }};
        }}

        global.document = {{
            getElementById() {{ return makeElement(); }},
            createElement() {{ return makeElement(); }},
            addEventListener() {{}},
            removeEventListener() {{}},
            body: {{
                classList: makeClassList(),
                appendChild() {{}},
                removeChild() {{}},
            }},
        }};
        global.window = {{
            addEventListener() {{}},
            removeEventListener() {{}},
            innerHeight: 800,
            URL: {{
                createObjectURL() {{ return 'blob:test'; }},
                revokeObjectURL() {{}},
            }},
        }};
        global.FileReader = function FileReader() {{}};

        vm.runInThisContext(fs.readFileSync({json.dumps(str(_APP))}, 'utf8'), {{ filename: 'app.js' }});

        const entry = {{
            result: {{
                channels: [
                    {{
                        name: 'CH1',
                        times: Float64Array.from([0, 1e-6, 2e-6]),
                        volts: Float64Array.from([0.25, -0.5, 0.75]),
                        voltPerDiv: 1e-3,
                        timeScale: 1e-6,
                    }},
                    {{
                        name: 'D6',
                        kind: 'digital',
                        times: Float64Array.from([0, 1e-6, 2e-6]),
                        volts: Float64Array.from([0, 1, 0]),
                        voltPerDiv: 0.25,
                        timeScale: 1e-6,
                    }},
                ],
            }},
            channelEnabled: [true, true],
        }};

        const archive = buildExportSigrokArchive(entry);
        if (!archive) {{
            throw new Error('Expected mixed entry to produce an SR archive.');
        }}
        process.stdout.write(Buffer.from(archive));
        """)

    result = subprocess.run(["node", "-e", script], check=True, stdout=subprocess.PIPE)
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
    script = textwrap.dedent(f"""
        const fs = require('fs');
        const vm = require('vm');

        function makeClassList() {{
            return {{
                add() {{}},
                remove() {{}},
                toggle() {{}},
                contains() {{ return false; }},
            }};
        }}

        function makeElement() {{
            return {{
                checked: false,
                disabled: false,
                innerHTML: '',
                textContent: '',
                value: '',
                dataset: {{}},
                style: {{}},
                classList: makeClassList(),
                addEventListener() {{}},
                removeEventListener() {{}},
                appendChild() {{}},
                removeChild() {{}},
                setAttribute() {{}},
                getAttribute() {{ return null; }},
                getContext() {{
                    return {{
                        fillRect() {{}},
                        beginPath() {{}},
                        moveTo() {{}},
                        lineTo() {{}},
                        stroke() {{}},
                        fillText() {{}},
                        measureText() {{ return {{ width: 0 }}; }},
                        save() {{}},
                        restore() {{}},
                        clearRect() {{}},
                        arc() {{}},
                        closePath() {{}},
                        setLineDash() {{}},
                    }};
                }},
                getBoundingClientRect() {{
                    return {{ left: 0, top: 0, right: 800, bottom: 480, width: 800, height: 480 }};
                }},
                closest() {{ return null; }},
                click() {{}},
                width: 800,
                height: 480,
                offsetWidth: 800,
                offsetHeight: 480,
                clientWidth: 800,
                clientHeight: 480,
            }};
        }}

        global.document = {{
            getElementById() {{ return makeElement(); }},
            createElement() {{ return makeElement(); }},
            addEventListener() {{}},
            removeEventListener() {{}},
            body: {{
                classList: makeClassList(),
                appendChild() {{}},
                removeChild() {{}},
            }},
        }};
        global.window = {{
            addEventListener() {{}},
            removeEventListener() {{}},
            innerHeight: 800,
            URL: {{
                createObjectURL() {{ return 'blob:test'; }},
                revokeObjectURL() {{}},
            }},
        }};
        global.FileReader = function FileReader() {{}};

        vm.runInThisContext(fs.readFileSync({json.dumps(str(_APP))}, 'utf8'), {{ filename: 'app.js' }});

        const entry = {{
            result: {{
                channels: [
                    {{
                        name: 'D6',
                        kind: 'digital',
                        times: Float64Array.from([0.001, 0.002, 0.003]),
                        volts: Float64Array.from([0, 1, 1]),
                        voltPerDiv: 0.25,
                        timeScale: 0.001,
                    }},
                ],
            }},
            channelEnabled: [true],
        }};

        const archive = buildExportSigrokArchive(entry);
        if (!archive) {{
            throw new Error('Expected logic-only entry to produce an SR archive.');
        }}
        process.stdout.write(Buffer.from(archive));
        """)

    result = subprocess.run(["node", "-e", script], check=True, stdout=subprocess.PIPE)
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


@pytest.mark.skipif(shutil.which("node") is None, reason="node is not installed")
def test_wfmview_sigrok_export_downloads_sr_archive():
    """The SR export action should download a real `.sr` archive."""
    script = textwrap.dedent(f"""
        const fs = require('fs');
        const vm = require('vm');

        function makeClassList() {{
            return {{
                add() {{}},
                remove() {{}},
                toggle() {{}},
                contains() {{ return false; }},
            }};
        }}

        function makeElement() {{
            return {{
                checked: false,
                disabled: false,
                innerHTML: '',
                textContent: '',
                value: '',
                dataset: {{}},
                style: {{}},
                classList: makeClassList(),
                addEventListener() {{}},
                removeEventListener() {{}},
                appendChild() {{}},
                removeChild() {{}},
                setAttribute() {{}},
                getAttribute() {{ return null; }},
                getContext() {{
                    return {{
                        fillRect() {{}},
                        beginPath() {{}},
                        moveTo() {{}},
                        lineTo() {{}},
                        stroke() {{}},
                        fillText() {{}},
                        measureText() {{ return {{ width: 0 }}; }},
                        save() {{}},
                        restore() {{}},
                        clearRect() {{}},
                        arc() {{}},
                        closePath() {{}},
                        setLineDash() {{}},
                    }};
                }},
                getBoundingClientRect() {{
                    return {{ left: 0, top: 0, right: 800, bottom: 480, width: 800, height: 480 }};
                }},
                closest() {{ return null; }},
                click() {{}},
                width: 800,
                height: 480,
                offsetWidth: 800,
                offsetHeight: 480,
                clientWidth: 800,
                clientHeight: 480,
            }};
        }}

        global.document = {{
            getElementById() {{ return makeElement(); }},
            createElement() {{ return makeElement(); }},
            addEventListener() {{}},
            removeEventListener() {{}},
            body: {{
                classList: makeClassList(),
                appendChild() {{}},
                removeChild() {{}},
            }},
        }};
        global.window = {{
            addEventListener() {{}},
            removeEventListener() {{}},
            innerHeight: 800,
            URL: {{
                createObjectURL() {{ return 'blob:test'; }},
                revokeObjectURL() {{}},
            }},
        }};
        global.FileReader = function FileReader() {{}};

        vm.runInThisContext(fs.readFileSync({json.dumps(str(_APP))}, 'utf8'), {{ filename: 'app.js' }});

        loadedFiles = [{{
            id: 'file-1',
            stem: 'scope-shot',
            filename: 'scope-shot.wfm',
            result: {{
                channels: [
                    {{
                        name: 'D6',
                        kind: 'digital',
                        times: Float64Array.from([0, 1e-6]),
                        volts: Float64Array.from([0, 1]),
                        voltPerDiv: 0.25,
                        timeScale: 1e-6,
                    }},
                ],
            }},
            channelEnabled: [true],
        }}];
        activeFileId = 'file-1';
        currentFilename = 'scope-shot';

        let captured = null;
        triggerDownload = function(data, filename, mime) {{
            captured = {{ filename, mime, bytes: Array.from(data.slice(0, 4)) }};
        }};

        doExportSigrok();
        if (!captured) {{
            throw new Error('SR export did not trigger a download.');
        }}
        if (captured.filename !== 'scope-shot.sr') {{
            throw new Error('SR export should download a .sr file.');
        }}
        if (captured.mime !== 'application/zip') {{
            throw new Error('SR export should download the archive as application/zip.');
        }}
        if (JSON.stringify(captured.bytes) !== JSON.stringify([80, 75, 3, 4])) {{
            throw new Error('SR export should begin with a ZIP local-file header.');
        }}
        """)

    subprocess.run(["node", "-e", script], check=True, text=True)


@pytest.mark.skipif(shutil.which("node") is None, reason="node is not installed")
def test_wfmview_z_logic_helpers_execute_under_node():
    """Selected Z-series logic helper functions should expose digital traces like channels."""
    script = textwrap.dedent(f"""
        const fs = require('fs');
        const vm = require('vm');

        function makeClassList() {{
            return {{
                add() {{}},
                remove() {{}},
                toggle() {{}},
                contains() {{ return false; }},
            }};
        }}

        function makeElement() {{
            return {{
                checked: false,
                disabled: false,
                innerHTML: '',
                textContent: '',
                value: '',
                dataset: {{}},
                style: {{}},
                classList: makeClassList(),
                addEventListener() {{}},
                removeEventListener() {{}},
                appendChild() {{}},
                removeChild() {{}},
                setAttribute() {{}},
                getAttribute() {{ return null; }},
                getContext() {{
                    return {{
                        fillRect() {{}},
                        beginPath() {{}},
                        moveTo() {{}},
                        lineTo() {{}},
                        stroke() {{}},
                        fillText() {{}},
                        measureText() {{ return {{ width: 0 }}; }},
                        save() {{}},
                        restore() {{}},
                        clearRect() {{}},
                        arc() {{}},
                        closePath() {{}},
                        setLineDash() {{}},
                    }};
                }},
                getBoundingClientRect() {{
                    return {{ left: 0, top: 0, right: 800, bottom: 480, width: 800, height: 480 }};
                }},
                closest() {{ return null; }},
                click() {{}},
                width: 800,
                height: 480,
                offsetWidth: 800,
                offsetHeight: 480,
                clientWidth: 800,
                clientHeight: 480,
            }};
        }}

        global.document = {{
            getElementById() {{ return makeElement(); }},
            createElement() {{ return makeElement(); }},
            addEventListener() {{}},
            removeEventListener() {{}},
            body: {{
                classList: makeClassList(),
                appendChild() {{}},
                removeChild() {{}},
            }},
        }};
        global.window = {{
            addEventListener() {{}},
            removeEventListener() {{}},
            innerHeight: 800,
            URL: {{
                createObjectURL() {{ return 'blob:test'; }},
                revokeObjectURL() {{}},
            }},
        }};
        global.FileReader = function FileReader() {{}};

        vm.runInThisContext(fs.readFileSync({json.dumps(str(_APP))}, 'utf8'), {{ filename: 'app.js' }});

        function interleave() {{
            const lanes = Array.from(arguments);
            const count = lanes[0].length;
            const out = new Uint8Array(count * lanes.length);
            for (let i = 0; i < count; i += 1) {{
                for (let lane = 0; lane < lanes.length; lane += 1) {{
                    out[i * lanes.length + lane] = lanes[lane][i];
                }}
            }}
            return out;
        }}

        const logicA = Uint8Array.from([0, 64, 64, 0, 64, 0]);
        const logicB = Uint8Array.from([0, 64, 64, 0, 64, 0]);
        const analogA = Uint8Array.from([115, 116, 115, 116, 115, 116]);
        const analogB = Uint8Array.from([116, 115, 116, 115, 116, 115]);

        const splitLogic = zSplitRawPayload(interleave(logicA, logicB), 0);
        if (!splitLogic.usesLogicLayout || splitLogic.inferredStride !== 2) {{
            throw new Error('Failed to detect logic-only Z payload.');
        }}
        const namedLogic = zNamedDigitalTraces(splitLogic);
        if (namedLogic.mapping !== 'mirrored D7-D0 byte lanes') {{
            throw new Error('Unexpected mapping for mirrored logic lanes.');
        }}
        if (namedLogic.traces.length !== 1 || namedLogic.traces[0].name !== 'D6') {{
            throw new Error('Expected mirrored logic lanes to collapse to D6.');
        }}

        const splitMixed = zSplitRawPayload(interleave(logicA, analogA, logicB, analogB), 1);
        if (!splitMixed.usesLogicLayout || splitMixed.inferredStride !== 4 || splitMixed.analogLanes.length !== 1) {{
            throw new Error('Failed to detect mixed Z analog+logic payload.');
        }}
        if (splitMixed.analogLanes[0][0] !== 115 || splitMixed.analogLanes[0][1] !== 116) {{
            throw new Error('Mixed-payload analog lane extraction is wrong.');
        }}

        const infoHeader = buildInfoHeaderText({{
            fileModel: 'DS1074Z Plus',
            userModel: 'Z',
            parserModel: 'wfm1000z',
            serialNumber: 'DS1ZA000000001',
            firmware: '00.04.05.SP2',
            channels: [{{ channelNumber: 1 }}, {{ channelNumber: 6, infoLabel: 'D6' }}],
        }}, 'test3.wfm');
        if (
            !infoHeader.includes('Filename     = test3.wfm\\n') ||
            !infoHeader.includes('Scope        = DS1074Z Plus\\n') ||
            !infoHeader.includes('Parser Model = wfm1000z\\n')
        ) {{
            throw new Error('Info header should list filename first, then scope, then parser model.');
        }}
        if (infoHeader.includes('User Model')) {{
            throw new Error('Info header should not include the user model.');
        }}
        if (!infoHeader.includes('Serial Number = DS1ZA000000001')) {{
            throw new Error('Full info header should still include the serial number.');
        }}
        if (!infoHeader.includes('Channels     = [1, D6]')) {{
            throw new Error('Digital channels should appear in the info header like analog channels.');
        }}

        const tooltipHeader = buildInfoHeaderText({{
            fileModel: 'DS1074Z Plus',
            parserModel: 'wfm1000z',
            serialNumber: 'DS1ZA000000001',
            firmware: '00.04.05.SP2',
            channels: [{{ channelNumber: 1 }}, {{ channelNumber: 6, infoLabel: 'D6' }}],
        }}, 'test3.wfm', false);
        if (tooltipHeader.includes('Serial Number')) {{
            throw new Error('Filename hover popup should omit the serial number.');
        }}

        const digitalInfo = channelInfoText({{
            channelNumber: 6,
            infoLabel: 'D6',
            coupling: 'DIGITAL',
            voltPerDiv: 0.25,
            voltOffset: 0,
            probeValue: 1,
            inverted: false,
            timeScale: 0.01,
            timeOffset: 0.052,
            secondsPerPoint: 2e-8,
            logicMapping: 'mirrored D7-D0 byte lanes',
            observedLabels: ['L0.B6', 'L1.B6'],
        }}, {{
            points: 6,
            vMin: 0,
            vMax: 1,
            vAve: 0.5,
            vRms: Math.sqrt(0.5),
        }});
        if (!digitalInfo.includes('Channel D6:')) {{
            throw new Error('Digital channel tooltip should use the D6 heading.');
        }}
        if (!digitalInfo.includes('Observed = [L0.B6, L1.B6]')) {{
            throw new Error('Digital channel tooltip should preserve the observed lane labels.');
        }}

        const digitalVertices = channelPlotVertices({{
            kind: 'digital',
            times: Float64Array.from([0, 1, 2, 3]),
            volts: Float64Array.from([0, 0, 1, 1]),
        }}, (x) => x, (y) => y, 100);
        const expectedVertices = JSON.stringify([[0, 0], [2, 0], [2, 1], [3, 1]]);
        if (JSON.stringify(digitalVertices) !== expectedVertices) {{
            throw new Error('Digital channels should render as step traces with vertical transitions.');
        }}
        """)

    subprocess.run(["node", "-e", script], check=True, text=True)


@pytest.mark.skipif(shutil.which("node") is None, reason="node is not installed")
def test_wfmview_rg01_logic_helpers_execute_under_node():
    """RG01/MSO5000 logic records should surface digital channels in the viewer."""
    script = textwrap.dedent(f"""
        const fs = require('fs');
        const vm = require('vm');

        function makeClassList() {{
            return {{
                add() {{}},
                remove() {{}},
                toggle() {{}},
                contains() {{ return false; }},
            }};
        }}

        function makeElement() {{
            return {{
                checked: false,
                disabled: false,
                innerHTML: '',
                textContent: '',
                value: '',
                dataset: {{}},
                style: {{}},
                classList: makeClassList(),
                addEventListener() {{}},
                removeEventListener() {{}},
                appendChild() {{}},
                removeChild() {{}},
                setAttribute() {{}},
                getAttribute() {{ return null; }},
                getContext() {{
                    return {{
                        fillRect() {{}},
                        beginPath() {{}},
                        moveTo() {{}},
                        lineTo() {{}},
                        stroke() {{}},
                        fillText() {{}},
                        measureText() {{ return {{ width: 0 }}; }},
                        save() {{}},
                        restore() {{}},
                        clearRect() {{}},
                        arc() {{}},
                        closePath() {{}},
                        setLineDash() {{}},
                    }};
                }},
                getBoundingClientRect() {{
                    return {{ left: 0, top: 0, right: 800, bottom: 480, width: 800, height: 480 }};
                }},
                closest() {{ return null; }},
                click() {{}},
                width: 800,
                height: 480,
                offsetWidth: 800,
                offsetHeight: 480,
                clientWidth: 800,
                clientHeight: 480,
            }};
        }}

        global.document = {{
            getElementById() {{ return makeElement(); }},
            createElement() {{ return makeElement(); }},
            addEventListener() {{}},
            removeEventListener() {{}},
            body: {{
                classList: makeClassList(),
                appendChild() {{}},
                removeChild() {{}},
            }},
        }};
        global.window = {{
            addEventListener() {{}},
            removeEventListener() {{}},
            innerHeight: 800,
            URL: {{
                createObjectURL() {{ return 'blob:test'; }},
                revokeObjectURL() {{}},
            }},
        }};
        global.FileReader = function FileReader() {{}};

        vm.runInThisContext(fs.readFileSync({json.dumps(str(_APP))}, 'utf8'), {{ filename: 'app.js' }});

        function float32Bytes(values) {{
            const buffer = new ArrayBuffer(values.length * 4);
            const view = new DataView(buffer);
            for (let i = 0; i < values.length; i += 1) {{
                view.setFloat32(i * 4, values[i], true);
            }}
            return new Uint8Array(buffer);
        }}

        const result = parseBinWaveforms({{
            fileHeader: {{ version: '01' }},
            waveforms: [{{
                wfmHeader: {{
                    waveformType: 6,
                    waveformLabel: 'LA',
                    nPts: 4,
                    xIncrement: 1e-9,
                    xOrigin: 2e-9,
                    xDisplayRange: 4e-9,
                    frameString: 'MSO5074:TEST',
                }},
                dataHeader: {{
                    bufferType: 5,
                    bytesPerPoint: 4,
                }},
                dataRaw: float32Bytes([0, 1, 2, 3]),
            }}],
        }}, 'MSO5000', '5', 'bin5000');

        if (result.fileModel !== 'MSO5074') {{
            throw new Error('RG01 logic parser should preserve the model from the frame string.');
        }}
        if (result.channels.length !== 8) {{
            throw new Error('Single RG01 logic byte lane should expose D0-D7.');
        }}
        if (result.channels[0].infoLabel !== 'D0' || result.channels[1].infoLabel !== 'D1') {{
            throw new Error('RG01 logic channels should be named D0, D1, ...');
        }}
        if (JSON.stringify(Array.from(result.channels[0].volts)) !== JSON.stringify([0, 1, 0, 1])) {{
            throw new Error('D0 should follow bit 0 of the RG01 logic byte stream.');
        }}
        if (JSON.stringify(Array.from(result.channels[1].volts)) !== JSON.stringify([0, 0, 1, 1])) {{
            throw new Error('D1 should follow bit 1 of the RG01 logic byte stream.');
        }}
        if (
            !buildInfoHeaderText(result, 'MSO5074-C.bin')
                .includes('Channels     = [D0, D1, D2, D3, D4, D5, D6, D7]')
        ) {{
            throw new Error('RG01 logic channels should appear in the viewer info header.');
        }}

        const digitalInfo = channelInfoText(result.channels[0], {{
            points: 4,
            vMin: 0,
            vMax: 1,
            vAve: 0.5,
            vRms: Math.sqrt(0.5),
        }});
        if (!digitalInfo.includes('Mapping = LA D7-D0')) {{
            throw new Error('RG01 digital channel tooltip should include the logic mapping.');
        }}
        """)

    subprocess.run(["node", "-e", script], check=True, text=True)
