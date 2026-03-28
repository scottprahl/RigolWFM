'use strict';

var TRACE_BASE_PALETTE = [
    '#4477aa', '#ee6677', '#228833', '#ccbb44',
    '#66ccee', '#aa3377', '#bbbbbb',
];
var TRACE_STYLE_CYCLE = [
    { id: 'solid', dash: [], cap: 'round' },
    { id: 'dashed', dash: [10, 6], cap: 'butt' },
    { id: 'dotted', dash: [1.5, 5], cap: 'round' },
];
var CH_COLORS = TRACE_BASE_PALETTE.slice(0, 4);
var FONT_PX = 20;
var M = { l: 115, r: 40, t: 20, b: 55 };
var GRAPH_BRAND = 'RigolWFM';
var DHO_FILE_HEADER_SIZE = 24;
var DHO_BLOCK_HEADER_SIZE = 12;
var DHO_ADC_MIDPOINT = 32768;
var DHO_X_INCREMENT_SCALE = 1e-8;
// DHO824 .wfm captures use 0.8 ns units here; 1.0 ns makes the trace 25%
// wider than the matching official .bin export.
var DHO_X_INCREMENT_SCALE_DHO800 = 8e-10;

function hslToHex(h, s, l) {
    var hh = ((h % 360) + 360) % 360 / 360;
    var ss = Math.max(0, Math.min(100, s)) / 100;
    var ll = Math.max(0, Math.min(100, l)) / 100;

    function hueToRgb(p, q, t) {
        var tt = t;
        if (tt < 0) {
            tt += 1;
        }
        if (tt > 1) {
            tt -= 1;
        }
        if (tt < 1 / 6) {
            return p + (q - p) * 6 * tt;
        }
        if (tt < 1 / 2) {
            return q;
        }
        if (tt < 2 / 3) {
            return p + (q - p) * (2 / 3 - tt) * 6;
        }
        return p;
    }

    var q = ll < 0.5 ? ll * (1 + ss) : ll + ss - ll * ss;
    var p = 2 * ll - q;
    var rgb = [
        hueToRgb(p, q, hh + 1 / 3),
        hueToRgb(p, q, hh),
        hueToRgb(p, q, hh - 1 / 3),
    ];

    return '#' + rgb.map(function(value) {
        return Math.round(value * 255).toString(16).padStart(2, '0');
    }).join('');
}

function fmtSI(val, unit) {
    var abs = Math.abs(val);
    var pfx;
    var div;
    if (abs === 0) {
        return '0 ' + unit;
    }
    if (abs >= 1e9) {
        pfx = 'G';
        div = 1e9;
    } else if (abs >= 1e6) {
        pfx = 'M';
        div = 1e6;
    } else if (abs >= 1e3) {
        pfx = 'k';
        div = 1e3;
    } else if (abs >= 1) {
        pfx = '';
        div = 1;
    } else if (abs >= 1e-3) {
        pfx = 'm';
        div = 1e-3;
    } else if (abs >= 1e-6) {
        pfx = '\u00b5';
        div = 1e-6;
    } else if (abs >= 1e-9) {
        pfx = 'n';
        div = 1e-9;
    } else {
        pfx = 'p';
        div = 1e-12;
    }
    return (val / div).toPrecision(3) + '\u202f' + pfx + unit;
}

function enumName(enumObj, value) {
    if (enumObj && Object.prototype.hasOwnProperty.call(enumObj, value)) {
        return String(enumObj[value]);
    }
    return String(value);
}

function titleBool(value) {
    return value ? 'True' : 'False';
}

function bestScaleInfo(number) {
    var absnr = Math.abs(number);
    var thresholds = [
        [0.99999999e-9, 1e12, 'p'],
        [0.99999999e-6, 1e9, 'n'],
        [0.99999999e-3, 1e6, '\u00b5'],
        [0.99999999, 1e3, 'm'],
        [0.99999999e3, 1, ' '],
        [0.99999999e6, 1e-3, 'k'],
        [0.999999991e9, 1e-6, 'M'],
    ];

    if (absnr === 0) {
        return [1, ' '];
    }

    for (var i = 0; i < thresholds.length; i++) {
        if (absnr < thresholds[i][0]) {
            return [thresholds[i][1], thresholds[i][2]];
        }
    }

    return [1e-9, 'G'];
}

function engineeringString(number, digits) {
    var scaled = bestScaleInfo(number);
    return (number * scaled[0]).toFixed(digits) + ' ' + scaled[1];
}

function compactEngineeringValue(number, unit) {
    if (!Number.isFinite(number)) {
        return '';
    }
    if (number === 0) {
        return '0' + unit;
    }
    var scaled = bestScaleInfo(number);
    var prefix = scaled[1].trim();
    var value = Number((number * scaled[0]).toPrecision(3)).toString();
    return value + prefix + unit;
}

function sweepName(value) {
    return { 0: 'AUTO', 1: 'NORMAL', 2: 'SINGLE' }[value] || String(value);
}

function triggerCouplingName(value) {
    return { 0: 'DC', 1: 'LF', 2: 'HF', 3: 'AC' }[value] || String(value);
}

function ds2000SourceName(value) {
    if (value === 0) {
        return 'CH1';
    }
    if (value === 1) {
        return 'CH2';
    }
    if (value === 2) {
        return 'EXT';
    }
    if (value === 3) {
        return 'AC LINE';
    }
    if (value >= 4 && value < 20) {
        return 'D' + (value - 4);
    }
    return '';
}

function ds2000TriggerModeName(value) {
    if (value === 30) {
        return 'Edge';
    }
    return '';
}

function decode2000Trigger(h) {
    var setup = h.setup;
    if (!setup || !setup.triggerLevels) {
        return null;
    }

    var inputLevels = {
        CH1: setup.triggerLevels.ch1LevelUv * 1e-6,
        CH2: setup.triggerLevels.ch2LevelUv * 1e-6,
        EXT: setup.triggerLevels.extLevelUv * 1e-6,
    };
    var hasMeaningfulSetup = setup.triggerHoldoffNs !== 0 ||
        inputLevels.CH1 !== 0 || inputLevels.CH2 !== 0 || inputLevels.EXT !== 0;
    if (!hasMeaningfulSetup) {
        return null;
    }

    var info = {
        inputLevels: inputLevels,
    };

    if (setup.triggerSourcePrimary === setup.triggerSourceShadow) {
        var source = ds2000SourceName(setup.triggerSourcePrimary);
        if (source) {
            info.source = source;
            if (Object.prototype.hasOwnProperty.call(inputLevels, source)) {
                info.level = inputLevels[source];
            }
        }
    }

    var mode = ds2000TriggerModeName(setup.triggerModeCode);
    if (mode) {
        info.mode = mode;
    }

    return info;
}

function scaled4000TriggerLevels(levelBlock, probeValues) {
    return {
        CH1: levelBlock.ch1LevelUv * 1e-6 * probeValues[0],
        CH2: levelBlock.ch2LevelUv * 1e-6 * probeValues[1],
        CH3: levelBlock.ch3LevelUv * 1e-6 * probeValues[2],
        CH4: levelBlock.ch4LevelUv * 1e-6 * probeValues[3],
        EXT: levelBlock.extLevelUv * 1e-6,
    };
}

function decode4000Trigger(h) {
    var setup = h.setup;
    if (!setup) {
        return null;
    }

    var probeValues = h.ch.map(function(ch) {
        return ch.probeValue || 1;
    });

    if (
        setup.modernTriggerLevels &&
        Object.prototype.hasOwnProperty.call(Wfm4000.Wfm4000.TriggerModeEnum, setup.modernTriggerMode) &&
        Object.prototype.hasOwnProperty.call(Wfm4000.Wfm4000.TriggerSourceEnum, setup.modernTriggerSource)
    ) {
        var inputLevels = scaled4000TriggerLevels(setup.modernTriggerLevels, probeValues);
        var source = enumName(Wfm4000.Wfm4000.TriggerSourceEnum, setup.modernTriggerSource).toUpperCase();
        var info = {
            mode: enumName(Wfm4000.Wfm4000.TriggerModeEnum, setup.modernTriggerMode).toLowerCase(),
            source: source,
            inputLevels: inputLevels,
        };
        if (Object.prototype.hasOwnProperty.call(inputLevels, source)) {
            info.level = inputLevels[source];
        }
        info.mode = info.mode.charAt(0).toUpperCase() + info.mode.slice(1);
        return info;
    }

    if (setup.legacyTriggerLevels) {
        return {
            inputLevels: scaled4000TriggerLevels(setup.legacyTriggerLevels, probeValues),
        };
    }

    return null;
}

function modelFromFrameString(frameString, fallback) {
    if (frameString && frameString.indexOf(':') >= 0) {
        return frameString.split(':', 1)[0];
    }
    return frameString || fallback;
}

function dhoFamilyLabel(model, fallback) {
    var text = String(model || '').toUpperCase();
    if (/^(?:DHO|HDO)8/.test(text)) {
        return 'DHO800';
    }
    if (/^(?:DHO|HDO)1/.test(text)) {
        return 'DHO1000';
    }
    return fallback;
}

function channelNumberFromName(name, fallback) {
    var match = /^CH\s*([1-4])$/i.exec(name || '');
    return match ? parseInt(match[1], 10) : fallback;
}

function proxyRawFromCalibrated(values) {
    var out = new Uint8Array(values.length);
    if (!values.length) {
        return out;
    }

    var low = Infinity;
    var high = -Infinity;
    for (var i = 0; i < values.length; i++) {
        if (Number.isFinite(values[i])) {
            if (values[i] < low) {
                low = values[i];
            }
            if (values[i] > high) {
                high = values[i];
            }
        }
    }
    if (!Number.isFinite(low) || !Number.isFinite(high)) {
        out.fill(127);
        return out;
    }
    if (high <= low) {
        out.fill(127);
        return out;
    }

    var center = (high + low) / 2;
    var halfSpan = Math.max((high - low) / 2, 1e-12);
    for (var j = 0; j < values.length; j++) {
        var raw = 127 - 127 * (values[j] - center) / halfSpan;
        out[j] = Math.max(0, Math.min(255, Math.round(raw)));
    }
    return out;
}

function proxyRawFromDhoVolts(values) {
    var out = new Uint8Array(values.length);
    for (var i = 0; i < values.length; i++) {
        var raw16 = Math.max(0, Math.min(65535, Math.round(values[i] * 1000 + 32768)));
        out[i] = raw16 >> 8;
    }
    return out;
}

function describeTriggerBlock(triggerInfo, indent) {
    var s = '';
    if (triggerInfo.mode) {
        s += indent + 'Mode     = ' + triggerInfo.mode + '\n';
    }
    if (triggerInfo.source) {
        s += indent + 'Source   = ' + triggerInfo.source + '\n';
    }
    if (typeof triggerInfo.level === 'number') {
        s += indent + 'Level    = ' + engineeringString(triggerInfo.level, 2) + 'V\n';
    }
    if (triggerInfo.sweep) {
        s += indent + 'Sweep    = ' + triggerInfo.sweep + '\n';
    }
    if (triggerInfo.coupling) {
        s += indent + 'Coupling = ' + triggerInfo.coupling + '\n';
    }
    return s;
}

function derivedLevels(result) {
    var source = result.triggerInfo && result.triggerInfo.source ? result.triggerInfo.source : '';
    var sourceChannelNumber = { CH1: 1, CH2: 2, CH3: 3, CH4: 4 }[source];
    var knownNonAnalog = Boolean(source) && !sourceChannelNumber;
    var levels = [];

    if (knownNonAnalog) {
        return levels;
    }

    result.channels.forEach(function(ch) {
        if (sourceChannelNumber && ch.channelNumber !== sourceChannelNumber) {
            return;
        }
        if (!ch.times.length || !ch.volts.length) {
            return;
        }
        var bestIndex = 0;
        var bestAbs = Math.abs(ch.times[0]);
        for (var i = 1; i < ch.times.length; i++) {
            var here = Math.abs(ch.times[i]);
            if (here < bestAbs) {
                bestAbs = here;
                bestIndex = i;
            }
        }
        levels.push({ channelNumber: ch.channelNumber, value: ch.volts[bestIndex] });
    });

    levels.sort(function(a, b) {
        return a.channelNumber - b.channelNumber;
    });
    return levels;
}

function summarizeChannelVoltages(ch, bounds) {
    var points = 0;
    var vMin = Infinity;
    var vMax = -Infinity;
    var sum = 0;
    var sumSquares = 0;
    var useBounds = bounds && graphBoundsAreUsable(bounds);

    for (var i = 0; i < ch.volts.length; i++) {
        var t = ch.times[i];
        var v = ch.volts[i];
        if (!Number.isFinite(t) || !Number.isFinite(v)) {
            continue;
        }
        if (useBounds && (t < bounds.tMin || t > bounds.tMax)) {
            continue;
        }

        points++;
        if (v < vMin) {
            vMin = v;
        }
        if (v > vMax) {
            vMax = v;
        }
        sum += v;
        sumSquares += v * v;
    }

    if (!points) {
        return {
            points: 0,
            vMin: NaN,
            vMax: NaN,
            vAve: NaN,
            vRms: NaN,
        };
    }

    return {
        points: points,
        vMin: vMin,
        vMax: vMax,
        vAve: sum / points,
        vRms: Math.sqrt(sumSquares / points),
    };
}

function formatChannelVoltageStat(value) {
    if (!Number.isFinite(value)) {
        return '       n/a';
    }
    return engineeringString(value, 2).padStart(10, ' ') + 'V';
}

function channelInfoText(ch, stats) {
    var channelStats = stats || summarizeChannelVoltages(ch, null);
    var s = '     Channel ' + ch.channelNumber + ':\n';
    s += '         Coupling = ' + String(ch.coupling || 'unknown').padStart(8, ' ') + '\n';
    s += '            Scale = ' + engineeringString(ch.voltPerDiv, 2).padStart(10, ' ') + 'V/div\n';
    s += '           Offset = ' + engineeringString(ch.voltOffset, 2).padStart(10, ' ') + 'V\n';
    s += '            Probe = ' + String(ch.probeValue).padStart(7, ' ') + 'X\n';
    s += '         Inverted = ' + titleBool(ch.inverted).padStart(8, ' ') + '\n\n';
    s += '        Time Base = ' + engineeringString(ch.timeScale, 3).padStart(10, ' ') + 's/div\n';
    s += '           Offset = ' + engineeringString(ch.timeOffset, 3).padStart(10, ' ') + 's\n';
    s += '            Delta = ' + engineeringString(ch.secondsPerPoint, 3).padStart(10, ' ') + 's/point\n';
    s += '           Points = ' + String(channelStats.points).padStart(8, ' ') + '\n';
    s += '\n';
    s += '             Vmin = ' + formatChannelVoltageStat(channelStats.vMin) + '\n';
    s += '             Vmax = ' + formatChannelVoltageStat(channelStats.vMax) + '\n';
    s += '             Vave = ' + formatChannelVoltageStat(channelStats.vAve) + '\n';
    s += '             Vrms = ' + formatChannelVoltageStat(channelStats.vRms) + '\n';

    return s;
}

