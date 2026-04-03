// This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild

(function (root, factory) {
  if (typeof define === 'function' && define.amd) {
    define(['exports', 'kaitai-struct/KaitaiStream'], factory);
  } else if (typeof exports === 'object' && exports !== null && typeof exports.nodeType !== 'number') {
    factory(exports, require('kaitai-struct/KaitaiStream'));
  } else {
    factory(root.AgilentAgxxBin || (root.AgilentAgxxBin = {}), root.KaitaiStream);
  }
})(typeof self !== 'undefined' ? self : this, function (AgilentAgxxBin_, KaitaiStream) {
/**
 * Binary waveform export used by Agilent and Keysight oscilloscopes.
 * 
 * This schema is based on the checked-in vendor parsers plus the Agilent
 * 6000 Series and InfiniiVision 2000 manuals. Those sources describe the
 * `AG01` / `AG03` / `AG10` container family written by several
 * Agilent / Keysight oscilloscopes.
 * 
 * File layout::
 *   [File Header: 12 bytes for AG01 / AG10, 16 bytes for AG03]
 *   for each exported waveform:
 *     [Waveform Header: usually 140 bytes]
 *     repeat n_buffers times:
 *       [Data Header: 12 bytes for AG01 / AG10, 16 bytes for AG03]
 *       [Sample Data: buffer_size bytes]
 * 
 * Normal analog waveforms are float32. Peak Detect acquisitions can store
 * separate minimum and maximum float32 buffers for a single waveform header.
 * Logic-style records use byte-oriented buffers.
 * 
 * Sources used for this KSY binary format: `Agilent InfiniiVision
 * 6000 Series Oscilloscopes` and `Agilent InfiniiVision 2000 X-Series
 * Oscilloscopes` as well as GitHub repositories 
 * <https://github.com/shotaizu/agilent-oscilloscope-bin-parser>,
 * <https://github.com/AntonBryansky/ImportAgilentBin>,
 * <https://github.com/yodalee/keysightBin>, and
 * <https://github.com/FaustinCarter/agilent_read_binary>
 * 
 * Tested file formats: `agilent_1.bin` through `agilent_5.bin`
 * and `agilent_msox4154a_01.bin`; all checked-in real samples are `AG10`
 * captures, and the regression builders additionally exercise multi-buffer and
 * per-channel-timing edge cases within the same `AG10` container layout.
 * 
 * Oscilloscope models this format may apply to: confirmed `DSO-X 1102G` and
 * `MSO-X 4154A` captures, plus other Agilent / Keysight 6000 Series and
 * InfiniiVision 2000/3000/4000/X instruments that export `AG01`, `AG03`, or
 * `AG10` `.bin` files.
 */

var AgilentAgxxBin = (function() {
  AgilentAgxxBin.BufferTypeEnum = Object.freeze({
    UNKNOWN: 0,
    NORMAL_FLOAT32: 1,
    MAXIMUM_FLOAT32: 2,
    MINIMUM_FLOAT32: 3,
    COUNTS_I32: 4,
    LOGIC_U8: 5,
    DIGITAL_U8: 6,

    0: "UNKNOWN",
    1: "NORMAL_FLOAT32",
    2: "MAXIMUM_FLOAT32",
    3: "MINIMUM_FLOAT32",
    4: "COUNTS_I32",
    5: "LOGIC_U8",
    6: "DIGITAL_U8",
  });

  AgilentAgxxBin.UnitEnum = Object.freeze({
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

  AgilentAgxxBin.WaveformTypeEnum = Object.freeze({
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

  function AgilentAgxxBin(_io, _parent, _root) {
    this._io = _io;
    this._parent = _parent;
    this._root = _root || this;

    this._read();
  }
  AgilentAgxxBin.prototype._read = function() {
    this.fileHeader = new FileHeader(this._io, this, this._root);
    this.waveforms = [];
    for (var i = 0; i < this.fileHeader.nWaveforms; i++) {
      this.waveforms.push(new Waveform(this._io, this, this._root));
    }
  }

  var DataHeader = AgilentAgxxBin.DataHeader = (function() {
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

  var FileHeader = AgilentAgxxBin.FileHeader = (function() {
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

  var Waveform = AgilentAgxxBin.Waveform = (function() {
    function Waveform(_io, _parent, _root) {
      this._io = _io;
      this._parent = _parent;
      this._root = _root;

      this._read();
    }
    Waveform.prototype._read = function() {
      this.wfmHeader = new WaveformHeader(this._io, this, this._root);
      this.buffers = [];
      for (var i = 0; i < this.wfmHeader.nBuffers; i++) {
        this.buffers.push(new WaveformBuffer(this._io, this, this._root));
      }
    }

    return Waveform;
  })();

  var WaveformBuffer = AgilentAgxxBin.WaveformBuffer = (function() {
    function WaveformBuffer(_io, _parent, _root) {
      this._io = _io;
      this._parent = _parent;
      this._root = _root;

      this._read();
    }
    WaveformBuffer.prototype._read = function() {
      this.dataHeader = new DataHeader(this._io, this, this._root);
      this.dataRaw = this._io.readBytes(this.dataHeader.bufferSize);
    }

    return WaveformBuffer;
  })();

  var WaveformHeader = AgilentAgxxBin.WaveformHeader = (function() {
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

  return AgilentAgxxBin;
})();
AgilentAgxxBin_.AgilentAgxxBin = AgilentAgxxBin;
});
