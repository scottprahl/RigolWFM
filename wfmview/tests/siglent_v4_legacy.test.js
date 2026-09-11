// Further Siglent V4.0 helpers in wfmview/app.js.
//
// Migrated verbatim from tests/test_wfmview.py; the conditions are unchanged,
// so they still guard exactly what they did there.
'use strict';

const { test } = require('node:test');

const { loadViewer } = require('./harness');

loadViewer();

test('siglent v4 legacy helpers behave as the library expects', () => {
    // A math (F1-F4) save clears every ch_on flag and stores its length in
    // math_store_len, so detection has to fall back to the math payload.
    const header = new Uint8Array(0x1000);
    const view = new DataView(header.buffer);
    view.setUint32(0x00, 4, true);
    view.setUint32(0x04, 0x1000, true);
    view.setUint32(0x1EC, 0, true);
    view.setUint32(0x280, 1, true);
    view.setUint32(0x3D0, 8, true);
    if (!siglentLooksLikeV4(header, 0x1000 + 16)) {
        throw new Error('A math-only V4.0 header should be recognized.');
    }
    view.setUint32(0x280, 0, true);
    if (siglentLooksLikeV4(header, 0x1000 + 16)) {
        throw new Error('A V4.0 header with no traces at all should be rejected.');
    }

    const codes = new Uint8Array([128, 148, 108, 128]);
    const analog = buildSiglentFixedHeaderResult({
        revision: 'V4.0',
        model: 'Siglent V4.0',
        payload: codes,
        enabled: [true, false, false, false],
        voltDivs: [0.1, 0.1, 0.1, 0.1],
        vertOffsets: [1, 0, 0, 0],
        probes: [10, 1, 1, 1],
        codePerDivs: [10, 10, 10, 10],
        waveLength: 4,
        sampleRate: 1000,
        xOrigin: -0.002,
    });
    // ((code - 128) * 0.1 / 10 - 1) * 10
    const expected = [-10, -8, -12, -10];
    for (let i = 0; i < expected.length; i++) {
        if (Math.abs(analog.channels[0].volts[i] - expected[i]) > 1e-9) {
            throw new Error('V4.0 volts must subtract vert_offset and apply the probe factor.');
        }
    }
    if (Math.abs(analog.channels[0].voltPerDiv - 1) > 1e-9) {
        throw new Error('V4.0 volts/div must carry the probe factor too.');
    }

    const math = buildSiglentFixedHeaderResult({
        revision: 'V4.0',
        model: 'Siglent V4.0',
        payload: codes,
        enabled: [false, false, false, false],
        voltDivs: [1, 1, 1, 1],
        vertOffsets: [0, 0, 0, 0],
        probes: [10, 10, 10, 10],
        codePerDivs: [10, 10, 10, 10],
        waveLength: 4,
        sampleRate: 1000,
        xOrigin: -0.002,
        mathTraces: [{ name: 'F1', points: 4, voltDiv: 1, vertPos: -20, codePerDiv: 10, xIncrement: 0.001 }],
    });
    const trace = math.channels[0];
    if (trace.name !== 'F1' || trace.points !== 4 || trace.probeValue !== 1) {
        throw new Error('A math-only file should yield one unprobed F1 trace.');
    }
    // (code - 128) * 1 / 10 + 20, with no probe factor
    const expectedMath = [20, 22, 18, 20];
    for (let i = 0; i < expectedMath.length; i++) {
        if (Math.abs(trace.volts[i] - expectedMath[i]) > 1e-9) {
            throw new Error('Math traces use the math header fields and no probe factor.');
        }
    }
    if (Math.abs(trace.secondsPerPoint - 0.001) > 1e-12) {
        throw new Error('Math traces are timed by math_f_time.');
    }

    // [type, V_num, V_den, A_num, A_den, s_num, s_den]
    const unitCases = [
        [[0, 1, 1, 0, 1, 0, 1], 'V'],
        [[0, 0, 1, 1, 1, 0, 1], 'A'],
        [[0, 1, 1, 1, 1, 0, 1], 'W'],
        [[0, 0, 1, 0, 1, 1, 1], '?'],
        [[5, 0, 0, 0, 0, 0, 0], 'V'],
        [[3, 0, 0, 0, 0, 0, 0], '?'],
    ];
    for (const [words, want] of unitCases) {
        if (siglentUnitFromWords(words) !== want) {
            throw new Error('Unit descriptor ' + words.join(',') + ' should read as ' + want + '.');
        }
    }

    if (sharedChannelUnit([{ unit: 'A' }, { kind: 'digital' }]) !== 'A') {
        throw new Error('Digital channels must not disturb the shared vertical unit.');
    }
    if (sharedChannelUnit([{ unit: 'V' }, { unit: 'A' }]) !== '') {
        throw new Error('Mixed units must leave the shared vertical axis unlabeled.');
    }
    if (sharedChannelUnit([{}]) !== 'V') {
        throw new Error('Channels from formats without a unit stay volts.');
    }
    if (axisTitleForUnit('A') !== 'Current' || axisTitleForUnit('') !== 'Amplitude') {
        throw new Error('Unexpected vertical axis title.');
    }

    getVisibleChannelsForEntry = function() {
        return [{
            name: 'CH1',
            unit: 'A',
            kind: 'analog',
            volts: [0.1, 0.2],
            times: [0, 1e-3],
            timeScale: 1e-3,
            voltPerDiv: 0.1,
        }];
    };
    const csvRows = buildExportCSVText({}).split('\n');
    if (csvRows[1] !== 'ms,mA,0,1') {
        throw new Error('CSV columns should carry the unit of each channel, got: ' + csvRows[1]);
    }
});