function buildInfoHeaderText(result, filename) {
    var s = '    General:\n';
    s += '        File Model   = ' + (result.fileModel || result.format) + '\n';
    if (result.serialNumber) {
        s += '        Serial Number = ' + result.serialNumber + '\n';
    }
    s += '        User Model   = ' + (result.userModel || 'auto') + '\n';
    s += '        Parser Model = ' + (result.parserModel || 'browser') + '\n';
    s += '        Firmware     = ' + (result.firmware || 'unknown') + '\n';
    s += '        Filename     = ' + filename + '\n';
    s += '        Channels     = [' + result.channels.map(function(ch) {
        return ch.channelNumber;
    }).join(', ') + ']\n\n';

    var levels = derivedLevels(result);
    if (result.triggerInfo || levels.length) {
        s += '    Trigger:\n';
        if (result.triggerInfo) {
            if (result.triggerInfo.mode === 'alt') {
                s += '        Mode     = alt\n';
                if (result.triggerInfo.trigger1) {
                    s += '\n        Trigger 1:\n';
                    s += describeTriggerBlock(result.triggerInfo.trigger1, '            ');
                }
                if (result.triggerInfo.trigger2) {
                    s += '\n        Trigger 2:\n';
                    s += describeTriggerBlock(result.triggerInfo.trigger2, '            ');
                }
            } else {
                s += describeTriggerBlock(result.triggerInfo, '        ');
            }
        }

        var source = result.triggerInfo && result.triggerInfo.source ? result.triggerInfo.source : '';
        var showChannelLabel = !{ CH1: 1, CH2: 1, CH3: 1, CH4: 1 }[source];
        levels.forEach(function(level) {
            var label = showChannelLabel ? 'Derived Level (CH' + level.channelNumber + ')' : 'Derived Level    ';
            s += '        ' + label + ' = ' + engineeringString(level.value, 2) + 'V\n';
        });
        s += '\n';
    }

    return s;
}

function buildInfoText(result, filename) {
    var s = buildInfoHeaderText(result, filename);

    result.channels.forEach(function(ch) {
        s += channelInfoText(ch);
        s += '\n';
    });
    return s;
}

function toU8(buf) {
    if (!buf) {
        return null;
    }
    return buf instanceof Uint8Array ? buf : new Uint8Array(buf);
}

function sliceArrayBuffer(bytes) {
    var view = toU8(bytes);
    return view.buffer.slice(view.byteOffset, view.byteOffset + view.byteLength);
}

function bytesToAscii(bytes) {
    var view = toU8(bytes);
    var text = '';
    for (var i = 0; i < view.length; i++) {
        text += String.fromCharCode(view[i]);
    }
    return text;
}

async function maybeInflateDeflate(bytes, expectedLength) {
    var view = toU8(bytes);
    if (!view || !view.length) {
        return new Uint8Array(0);
    }
    if (view.length === expectedLength) {
        return view;
    }
    if (typeof DecompressionStream === 'undefined') {
        throw new Error('This browser cannot decompress DHO .wfm metadata blocks.');
    }

    try {
        var inflated = await new Response(
            new Blob([view]).stream().pipeThrough(new DecompressionStream('deflate'))
        ).arrayBuffer();
        return new Uint8Array(inflated);
    } catch (err) {
        throw new Error('Could not decompress DHO .wfm metadata block.');
    }
}

function parseDhoPayload(ctor, content) {
    return new ctor(new KaitaiStream(sliceArrayBuffer(content)), null, null);
}

async function parseDhoBlocks(buffer) {
    var parsed = new Wfmdho1000.Wfmdho1000(new KaitaiStream(buffer), null, null);
    var blocks = [];
    var offset = DHO_FILE_HEADER_SIZE;

    for (var i = 0; i < parsed.blocks.length; i++) {
        var block = parsed.blocks[i];
        if (block.isTerminator) {
            break;
        }
        var rawContent = toU8(block.contentRaw).slice(0, block.compSize);
        var content = await maybeInflateDeflate(rawContent, block.decompSize);
        blocks.push({ block: block, content: content, offset: offset });
        offset += DHO_BLOCK_HEADER_SIZE + block.lenContentRaw;
    }

    return { blocks: blocks, blocksEnd: offset };
}

function extractDhoVoltCalibration(blocks) {
    var blockTypes = Wfmdho1000.Wfmdho1000.BlockTypeEnum;
    var isDho800 = blocks.some(function(entry) {
        return entry.block.blockType === blockTypes.DHO800_CHANNEL_PARAMS &&
            entry.block.blockId >= 1 && entry.block.blockId <= 4;
    });
    var cal = {};
    var settingsCenter = null;
    var scale1 = null;

    if (isDho800) {
        blocks.forEach(function(entry) {
            if (entry.block.blockType === blockTypes.DHO800_CHANNEL_PARAMS &&
                entry.block.blockId >= 1 && entry.block.blockId <= 4) {
                var params = parseDhoPayload(Wfmdho1000.Wfmdho1000.Dho800ChannelParams, entry.content);
                cal[entry.block.blockId] = {
                    scale: params.scale,
                    vCenter: params.vCenter,
                    offset: params.offset,
                };
            }
        });
        return { isDho800: true, calibration: cal };
    }

    blocks.forEach(function(entry) {
        if (entry.block.blockType === blockTypes.CHANNEL_PARAMS &&
            entry.block.blockId >= 1 && entry.block.blockId <= 4) {
            var params = parseDhoPayload(Wfmdho1000.Wfmdho1000.Dho1000ChannelParams, entry.content);
            cal[entry.block.blockId] = {
                scale: params.scale,
                vCenter: params.vCenter,
                offset: params.offset,
            };
            if (entry.block.blockId === 1) {
                scale1 = params.scale;
            }
        } else if (entry.block.blockType === blockTypes.SETTINGS) {
            settingsCenter = parseDhoPayload(Wfmdho1000.Wfmdho1000.SettingsBlock, entry.content).vCenter;
        }
    });

    if (!Object.keys(cal).length && scale1 !== null && settingsCenter !== null) {
        cal[1] = {
            scale: scale1,
            vCenter: settingsCenter,
            offset: -settingsCenter - scale1 * DHO_ADC_MIDPOINT,
        };
    }

    return { isDho800: false, calibration: cal };
}

function findDhoDataSection(buffer, blocksEnd, isDho800) {
    var bytes = new Uint8Array(buffer);
    var dv = new DataView(buffer);
    var offset = blocksEnd;

    while (offset < bytes.length && bytes[offset] === 0) {
        offset += 1;
    }
    if (offset + 40 >= bytes.length || offset + 28 > bytes.length) {
        return null;
    }

    var nPtsU64 = dv.getUint32(offset, true) + dv.getUint32(offset + 4, true) * 4294967296;
    var totalPts;
    if (isDho800) {
        if (nPtsU64 === 0 || nPtsU64 > 2000000000) {
            return null;
        }
        totalPts = nPtsU64;
    } else {
        if (nPtsU64 <= 64 || nPtsU64 > 2000000000) {
            return null;
        }
        totalPts = nPtsU64 - 64;
    }

    var nPtsHint = dv.getUint32(offset + 24, true);
    var nPtsPerChannel;
    var nChannels;
    if (nPtsHint > 0 && totalPts % nPtsHint === 0) {
        nPtsPerChannel = nPtsHint;
        nChannels = totalPts / nPtsHint;
    } else {
        nPtsPerChannel = totalPts;
        nChannels = 1;
    }

    if (nPtsPerChannel === 0 || nChannels <= 0 || nChannels > 4) {
        return null;
    }

    var xIncrementNs = dv.getUint32(offset + 16, true);
    if (xIncrementNs === 0 || xIncrementNs > 1000000000) {
        xIncrementNs = 1;
    }

    var xIncrement = xIncrementNs * (isDho800 ? DHO_X_INCREMENT_SCALE_DHO800 : DHO_X_INCREMENT_SCALE);
    return {
        nPts: nPtsPerChannel,
        nChannels: nChannels,
        xOrigin: -(nPtsPerChannel / 2) * xIncrement,
        xIncrement: xIncrement,
        dataStart: offset + 40,
    };
}

function parseDhoModel(blocks, fallback) {
    for (var i = 0; i < blocks.length; i++) {
        var text = bytesToAscii(blocks[i].content);
        for (var p = 0; p < 2; p++) {
            var prefix = p === 0 ? 'DHO' : 'MSO';
            var idx = text.indexOf(prefix);
            if (idx < 0) {
                continue;
            }
            var model = '';
            for (var j = idx; j < Math.min(text.length, idx + 20); j++) {
                var ch = text.charAt(j);
                if (!ch || ch === '\u0000') {
                    break;
                }
                model += ch;
            }
            if (model.length >= 3) {
                return model;
            }
        }
    }
    return fallback;
}

async function detectAndParse(buffer, filename) {
    var b = new Uint8Array(buffer);
    var fsize = buffer.byteLength;

    if (b.length < 4) {
        throw new Error('File too short to detect model.');
    }

    var b0 = b[0];
    var b1 = b[1];
    var b2 = b[2];
    var b3 = b[3];

    function u32le(off) {
        return (b[off] | b[off + 1] << 8 | b[off + 2] << 16 | b[off + 3] << 24) >>> 0;
    }

    function asciiStr(off, maxLen) {
        var s = '';
        for (var i = 0; i < maxLen && b[off + i]; i++) {
            s += String.fromCharCode(b[off + i]);
        }
        return s;
    }

    if (b0 === 0xA5 && b1 === 0xA5 && b2 === 0xA4 && b3 === 0x01) {
        return parseB(buffer);
    }
    if (b0 === 0xA1 && b1 === 0xA5 && b2 === 0x00 && b3 === 0x00) {
        return parseC(buffer);
    }
    if (b0 === 0x01 && b1 === 0xFF && b2 === 0xFF && b3 === 0xFF) {
        return parseZ(buffer);
    }

    if (b0 === 0x02 && b1 === 0x00 && b2 === 0x00 && b3 === 0x00) {
        return parseDhoWfm(buffer);
    }

    var magicStr = String.fromCharCode(b0, b1, b2, b3);

    if (magicStr === 'RG03') {
        return parseDhoBin(buffer);
    }

    if (magicStr === 'RG01') {
        return u32le(12) === 128 ? parseBin70008000(buffer) : parseBin5000(buffer);
    }

    if (b0 === 0xA5 && b1 === 0xA5 && b2 === 0x38 && b3 === 0x00) {
        var modelStr = asciiStr(4, 20);
        if (modelStr.indexOf('DS4') === 0 || modelStr.indexOf('MSO4') === 0) {
            return parse4000(buffer);
        }
        if (modelStr.indexOf('DS6') === 0 || modelStr.indexOf('MSO6') === 0) {
            throw new Error('DS6000 format is not yet supported by this viewer.');
        }
        return parse2000(buffer);
    }

    if (b0 === 0xA5 && b1 === 0xA5 && b2 === 0x00 && b3 === 0x00) {
        try {
            var pts = u32le(28);
            var ch1en = b[49] !== 0;
            var ch2en = b[73] !== 0;
            var nch = (ch1en ? 1 : 0) + (ch2en ? 1 : 0);
            if (pts > 0 && nch > 0) {
                if (fsize === 256 + nch * pts) {
                    return parseC(buffer);
                }
                if (fsize === 272 + nch * pts) {
                    return parseC(buffer);
                }
                if (fsize === 276 + nch * pts) {
                    return parseE(buffer);
                }
            }
        } catch (_) {
            // fall back to the DS1000E parser below
        }
        return parseE(buffer);
    }

    // LeCroy .trc: "WAVEDESC" ASCII somewhere in the first 64 bytes
    // (SCPI-prefixed files have a #N<digits> header before WAVEDESC)
    var wavDesc = [0x57, 0x41, 0x56, 0x45, 0x44, 0x45, 0x53, 0x43]; // "WAVEDESC"
    var wdOffset = -1;
    for (var wi = 0; wi <= Math.min(56, b.length - 8); wi++) {
        var match = true;
        for (var wj = 0; wj < 8; wj++) {
            if (b[wi + wj] !== wavDesc[wj]) { match = false; break; }
        }
        if (match) { wdOffset = wi; break; }
    }
    if (wdOffset >= 0) {
        return parseLeCroy(buffer, wdOffset);
    }

    throw new Error((filename || 'This file') + ' is not a supported file type.');
}

