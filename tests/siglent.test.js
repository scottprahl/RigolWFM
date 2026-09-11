// Siglent helpers in wfmview/app.js.
//
// The V4.0 conversion departs from Siglent's document in two ways that were
// established on the bench, so these pin the viewer to the same arithmetic the
// Python library uses.
'use strict';

const { test } = require('node:test');
const assert = require('node:assert');

const { loadViewer } = require('./harness');

loadViewer();

const CODES = new Uint8Array([128, 148, 108, 128]);

function v4Options(extra) {
    return Object.assign({
        revision: 'V4.0',
        model: 'Siglent V4.0',
        payload: CODES,
        enabled: [true, false, false, false],
        voltDivs: [0.1, 0.1, 0.1, 0.1],
        vertOffsets: [1, 0, 0, 0],
        probes: [10, 1, 1, 1],
        codePerDivs: [10, 10, 10, 10],
        waveLength: 4,
        sampleRate: 1000,
        xOrigin: -0.002,
    }, extra || {});
}

test('V4.0 subtracts vert_offset and applies the probe factor', () => {
    const result = buildSiglentFixedHeaderResult(v4Options());

    // ((code - 128) * 0.1 / 10 - 1) * 10
    const expected = [-10, -8, -12, -10];
    for (let i = 0; i < expected.length; i++) {
        assert.ok(Math.abs(result.channels[0].volts[i] - expected[i]) < 1e-9);
    }
    assert.ok(Math.abs(result.channels[0].voltPerDiv - 1) < 1e-9, 'volts/div carries the probe too');
});

test('earlier revisions keep the vendor document formula', () => {
    const result = buildSiglentFixedHeaderResult(v4Options({ revision: 'V3.0' }));

    // (code - 128) * 0.1 / 10 + 1, with no probe factor
    const expected = [1, 1.2, 0.8, 1];
    for (let i = 0; i < expected.length; i++) {
        assert.ok(Math.abs(result.channels[0].volts[i] - expected[i]) < 1e-9);
    }
});

test('a math-only file yields one unprobed F1 trace', () => {
    const result = buildSiglentFixedHeaderResult(v4Options({
        enabled: [false, false, false, false],
        voltDivs: [1, 1, 1, 1],
        vertOffsets: [0, 0, 0, 0],
        mathTraces: [{ name: 'F1', points: 4, voltDiv: 1, vertPos: -20, codePerDiv: 10, xIncrement: 0.001 }],
    }));

    const trace = result.channels[0];
    assert.strictEqual(trace.name, 'F1');
    assert.strictEqual(trace.probeValue, 1);

    // (code - 128) * 1 / 10 + 20, with no probe factor
    const expected = [20, 22, 18, 20];
    for (let i = 0; i < expected.length; i++) {
        assert.ok(Math.abs(trace.volts[i] - expected[i]) < 1e-9);
    }
});

test('the unit descriptor maps onto the units the viewer can label', () => {
    // [type, V_num, V_den, A_num, A_den, s_num, s_den]
    assert.strictEqual(siglentUnitFromWords([0, 1, 1, 0, 1, 0, 1]), 'V');
    assert.strictEqual(siglentUnitFromWords([0, 0, 1, 1, 1, 0, 1]), 'A');
    assert.strictEqual(siglentUnitFromWords([0, 1, 1, 1, 1, 0, 1]), 'W');
    assert.strictEqual(siglentUnitFromWords([0, 0, 1, 0, 1, 1, 1]), '?', 'seconds is not a vertical unit');
    assert.strictEqual(siglentUnitFromWords([5, 0, 0, 0, 0, 0, 0]), 'V', 'Vdc names volts outright');
    assert.strictEqual(siglentUnitFromWords([3, 0, 0, 0, 0, 0, 0]), '?', 'dB is not expressible');
});

test('the vertical axis follows the channels only when they agree', () => {
    assert.strictEqual(sharedChannelUnit([{ unit: 'A' }, { kind: 'digital' }]), 'A');
    assert.strictEqual(sharedChannelUnit([{ unit: 'V' }, { unit: 'A' }]), '');
    assert.strictEqual(sharedChannelUnit([{}]), 'V', 'formats without a unit stay volts');
    assert.strictEqual(axisTitleForUnit('A'), 'Current');
    assert.strictEqual(axisTitleForUnit(''), 'Amplitude');
});
