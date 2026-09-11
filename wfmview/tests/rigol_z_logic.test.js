// Rigol DS1000Z logic helpers in wfmview/app.js.
//
// A Z-series payload interleaves analog and logic lanes, so the viewer has to
// infer the stride and name the digital traces from what it finds.
'use strict';

const { test } = require('node:test');

const { loadViewer } = require('./harness');

loadViewer();

test('rigol z logic helpers behave as the library expects', () => {
    function interleave() {
        const lanes = Array.from(arguments);
        const count = lanes[0].length;
        const out = new Uint8Array(count * lanes.length);
        for (let i = 0; i < count; i += 1) {
            for (let lane = 0; lane < lanes.length; lane += 1) {
                out[i * lanes.length + lane] = lanes[lane][i];
            }
        }
        return out;
    }

    const logicA = Uint8Array.from([0, 64, 64, 0, 64, 0]);
    const logicB = Uint8Array.from([0, 64, 64, 0, 64, 0]);
    const analogA = Uint8Array.from([115, 116, 115, 116, 115, 116]);
    const analogB = Uint8Array.from([116, 115, 116, 115, 116, 115]);

    const splitLogic = zSplitRawPayload(interleave(logicA, logicB), 0);
    if (!splitLogic.usesLogicLayout || splitLogic.inferredStride !== 2) {
        throw new Error('Failed to detect logic-only Z payload.');
    }
    const namedLogic = zNamedDigitalTraces(splitLogic);
    if (namedLogic.mapping !== 'mirrored D7-D0 byte lanes') {
        throw new Error('Unexpected mapping for mirrored logic lanes.');
    }
    if (namedLogic.traces.length !== 1 || namedLogic.traces[0].name !== 'D6') {
        throw new Error('Expected mirrored logic lanes to collapse to D6.');
    }

    const splitMixed = zSplitRawPayload(interleave(logicA, analogA, logicB, analogB), 1);
    if (!splitMixed.usesLogicLayout || splitMixed.inferredStride !== 4 || splitMixed.analogLanes.length !== 1) {
        throw new Error('Failed to detect mixed Z analog+logic payload.');
    }
    if (splitMixed.analogLanes[0][0] !== 115 || splitMixed.analogLanes[0][1] !== 116) {
        throw new Error('Mixed-payload analog lane extraction is wrong.');
    }

    const infoHeader = buildInfoHeaderText({
        fileModel: 'DS1074Z Plus',
        userModel: 'Z',
        parserModel: 'wfm1000z',
        serialNumber: 'DS1ZA000000001',
        firmware: '00.04.05.SP2',
        channels: [{ channelNumber: 1 }, { channelNumber: 6, infoLabel: 'D6' }],
    }, 'test3.wfm');
    if (
        !infoHeader.includes('Filename     = test3.wfm\n') ||
        !infoHeader.includes('Scope        = DS1074Z Plus\n') ||
        !infoHeader.includes('Parser Model = wfm1000z\n')
    ) {
        throw new Error('Info header should list filename first, then scope, then parser model.');
    }
    if (infoHeader.includes('User Model')) {
        throw new Error('Info header should not include the user model.');
    }
    if (!infoHeader.includes('Serial Number = DS1ZA000000001')) {
        throw new Error('Full info header should still include the serial number.');
    }
    if (!infoHeader.includes('Channels     = [1, D6]')) {
        throw new Error('Digital channels should appear in the info header like analog channels.');
    }

    const tooltipHeader = buildInfoHeaderText({
        fileModel: 'DS1074Z Plus',
        parserModel: 'wfm1000z',
        serialNumber: 'DS1ZA000000001',
        firmware: '00.04.05.SP2',
        channels: [{ channelNumber: 1 }, { channelNumber: 6, infoLabel: 'D6' }],
    }, 'test3.wfm', false);
    if (tooltipHeader.includes('Serial Number')) {
        throw new Error('Filename hover popup should omit the serial number.');
    }

    const digitalInfo = channelInfoText({
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
    }, {
        points: 6,
        vMin: 0,
        vMax: 1,
        vAve: 0.5,
        vRms: Math.sqrt(0.5),
    });
    if (!digitalInfo.includes('Channel D6:')) {
        throw new Error('Digital channel tooltip should use the D6 heading.');
    }
    if (!digitalInfo.includes('Observed = [L0.B6, L1.B6]')) {
        throw new Error('Digital channel tooltip should preserve the observed lane labels.');
    }

    const digitalVertices = channelPlotVertices({
        kind: 'digital',
        times: Float64Array.from([0, 1, 2, 3]),
        volts: Float64Array.from([0, 0, 1, 1]),
    }, (x) => x, (y) => y, 100);
    const expectedVertices = JSON.stringify([[0, 0], [2, 0], [2, 1], [3, 1]]);
    if (JSON.stringify(digitalVertices) !== expectedVertices) {
        throw new Error('Digital channels should render as step traces with vertical transitions.');
    }
});