function parseLeCroy(buffer, wavedescOffset) {
    // Slice to WAVEDESC so the parser sees offset 0 = start of WAVEDESC
    var offset = wavedescOffset || 0;
    var payload = buffer.slice(offset);
    var b = new Uint8Array(payload);

    // Byte 34 of WAVEDESC is the low byte of COMM_ORDER: 1 = LOFIRST (LE), 0 = HIFIRST (BE)
    var isLe = b[34] === 1;

    // Bytes 16–31 of WAVEDESC contain the null-terminated template name
    var templateStr = '';
    for (var ti = 0; ti < 16 && b[16 + ti]; ti++) {
        templateStr += String.fromCharCode(b[16 + ti]);
    }
    var isV1 = templateStr.trim() === 'LECROY_1_0';

    var w = isV1
        ? (isLe
            ? new Lecroy10Le.Lecroy10Le(new KaitaiStream(payload), null, null)
            : new Lecroy10Be.Lecroy10Be(new KaitaiStream(payload), null, null))
        : (isLe
            ? new Lecroy23Le.Lecroy23Le(new KaitaiStream(payload), null, null)
            : new Lecroy23Be.Lecroy23Be(new KaitaiStream(payload), null, null));

    var wd = w.wavedesc;
    var n = wd.waveArrayCount;
    var vertGain = wd.verticalGain;
    // LECROY_1_0 uses acqVertOffset; LECROY_2_3 uses verticalOffset
    var vertOffset = isV1 ? wd.acqVertOffset : wd.verticalOffset;
    var horizInterval = wd.horizInterval;
    var horizOffset = wd.horizOffset;
    var maxVal = wd.maxValue;
    var minVal = wd.minValue;
    var is16bit = wd.is16bit;

    // Decode instrument name (null-terminated bytes)
    var instBytes = wd.instrumentName;
    var instName = '';
    for (var i = 0; i < instBytes.length && instBytes[i]; i++) {
        instName += String.fromCharCode(instBytes[i]);
    }
    instName = instName.trim() || 'LeCroy';

    // WAVE_SOURCE: LECROY_1_0 is 1-indexed s2; LECROY_2_3 is 0-indexed IntEnum
    var waveSource = typeof wd.waveSource === 'object' ? wd.waveSource.value : wd.waveSource;
    var slot;
    if (isV1) {
        slot = Math.max(0, Math.min(3, waveSource - 1)); // 1-indexed → 0-based
    } else {
        slot = (waveSource >= 0 && waveSource <= 3) ? waveSource : 0;
    }
    var chName = 'CH' + (slot + 1);

    // Coupling
    var couplingVal = typeof wd.vertCoupling === 'object' ? wd.vertCoupling.value : wd.vertCoupling;
    var couplingMap = { 0: 'DC', 1: 'GND', 2: 'DC', 3: 'GND', 4: 'AC' };
    var coupling = couplingMap[couplingVal] || 'DC';

    var probeAtt = wd.probeAtt || 1.0;

    // Decode ADC samples
    var rawBytes = w.waveArray1;
    var adc = new Float64Array(n);
    if (is16bit) {
        var view = new DataView(rawBytes.buffer, rawBytes.byteOffset, rawBytes.byteLength);
        for (var j = 0; j < n && j * 2 + 1 < rawBytes.length; j++) {
            adc[j] = view.getInt16(j * 2, isLe);
        }
    } else {
        var adcLen = Math.min(n, rawBytes.length);
        for (var k = 0; k < adcLen; k++) {
            // int8 from uint8
            adc[k] = rawBytes[k] < 128 ? rawBytes[k] : rawBytes[k] - 256;
        }
    }
    if (adc.length > n) {
        adc = adc.subarray(0, n);
    }

    // Calibrate voltage and build time axis
    var times = new Float64Array(n);
    var volts = new Float64Array(n);
    for (var m = 0; m < n; m++) {
        times[m] = horizOffset + m * horizInterval;
        volts[m] = vertGain * adc[m] - vertOffset;
    }

    // max/min_value are ADC counts; convert to volts-per-div
    var voltPerDiv = (maxVal !== minVal) ? (maxVal - minVal) * Math.abs(vertGain) / 8.0 : 1.0;

    // Build proxy raw (uint8) from calibrated volts
    var raw = proxyRawFromCalibrated(volts);

    return {
        format: 'LeCroy TRC',
        fileModel: instName,
        userModel: 'LeCroy',
        parserModel: isV1 ? 'lecroy_1_0' : 'lecroy_2_3',
        firmware: 'unknown',
        triggerInfo: null,
        channels: [{
            name: chName,
            color: CH_COLORS[slot % CH_COLORS.length],
            times: times,
            volts: volts,
            raw: raw,
            channelNumber: slot + 1,
            points: n,
            coupling: coupling,
            voltPerDiv: voltPerDiv,
            voltOffset: vertOffset,
            probeValue: probeAtt,
            inverted: false,
            timeScale: n > 0 ? n * horizInterval / 10.0 : 1e-3,
            timeOffset: horizOffset,
            secondsPerPoint: horizInterval,
        }],
    };
}

function parseB(buffer) {
    var w = new Wfm1000b.Wfm1000b(new KaitaiStream(buffer), null, null);
    var h = w.header;
    var channels = [];
    var spp = h.secondsPerPoint;
    var timeScale = 1e-12 * h.timeScale;
    var timeOffset = 1e-12 * h.timeOffset;
    var points = h.points;
    var start = timeOffset - points * spp / 2;
    var rawArrays = [h.ch1, h.ch2, h.ch3, h.ch4];
    for (var ci = 0; ci < 4; ci++) {
        if (!h.ch[ci].enabled) {
            continue;
        }
        var raw = toU8(rawArrays[ci]);
        if (!raw || raw.length === 0) {
            continue;
        }
        var n = raw.length;
        var vScale = h.ch[ci].voltScale;
        var vOff = h.ch[ci].voltOffset + 1.12 * h.ch[ci].voltPerDivision;
        var coupling = 'AC';
        if ((ci === 0 && (h.couplingCh12 & 0xC0) === 0xC0) ||
            (ci === 1 && (h.couplingCh12 & 0x0C) === 0x0C) ||
            (ci === 2 && (h.couplingCh34 & 0xC0) === 0xC0) ||
            (ci === 3 && (h.couplingCh34 & 0x0C) === 0x0C)) {
            coupling = 'DC';
        }
        var times = new Float64Array(n);
        var volts = new Float64Array(n);
        for (var i = 0; i < n; i++) {
            times[i] = start + i * spp;
            volts[i] = vScale * (127 - raw[i]) - vOff;
        }
        channels.push({
            name: 'CH' + (ci + 1),
            color: CH_COLORS[ci],
            times: times,
            volts: volts,
            raw: raw,
            channelNumber: ci + 1,
            points: n,
            coupling: coupling,
            voltPerDiv: h.ch[ci].voltPerDivision,
            voltOffset: h.ch[ci].voltOffset,
            probeValue: h.ch[ci].probeValue,
            inverted: h.ch[ci].inverted,
            timeScale: timeScale,
            timeOffset: timeOffset,
            secondsPerPoint: spp,
        });
    }
    return {
        format: 'DS1000B',
        fileModel: 'DS1000B',
        userModel: 'B',
        parserModel: 'wfm1000b',
        firmware: 'unknown',
        triggerInfo: {
            mode: enumName(Wfm1000b.Wfm1000b.TriggerModeEnum, h.triggerMode).toLowerCase(),
            source: enumName(Wfm1000b.Wfm1000b.TriggerSourceEnum, h.triggerSource).toUpperCase(),
        },
        channels: channels,
    };
}

function parseE(buffer) {
    var w = new Wfm1000e.Wfm1000e(new KaitaiStream(buffer), null, null);
    var h = w.header;
    var channels = [];
    function triggerHeaderInfo(th) {
        return {
            mode: enumName(Wfm1000e.Wfm1000e.TriggerModeEnum, th.mode).toLowerCase(),
            source: enumName(Wfm1000e.Wfm1000e.SourceEnum, th.source).toUpperCase(),
            level: th.level,
            sweep: sweepName(th.sweep),
            coupling: triggerCouplingName(th.coupling),
        };
    }
    for (var ci = 0; ci < 2; ci++) {
        var chh = h.ch[ci];
        if (!chh.enabled) {
            continue;
        }
        var raw = toU8(ci === 0 ? w.data.ch1 : w.data.ch2);
        if (!raw || raw.length === 0) {
            continue;
        }
        var n = raw.length;
        var memDepth = ci === 0 ? h.ch1MemoryDepth : h.ch2MemoryDepth;
        var channelTimeOffset = ci === 0 ? h.ch1TimeOffset : h.ch2TimeOffset;
        var channelTimeScale = ci === 0 ? h.ch1TimeScale : h.ch2TimeScale;
        var spp = h.secondsPerPoint;
        var start = channelTimeOffset - memDepth * spp / 2;
        var times = new Float64Array(n);
        var volts = new Float64Array(n);
        for (var i = 0; i < n; i++) {
            times[i] = start + i * spp;
            volts[i] = chh.voltScale * (125 - raw[i]) - chh.voltOffset;
        }
        channels.push({
            name: 'CH' + (ci + 1),
            color: CH_COLORS[ci],
            times: times,
            volts: volts,
            raw: raw,
            channelNumber: ci + 1,
            points: n,
            coupling: 'unknown',
            voltPerDiv: chh.voltPerDivision,
            voltOffset: chh.voltOffset,
            probeValue: chh.probeValue,
            inverted: chh.inverted,
            timeScale: channelTimeScale,
            timeOffset: channelTimeOffset,
            secondsPerPoint: spp,
        });
    }
    var triggerMode = enumName(Wfm1000e.Wfm1000e.TriggerModeEnum, h.triggerMode).toLowerCase();
    var triggerInfo = triggerMode === 'alt' ? {
        mode: 'alt',
        trigger1: triggerHeaderInfo(h.trigger1),
        trigger2: triggerHeaderInfo(h.trigger2),
    } : triggerHeaderInfo(h.trigger1);
    if (triggerMode !== 'alt') {
        triggerInfo.mode = triggerMode;
    }
    return {
        format: 'DS1000E',
        fileModel: 'DS1000E',
        userModel: 'E',
        parserModel: 'wfm1000e',
        firmware: 'unknown',
        triggerInfo: triggerInfo,
        channels: channels,
    };
}

function parseC(buffer) {
    var w = new Wfm1000c.Wfm1000c(new KaitaiStream(buffer), null, null);
    var h = w.header;
    var channels = [];
    var spp = h.secondsPerPoint;
    var timeOffset = Number(h.timeOffset) * 1e-12;
    var timeScale = Number(h.timeScale) * 1e-12;
    var n = h.points;
    var halfWin = n * spp / 2;
    var step = n > 1 ? 2 * halfWin / (n - 1) : 0;
    for (var ci = 0; ci < 2; ci++) {
        var chh = h.ch[ci];
        if (!chh.enabled) {
            continue;
        }
        var raw = toU8(ci === 0 ? w.data.ch1 : w.data.ch2);
        if (!raw || raw.length === 0) {
            continue;
        }
        var len = raw.length;
        var times = new Float64Array(len);
        var volts = new Float64Array(len);
        for (var i = 0; i < len; i++) {
            times[i] = timeOffset - halfWin + i * step;
            volts[i] = chh.voltScale * (125 - raw[i]) - chh.voltOffset;
        }
        channels.push({
            name: 'CH' + (ci + 1),
            color: CH_COLORS[ci],
            times: times,
            volts: volts,
            raw: raw,
            channelNumber: ci + 1,
            points: len,
            coupling: 'unknown',
            voltPerDiv: chh.voltPerDivision,
            voltOffset: chh.voltOffset,
            probeValue: chh.probeValue,
            inverted: chh.inverted,
            timeScale: timeScale,
            timeOffset: timeOffset,
            secondsPerPoint: spp,
        });
    }
    return {
        format: 'DS1000C',
        fileModel: 'DS1000C',
        userModel: 'C',
        parserModel: 'wfm1000c',
        firmware: 'unknown',
        triggerInfo: {
            mode: enumName(Wfm1000c.Wfm1000c.TriggerModeEnum, h.triggerMode).toLowerCase(),
            source: enumName(Wfm1000c.Wfm1000c.TriggerSourceEnum, h.triggerSource).toUpperCase(),
        },
        channels: channels,
    };
}

function parseZ(buffer) {
    var w = new Wfm1000z.Wfm1000z(new KaitaiStream(buffer), null, null);
    var h = w.header;
    var all = toU8(w.data.raw);
    var spp = h.secondsPerPoint;
    var tOff = h.timeOffset;
    var stride = h.stride;
    var points = h.points;
    var start = tOff - points * spp / 2;
    var enabledFlags = [h.ch1Enabled, h.ch2Enabled, h.ch3Enabled, h.ch4Enabled];
    var channels = [];
    for (var ci = 0; ci < 4; ci++) {
        var chh = h.ch[ci];
        if (!enabledFlags[ci]) {
            continue;
        }
        var offset;
        if (stride === 1) {
            offset = 0;
        } else if (stride === 2) {
            var anyLower = false;
            for (var j = 0; j < ci; j++) {
                if (enabledFlags[j]) {
                    anyLower = true;
                    break;
                }
            }
            offset = anyLower ? 0 : 1;
        } else {
            offset = 3 - ci;
        }
        var raw = new Uint8Array(points);
        var times = new Float64Array(points);
        var volts = new Float64Array(points);
        for (var i = 0; i < points; i++) {
            raw[i] = all[offset + i * stride];
            times[i] = start + i * spp;
            volts[i] = chh.yScale * (127 - raw[i]) - chh.yOffset;
        }
        channels.push({
            name: 'CH' + (ci + 1),
            color: CH_COLORS[ci],
            times: times,
            volts: volts,
            raw: raw,
            channelNumber: ci + 1,
            points: points,
            coupling: enumName(Wfm1000z.Wfm1000z.CouplingEnum, chh.coupling).toUpperCase(),
            voltPerDiv: chh.voltPerDivision,
            voltOffset: chh.voltOffset,
            probeValue: chh.probeValue,
            inverted: chh.inverted,
            timeScale: h.timeScale,
            timeOffset: tOff,
            secondsPerPoint: spp,
        });
    }
    return {
        format: 'DS1000Z',
        fileModel: w.preheader.modelNumber,
        userModel: 'Z',
        parserModel: 'wfm1000z',
        firmware: w.preheader.firmwareVersion || 'unknown',
        triggerInfo: null,
        channels: channels,
    };
}

function effective2000TimeOffset(h) {
    var modelNumber = h.modelNumber || '';
    var firmwareVersion = h.firmwareVersion || '';

    // Older DS2A captures store a nonzero time offset even though the
    // saved screenshot shows the trigger marker centered.
    if (modelNumber.indexOf('DS2A') === 0 && firmwareVersion === '00.03.00.01.03') {
        return 0;
    }

    return h.timeOffset;
}

function parse2000(buffer) {
    var w = new Wfm2000.Wfm2000(new KaitaiStream(buffer), null, null);
    var h = w.header;
    var channels = [];
    var spp = h.secondsPerPoint;
    var adjTOff = effective2000TimeOffset(h) + h.zPtOffset * spp;
    var start = adjTOff - h.storageDepth * spp / 2;
    var rawArrays = [h.raw1, h.raw2, h.raw3, h.raw4];
    for (var ci = 0; ci < 4; ci++) {
        var chh = h.ch[ci];
        if (!chh.enabled) {
            continue;
        }
        var raw = toU8(rawArrays[ci]);
        if (!raw || raw.length === 0) {
            continue;
        }
        var n = raw.length;
        var times = new Float64Array(n);
        var volts = new Float64Array(n);
        for (var i = 0; i < n; i++) {
            times[i] = start + i * spp;
            volts[i] = -chh.voltScale * (127 - raw[i]) - chh.voltOffset;
        }
        channels.push({
            name: 'CH' + (ci + 1),
            color: CH_COLORS[ci],
            times: times,
            volts: volts,
            raw: raw,
            channelNumber: ci + 1,
            points: n,
            coupling: enumName(Wfm2000.Wfm2000.CouplingEnum, chh.coupling).toUpperCase(),
            voltPerDiv: chh.voltPerDivision,
            voltOffset: chh.voltOffset,
            probeValue: chh.probeValue || 1,
            inverted: chh.inverted || false,
            timeScale: h.timeScale,
            timeOffset: adjTOff,
            secondsPerPoint: spp,
        });
    }
    return {
        format: 'DS2000',
        fileModel: 'DS2000',
        serialNumber: h.serialNumber || h.modelNumber || '',
        userModel: '2',
        parserModel: 'wfm2000',
        firmware: h.firmwareVersion || 'unknown',
        triggerInfo: decode2000Trigger(h),
        channels: channels,
    };
}

