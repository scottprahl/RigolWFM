// Sigrok (.sr) export in wfmview/app.js.
'use strict';

const { test } = require('node:test');

const { loadViewer } = require('./harness');

loadViewer();

test('the sigrok export downloads a zip-framed .sr archive', () => {
    loadedFiles = [{
        id: 'file-1',
        stem: 'scope-shot',
        filename: 'scope-shot.wfm',
        result: {
            channels: [
                {
                    name: 'D6',
                    kind: 'digital',
                    times: Float64Array.from([0, 1e-6]),
                    volts: Float64Array.from([0, 1]),
                    voltPerDiv: 0.25,
                    timeScale: 1e-6,
                },
            ],
        },
        channelEnabled: [true],
    }];
    activeFileId = 'file-1';
    currentFilename = 'scope-shot';

    let captured = null;
    triggerDownload = function(data, filename, mime) {
        captured = { filename, mime, bytes: Array.from(data.slice(0, 4)) };
    };

    doExportSigrok();
    if (!captured) {
        throw new Error('SR export did not trigger a download.');
    }
    if (captured.filename !== 'scope-shot.sr') {
        throw new Error('SR export should download a .sr file.');
    }
    if (captured.mime !== 'application/zip') {
        throw new Error('SR export should download the archive as application/zip.');
    }
    if (JSON.stringify(captured.bytes) !== JSON.stringify([80, 75, 3, 4])) {
        throw new Error('SR export should begin with a ZIP local-file header.');
    }
});
