"""Smoke tests for the browser-side `wfmview` assets."""

import json
from pathlib import Path
import re
import shutil
import subprocess
import textwrap

import pytest

_ROOT = Path(__file__).resolve().parents[1]
_INDEX = _ROOT / "wfmview" / "index.html"
_APP = _ROOT / "wfmview" / "app.js"
_SCRIPT_RE = re.compile(r'<script defer src="\./([^"]+\.js)"></script>')


def _viewer_script_paths() -> list[Path]:
    """Return local JS assets referenced by the viewer index page."""
    text = _INDEX.read_text(encoding="utf-8")
    return [(_ROOT / "wfmview" / match.group(1)) for match in _SCRIPT_RE.finditer(text)]


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