function parse4000(buffer) {
    var w = new Wfm4000.Wfm4000(new KaitaiStream(buffer), null, null);
    var h = w.header;
    var channels = [];
    var spp = h.secondsPerPoint;
    var start = h.timeOffset - h.memDepth * spp / 2;
    var enFlags = [h.enabled.channel1, h.enabled.channel2, h.enabled.channel3, h.enabled.channel4];
    var rawArrays = [h.raw1, h.raw2, h.raw3, h.raw4];
    for (var ci = 0; ci < 4; ci++) {
        if (!enFlags[ci]) {
            continue;
        }
        var raw = toU8(rawArrays[ci]);
        if (!raw || raw.length === 0) {
            continue;
        }
        var n = raw.length;
        var times = new Float64Array(n);
        var volts = new Float64Array(n);
        for (var i = 0; i < n; i++) {
            times[i] = start + i * spp;
            volts[i] = -h.ch[ci].voltScale * (127 - raw[i]) - h.ch[ci].voltOffset;
        }
        channels.push({
            name: 'CH' + (ci + 1),
            color: CH_COLORS[ci],
            times: times,
            volts: volts,
            raw: raw,
            channelNumber: ci + 1,
            points: n,
            coupling: enumName(Wfm4000.Wfm4000.CouplingEnum, h.ch[ci].coupling).toUpperCase(),
            voltPerDiv: h.ch[ci].voltPerDivision,
            voltOffset: h.ch[ci].voltOffset,
            probeValue: h.ch[ci].probeValue || 1,
            inverted: h.ch[ci].inverted || false,
            timeScale: h.timeScale,
            timeOffset: h.timeOffset,
            secondsPerPoint: spp,
        });
    }
    return {
        format: 'DS4000',
        fileModel: 'DS4000',
        serialNumber: h.serialNumber || h.modelNumber || '',
        userModel: '4',
        parserModel: 'wfm4000',
        firmware: h.firmwareVersion || 'unknown',
        triggerInfo: decode4000Trigger(h),
        channels: channels,
    };
}

function parseBinWaveforms(w, format, userModel, parserModel) {
    var channels = [];
    var fileModel = format;
    var firmware = w.fileHeader && w.fileHeader.version ? w.fileHeader.version : 'unknown';
    for (var wi = 0; wi < w.waveforms.length; wi++) {
        var wfm = w.waveforms[wi];
        var dh = wfm.dataHeader;
        if (dh.bufferType < 1 || dh.bufferType > 3) {
            continue;
        }
        var wh = wfm.wfmHeader;
        var dataRaw = wfm.dataRaw;
        var n = wh.nPts;
        var dv = new DataView(dataRaw.buffer, dataRaw.byteOffset, dataRaw.byteLength);
        var times = new Float64Array(n);
        var volts = new Float64Array(n);
        var vMin = Infinity;
        var vMax = -Infinity;
        for (var i = 0; i < n; i++) {
            times[i] = -wh.xOrigin + i * wh.xIncrement;
            var v = dv.getFloat32(i * 4, true);
            volts[i] = v;
            if (v < vMin) {
                vMin = v;
            }
            if (v > vMax) {
                vMax = v;
            }
        }
        fileModel = modelFromFrameString(wh.frameString, fileModel);
        var timeScale = wh.xDisplayRange > 0 ? wh.xDisplayRange / 10 : n * wh.xIncrement / 10;
        var timeOffset = n * wh.xIncrement / 2 - wh.xOrigin;
        channels.push({
            name: wh.waveformLabel || ('CH' + (channels.length + 1)),
            color: CH_COLORS[channels.length % CH_COLORS.length],
            times: times,
            volts: volts,
            raw: proxyRawFromCalibrated(volts),
            channelNumber: channelNumberFromName(wh.waveformLabel, channels.length + 1),
            points: n,
            coupling: 'unknown',
            voltPerDiv: vMax > vMin ? (vMax - vMin) / 8 : 1,
            voltOffset: 0,
            probeValue: 1,
            inverted: false,
            timeScale: timeScale,
            timeOffset: timeOffset,
            secondsPerPoint: wh.xIncrement,
        });
    }
    return {
        format: format,
        fileModel: fileModel,
        userModel: userModel,
        parserModel: parserModel,
        firmware: firmware,
        triggerInfo: null,
        channels: channels,
    };
}

function parseBin5000(buffer) {
    return parseBinWaveforms(new Bin5000.Bin5000(new KaitaiStream(buffer), null, null), 'MSO5000', '5', 'bin5000');
}

function parseBin70008000(buffer) {
    return parseBinWaveforms(new Bin70008000.Bin70008000(new KaitaiStream(buffer), null, null), 'MSO7000/8000', '7', 'bin7000_8000');
}

async function parseDhoWfm(buffer) {
    if (buffer.byteLength < DHO_FILE_HEADER_SIZE + DHO_BLOCK_HEADER_SIZE) {
        throw new Error('File too small to be a valid DHO .wfm file.');
    }

    var parsedBlocks = await parseDhoBlocks(buffer);
    if (!parsedBlocks.blocks.length) {
        throw new Error('No valid metadata blocks found in DHO .wfm file.');
    }

    var extracted = extractDhoVoltCalibration(parsedBlocks.blocks);
    var calibration = extracted.calibration;
    var calibrationKeys = Object.keys(calibration);
    if (!calibrationKeys.length) {
        throw new Error('Could not extract DHO .wfm voltage calibration.');
    }

    var dataSection = findDhoDataSection(buffer, parsedBlocks.blocksEnd, extracted.isDho800);
    if (!dataSection) {
        throw new Error('Could not locate DHO .wfm sample data section.');
    }

    var requiredBytes = dataSection.dataStart + dataSection.nPts * dataSection.nChannels * 2;
    if (requiredBytes > buffer.byteLength) {
        throw new Error('DHO .wfm data section is truncated.');
    }

    var defaultCal = calibration[1] || calibration[calibrationKeys[0]];
    var channels = [];
    var fileModel = parseDhoModel(parsedBlocks.blocks, extracted.isDho800 ? 'DHO800' : 'DHO1000');
    var dv = new DataView(buffer);

    for (var ci = 0; ci < dataSection.nChannels; ci++) {
        var chNum = ci + 1;
        var cal = calibration[chNum] || defaultCal;
        var raw = new Uint8Array(dataSection.nPts);
        var times = new Float64Array(dataSection.nPts);
        var volts = new Float64Array(dataSection.nPts);

        for (var i = 0; i < dataSection.nPts; i++) {
            var raw16 = dv.getUint16(
                dataSection.dataStart + 2 * (ci + i * dataSection.nChannels),
                true
            );
            raw[i] = raw16 >> 8;
            times[i] = dataSection.xOrigin + i * dataSection.xIncrement;
            volts[i] = cal.scale * raw16 + cal.offset;
        }

        channels.push({
            name: 'CH' + chNum,
            color: CH_COLORS[ci % CH_COLORS.length],
            times: times,
            volts: volts,
            raw: raw,
            channelNumber: chNum,
            points: dataSection.nPts,
            coupling: 'DC',
            voltPerDiv: Math.abs(cal.scale * 65536 / 8),
            voltOffset: cal.vCenter,
            probeValue: 1,
            inverted: false,
            timeScale: dataSection.nPts * dataSection.xIncrement / 10,
            timeOffset: 0,
            secondsPerPoint: dataSection.xIncrement,
        });
    }

    var family = dhoFamilyLabel(fileModel, extracted.isDho800 ? 'DHO800' : 'DHO1000');
    return {
        format: family,
        fileModel: fileModel,
        userModel: 'DHO',
        parserModel: 'wfmdho1000',
        firmware: 'unknown',
        triggerInfo: null,
        channels: channels,
    };
}

function parseDhoBin(buffer) {
    var w = new Bindho1000.Bindho1000(new KaitaiStream(buffer), null, null);
    var channels = [];
    var fileModel = 'DHO1000';
    for (var wi = 0; wi < w.waveforms.length; wi++) {
        var wfm = w.waveforms[wi];
        if (wfm.dataHeader.bufferType !== 1) {
            continue;
        }
        var wh = wfm.wfmHeader;
        var vals = wfm.samples.values;
        var n = vals.length;
        var times = new Float64Array(n);
        var volts = new Float64Array(n);
        var vMin = Infinity;
        var vMax = -Infinity;
        for (var i = 0; i < n; i++) {
            times[i] = wh.t0 + i * wh.xIncrement;
            volts[i] = vals[i];
            if (vals[i] < vMin) {
                vMin = vals[i];
            }
            if (vals[i] > vMax) {
                vMax = vals[i];
            }
        }
        fileModel = wh.model || fileModel;
        channels.push({
            name: wh.channelName || ('CH' + (channels.length + 1)),
            color: CH_COLORS[channels.length % CH_COLORS.length],
            times: times,
            volts: volts,
            raw: proxyRawFromDhoVolts(vals),
            channelNumber: channelNumberFromName(wh.channelName, channels.length + 1),
            points: n,
            coupling: 'unknown',
            voltPerDiv: vMax > vMin ? (vMax - vMin) / 8 : 1,
            voltOffset: 0,
            probeValue: 1,
            inverted: false,
            timeScale: wh.xDisplayRange / 10,
            timeOffset: 0,
            secondsPerPoint: wh.xIncrement,
        });
    }
    var family = dhoFamilyLabel(fileModel, 'DHO1000');
    return {
        format: family + ' (BIN)',
        fileModel: fileModel,
        userModel: 'DHO',
        parserModel: 'dho1000',
        firmware: 'unknown',
        triggerInfo: null,
        channels: channels,
    };
}

function niceStep(rawStep) {
    if (rawStep <= 0) {
        return 1;
    }
    var exp = Math.floor(Math.log10(rawStep));
    var frac = rawStep / Math.pow(10, exp);
    return (frac < 1.5 ? 1 : frac < 3.5 ? 2 : frac < 7.5 ? 5 : 10) * Math.pow(10, exp);
}

function niceAxis(dataMin, dataMax, targetDivs) {
    if (dataMin === dataMax) {
        dataMin -= 1;
        dataMax += 1;
    }
    var step = niceStep((dataMax - dataMin) / targetDivs);
    var axMin = Math.floor(dataMin / step) * step;
    var axMax = Math.ceil(dataMax / step) * step;
    return { min: axMin, max: axMax, step: step, count: Math.round((axMax - axMin) / step) };
}

function axisRangeIsUsable(min, max) {
    return Number.isFinite(min) &&
        Number.isFinite(max) &&
        max > min;
}

function graphBoundsAreUsable(bounds) {
    return bounds &&
        axisRangeIsUsable(bounds.tMin, bounds.tMax) &&
        axisRangeIsUsable(bounds.vMin, bounds.vMax);
}

function collectChannelExtents(channels) {
    var tMin = Infinity;
    var tMax = -Infinity;
    var vMin = Infinity;
    var vMax = -Infinity;

    channels.forEach(function(ch) {
        for (var i = 0; i < ch.times.length; i++) {
            if (ch.times[i] < tMin) {
                tMin = ch.times[i];
            }
            if (ch.times[i] > tMax) {
                tMax = ch.times[i];
            }
            if (ch.volts[i] < vMin) {
                vMin = ch.volts[i];
            }
            if (ch.volts[i] > vMax) {
                vMax = ch.volts[i];
            }
        }
    });

    if (!isFinite(tMin)) {
        tMin = -1;
        tMax = 1;
    }
    if (!isFinite(vMin)) {
        vMin = -1;
        vMax = 1;
    }

    return { tMin: tMin, tMax: tMax, vMin: vMin, vMax: vMax };
}

function collectVisibleVoltageExtents(channels, tMin, tMax) {
    var vMin = Infinity;
    var vMax = -Infinity;

    channels.forEach(function(ch) {
        for (var i = 0; i < ch.times.length; i++) {
            var t = ch.times[i];
            if (t < tMin || t > tMax) {
                continue;
            }
            if (ch.volts[i] < vMin) {
                vMin = ch.volts[i];
            }
            if (ch.volts[i] > vMax) {
                vMax = ch.volts[i];
            }
        }
    });

    if (!Number.isFinite(vMin) || !Number.isFinite(vMax)) {
        return null;
    }

    return { vMin: vMin, vMax: vMax };
}

function computeAutoVerticalBounds(vMin, vMax) {
    var paddedVMin = vMin;
    var paddedVMax = vMax;
    var vSpan = paddedVMax - paddedVMin || 1;
    paddedVMin -= vSpan * 0.05;
    paddedVMax += vSpan * 0.05;

    var vAx = niceAxis(paddedVMin, paddedVMax, 8);
    return {
        vMin: vAx.min,
        vMax: vAx.max,
        vAx: vAx,
    };
}

function computeExactAxis(min, max, targetDivs) {
    var step = niceStep((max - min) / targetDivs);
    return {
        min: min,
        max: max,
        step: step,
        count: Math.max(1, Math.round((max - min) / step)),
    };
}

function resolveGraphBounds(channels) {
    var extents = collectChannelExtents(channels);
    var tManual = graphAxisModes.t === 'manual' && axisRangeIsUsable(graphManualBounds.tMin, graphManualBounds.tMax);
    var vManual = graphAxisModes.v === 'manual' && axisRangeIsUsable(graphManualBounds.vMin, graphManualBounds.vMax);
    var tMin;
    var tMax;
    var vMin;
    var vMax;
    var tAx;
    var vAx;

    if (tManual) {
        tMin = graphManualBounds.tMin;
        tMax = graphManualBounds.tMax;
        tAx = computeExactAxis(tMin, tMax, 10);
    } else {
        tAx = niceAxis(extents.tMin, extents.tMax, 10);
        tMin = tAx.min;
        tMax = tAx.max;
    }

    if (vManual) {
        vMin = graphManualBounds.vMin;
        vMax = graphManualBounds.vMax;
        vAx = computeExactAxis(vMin, vMax, 8);
    } else {
        var visibleVoltageExtents = tManual ? collectVisibleVoltageExtents(channels, tMin, tMax) : null;
        var voltageExtents = visibleVoltageExtents || { vMin: extents.vMin, vMax: extents.vMax };
        var autoVertical = computeAutoVerticalBounds(voltageExtents.vMin, voltageExtents.vMax);
        vMin = autoVertical.vMin;
        vMax = autoVertical.vMax;
        vAx = autoVertical.vAx;
    }

    return {
        tMin: tMin,
        tMax: tMax,
        vMin: vMin,
        vMax: vMax,
        tAx: tAx,
        vAx: vAx,
    };
}

