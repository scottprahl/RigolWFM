// This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild

(function (root, factory) {
  if (typeof define === 'function' && define.amd) {
    define(['exports', 'kaitai-struct/KaitaiStream'], factory);
  } else if (typeof exports === 'object' && exports !== null && typeof exports.nodeType !== 'number') {
    factory(exports, require('kaitai-struct/KaitaiStream'));
  } else {
    factory(root.Rigol70008000Bin || (root.Rigol70008000Bin = {}), root.KaitaiStream);
  }
})(typeof self !== 'undefined' ? self : this, function (Rigol70008000Bin_, KaitaiStream) {
/**
 * Binary waveform export used by Rigol MSO7000/DS7000 and MSO8000 scopes.
 * 
 * This schema follows the "Binary Data Format (.bin)" tables in:
 * 
 *   - `docs/manuals/Rigol MSO7000 Series User Manual.pdf`
 *   - `docs/manuals/MSO8000 Series Digital.pdf`
 * 
 * Documented layout::
 * 
 *   [File Header:      12 bytes]
 *   for each exported waveform:
 *     [Waveform Header: 128 bytes]
 *     [Data Header:      12 bytes]
 *     [Sample Data:      buffer_size bytes]
 * 
 * The manuals document analog, logic, and math records in the same container.
 * The handwritten adapter currently normalizes analog float32 buffers only.
 * 
 * Sources used for this KSY binary format: the Rigol "Binary Data Format
 * (.bin)" tables in `Rigol MSO7000 Series User Manual.pdf` plus the
 * checked-in synthetic regression builder in `tests/test_7_8.py`.
 * 
 * Tested file formats: synthetic `MSO7034` and `MSO8204` analog float32 `.bin`
 * captures generated in `tests/test_7_8.py`, plus a negative regression that
 * confirms logic-record rejection.
 * 
 * Oscilloscope models this format may apply to: Rigol `DS7000` / `MSO7000`
 * and `MSO8000` family scopes that emit the documented float32 `.bin` export,
 * including the synthetic reference models `MSO7034` and `MSO8204`.
 */

var Rigol70008000Bin = (function() {
  Rigol70008000Bin.BufferTypeEnum = Object.freeze({
    UNKNOWN: 0,
    NORMAL_FLOAT32: 1,
    MAXIMUM_FLOAT32: 2,
    MINIMUM_FLOAT32: 3,
    UNUSED4: 4,
    UNUSED5: 5,
    DIGITAL_U8: 6,

    0: "UNKNOWN",
    1: "NORMAL_FLOAT32",
    2: "MAXIMUM_FLOAT32",
    3: "MINIMUM_FLOAT32",
    4: "UNUSED4",
    5: "UNUSED5",
    6: "DIGITAL_U8",
  });

  Rigol70008000Bin.UnitEnum = Object.freeze({
    UNKNOWN: 0,
    V: 1,
    S: 2,
    CONSTANT: 3,
    A: 4,
    DB: 5,
    HZ: 6,

    0: "UNKNOWN",
    1: "V",
    2: "S",
    3: "CONSTANT",
    4: "A",
    5: "DB",
    6: "HZ",
  });

  Rigol70008000Bin.WaveformTypeEnum = Object.freeze({
    UNKNOWN: 0,
    NORMAL: 1,
    PEAK_DETECT: 2,
    AVERAGE: 3,
    UNUSED4: 4,
    UNUSED5: 5,
    LOGIC: 6,

    0: "UNKNOWN",
    1: "NORMAL",
    2: "PEAK_DETECT",
    3: "AVERAGE",
    4: "UNUSED4",
    5: "UNUSED5",
    6: "LOGIC",
  });

  function Rigol70008000Bin(_io, _parent, _root) {
    this._io = _io;
    this._parent = _parent;
    this._root = _root || this;

    this._read();
  }
  Rigol70008000Bin.prototype._read = function() {
    this.fileHeader = new FileHeader(this._io, this, this._root);
    this.waveforms = [];
    for (var i = 0; i < this.fileHeader.nWaveforms; i++) {
      this.waveforms.push(new Waveform(this._io, this, this._root));
    }
  }

  var DataHeader = Rigol70008000Bin.DataHeader = (function() {
    function DataHeader(_io, _parent, _root) {
      this._io = _io;
      this._parent = _parent;
      this._root = _root;

      this._read();
    }
    DataHeader.prototype._read = function() {
      this.headerSize = this._io.readU4le();
      this.bufferType = this._io.readU2le();
      this.bytesPerPoint = this._io.readU2le();
      this.bufferSize = this._io.readU4le();
    }

    return DataHeader;
  })();

  var FileHeader = Rigol70008000Bin.FileHeader = (function() {
    function FileHeader(_io, _parent, _root) {
      this._io = _io;
      this._parent = _parent;
      this._root = _root;

      this._read();
    }
    FileHeader.prototype._read = function() {
      this.cookie = this._io.readBytes(2);
      if (!((KaitaiStream.byteArrayCompare(this.cookie, new Uint8Array([82, 71])) == 0))) {
        throw new KaitaiStream.ValidationNotEqualError(new Uint8Array([82, 71]), this.cookie, this._io, "/types/file_header/seq/0");
      }
      this.version = KaitaiStream.bytesToStr(this._io.readBytes(2), "ASCII");
      this.fileSize = this._io.readU4le();
      this.nWaveforms = this._io.readU4le();
    }

    return FileHeader;
  })();

  var Waveform = Rigol70008000Bin.Waveform = (function() {
    function Waveform(_io, _parent, _root) {
      this._io = _io;
      this._parent = _parent;
      this._root = _root;

      this._read();
    }
    Waveform.prototype._read = function() {
      this.wfmHeader = new WaveformHeader(this._io, this, this._root);
      this.dataHeader = new DataHeader(this._io, this, this._root);
      this.dataRaw = this._io.readBytes(this.dataHeader.bufferSize);
    }

    return Waveform;
  })();

  var WaveformHeader = Rigol70008000Bin.WaveformHeader = (function() {
    function WaveformHeader(_io, _parent, _root) {
      this._io = _io;
      this._parent = _parent;
      this._root = _root;

      this._read();
    }
    WaveformHeader.prototype._read = function() {
      this.headerSize = this._io.readU4le();
      this.waveformType = this._io.readU4le();
      this.nBuffers = this._io.readU4le();
      this.nPts = this._io.readU4le();
      this.count = this._io.readU4le();
      this.xDisplayRange = this._io.readF4le();
      this.xDisplayOrigin = this._io.readF8le();
      this.xIncrement = this._io.readF8le();
      this.xOrigin = this._io.readF8le();
      this.xUnits = this._io.readU4le();
      this.yUnits = this._io.readU4le();
      this.date = KaitaiStream.bytesToStr(KaitaiStream.bytesTerminate(this._io.readBytes(16), 0, false), "ASCII");
      this.timeStr = KaitaiStream.bytesToStr(KaitaiStream.bytesTerminate(this._io.readBytes(16), 0, false), "ASCII");
      this.frameString = KaitaiStream.bytesToStr(KaitaiStream.bytesTerminate(this._io.readBytes(24), 0, false), "ASCII");
      this.waveformLabel = KaitaiStream.bytesToStr(KaitaiStream.bytesTerminate(this._io.readBytes(16), 0, false), "ASCII");
    }

    return WaveformHeader;
  })();

  return Rigol70008000Bin;
})();
Rigol70008000Bin_.Rigol70008000Bin = Rigol70008000Bin;
});
