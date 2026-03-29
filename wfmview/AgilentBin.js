// This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild

(function (root, factory) {
  if (typeof define === 'function' && define.amd) {
    define(['exports', 'kaitai-struct/KaitaiStream'], factory);
  } else if (typeof exports === 'object' && exports !== null && typeof exports.nodeType !== 'number') {
    factory(exports, require('kaitai-struct/KaitaiStream'));
  } else {
    factory(root.AgilentBin || (root.AgilentBin = {}), root.KaitaiStream);
  }
})(typeof self !== 'undefined' ? self : this, function (AgilentBin_, KaitaiStream) {
/**
 * Binary waveform export used by Agilent and Keysight oscilloscopes.
 * 
 * This schema is based on the reverse-engineered parser and checked-in sample
 * captures from `docs/vendors/wavebin-master`, which exercise the `AG10`
 * container written by DSO-X / MSO-X scopes. The same container family also
 * appears to exist in `AG01` and `AG03` variants; the vendor parser handles
 * those by widening the file-size and buffer-size fields for version 3.
 * 
 * File layout:
 *   [File Header: 12 bytes for AG01 / AG10, 16 bytes for AG03]
 *   for each exported waveform:
 *     [Waveform Header: usually 140 bytes]
 *     [Data Header: 12 bytes for AG01 / AG10, 16 bytes for AG03]
 *     [Sample Data:   buffer_size bytes]
 * 
 * Analog waveforms are stored as float32 buffers. Digital / logic-like
 * captures use the same container but store `u1` samples and are handled by
 * handwritten code rather than normalized directly by the Kaitai schema.
 */

var AgilentBin = (function() {
  AgilentBin.BufferTypeEnum = Object.freeze({
    UNKNOWN: 0,
    NORMAL_FLOAT32: 1,
    MAXIMUM_FLOAT32: 2,
    MINIMUM_FLOAT32: 3,
    TIME_FLOAT32: 4,
    COUNTS_FLOAT32: 5,
    DIGITAL_U8: 6,

    0: "UNKNOWN",
    1: "NORMAL_FLOAT32",
    2: "MAXIMUM_FLOAT32",
    3: "MINIMUM_FLOAT32",
    4: "TIME_FLOAT32",
    5: "COUNTS_FLOAT32",
    6: "DIGITAL_U8",
  });

  AgilentBin.UnitEnum = Object.freeze({
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

  AgilentBin.WaveformTypeEnum = Object.freeze({
    UNKNOWN: 0,
    NORMAL: 1,
    PEAK_DETECT: 2,
    AVERAGE: 3,
    HORIZONTAL_HISTOGRAM: 4,
    VERTICAL_HISTOGRAM: 5,
    LOGIC: 6,

    0: "UNKNOWN",
    1: "NORMAL",
    2: "PEAK_DETECT",
    3: "AVERAGE",
    4: "HORIZONTAL_HISTOGRAM",
    5: "VERTICAL_HISTOGRAM",
    6: "LOGIC",
  });

  function AgilentBin(_io, _parent, _root) {
    this._io = _io;
    this._parent = _parent;
    this._root = _root || this;

    this._read();
  }
  AgilentBin.prototype._read = function() {
    this.fileHeader = new FileHeader(this._io, this, this._root);
    this.waveforms = [];
    for (var i = 0; i < this.fileHeader.nWaveforms; i++) {
      this.waveforms.push(new Waveform(this._io, this, this._root));
    }
  }

  var DataHeader = AgilentBin.DataHeader = (function() {
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
      if ( ((this._root.fileHeader.versionNum == 1) || (this._root.fileHeader.versionNum == 10)) ) {
        this.bufferSize32 = this._io.readU4le();
      }
      if (this._root.fileHeader.versionNum == 3) {
        this.bufferSize64 = this._io.readU8le();
      }
    }
    Object.defineProperty(DataHeader.prototype, 'bufferSize', {
      get: function() {
        if (this._m_bufferSize !== undefined)
          return this._m_bufferSize;
        this._m_bufferSize = (this._root.fileHeader.versionNum == 3 ? this.bufferSize64 : this.bufferSize32);
        return this._m_bufferSize;
      }
    });

    return DataHeader;
  })();

  var FileHeader = AgilentBin.FileHeader = (function() {
    function FileHeader(_io, _parent, _root) {
      this._io = _io;
      this._parent = _parent;
      this._root = _root;

      this._read();
    }
    FileHeader.prototype._read = function() {
      this.cookie = this._io.readBytes(2);
      if (!((KaitaiStream.byteArrayCompare(this.cookie, new Uint8Array([65, 71])) == 0))) {
        throw new KaitaiStream.ValidationNotEqualError(new Uint8Array([65, 71]), this.cookie, this._io, "/types/file_header/seq/0");
      }
      this.version = KaitaiStream.bytesToStr(this._io.readBytes(2), "ASCII");
      if ( ((this.versionNum == 1) || (this.versionNum == 10)) ) {
        this.fileSize32 = this._io.readU4le();
      }
      if (this.versionNum == 3) {
        this.fileSize64 = this._io.readU8le();
      }
      this.nWaveforms = this._io.readU4le();
    }
    Object.defineProperty(FileHeader.prototype, 'fileSize', {
      get: function() {
        if (this._m_fileSize !== undefined)
          return this._m_fileSize;
        this._m_fileSize = (this.versionNum == 3 ? this.fileSize64 : this.fileSize32);
        return this._m_fileSize;
      }
    });
    Object.defineProperty(FileHeader.prototype, 'versionNum', {
      get: function() {
        if (this._m_versionNum !== undefined)
          return this._m_versionNum;
        this._m_versionNum = Number.parseInt(this.version, 10);
        return this._m_versionNum;
      }
    });

    return FileHeader;
  })();

  var Waveform = AgilentBin.Waveform = (function() {
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

  var WaveformHeader = AgilentBin.WaveformHeader = (function() {
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
      this.timeTag = this._io.readF8le();
      this.segmentIndex = this._io.readU4le();
      if (this.headerSize > 140) {
        this.extraPadding = this._io.readBytes(this.headerSize - 140);
      }
    }

    /**
     * Reserved extension bytes present in some firmware revisions.
     */

    return WaveformHeader;
  })();

  return AgilentBin;
})();
AgilentBin_.AgilentBin = AgilentBin;
});