function buildAxisTickValues(axis, subdivisions) {
    var step = axis.step / subdivisions;
    if (!axisRangeIsUsable(axis.min, axis.max) || !Number.isFinite(step) || step <= 0) {
        return [];
    }

    var epsilon = step * 1e-9;
    var startIndex = Math.ceil((axis.min - epsilon) / step);
    var endIndex = Math.floor((axis.max + epsilon) / step);
    var values = [];

    for (var i = startIndex; i <= endIndex; i++) {
        var value = i * step;
        if (Math.abs(value) < epsilon) {
            value = 0;
        }
        values.push(value);
    }

    return values;
}

function numbersAreClose(a, b) {
    var scale = Math.max(1, Math.abs(a), Math.abs(b));
    return Math.abs(a - b) <= scale * 1e-9;
}

function axisRangesMatch(minA, maxA, minB, maxB) {
    return numbersAreClose(minA, minB) && numbersAreClose(maxA, maxB);
}

function countAxisLabelDecimals(step) {
    var abs = Math.abs(step);
    if (!Number.isFinite(abs) || abs === 0) {
        return 0;
    }
    for (var decimals = 0; decimals < 9; decimals++) {
        var scaled = abs * Math.pow(10, decimals);
        if (numbersAreClose(scaled, Math.round(scaled))) {
            return decimals;
        }
    }
    return 9;
}

function trimFixedNumber(value, decimals) {
    var text = value.toFixed(Math.max(0, decimals));
    text = text.replace(/(\.\d*?)0+$/, '$1').replace(/\.$/, '');
    if (text === '-0') {
        return '0';
    }
    return text;
}

function createAxisLabelFormatter(axis, unit) {
    var maxAbs = Math.max(Math.abs(axis.min), Math.abs(axis.max), Math.abs(axis.step));
    var exponent = 0;
    var prefixes = {
        '-12': 'p',
        '-9': 'n',
        '-6': '\u00b5',
        '-3': 'm',
        '0': '',
        '3': 'k',
        '6': 'M',
        '9': 'G',
        '12': 'T',
    };
    if (Number.isFinite(maxAbs) && maxAbs > 0) {
        exponent = Math.floor(Math.log10(maxAbs) / 3) * 3;
        exponent = Math.max(-12, Math.min(12, exponent));
    }
    var divisor = Math.pow(10, exponent);
    var prefix = prefixes[String(exponent)] || '';
    var decimals = countAxisLabelDecimals(axis.step / divisor);

    function formatNumber(value) {
        var scaled = value / divisor;
        if (Math.abs(scaled) < Math.pow(10, -decimals) / 2) {
            scaled = 0;
        }
        return trimFixedNumber(scaled, decimals);
    }

    return {
        prefix: prefix,
        unit: unit,
        formatNumber: formatNumber,
        formatWithUnit: function(value) {
            return formatNumber(value) + prefix + unit;
        },
    };
}

function axisTitleText(label, formatter) {
    return label + ' [' + formatter.prefix + formatter.unit + ']';
}

function currentPlotTheme() {
    if (lightMode) {
        return {
            background: '#ffffff',
            minorGrid: '#8f8f8f',
            majorGrid: '#4f4f4f',
            frame: '#202020',
            labels: '#000000',
            brand: '#202020',
            legendFill: '#f4f4f4',
            legendFillOpacity: 0.92,
            legendStroke: '#5f5f5f',
            legendStrokeOpacity: 0.8,
            legendText: '#111111',
        };
    }
    return {
        background: '#000000',
        minorGrid: '#1a1a1a',
        majorGrid: '#2a2a2a',
        frame: '#666666',
        labels: '#8a8a8a',
        brand: '#7c7c7c',
        legendFill: '#0c0c0c',
        legendFillOpacity: 0.78,
        legendStroke: '#a0a0a0',
        legendStrokeOpacity: 0.4,
        legendText: '#dcdcdc',
    };
}

function legendEntries(channels) {
    return channels.map(function(ch) {
        return {
            color: ch.color,
            lineDash: traceDashArray(ch),
            lineCap: traceLineCap(ch),
            label: ch.legendLabel || ch.displayName || ch.name,
        };
    });
}

function drawLegendCanvas(ctx, channels, plotX, plotY) {
    if (!showLegend || !channels.length) {
        return;
    }

    var entries = legendEntries(channels);
    var theme = currentPlotTheme();
    var fontPx = 14;
    var lineHeight = 18;
    var swatchWidth = 22;
    var padX = 10;
    var padY = 8;
    var gap = 8;
    var maxLabelWidth = 0;

    ctx.save();
    ctx.font = fontPx + 'px monospace';
    entries.forEach(function(entry) {
        maxLabelWidth = Math.max(maxLabelWidth, ctx.measureText(entry.label).width);
    });

    var boxWidth = padX * 2 + swatchWidth + gap + maxLabelWidth;
    var boxHeight = padY * 2 + entries.length * lineHeight;
    var boxX = plotX + 10;
    var boxY = plotY + 10;

    ctx.fillStyle = theme.legendFill;
    ctx.globalAlpha = theme.legendFillOpacity;
    ctx.strokeStyle = theme.legendStroke;
    ctx.globalAlpha = 1;
    ctx.lineWidth = 1;
    ctx.fillRect(boxX, boxY, boxWidth, boxHeight);
    ctx.globalAlpha = theme.legendStrokeOpacity;
    ctx.strokeRect(boxX + 0.5, boxY + 0.5, boxWidth - 1, boxHeight - 1);
    ctx.globalAlpha = 1;

    ctx.textAlign = 'left';
    ctx.textBaseline = 'middle';
    entries.forEach(function(entry, index) {
        var y = boxY + padY + index * lineHeight + lineHeight / 2;
        ctx.strokeStyle = entry.color;
        ctx.lineWidth = 2;
        ctx.lineCap = entry.lineCap;
        ctx.setLineDash(entry.lineDash);
        ctx.beginPath();
        ctx.moveTo(boxX + padX, y);
        ctx.lineTo(boxX + padX + swatchWidth, y);
        ctx.stroke();
        ctx.fillStyle = theme.legendText;
        ctx.fillText(entry.label, boxX + padX + swatchWidth + gap, y);
    });
    ctx.restore();
}

function drawLegendSvg(channels, plotX, plotY, fx, esc) {
    if (!showLegend || !channels.length) {
        return [];
    }

    var entries = legendEntries(channels);
    var theme = currentPlotTheme();
    var fontPx = 14;
    var lineHeight = 18;
    var swatchWidth = 22;
    var padX = 10;
    var padY = 8;
    var maxLabelChars = 0;
    var out = [];

    entries.forEach(function(entry) {
        maxLabelChars = Math.max(maxLabelChars, entry.label.length);
    });

    var approxCharWidth = fontPx * 0.62;
    var boxWidth = padX * 2 + swatchWidth + 8 + maxLabelChars * approxCharWidth;
    var boxHeight = padY * 2 + entries.length * lineHeight;
    var boxX = plotX + 10;
    var boxY = plotY + 10;

    out.push('<g class="legend">');
    out.push('<rect x="' + fx(boxX) + '" y="' + fx(boxY) + '" width="' + fx(boxWidth) + '" height="' + fx(boxHeight) + '" fill="' + theme.legendFill + '" fill-opacity="' + theme.legendFillOpacity + '" stroke="' + theme.legendStroke + '" stroke-opacity="' + theme.legendStrokeOpacity + '" stroke-width="1"/>');
    entries.forEach(function(entry, index) {
        var y = boxY + padY + index * lineHeight + lineHeight / 2;
        out.push('<line x1="' + fx(boxX + padX) + '" y1="' + fx(y) + '" x2="' + fx(boxX + padX + swatchWidth) + '" y2="' + fx(y) + '" stroke="' + esc(entry.color) + '" stroke-width="2" stroke-linecap="' + entry.lineCap + '"' + (traceSvgDash(entry) ? ' stroke-dasharray="' + traceSvgDash(entry) + '"' : '') + '/>');
        out.push('<text x="' + fx(boxX + padX + swatchWidth + 8) + '" y="' + fx(y) + '" fill="' + theme.legendText + '" text-anchor="start" dominant-baseline="middle" font-size="' + fontPx + 'px">' + esc(entry.label) + '</text>');
    });
    out.push('</g>');
    return out;
}

function buildDisplayedTimeTicks(ticks, skip) {
    var displayed = [];
    ticks.forEach(function(tick, index) {
        if (index % skip === 0) {
            displayed.push(tick);
        }
    });
    if (ticks.length) {
        var lastTick = ticks[ticks.length - 1];
        if (!displayed.length || !numbersAreClose(displayed[displayed.length - 1], lastTick)) {
            displayed.push(lastTick);
        }
    }
    return displayed;
}

function clampCanvasLabelX(ctx, x, text, width) {
    var halfWidth = ctx.measureText(text).width / 2;
    return Math.min(Math.max(x, halfWidth + 4), width - halfWidth - 4);
}

function clampSvgLabelX(x, text, width) {
    var halfWidth = text.length * FONT_PX * 0.3;
    return Math.min(Math.max(x, halfWidth + 4), width - halfWidth - 4);
}

function formatAxisInputValue(value, unit) {
    if (!Number.isFinite(value)) {
        return '';
    }
    if (value === 0) {
        return '0' + unit;
    }
    var abs = Math.abs(value);
    var exponent = Math.floor(Math.log10(abs) / 3) * 3;
    if (exponent < -12 || exponent > 12) {
        return value.toExponential(6) + unit;
    }
    var suffixes = {
        '-12': 'p',
        '-9': 'n',
        '-6': '\u00b5',
        '-3': 'm',
        '0': '',
        '3': 'k',
        '6': 'M',
        '9': 'G',
        '12': 'T',
    };
    var scaled = value / Math.pow(10, exponent);
    var text = Number(scaled.toPrecision(6));
    if (Math.abs(text) >= 1000 && exponent < 12) {
        exponent += 3;
        text /= 1000;
    }
    return text.toString() + suffixes[String(exponent)] + unit;
}

function stripAxisInputUnit(text, unit) {
    var value = String(text || '').trim();
    if (!value) {
        return value;
    }

    if (unit === 's') {
        return value.replace(/\s*(?:s|sec|second|seconds)\s*$/i, '');
    }
    if (unit === 'V') {
        return value.replace(/\s*(?:v|volt|volts)\s*$/i, '');
    }
    return value;
}

