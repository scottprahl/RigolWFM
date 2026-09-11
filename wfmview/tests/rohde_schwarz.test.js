// Rohde & Schwarz helpers in wfmview/app.js.
//
// An RTP capture is a metadata .bin plus a companion .Wfm.bin payload, so the
// viewer has to pair them up and not mistake one for the other.
'use strict';

const { test } = require('node:test');

const { loadViewer } = require('./harness');

loadViewer();

test('rohde schwarz helpers behave as the library expects', () => {
    const fileMap = buildSelectedFileMap([
        { name: 'singleChan.bin' },
        { name: 'singleChan.Wfm.bin' },
    ]);
    if (!shouldSkipRohdeSchwarzPayload({ name: 'singleChan.Wfm.bin' }, fileMap)) {
        throw new Error('Expected companion payload to be skipped when metadata is selected.');
    }
    if (shouldSkipRohdeSchwarzPayload({ name: 'orphan.Wfm.bin' }, {})) {
        throw new Error('Unexpected skip for an orphan payload file.');
    }
    if (rohdeSchwarzPayloadLookupName('singleChan.bin') !== 'singlechan.wfm.bin') {
        throw new Error('Unexpected companion lookup name.');
    }

    const xml = new TextEncoder().encode('<?xml version="1.0"?><Database SaveItemType="Data"></Database>');
    if (!looksLikeRohdeSchwarzMetadata(xml.buffer, 'singleChan.bin')) {
        throw new Error('Failed to recognize R&S metadata.');
    }
    if (looksLikeRohdeSchwarzMetadata(xml.buffer, 'singleChan.Wfm.bin')) {
        throw new Error('Payload files must not be treated as metadata.');
    }
});
