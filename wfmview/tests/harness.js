// Loads wfmview/app.js under Node with a stubbed DOM so its helpers can be
// called directly from tests.
//
// app.js is written for a browser: it runs top-level code that touches document
// and window, and defines its functions as globals rather than as modules.  The
// stub below is the minimum that lets it load; tests then call those globals.
//
// The Kaitai runtime is fetched from a CDN by index.html and is not in the
// repository, so these tests exercise the helpers that take plain JavaScript
// values rather than parsing fixtures end to end.  The Python suite covers the
// cross-language paths, where the point is that Python can read what the
// viewer wrote.
'use strict';

const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');

const VIEWER_DIR = path.resolve(__dirname, '..');

function classList() {
    return { add() {}, remove() {}, toggle() {}, contains() { return false; } };
}

function element() {
    return {
        checked: false, disabled: false, innerHTML: '', textContent: '', value: '',
        dataset: {}, style: {}, classList: classList(),
        addEventListener() {}, removeEventListener() {},
        appendChild() {}, removeChild() {}, setAttribute() {},
        getAttribute() { return null; },
        getContext() {
            return {
                fillRect() {}, beginPath() {}, moveTo() {}, lineTo() {}, stroke() {},
                fillText() {}, measureText() { return { width: 0 }; }, save() {},
                restore() {}, clearRect() {}, arc() {}, closePath() {}, setLineDash() {},
            };
        },
        getBoundingClientRect() {
            return { left: 0, top: 0, right: 800, bottom: 480, width: 800, height: 480 };
        },
        closest() { return null; }, click() {},
        width: 800, height: 480, offsetWidth: 800, offsetHeight: 480,
        clientWidth: 800, clientHeight: 480,
    };
}

let loaded = false;

/** Load app.js into this context, once per process. */
function loadViewer() {
    if (loaded) {
        return;
    }

    global.document = {
        getElementById() { return element(); },
        createElement() { return element(); },
        addEventListener() {}, removeEventListener() {},
        body: { classList: classList(), appendChild() {}, removeChild() {} },
    };
    global.window = {
        addEventListener() {}, removeEventListener() {}, innerHeight: 800,
        URL: { createObjectURL() { return 'blob:test'; }, revokeObjectURL() {} },
    };
    global.FileReader = function FileReader() {};

    vm.runInThisContext(fs.readFileSync(path.join(VIEWER_DIR, 'app.js'), 'utf8'), { filename: 'app.js' });
    loaded = true;
}

/** Build the bytes of a `tekmeta!` block, for the metadata tests. */
function tekmetaBlock(entries) {
    const parts = [];
    const u32 = (value) => {
        const b = Buffer.alloc(4);
        b.writeUInt32LE(value);
        return b;
    };

    parts.push(Buffer.from('tekmeta!', 'ascii'));
    parts.push(u32(entries.length));
    for (const [key, tag, value] of entries) {
        parts.push(u32(key.length));
        parts.push(Buffer.from(key, 'ascii'));
        parts.push(Buffer.from([tag]));
        if (tag === 1) {
            parts.push(u32(value.length));
            parts.push(Buffer.from(value, 'ascii'));
        } else if (tag === 3) {
            const b = Buffer.alloc(8);
            b.writeDoubleLE(value);
            parts.push(b);
        } else {
            parts.push(u32(value));
        }
    }
    return new Uint8Array(Buffer.concat(parts));
}

module.exports = { loadViewer, tekmetaBlock };