function parseAxisInputValue(text, unit) {
    var value = String(text || '').trim();
    if (!value) {
        return NaN;
    }
    value = stripAxisInputUnit(value, unit);

    var direct = Number(value);
    if (Number.isFinite(direct)) {
        return direct;
    }

    var match = value.match(/^([+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?)\s*([pnumkKMGT]|[u\u00b5\u03bc])?$/);
    if (!match) {
        return NaN;
    }

    var base = Number(match[1]);
    if (!Number.isFinite(base)) {
        return NaN;
    }

    var suffix = match[2];
    var scale = 1;
    switch (suffix) {
    case 'p':
        scale = 1e-12;
        break;
    case 'n':
        scale = 1e-9;
        break;
    case 'u':
    case '\u00b5':
    case '\u03bc':
        scale = 1e-6;
        break;
    case 'm':
        scale = 1e-3;
        break;
    case 'k':
    case 'K':
        scale = 1e3;
        break;
    case 'M':
        scale = 1e6;
        break;
    case 'G':
        scale = 1e9;
        break;
    case 'T':
        scale = 1e12;
        break;
    default:
        return NaN;
    }

    return base * scale;
}

function syncAxisInputs(bounds, enabled) {
    [axisTminInput, axisTmaxInput, axisVminInput, axisVmaxInput].forEach(function(input) {
        input.disabled = !enabled;
    });
    axisResetBtn.disabled = !enabled;

    if (!bounds) {
        axisTminInput.value = '';
        axisTmaxInput.value = '';
        axisVminInput.value = '';
        axisVmaxInput.value = '';
        return;
    }

    axisTminInput.value = formatAxisInputValue(bounds.tMin, 's');
    axisTmaxInput.value = formatAxisInputValue(bounds.tMax, 's');
    axisVminInput.value = formatAxisInputValue(bounds.vMin, 'V');
    axisVmaxInput.value = formatAxisInputValue(bounds.vMax, 'V');
}

function render(result) {
    var canvas = document.getElementById('scope');
    var W = canvas.offsetWidth || 800;
    var H = canvas.offsetHeight || 480;
    canvas.width = W;
    canvas.height = H;

    var ctx = canvas.getContext('2d');
    var ml = M.l;
    var mr = M.r;
    var mt = M.t;
    var mb = M.b;
    var pw = W - ml - mr;
    var ph = H - mt - mb;
    var bounds = result.bounds || resolveGraphBounds(result.channels);
    var tAx = bounds.tAx;
    var vAx = bounds.vAx;
    var tMinorTicks = buildAxisTickValues(tAx, 5);
    var vMinorTicks = buildAxisTickValues(vAx, 5);
    var tMajorTicks = buildAxisTickValues(tAx, 1);
    var vMajorTicks = buildAxisTickValues(vAx, 1);
    var tLabelFormatter = createAxisLabelFormatter(tAx, 's');
    var vLabelFormatter = createAxisLabelFormatter(vAx, 'V');
    var tAxisTitle = axisTitleText('Time', tLabelFormatter);
    var vAxisTitle = axisTitleText('Voltage', vLabelFormatter);
    var theme = currentPlotTheme();

    function xOf(t) {
        return ml + (t - tAx.min) / (tAx.max - tAx.min) * pw;
    }

    function yOf(v) {
        return mt + (vAx.max - v) / (vAx.max - vAx.min) * ph;
    }

    ctx.fillStyle = theme.background;
    ctx.fillRect(0, 0, W, H);

    function vline(x) {
        var cx = Math.round(x) + 0.5;
        ctx.beginPath();
        ctx.moveTo(cx, mt);
        ctx.lineTo(cx, mt + ph);
        ctx.stroke();
    }

    function hline(y) {
        var cy = Math.round(y) + 0.5;
        ctx.beginPath();
        ctx.moveTo(ml, cy);
        ctx.lineTo(ml + pw, cy);
        ctx.stroke();
    }

    if (showFineGrid) {
        ctx.lineWidth = 0.5;
        ctx.strokeStyle = theme.minorGrid;
        tMinorTicks.forEach(function(tick) {
            vline(xOf(tick));
        });
        vMinorTicks.forEach(function(tick) {
            hline(yOf(tick));
        });
    }

    ctx.lineWidth = 1;
    ctx.strokeStyle = theme.majorGrid;
    tMajorTicks.forEach(function(tick) {
        vline(xOf(tick));
    });
    vMajorTicks.forEach(function(tick) {
        hline(yOf(tick));
    });

    ctx.lineWidth = 1;
    ctx.strokeStyle = theme.frame;
    ctx.strokeRect(ml + 0.5, mt + 0.5, pw, ph);

    ctx.fillStyle = theme.labels;
    ctx.font = FONT_PX + 'px monospace';
    ctx.textAlign = 'right';
    ctx.textBaseline = 'middle';
    vMajorTicks.forEach(function(v) {
        var y = yOf(v);
        if (y >= mt - 2 && y <= mt + ph + 2) {
            var yLabel = vLabelFormatter.formatNumber(v);
            ctx.fillText(yLabel, ml - 6, y);
        }
    });

    ctx.textAlign = 'center';
    ctx.textBaseline = 'top';
    var tPixPerDiv = pw * tAx.step / (tAx.max - tAx.min);
    var tLabelSkip = Math.max(1, Math.ceil(FONT_PX * 7 / Math.max(tPixPerDiv, 1)));
    var tDisplayedTicks = buildDisplayedTimeTicks(tMajorTicks, tLabelSkip);
    tDisplayedTicks.forEach(function(tick) {
        var tLabel = tLabelFormatter.formatNumber(tick);
        var labelX = clampCanvasLabelX(ctx, xOf(tick), tLabel, W);
        ctx.fillText(tLabel, labelX, mt + ph + 6);
    });

    ctx.fillStyle = theme.labels;
    ctx.font = FONT_PX + 'px monospace';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'top';
    ctx.fillText(tAxisTitle, ml + pw / 2, H - 24);

    ctx.save();
    ctx.translate(28, mt + ph / 2);
    ctx.rotate(-Math.PI / 2);
    ctx.textAlign = 'center';
    ctx.textBaseline = 'top';
    ctx.fillText(vAxisTitle, 0, 0);
    ctx.restore();

    var maxPts = pw * 2;
    ctx.save();
    ctx.beginPath();
    ctx.rect(ml, mt, pw, ph);
    ctx.clip();
    result.channels.forEach(function(ch) {
        var count = ch.times.length;
        if (!count) {
            return;
        }
        ctx.strokeStyle = ch.color;
        ctx.lineWidth = 1.5;
        ctx.lineCap = traceLineCap(ch);
        ctx.lineJoin = 'round';
        ctx.setLineDash(traceDashArray(ch));
        ctx.beginPath();
        var skip = Math.max(1, Math.floor(count / maxPts));
        var first = true;
        for (var i = 0; i < count; i += skip) {
            var px = xOf(ch.times[i]);
            var py = yOf(ch.volts[i]);
            if (first) {
                ctx.moveTo(px, py);
                first = false;
            } else {
                ctx.lineTo(px, py);
            }
        }
        ctx.stroke();
    });
    ctx.restore();

    drawLegendCanvas(ctx, result.channels, ml, mt);

    ctx.fillStyle = theme.brand;
    ctx.font = '14px monospace';
    ctx.textAlign = 'right';
    ctx.textBaseline = 'top';
    ctx.fillText(GRAPH_BRAND, ml + pw - 8, mt + 6);

}

function renderToSVG(result) {
    var W = 1200;
    var H = 700;
    var ml = M.l;
    var mr = M.r;
    var mt = M.t;
    var mb = M.b;
    var pw = W - ml - mr;
    var ph = H - mt - mb;
    var bounds = result.bounds || resolveGraphBounds(result.channels);
    var tAx = bounds.tAx;
    var vAx = bounds.vAx;
    var tMinorTicks = buildAxisTickValues(tAx, 5);
    var vMinorTicks = buildAxisTickValues(vAx, 5);
    var tMajorTicks = buildAxisTickValues(tAx, 1);
    var vMajorTicks = buildAxisTickValues(vAx, 1);
    var tLabelFormatter = createAxisLabelFormatter(tAx, 's');
    var vLabelFormatter = createAxisLabelFormatter(vAx, 'V');
    var tAxisTitle = axisTitleText('Time', tLabelFormatter);
    var vAxisTitle = axisTitleText('Voltage', vLabelFormatter);
    var theme = currentPlotTheme();

    function xOf(t) {
        return ml + (t - tAx.min) / (tAx.max - tAx.min) * pw;
    }

    function yOf(v) {
        return mt + (vAx.max - v) / (vAx.max - vAx.min) * ph;
    }

    function fx(n) {
        return n.toFixed(2);
    }

    function esc(s) {
        return String(s)
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;');
    }

    var o = [];
    o.push('<?xml version="1.0" encoding="UTF-8"?>');
    o.push('<svg xmlns="http://www.w3.org/2000/svg" width="' + W + '" height="' + H + '" font-family="monospace" font-size="' + FONT_PX + 'px">');
    o.push('<rect width="100%" height="100%" fill="' + theme.background + '"/>');
    o.push('<defs><clipPath id="plot-clip"><rect x="' + ml + '" y="' + mt + '" width="' + pw + '" height="' + ph + '"/></clipPath></defs>');

    if (showFineGrid) {
        tMinorTicks.forEach(function(tick) {
            var x = xOf(tick);
            o.push('<line x1="' + fx(x) + '" y1="' + mt + '" x2="' + fx(x) + '" y2="' + (mt + ph) + '" stroke="' + theme.minorGrid + '" stroke-width="0.5"/>');
        });
        vMinorTicks.forEach(function(tick) {
            var y = yOf(tick);
            o.push('<line x1="' + ml + '" y1="' + fx(y) + '" x2="' + (ml + pw) + '" y2="' + fx(y) + '" stroke="' + theme.minorGrid + '" stroke-width="0.5"/>');
        });
    }
    tMajorTicks.forEach(function(tick) {
        var majorX = xOf(tick);
        o.push('<line x1="' + fx(majorX) + '" y1="' + mt + '" x2="' + fx(majorX) + '" y2="' + (mt + ph) + '" stroke="' + theme.majorGrid + '" stroke-width="1"/>');
    });
    vMajorTicks.forEach(function(tick) {
        var majorY = yOf(tick);
        o.push('<line x1="' + ml + '" y1="' + fx(majorY) + '" x2="' + (ml + pw) + '" y2="' + fx(majorY) + '" stroke="' + theme.majorGrid + '" stroke-width="1"/>');
    });
    o.push('<rect x="' + (ml + 0.5) + '" y="' + (mt + 0.5) + '" width="' + pw + '" height="' + ph + '" fill="none" stroke="' + theme.frame + '" stroke-width="1"/>');

    vMajorTicks.forEach(function(v) {
        var labelY = yOf(v);
        if (labelY >= mt - 2 && labelY <= mt + ph + 2) {
            var yLabel = vLabelFormatter.formatNumber(v);
            o.push('<text x="' + (ml - 6) + '" y="' + fx(labelY) + '" fill="' + theme.labels + '" text-anchor="end" dominant-baseline="middle">' + esc(yLabel) + '</text>');
        }
    });

    var tPixPerDiv = pw * tAx.step / (tAx.max - tAx.min);
    var tLabelSkip = Math.max(1, Math.ceil(FONT_PX * 7 / Math.max(tPixPerDiv, 1)));
    var tDisplayedTicks = buildDisplayedTimeTicks(tMajorTicks, tLabelSkip);
    tDisplayedTicks.forEach(function(tick) {
        var tLabel = tLabelFormatter.formatNumber(tick);
        var labelX = clampSvgLabelX(xOf(tick), tLabel, W);
        o.push('<text x="' + fx(labelX) + '" y="' + (mt + ph + 6 + FONT_PX) + '" fill="' + theme.labels + '" text-anchor="middle">' + esc(tLabel) + '</text>');
    });

    o.push('<text x="' + fx(ml + pw / 2) + '" y="' + fx(H - 24 + FONT_PX) + '" fill="' + theme.labels + '" text-anchor="middle" font-size="' + FONT_PX + 'px">' + esc(tAxisTitle) + '</text>');
    o.push('<text x="28" y="' + fx(mt + ph / 2) + '" fill="' + theme.labels + '" text-anchor="middle" dominant-baseline="hanging" font-size="' + FONT_PX + 'px" transform="rotate(-90 28 ' + fx(mt + ph / 2) + ')">' + esc(vAxisTitle) + '</text>');

    var maxPts = pw * 2;
    o.push('<g clip-path="url(#plot-clip)">');
    result.channels.forEach(function(ch) {
        var count = ch.times.length;
        if (!count) {
            return;
        }
        var skip = Math.max(1, Math.floor(count / maxPts));
        var pts = [];
        for (var i = 0; i < count; i += skip) {
            pts.push(fx(xOf(ch.times[i])) + ',' + fx(yOf(ch.volts[i])));
        }
        o.push('<polyline points="' + pts.join(' ') + '" fill="none" stroke="' + ch.color + '" stroke-width="1.5" stroke-linecap="' + traceLineCap(ch) + '" stroke-linejoin="round"' + (traceSvgDash(ch) ? ' stroke-dasharray="' + traceSvgDash(ch) + '"' : '') + '/>');
    });
    o.push('</g>');
    drawLegendSvg(result.channels, ml, mt, fx, esc).forEach(function(item) {
        o.push(item);
    });
    o.push('<text x="' + fx(ml + pw - 8) + '" y="' + fx(mt + 20) + '" fill="' + theme.brand + '" text-anchor="end" font-size="14px">' + esc(GRAPH_BRAND) + '</text>');

    o.push('</svg>');
    return o.join('\n');
}

function bestScaleJS(number) {
    var abs = Math.abs(number);
    if (abs === 0) {
        return [1, ''];
    }
    if (abs < 9.9999999e-10) {
        return [1e12, 'p'];
    }
    if (abs < 9.9999999e-7) {
        return [1e9, 'n'];
    }
    if (abs < 9.9999999e-4) {
        return [1e6, '\u00b5'];
    }
    if (abs < 9.9999999e-1) {
        return [1e3, 'm'];
    }
    if (abs < 9.9999999e2) {
        return [1, ''];
    }
    if (abs < 9.9999999e5) {
        return [1e-3, 'k'];
    }
    return [1e-9, 'G'];
}

function triggerDownload(data, filename, mime) {
    var blob = new Blob([data], { type: mime });
    var url = URL.createObjectURL(blob);
    var a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    setTimeout(function() {
        URL.revokeObjectURL(url);
    }, 1000);
}

function doExportCSV() {
    var active = getActiveEntry();
    var chs = getVisibleChannelsForEntry(active);
    if (!chs.length) {
        return;
    }
    var hScale = 1e-30;
    var hPrefix = '';
    var vScale = 1e-30;
    var vPrefix = '';
    chs.forEach(function(ch) {
        var hs = bestScaleJS(ch.timeScale);
        var vs = bestScaleJS(ch.voltPerDiv);
        if (hs[0] > hScale) {
            hScale = hs[0];
            hPrefix = hs[1];
        }
        if (vs[0] > vScale) {
            vScale = vs[0];
            vPrefix = vs[1];
        }
    });
    var ch0 = chs[0];
    var npts = Math.min.apply(null, chs.map(function(c) {
        return c.times.length;
    }));
    var incr = ch0.timeScale / 100;
    var off = -6 * ch0.timeScale;
    var rows = [];
    rows.push('X,' + chs.map(function(c) {
        return c.name;
    }).join(',') + ',Start,Increment');
    rows.push(
        hPrefix + 's,' +
        chs.map(function() {
            return vPrefix + 'V';
        }).join(',') +
        ',' + off.toExponential() +
        ',' + incr.toExponential()
    );
    for (var i = 0; i < npts; i++) {
        var row = (ch0.times[i] * hScale).toFixed(6);
        chs.forEach(function(c) {
            row += ',' + (c.volts[i] * vScale).toFixed(2);
        });
        rows.push(row);
    }
    triggerDownload(rows.join('\n'), currentFilename + '.csv', 'text/csv');
}

function doExportInfo() {
    var active = getActiveEntry();
    if (!active) {
        return;
    }
    triggerDownload(buildInfoText(active.result, active.filename), currentFilename + '.txt', 'text/plain;charset=utf-8');
}

function doExportSigrok() {
    var active = getActiveEntry();
    var chs = getVisibleChannelsForEntry(active);
    if (!chs.length) {
        return;
    }
    var npts = Math.min.apply(null, chs.map(function(c) {
        return c.times.length;
    }));
    var rows = [];
    rows.push('X,' + chs.map(function(c) {
        return c.name + ' (V)';
    }).join(','));
    for (var i = 0; i < npts; i++) {
        var row = chs[0].times[i].toFixed(8);
        chs.forEach(function(c) {
            row += ',' + c.volts[i].toFixed(2);
        });
        rows.push(row);
    }
    triggerDownload(rows.join('\n'), currentFilename + '_sigrok.csv', 'text/csv');
}

function doExportWAV() {
    var active = getActiveEntry();
    var chs = getVisibleChannelsForEntry(active);
    if (!chs.length) {
        return;
    }
    var nch = chs.length;
    var npts = Math.min.apply(null, chs.map(function(c) {
        return c.times.length;
    }));
    if (!npts) {
        return;
    }
    var ch0 = chs[0];
    var spp = npts > 1 ? (ch0.times[npts - 1] - ch0.times[0]) / (npts - 1) : 1e-6;
    var maxU32 = 4294967295;
    var sampleRate = Math.min(Math.round(1 / spp), Math.floor(maxU32 / Math.max(nch, 1)));
    var scaled = chs.map(function(ch) {
        var vMin = Infinity;
        var vMax = -Infinity;
        for (var i = 0; i < npts; i++) {
            if (ch.volts[i] < vMin) {
                vMin = ch.volts[i];
            }
            if (ch.volts[i] > vMax) {
                vMax = ch.volts[i];
            }
        }
        var range = Math.max(vMax - vMin, 1e-30);
        var sc = 250 * 0.95 / range;
        var out = new Uint8Array(npts);
        for (var j = 0; j < npts; j++) {
            out[j] = Math.max(0, Math.min(255, Math.round((ch.volts[j] - vMin) * sc)));
        }
        return out;
    });
    var pcm = new Uint8Array(npts * nch);
    for (var ci = 0; ci < nch; ci++) {
        for (var k = 0; k < npts; k++) {
            pcm[k * nch + ci] = scaled[ci][k];
        }
    }
    var buf = new ArrayBuffer(44 + pcm.length);
    var dv = new DataView(buf);

    function wStr(off, s) {
        for (var i = 0; i < s.length; i++) {
            dv.setUint8(off + i, s.charCodeAt(i));
        }
    }

    wStr(0, 'RIFF');
    dv.setUint32(4, 36 + pcm.length, true);
    wStr(8, 'WAVE');
    wStr(12, 'fmt ');
    dv.setUint32(16, 16, true);
    dv.setUint16(20, 1, true);
    dv.setUint16(22, nch, true);
    dv.setUint32(24, sampleRate, true);
    dv.setUint32(28, sampleRate * nch, true);
    dv.setUint16(32, nch, true);
    dv.setUint16(34, 8, true);
    wStr(36, 'data');
    dv.setUint32(40, pcm.length, true);
    new Uint8Array(buf, 44).set(pcm);
    triggerDownload(buf, currentFilename + '.wav', 'audio/wav');
}

function doExportPNG() {
    var chs = getVisibleChannels();
    if (!chs.length) {
        return;
    }
    var cv = document.getElementById('scope');
    var url = cv.toDataURL('image/png');
    var a = document.createElement('a');
    a.href = url;
    a.download = currentFilename + '.png';
    a.click();
}

function doExportSVG() {
    var active = getActiveEntry();
    var chs = getVisibleChannels();
    if (!chs.length || !active) {
        return;
    }
    var svgStr = renderToSVG({
        format: active.result.format,
        formatLabel: currentFormatLabel(),
        bounds: currentGraphBounds,
        channels: chs,
    });
    triggerDownload(svgStr, currentFilename + '.svg', 'image/svg+xml');
}

var loadedFiles = [];
var activeFileId = null;
var nextFileId = 1;
var nextTraceColorIndex = 0;
var graphAxisModes = { t: 'auto', v: 'auto' };
var graphManualBounds = {
    tMin: NaN,
    tMax: NaN,
    vMin: NaN,
    vMax: NaN,
};
var currentGraphBounds = null;
var currentFilename = 'waveform';
var currentSourceFilename = 'waveform.wfm';
var zoomSelection = null;
var showLegend = false;
var showFineGrid = true;
var lightMode = false;

function resetGraphAxisState() {
    graphAxisModes.t = 'auto';
    graphAxisModes.v = 'auto';
    graphManualBounds.tMin = NaN;
    graphManualBounds.tMax = NaN;
    graphManualBounds.vMin = NaN;
    graphManualBounds.vMax = NaN;
}

function escapeHtml(value) {
    return String(value)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;');
}

function stemForFilename(filename) {
    return filename.replace(/\.[^.]+$/, '') || filename;
}

function traceAppearanceForIndex(index) {
    var paletteLength = TRACE_BASE_PALETTE.length;
    var styleIndex = Math.floor(index / paletteLength);
    var colorIndex = index % paletteLength;
    var style = TRACE_STYLE_CYCLE[styleIndex % TRACE_STYLE_CYCLE.length];
    var color = styleIndex < TRACE_STYLE_CYCLE.length ?
        TRACE_BASE_PALETTE[colorIndex] :
        hslToHex((index - paletteLength * TRACE_STYLE_CYCLE.length) * 137.508, 82, 60);

    return {
        color: color,
        lineStyle: style.id,
        lineDash: style.dash.slice(),
        lineCap: style.cap,
    };
}

function allocateTraceAppearance() {
    return traceAppearanceForIndex(nextTraceColorIndex++);
}

function traceDashArray(channel) {
    if (Array.isArray(channel && channel.lineDash)) {
        return channel.lineDash;
    }
    return [];
}

function traceLineCap(channel) {
    return channel && channel.lineCap ? channel.lineCap : 'round';
}

function traceSvgDash(channel) {
    var dash = traceDashArray(channel);
    return dash.length ? dash.join(' ') : '';
}

function normalizeColor(color, fallback) {
    return /^#[0-9a-f]{6}$/i.test(color || '') ? String(color).toLowerCase() : fallback;
}

function plural(word, count) {
    return count === 1 ? word : word + 's';
}

function triggerSummaryText(triggerInfo) {
    if (!triggerInfo) {
        return '';
    }
    var parts = [];
    if (triggerInfo.source) {
        parts.push(triggerInfo.source);
    }
    if (typeof triggerInfo.level === 'number') {
        parts.push(compactEngineeringValue(triggerInfo.level, 'V'));
    }
    return parts.join(' ');
}

function triggerSummary(entry) {
    var info = entry.result.triggerInfo;
    var unknownLabel = /\.wfm$/i.test(entry.filename) ? 'Unknown' : 'Not available';
    if (!info) {
        return unknownLabel;
    }
    if (info.mode === 'alt') {
        var altParts = [];
        if (info.trigger1) {
            altParts.push(triggerSummaryText(info.trigger1) || 'Unknown');
        }
        if (info.trigger2) {
            altParts.push(triggerSummaryText(info.trigger2) || 'Unknown');
        }
        return altParts.join(' | ') || unknownLabel;
    }
    return triggerSummaryText(info) || unknownLabel;
}

function findLoadedFile(fileId) {
    for (var i = 0; i < loadedFiles.length; i++) {
        if (loadedFiles[i].id === fileId) {
            return loadedFiles[i];
        }
    }
    return null;
}

function getActiveEntry() {
    if (!loadedFiles.length) {
        return null;
    }
    for (var i = 0; i < loadedFiles.length; i++) {
        if (loadedFiles[i].id === activeFileId) {
            return loadedFiles[i];
        }
    }
    return loadedFiles[0];
}

function syncCurrentFileContext() {
    var active = getActiveEntry();
    if (!active) {
        currentFilename = 'waveform';
        currentSourceFilename = 'waveform.wfm';
        return;
    }
    activeFileId = active.id;
    currentFilename = active.stem;
    currentSourceFilename = active.filename;
}

function channelSeriesName(entry, ch) {
    if (loadedFiles.length === 1) {
        return ch.name;
    }
    return ch.name + ' \u00b7 ' + entry.filename;
}

function getVisibleChannelsForEntry(entry) {
    if (!entry) {
        return [];
    }
    return entry.result.channels.filter(function(_, idx) {
        return entry.channelEnabled[idx];
    }).map(function(ch) {
        return Object.assign({}, ch);
    });
}

function getVisibleChannels() {
    var visible = [];
    loadedFiles.forEach(function(entry) {
        getVisibleChannelsForEntry(entry).forEach(function(ch) {
            var legendLabel = entry.stem + ' ' + ch.name;
            var seriesName = channelSeriesName(entry, ch);
            ch.name = seriesName;
            ch.displayName = seriesName;
            ch.legendLabel = legendLabel;
            visible.push(ch);
        });
    });
    return visible;
}

function currentFormatLabel() {
    if (!loadedFiles.length) {
        return '';
    }
    if (loadedFiles.length === 1) {
        var active = getActiveEntry();
        return active ? active.result.format : '';
    }
    return loadedFiles.length + ' ' + plural('file', loadedFiles.length);
}

function clearCanvas() {
    var cv = document.getElementById('scope');
    var width = cv.offsetWidth || cv.width || 800;
    var height = cv.offsetHeight || cv.height || 480;
    cv.width = width;
    cv.height = height;
    var ctx = cv.getContext('2d');
    ctx.fillStyle = currentPlotTheme().background;
    ctx.fillRect(0, 0, width, height);
}

function updateStatus() {
}

function renderFileList() {
    if (!loadedFiles.length) {
        fileList.innerHTML = '';
        return;
    }

    fileList.innerHTML = loadedFiles.map(function(entry) {
        return '<div class="file-card" data-file-id="' + entry.id + '">' +
            '<div class="file-card-header">' +
            '<div class="file-card-name" data-file-id="' + entry.id + '">' + escapeHtml(entry.filename) + '</div>' +
            '<button type="button" class="file-card-close" data-file-id="' + entry.id + '" aria-label="Remove ' + escapeHtml(entry.filename) + '">&times;</button>' +
            '</div>' +
            '<div class="file-card-body" data-file-id="' + entry.id + '">' +
            '<div class="file-card-line"><span class="file-card-label">Format</span><span class="file-card-value">' + escapeHtml(entry.result.format) + '</span></div>' +
            '<div class="file-card-channels">' +
            entry.result.channels.map(function(ch, idx) {
                var toggleId = 'file-channel-' + entry.id + '-' + idx;
                var colorValue = normalizeColor(ch.color, '#ffffff');
                return '<div class="file-channel' + (entry.channelEnabled[idx] ? '' : ' ch-off') + '" data-file-id="' + entry.id + '" data-channel-index="' + idx + '">' +
                    '<input type="checkbox" class="file-channel-toggle" id="' + toggleId + '" data-file-id="' + entry.id + '" data-channel-index="' + idx + '"' + (entry.channelEnabled[idx] ? ' checked' : '') + '>' +
                    '<input type="color" class="file-color-input" data-file-id="' + entry.id + '" data-channel-index="' + idx + '" value="' + colorValue + '" aria-label="Choose color for ' + escapeHtml(ch.name) + '" title="Choose color for ' + escapeHtml(ch.name) + '">' +
                    '<label class="file-channel-chip" for="' + toggleId + '" data-file-id="' + entry.id + '" data-channel-index="' + idx + '">' + escapeHtml(ch.name) + '</label>' +
                    '</div>';
            }).join('') +
            '</div>' +
            '</div>' +
            '</div>';
    }).join('');
}

function refreshView(extraMessage) {
    hideChannelTooltip();
    cancelZoomSelection();
    syncCurrentFileContext();
    renderFileList();
    filesPanel.classList.toggle('visible', loadedFiles.length > 0);
    exportBtn.disabled = !loadedFiles.length;
    updateStatus(extraMessage);

    if (!loadedFiles.length) {
        resetGraphAxisState();
        currentGraphBounds = null;
        dropZone.classList.remove('hidden');
        scopeCanvas.classList.remove('visible');
        hideError();
        syncAxisInputs(null, false);
        clearCanvas();
        return;
    }

    dropZone.classList.add('hidden');
    scopeCanvas.classList.add('visible');

    var visible = getVisibleChannels();
    if (!visible.length) {
        currentGraphBounds = null;
        hideError();
        syncAxisInputs(null, false);
        clearCanvas();
        return;
    }

    hideError();
    currentGraphBounds = resolveGraphBounds(visible);
    syncAxisInputs(currentGraphBounds, true);
    render({
        format: currentSourceFilename,
        formatLabel: currentFormatLabel(),
        bounds: currentGraphBounds,
        channels: visible,
    });
}

function setActiveFile(fileId) {
    if (activeFileId === fileId) {
        return;
    }
    activeFileId = fileId;
    syncCurrentFileContext();
}

function removeLoadedFile(fileId) {
    var index = -1;
    for (var i = 0; i < loadedFiles.length; i++) {
        if (loadedFiles[i].id === fileId) {
            index = i;
            break;
        }
    }
    if (index < 0) {
        return;
    }

    loadedFiles.splice(index, 1);
    if (!loadedFiles.length) {
        nextTraceColorIndex = 0;
    }
    if (activeFileId === fileId) {
        if (loadedFiles[index]) {
            activeFileId = loadedFiles[index].id;
        } else if (loadedFiles[index - 1]) {
            activeFileId = loadedFiles[index - 1].id;
        } else {
            activeFileId = null;
        }
    }
    refreshView();
}

var dropZone = document.getElementById('drop-zone');
var scopeCanvas = document.getElementById('scope');
var zoomRect = document.getElementById('zoom-rect');
var errorBox = document.getElementById('error-box');
var errorBoxClose = document.getElementById('error-box-close');
var errorBoxMessage = document.getElementById('error-box-message');
var mainContainer = document.getElementById('main-container');
var displayArea = document.getElementById('display-area');
var axisTminInput = document.getElementById('axis-tmin');
var axisTmaxInput = document.getElementById('axis-tmax');
var axisVminInput = document.getElementById('axis-vmin');
var axisVmaxInput = document.getElementById('axis-vmax');
var showLegendToggle = document.getElementById('show-legend-toggle');
var showFineGridToggle = document.getElementById('show-fine-grid-toggle');
var lightModeToggle = document.getElementById('light-mode-toggle');
var axisResetBtn = document.getElementById('axis-reset-btn');
var filesPanel = document.getElementById('files-panel');
var fileList = document.getElementById('file-list');
var dragOverlay = document.getElementById('drag-overlay');
var channelTooltip = document.getElementById('channel-tooltip');
var channelTooltipText = document.getElementById('channel-tooltip-text');
var exportModal = document.getElementById('export-modal');
var exportBtn = document.getElementById('export-btn');
var dragDepth = 0;
showLegend = showLegendToggle.checked;
showFineGrid = showFineGridToggle.checked;
lightMode = lightModeToggle.checked;
document.body.classList.toggle('light-mode', lightMode);

function hideChannelTooltip() {
    channelTooltip.classList.remove('visible');
    channelTooltip.classList.remove('file-tooltip');
    channelTooltip.style.left = '';
    channelTooltip.style.top = '';
    channelTooltip.style.visibility = '';
}

function showSidebarTooltip(text, anchorEl, isFileTooltip) {
    if (!text || !anchorEl) {
        hideChannelTooltip();
        return;
    }

    channelTooltipText.textContent = text;
    channelTooltip.classList.toggle('file-tooltip', Boolean(isFileTooltip));
    channelTooltip.classList.add('visible');
    channelTooltip.style.visibility = 'hidden';

    var tooltipRect = channelTooltip.getBoundingClientRect();
    var graphRect = displayArea.getBoundingClientRect();
    var containerRect = mainContainer.getBoundingClientRect();
    var anchorRect = anchorEl.getBoundingClientRect();
    var minLeft = containerRect.left + 12;
    var maxLeft = Math.max(minLeft, containerRect.right - tooltipRect.width - 12);
    var minTop = Math.max(containerRect.top + 12, 12);
    var maxTop = Math.max(minTop, Math.min(containerRect.bottom - tooltipRect.height - 12, window.innerHeight - tooltipRect.height - 12));
    var preferredLeft = graphRect.left + (isFileTooltip ? 18 : -2);
    var left = Math.max(minLeft, Math.min(preferredLeft, maxLeft));
    var top = Math.min(Math.max(anchorRect.top - 8, minTop), maxTop);

    channelTooltip.style.left = Math.round(left) + 'px';
    channelTooltip.style.top = Math.round(top) + 'px';
    channelTooltip.style.visibility = 'visible';
}

function showChannelTooltip(fileId, channelIndex, anchorEl) {
    var entry = findLoadedFile(fileId);
    if (!entry || !entry.result.channels[channelIndex]) {
        hideChannelTooltip();
        return;
    }

    var channelBounds = entry.channelEnabled[channelIndex] ? currentGraphBounds : null;
    showSidebarTooltip(
        channelInfoText(entry.result.channels[channelIndex], summarizeChannelVoltages(entry.result.channels[channelIndex], channelBounds)),
        anchorEl,
        false
    );
}

function showFileInfoTooltip(fileId, anchorEl) {
    var entry = findLoadedFile(fileId);
    if (!entry) {
        hideChannelTooltip();
        return;
    }

    showSidebarTooltip(buildInfoHeaderText(entry.result, entry.filename).replace(/\s+$/, ''), anchorEl, true);
}

function clearDragState() {
    dragDepth = 0;
    dragOverlay.classList.remove('active');
    dropZone.classList.remove('drag-over');
}

function getPlotPixelRect() {
    var canvasRect = scopeCanvas.getBoundingClientRect();
    var width = canvasRect.width || scopeCanvas.clientWidth || scopeCanvas.width || 0;
    var height = canvasRect.height || scopeCanvas.clientHeight || scopeCanvas.height || 0;
    return {
        left: M.l,
        top: M.t,
        right: Math.max(M.l, width - M.r),
        bottom: Math.max(M.t, height - M.b),
    };
}

function canvasPointFromEvent(e) {
    var canvasRect = scopeCanvas.getBoundingClientRect();
    return {
        x: e.clientX - canvasRect.left,
        y: e.clientY - canvasRect.top,
    };
}

function pointInPlot(point, plotRect) {
    return point.x >= plotRect.left &&
        point.x <= plotRect.right &&
        point.y >= plotRect.top &&
        point.y <= plotRect.bottom;
}

function clampPointToPlot(point, plotRect) {
    return {
        x: Math.min(Math.max(point.x, plotRect.left), plotRect.right),
        y: Math.min(Math.max(point.y, plotRect.top), plotRect.bottom),
    };
}

function hideZoomRect() {
    zoomRect.classList.remove('visible');
    zoomRect.style.left = '';
    zoomRect.style.top = '';
    zoomRect.style.width = '';
    zoomRect.style.height = '';
}

function cancelZoomSelection() {
    zoomSelection = null;
    hideZoomRect();
}

function updateZoomRect() {
    if (!zoomSelection) {
        hideZoomRect();
        return;
    }

    var left = Math.min(zoomSelection.start.x, zoomSelection.current.x);
    var right = Math.max(zoomSelection.start.x, zoomSelection.current.x);
    var top = Math.min(zoomSelection.start.y, zoomSelection.current.y);
    var bottom = Math.max(zoomSelection.start.y, zoomSelection.current.y);

    zoomRect.style.left = Math.round(left) + 'px';
    zoomRect.style.top = Math.round(top) + 'px';
    zoomRect.style.width = Math.max(1, Math.round(right - left)) + 'px';
    zoomRect.style.height = Math.max(1, Math.round(bottom - top)) + 'px';
    zoomRect.classList.add('visible');
}

function selectionBoundsFromZoom(selection) {
    var plotWidth = selection.plotRect.right - selection.plotRect.left;
    var plotHeight = selection.plotRect.bottom - selection.plotRect.top;
    var x1 = Math.min(selection.start.x, selection.current.x);
    var x2 = Math.max(selection.start.x, selection.current.x);
    var y1 = Math.min(selection.start.y, selection.current.y);
    var y2 = Math.max(selection.start.y, selection.current.y);
    var bounds = selection.bounds;

    function tOf(x) {
        return bounds.tMin + (x - selection.plotRect.left) / plotWidth * (bounds.tMax - bounds.tMin);
    }

    function vOf(y) {
        return bounds.vMax - (y - selection.plotRect.top) / plotHeight * (bounds.vMax - bounds.vMin);
    }

    return {
        tMin: tOf(x1),
        tMax: tOf(x2),
        vMin: vOf(y2),
        vMax: vOf(y1),
    };
}

function beginZoomSelection(e) {
    if (e.button !== 0 || !currentGraphBounds || !scopeCanvas.classList.contains('visible')) {
        return;
    }

    var plotRect = getPlotPixelRect();
    var point = canvasPointFromEvent(e);
    if (!pointInPlot(point, plotRect)) {
        return;
    }

    hideChannelTooltip();
    zoomSelection = {
        bounds: currentGraphBounds,
        plotRect: plotRect,
        start: clampPointToPlot(point, plotRect),
        current: clampPointToPlot(point, plotRect),
    };
    updateZoomRect();
    e.preventDefault();
}

function updateZoomSelection(e) {
    if (!zoomSelection) {
        return;
    }

    zoomSelection.current = clampPointToPlot(canvasPointFromEvent(e), zoomSelection.plotRect);
    updateZoomRect();
    e.preventDefault();
}

function finishZoomSelection(e) {
    if (!zoomSelection) {
        return;
    }

    if (e) {
        zoomSelection.current = clampPointToPlot(canvasPointFromEvent(e), zoomSelection.plotRect);
    }

    var selection = zoomSelection;
    var width = Math.abs(selection.current.x - selection.start.x);
    var height = Math.abs(selection.current.y - selection.start.y);
    cancelZoomSelection();

    if (width < 6 || height < 6) {
        return;
    }

    var zoomBounds = selectionBoundsFromZoom(selection);
    if (!graphBoundsAreUsable(zoomBounds)) {
        return;
    }

    graphAxisModes.t = 'manual';
    graphAxisModes.v = 'manual';
    graphManualBounds.tMin = zoomBounds.tMin;
    graphManualBounds.tMax = zoomBounds.tMax;
    graphManualBounds.vMin = zoomBounds.vMin;
    graphManualBounds.vMax = zoomBounds.vMax;
    refreshView();
}

function hideError() {
    errorBox.classList.remove('visible');
    errorBox.setAttribute('aria-hidden', 'true');
}

function applyAxisInputs() {
    if (!currentGraphBounds) {
        return;
    }

    var bounds = {
        tMin: parseAxisInputValue(axisTminInput.value, 's'),
        tMax: parseAxisInputValue(axisTmaxInput.value, 's'),
        vMin: parseAxisInputValue(axisVminInput.value, 'V'),
        vMax: parseAxisInputValue(axisVmaxInput.value, 'V'),
    };

    if (!graphBoundsAreUsable(bounds)) {
        return;
    }

    if (graphAxisModes.t === 'manual' || !axisRangesMatch(bounds.tMin, bounds.tMax, currentGraphBounds.tMin, currentGraphBounds.tMax)) {
        graphAxisModes.t = 'manual';
        graphManualBounds.tMin = bounds.tMin;
        graphManualBounds.tMax = bounds.tMax;
    }

    if (graphAxisModes.v === 'manual' || !axisRangesMatch(bounds.vMin, bounds.vMax, currentGraphBounds.vMin, currentGraphBounds.vMax)) {
        graphAxisModes.v = 'manual';
        graphManualBounds.vMin = bounds.vMin;
        graphManualBounds.vMax = bounds.vMax;
    }

    refreshView();
}

function resetAxisView() {
    resetGraphAxisState();
    refreshView();
}

function openFilePicker() {
    var inp = document.createElement('input');
    inp.type = 'file';
    inp.accept = '.wfm,.bin';
    inp.multiple = true;
    inp.onchange = function(e) {
        loadFiles(e.target.files);
    };
    inp.click();
}

document.getElementById('open-btn').addEventListener('click', openFilePicker);
dropZone.addEventListener('click', openFilePicker);
dropZone.addEventListener('dragover', function(e) {
    e.preventDefault();
    dropZone.classList.add('drag-over');
});
dropZone.addEventListener('dragleave', function() {
    dropZone.classList.remove('drag-over');
});
dropZone.addEventListener('drop', function(e) {
    e.preventDefault();
    e.stopPropagation();
    clearDragState();
    loadFiles(e.dataTransfer.files);
});

document.addEventListener('dragenter', function(e) {
    if (e.dataTransfer && e.dataTransfer.types && Array.from(e.dataTransfer.types).indexOf('Files') >= 0) {
        dragDepth++;
        dragOverlay.classList.add('active');
    }
});
document.addEventListener('dragleave', function() {
    if (--dragDepth <= 0) {
        dragDepth = 0;
        dragOverlay.classList.remove('active');
    }
});
document.addEventListener('dragover', function(e) {
    e.preventDefault();
});
document.addEventListener('drop', function(e) {
    e.preventDefault();
    clearDragState();
    loadFiles(e.dataTransfer.files);
});
document.addEventListener('scroll', hideChannelTooltip, true);
document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') {
        cancelZoomSelection();
        hideError();
    }
});
window.addEventListener('blur', cancelZoomSelection);
scopeCanvas.addEventListener('mousedown', beginZoomSelection);
window.addEventListener('mousemove', updateZoomSelection);
window.addEventListener('mouseup', finishZoomSelection);

