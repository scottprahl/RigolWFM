// Rigol RG01 (MSO5000) logic helpers in wfmview/app.js.
'use strict';

const { test } = require('node:test');

const { loadViewer } = require('./harness');

loadViewer();

test('rigol rg01 logic helpers behave as the library expects', () => {
    function float32Bytes(values) {
        const buffer = new ArrayBuffer(values.length * 4);
        const view = new DataView(buffer);
        for (let i = 0; i < values.length; i += 1) {
            view.setFloat32(i * 4, values[i], true);
        }
        return new Uint8Array(buffer);
    }

    const result = parseBinWaveforms({
        fileHeader: { version: '01' },
        waveforms: [{
            wfmHeader: {
                waveformType: 6,
                waveformLabel: 'LA',
                nPts: 4,
                xIncrement: 1e-9,
                xOrigin: 2e-9,
                xDisplayRange: 4e-9,
                frameString: 'MSO5074:TEST',
            },
            dataHeader: {
                bufferType: 5,
                bytesPerPoint: 4,
            },
            dataRaw: float32Bytes([0, 1, 2, 3]),
        }],
    }, 'MSO5000', '5', 'bin5000');

    if (result.fileModel !== 'MSO5074') {
        throw new Error('RG01 logic parser should preserve the model from the frame string.');
    }
    if (result.channels.length !== 8) {
        throw new Error('Single RG01 logic byte lane should expose D0-D7.');
    }
    if (result.channels[0].infoLabel !== 'D0' || result.channels[1].infoLabel !== 'D1') {
        throw new Error('RG01 logic channels should be named D0, D1, ...');
    }
    if (JSON.stringify(Array.from(result.channels[0].volts)) !== JSON.stringify([0, 1, 0, 1])) {
        throw new Error('D0 should follow bit 0 of the RG01 logic byte stream.');
    }
    if (JSON.stringify(Array.from(result.channels[1].volts)) !== JSON.stringify([0, 0, 1, 1])) {
        throw new Error('D1 should follow bit 1 of the RG01 logic byte stream.');
    }
    if (
        !buildInfoHeaderText(result, 'MSO5074-C.bin')
            .includes('Channels     = [D0, D1, D2, D3, D4, D5, D6, D7]')
    ) {
        throw new Error('RG01 logic channels should appear in the viewer info header.');
    }

    const digitalInfo = channelInfoText(result.channels[0], {
        points: 4,
        vMin: 0,
        vMax: 1,
        vAve: 0.5,
        vRms: Math.sqrt(0.5),
    });
    if (!digitalInfo.includes('Mapping = LA D7-D0')) {
        throw new Error('RG01 digital channel tooltip should include the logic mapping.');
    }
});
