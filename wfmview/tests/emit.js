// Emits an export artifact from wfmview/app.js on stdout, so the Python suite
// can check that numpy, the MAT reader and zipfile can read what the viewer
// writes.  Those assertions have to live in Python; only the JavaScript that
// produces the bytes belongs here.
//
//   node wfmview/tests/emit.js npz            -> NPZ archive bytes
//   node wfmview/tests/emit.js mat            -> MAT file bytes
//   node wfmview/tests/emit.js sigrok-mixed   -> .sr archive bytes
//   node wfmview/tests/emit.js sigrok-logic   -> .sr archive bytes, logic only
//   node wfmview/tests/emit.js downloads      -> JSON describing the downloads
'use strict';

const { loadViewer } = require('./harness');

loadViewer();

/** One analog channel and one digital channel sharing a time axis. */
function mixedEntry() {
    return {
        result: {
            channels: [
                {
                    name: 'CH1',
                    times: Float64Array.from([0, 1e-6, 2e-6]),
                    volts: Float64Array.from([0.25, -0.5, 0.75]),
                    voltPerDiv: 1e-3,
                    timeScale: 1e-6,
                },
                {
                    name: 'D6',
                    kind: 'digital',
                    times: Float64Array.from([0, 1e-6, 2e-6]),
                    volts: Float64Array.from([0, 1, 0]),
                    voltPerDiv: 0.25,
                    timeScale: 1e-6,
                },
            ],
        },
        channelEnabled: [true, true],
    };
}

/** A capture with no analog channel at all. */
function logicOnlyEntry() {
    return {
        result: {
            channels: [
                {
                    name: 'D6',
                    kind: 'digital',
                    times: Float64Array.from([0.001, 0.002, 0.003]),
                    volts: Float64Array.from([0, 1, 1]),
                    voltPerDiv: 0.25,
                    timeScale: 0.001,
                },
            ],
        },
        channelEnabled: [true],
    };
}

function writeArchive(archive, what) {
    if (!archive) {
        throw new Error(`Expected the ${what} entry to produce an archive.`);
    }
    process.stdout.write(Buffer.from(archive));
}

/** Record what the viewer would hand the browser to download. */
function emitDownloads() {
    loadedFiles = [Object.assign({ id: 'file-1' }, mixedEntry())];
    activeFileId = 'file-1';
    currentFilename = 'scope-shot';

    const captures = [];
    triggerDownload = function (data, filename, mime) {
        captures.push({ filename, mime, bytes: Array.from(data.slice(0, 4)) });
    };

    doExportNPZ();
    doExportMAT();
    process.stdout.write(JSON.stringify(captures));
}

const EMITTERS = {
    npz: () => writeArchive(buildExportNPZArchive(mixedEntry()), 'mixed'),
    mat: () => writeArchive(buildExportMATPayload(mixedEntry()), 'mixed'),
    'sigrok-mixed': () => writeArchive(buildExportSigrokArchive(mixedEntry()), 'mixed'),
    'sigrok-logic': () => writeArchive(buildExportSigrokArchive(logicOnlyEntry()), 'logic-only'),
    downloads: emitDownloads,
};

const what = process.argv[2];
if (!Object.prototype.hasOwnProperty.call(EMITTERS, what)) {
    process.stderr.write(`usage: emit.js {${Object.keys(EMITTERS).join('|')}}\n`);
    process.exit(2);
}
EMITTERS[what]();