exportBtn.addEventListener('click', function() {
    exportModal.classList.add('open');
});
errorBoxClose.addEventListener('click', hideError);
document.getElementById('export-modal-close').addEventListener('click', function() {
    exportModal.classList.remove('open');
});
exportModal.addEventListener('click', function(e) {
    if (e.target === exportModal) {
        exportModal.classList.remove('open');
    }
});

document.getElementById('exp-csv').addEventListener('click', function() {
    doExportCSV();
    exportModal.classList.remove('open');
});
document.getElementById('exp-info').addEventListener('click', function() {
    doExportInfo();
    exportModal.classList.remove('open');
});
document.getElementById('exp-sigrok').addEventListener('click', function() {
    doExportSigrok();
    exportModal.classList.remove('open');
});
document.getElementById('exp-wav').addEventListener('click', function() {
    doExportWAV();
    exportModal.classList.remove('open');
});
document.getElementById('exp-png').addEventListener('click', function() {
    doExportPNG();
    exportModal.classList.remove('open');
});
document.getElementById('exp-svg').addEventListener('click', function() {
    doExportSVG();
    exportModal.classList.remove('open');
});

[axisTminInput, axisTmaxInput, axisVminInput, axisVmaxInput].forEach(function(input) {
    input.addEventListener('change', applyAxisInputs);
    input.addEventListener('keydown', function(e) {
        if (e.key === 'Enter') {
            e.preventDefault();
            applyAxisInputs();
        }
    });
});
axisResetBtn.addEventListener('click', resetAxisView);
showLegendToggle.addEventListener('change', function() {
    showLegend = showLegendToggle.checked;
    if (loadedFiles.length) {
        refreshView();
    }
});
showFineGridToggle.addEventListener('change', function() {
    showFineGrid = showFineGridToggle.checked;
    if (loadedFiles.length) {
        refreshView();
    }
});
lightModeToggle.addEventListener('change', function() {
    lightMode = lightModeToggle.checked;
    document.body.classList.toggle('light-mode', lightMode);
    refreshView();
});

