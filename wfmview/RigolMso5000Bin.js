// This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild

(function (root, factory) {
  if (typeof define === 'function' && define.amd) {
    define(['exports', 'kaitai-struct/KaitaiStream'], factory);
  } else if (typeof exports === 'object' && exports !== null && typeof exports.nodeType !== 'number') {
    factory(exports, require('kaitai-struct/KaitaiStream'));
  } else {
    factory(root.RigolMso5000Bin || (root.RigolMso5000Bin = {}), root.KaitaiStream);
  }
})(typeof self !== 'undefined' ? self : this, function (RigolMso5000Bin_, KaitaiStream) {
/**
 * Binary waveform export used by Rigol MSO5000 scopes.
 * 
 * This schema is based on:
 *   - example files in `docs/sources/rigol_mso5000-main/waveform_bin/examples`
 *   - `docs/sources/matlab/importRigolBinMSO5000.m`
 *   - `docs/sources/rigol_mso5000-main/waveform_bin/Rigol_MSO5000_Waveform_bin.bt`
 * 
 * File layout:
 *   [File Header:      12 bytes]
 *   for each exported waveform:
 *     [Waveform Header: 140 bytes]
 *     [Data Header:      12 bytes]
 *     [Sample Data:      buffer_size bytes]
 * 
 * The shipped examples only exercise analog float32 buffers. Logic-analyzer
 * records are identified by the enums below and handled in handwritten code.
 */

var RigolMso5000Bin = (function() {
  RigolMso5000Bin.BufferTypeEnum = Object.freeze({
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

  RigolMso5000Bin.UnitEnum = Object.freeze({
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

  RigolMso5000Bin.WaveformTypeEnum = Object.freeze({
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

  function RigolMso5000Bin(_io, _parent, _root) {
    this._io = _io;
    this._parent = _parent;
    this._root = _root || this;

    this._read();
  }
  RigolMso5000Bin.prototype._read = function() {
    this.fileHeader = new FileHeader(this._io, this, this._root);
    this.waveforms = [];
    for (var i = 0; i < this.fileHeader.nWaveforms; i++) {
      this.waveforms.push(new Waveform(this._io, this, this._root));
    }
  }

  var DataHeader = RigolMso5000Bin.DataHeader = (function() {
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

  var FileHeader = RigolMso5000Bin.FileHeader = (function() {
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

  var Waveform = RigolMso5000Bin.Waveform = (function() {
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

  var WaveformHeader = RigolMso5000Bin.WaveformHeader = (function() {
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
     * Reserved extension bytes present in some firmware versions (e.g. MSO5074).
     */

    return WaveformHeader;
  })();

  return RigolMso5000Bin;
})();
RigolMso5000Bin_.RigolMso5000Bin = RigolMso5000Bin;
});
