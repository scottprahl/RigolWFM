// Tektronix helpers in wfmview/app.js.
//
// The viewer re-implements every format the Python library reads, so these
// guard the places where the two drifted apart before: the version string's
// leading colon, and the tekmeta block that says whether a capture is digital
// or IQ.
'use strict';

const { test } = require('node:test');
const assert = require('node:assert');

const { loadViewer, tekmetaBlock } = require('./harness');

loadViewer();

test('tekmeta block decodes to its key/value pairs', () => {
    const bytes = tekmetaBlock([
        ['IQ_centerFrequency', 3, 1e6],
        ['IQ_windowType', 1, 'Blackharris'],
        ['clippingInitialized', 4, 1],
    ]);

    const meta = tekParseTekmeta(bytes, true);

    assert.strictEqual(meta.IQ_centerFrequency, 1e6);
    assert.strictEqual(meta.IQ_windowType, 'Blackharris');
    assert.strictEqual(meta.clippingInitialized, 1);
});

test('a missing or truncated tekmeta block is not an error', () => {
    assert.deepStrictEqual(tekParseTekmeta(new Uint8Array([1, 2, 3]), true), {});

    const truncated = tekmetaBlock([['IQ_span', 3, 1e6]]).slice(0, 14);
    assert.deepStrictEqual(tekParseTekmeta(truncated, true), {});
});

test('an unknown value tag stops the scan instead of throwing', () => {
    const bytes = tekmetaBlock([['first', 4, 7], ['second', 4, 9]]);
    bytes[8 + 4 + 4 + 5] = 99;  // corrupt the first entry's type tag

    assert.doesNotThrow(() => tekParseTekmeta(bytes, true));
});

test('digital captures are recognised by data_type or by line names', () => {
    assert.ok(tekIsDigital(6, {}), 'data_type 6 marks a digital capture');
    assert.ok(tekIsDigital(2, { d0: '', d1: '' }), 'd0..d7 keys mark one too');
    assert.ok(!tekIsDigital(2, { yOffset: 0 }), 'an ordinary analog capture is not digital');
});

test('digital line names come back in bit order', () => {
    assert.deepStrictEqual(tekDigitalLineNames({ d2: '', d0: '', d1: '' }), ['d0', 'd1', 'd2']);
    assert.deepStrictEqual(tekDigitalLineNames({ yOffset: 0 }), []);
});

test('IQ captures are recognised only by their acquisition parameters', () => {
    assert.ok(tekIsIq({ IQ_span: 1e6 }));
    assert.ok(tekIsIq({ IQ_windowType: 'Blackharris' }));
    assert.ok(!tekIsIq({ ANALOG_Thumbnail: '', yOffset: 0 }));
});

test('the version string is read past its leading colon', () => {
    // ":WFM#003" -- the colon is part of the eight-byte field, so the magic
    // starts at offset 3.  Looking at offset 2 made the viewer reject every
    // instrument-written file as unsupported.
    const header = Buffer.from('\x0f\x0f:WFM#003', 'binary');

    assert.strictEqual(header[2], 0x3a, 'byte 2 is the colon');
    assert.strictEqual(header[3], 0x57, 'the W of WFM# is at offset 3');
    assert.strictEqual(header.slice(3, 7).toString('ascii'), 'WFM#');
});