fileList.addEventListener('click', function(e) {
    var closeBtn = e.target.closest('.file-card-close');
    if (closeBtn) {
        removeLoadedFile(Number(closeBtn.dataset.fileId));
        return;
    }

    var channelControl = e.target.closest('.file-channel');
    if (channelControl) {
        return;
    }

    var card = e.target.closest('.file-card');
    if (card) {
        setActiveFile(Number(card.dataset.fileId));
    }
});

fileList.addEventListener('mouseover', function(e) {
    var nameEl = e.target.closest('.file-card-name');
    if (nameEl) {
        showFileInfoTooltip(Number(nameEl.dataset.fileId), nameEl);
        return;
    }

    var chip = e.target.closest('.file-channel-chip');
    if (chip) {
        showChannelTooltip(Number(chip.dataset.fileId), Number(chip.dataset.channelIndex), chip);
    }
});

fileList.addEventListener('mouseout', function(e) {
    if (e.target.closest('.file-card-name') || e.target.closest('.file-channel-chip')) {
        hideChannelTooltip();
    }
});

fileList.addEventListener('mouseleave', hideChannelTooltip);

fileList.addEventListener('change', function(e) {
    if (e.target.classList.contains('file-channel-toggle')) {
        var fileId = Number(e.target.dataset.fileId);
        var channelIndex = Number(e.target.dataset.channelIndex);
        setActiveFile(fileId);
        for (var i = 0; i < loadedFiles.length; i++) {
            if (loadedFiles[i].id === fileId) {
                loadedFiles[i].channelEnabled[channelIndex] = e.target.checked;
                break;
            }
        }
        refreshView();
        return;
    }

    if (e.target.classList.contains('file-color-input')) {
        setActiveFile(Number(e.target.dataset.fileId));
        updateChannelColor(Number(e.target.dataset.fileId), Number(e.target.dataset.channelIndex), e.target.value);
    }
});

fileList.addEventListener('input', function(e) {
    if (e.target.classList.contains('file-color-input')) {
        setActiveFile(Number(e.target.dataset.fileId));
        updateChannelColor(Number(e.target.dataset.fileId), Number(e.target.dataset.channelIndex), e.target.value);
    }
});

function loadFiles(fileSet) {
    var files = Array.prototype.slice.call(fileSet || []);
    if (!files.length) {
        return;
    }

    function next(index) {
        if (index >= files.length) {
            return;
        }
        loadFile(files[index], function() {
            next(index + 1);
        });
    }

    next(0);
}

function loadFile(file, done) {
    var reader = new FileReader();
    reader.onload = async function(e) {
        try {
            addLoadedFile(await detectAndParse(e.target.result, file.name), file.name);
        } catch (err) {
            showError(String(err.message || err));
        }
        if (done) {
            done();
        }
    };
    reader.onerror = function() {
        showError('Could not read ' + file.name + '.');
        if (done) {
            done();
        }
    };
    reader.readAsArrayBuffer(file);
}

function addLoadedFile(result, filename) {
    if (result.channels.length === 0) {
        showError('No enabled channels found in ' + filename + '.');
        return;
    }

    result.channels.forEach(function(ch) {
        var appearance = allocateTraceAppearance();
        ch.color = appearance.color;
        ch.lineStyle = appearance.lineStyle;
        ch.lineDash = appearance.lineDash;
        ch.lineCap = appearance.lineCap;
    });

    loadedFiles.push({
        id: nextFileId++,
        filename: filename,
        stem: stemForFilename(filename),
        result: result,
        channelEnabled: result.channels.map(function() {
            return true;
        }),
    });
    activeFileId = loadedFiles[loadedFiles.length - 1].id;
    hideError();
    refreshView();
}

function updateChannelColor(fileId, channelIndex, color) {
    var normalized = normalizeColor(color, '');
    if (!normalized) {
        return;
    }

    for (var i = 0; i < loadedFiles.length; i++) {
        if (loadedFiles[i].id === fileId && loadedFiles[i].result.channels[channelIndex]) {
            loadedFiles[i].result.channels[channelIndex].color = normalized;
            break;
        }
    }
    refreshView();
}

function showError(msg) {
    errorBoxMessage.textContent = 'Error: ' + msg;
    errorBox.classList.add('visible');
    errorBox.setAttribute('aria-hidden', 'false');
    if (!loadedFiles.length) {
        dropZone.classList.remove('hidden');
        scopeCanvas.classList.remove('visible');
    }
    updateStatus('Error: ' + msg);
}

window.addEventListener('resize', function() {
    hideChannelTooltip();
    if (loadedFiles.length) {
        refreshView();
    }
});
