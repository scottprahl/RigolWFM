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
_SCRIPT_RE = re.compile(r'<script defer src="\./([^"?]+\.js)(?:\?[^"]*)?"></script>')


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
            firmware: '00.04.05.SP2',
            channels: [{{ channelNumber: 1 }}, {{ channelNumber: 6, infoLabel: 'D6' }}],
        }}, 'test3.wfm');
        if (!infoHeader.includes('Channels     = [1, D6]')) {{
            throw new Error('Digital channels should appear in the info header like analog channels.');
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
