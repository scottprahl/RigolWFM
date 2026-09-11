// CSV export in wfmview/app.js.
//
// The expected rows below are the same shape the Python exporter writes.  That
// side is pinned separately in tests/test_wfmconvert.py, which asserts the same
// "mV,STATE" units row, so the two stay in step without either calling the other.
'use strict';

const { test } = require('node:test');

const { loadViewer } = require('./harness');

loadViewer();

test('CSV export matches the shape of the Python exporter', () => {
    const mixedEntry = {
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
    const mixedLines = buildExportCSVText(mixedEntry).split('\n');
    if (mixedLines[0] !== 'X,CH1,D6,Start,Increment') {
        throw new Error('Mixed CSV header should include the digital channel.');
    }
    if (mixedLines[1] !== 'µs,mV,STATE,0,1') {
        throw new Error('Mixed CSV units row should match the Python digital export shape.');
    }
    if (mixedLines[2] !== '0,250.00,0' || mixedLines[3] !== '1,-500.00,1') {
        throw new Error('Mixed CSV data rows should keep analog decimals and digital 0/1 values.');
    }

    const logicEntry = {
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
    const logicLines = buildExportCSVText(logicEntry).split('\n');
    if (logicLines[0] !== 'X,D6,Start,Increment') {
        throw new Error('Logic-only CSV header should include the digital trace name.');
    }
    if (logicLines[1] !== 'ms,STATE,1,1') {
        throw new Error('Logic-only CSV should export STATE units and linear metadata.');
    }
    if (logicLines[2] !== '1,0' || logicLines[3] !== '2,1') {
        throw new Error('Logic-only CSV rows should contain integer digital samples.');
    }
});
