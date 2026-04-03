// This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild

(function (root, factory) {
  if (typeof define === 'function' && define.amd) {
    define(['exports', 'kaitai-struct/KaitaiStream'], factory);
  } else if (typeof exports === 'object' && exports !== null && typeof exports.nodeType !== 'number') {
    factory(exports, require('kaitai-struct/KaitaiStream'));
  } else {
    factory(root.RigolDho8001000Bin || (root.RigolDho8001000Bin = {}), root.KaitaiStream);
  }
})(typeof self !== 'undefined' ? self : this, function (RigolDho8001000Bin_, KaitaiStream) {
/**
 * Official binary waveform export format documented in DHO1000 User Guide
 * §19.2.4 (Tables 19.1–19.4).
 * 
 * This schema currently models the float32 analog waveform buffers used by
 * this project. The user guide also documents digital unsigned 8-bit buffers
 * and math waveforms; those buffer types are identified in the enums below,
 * and the downstream wrapper rejects them explicitly instead of treating them
 * as calibrated volt samples.
 * 
 * File layout::
 *   [File Header:      16 bytes]
 *   for each waveform (channel):
 *     [Waveform Header: 140 bytes]
 *     [Data Header:      16 bytes]
 *     [Sample Data:      buffer_size bytes - float32 LE, volts]
 * 
 * Time axis reconstruction used by the current parser::
 *   t[i] = -x_origin + i * x_increment
 * 
 * The manual describes X Origin as the x-value of the first data point.
 * Empirically, the analog captures used by this repo behave as if x_origin
 * stores a positive pre-trigger distance, so downstream code negates it.
 * 
 * Sources used for this KSY binary format: the official DHO1000 User Guide
 * section 19.2.4 (Tables 19.1-19.4) plus comparison against checked-in
 * `DHO1074.bin`, `DHO824-ch1.bin`, `DHO824-ch12.bin`, and `DHO824-ch1234.bin`
 * captures.
 * 
 * Tested file formats: real repo fixtures `DHO1074.bin`, `DHO824-ch1.bin`,
 * `DHO824-ch12.bin`, and `DHO824-ch1234.bin`, covering one-, two-, and
 * four-channel analog float32 exports.
 * 
 * Oscilloscope models this format may apply to: `DHO804`, `DHO812`, `DHO814`,
 * `DHO824`, `DHO1072`, `DHO1074`, `DHO1102`, `DHO1202`, and related
 * `DHO800` / `DHO1000` family scopes that write the documented `.bin` export.
 */

var RigolDho8001000Bin = (function() {
  RigolDho8001000Bin.BufferTypeEnum = Object.freeze({
    UNKNOWN: 0,
    FLOAT32_NORMAL: 1,
    FLOAT32_MAXIMUM: 2,
    FLOAT32_MINIMUM: 3,
    NOT_USED: 4,
    DIGITAL_U8: 5,

    0: "UNKNOWN",
    1: "FLOAT32_NORMAL",
    2: "FLOAT32_MAXIMUM",
    3: "FLOAT32_MINIMUM",
    4: "NOT_USED",
    5: "DIGITAL_U8",
  });

  RigolDho8001000Bin.UnitEnum = Object.freeze({
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

  RigolDho8001000Bin.WaveformTypeEnum = Object.freeze({
    UNKNOWN: 0,
    NORMAL: 1,
    PEAK: 2,
    AVERAGE: 3,
    NOT_USED_4: 4,
    NOT_USED_5: 5,
    LOGIC: 6,

    0: "UNKNOWN",
    1: "NORMAL",
    2: "PEAK",
    3: "AVERAGE",
    4: "NOT_USED_4",
    5: "NOT_USED_5",
    6: "LOGIC",
  });

  function RigolDho8001000Bin(_io, _parent, _root) {
    this._io = _io;
    this._parent = _parent;
    this._root = _root || this;

    this._read();
  }
  RigolDho8001000Bin.prototype._read = function() {
    this.fileHeader = new FileHeader(this._io, this, this._root);
    this.waveforms = [];
    for (var i = 0; i < this.fileHeader.nWaveforms; i++) {
      this.waveforms.push(new Waveform(this._io, this, this._root));
    }
  }

  /**
   * 16-byte data buffer header (Table 19.4).
   */

  var DataHeader = RigolDho8001000Bin.DataHeader = (function() {
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
      this.bufferSize = this._io.readU8le();
    }

    /**
     * Size of this header in bytes (= 16).
     */

    /**
     * Sample encoding per Table 19.4.
     * The current wrapper supports float32 analog buffers only.
     */

    /**
     * Bytes per sample (= 4 for float32).
     */

    /**
     * Total byte count of sample data (= n_pts * 4).
     */

    return DataHeader;
  })();

  /**
   * 16-byte file header (Table 19.2).
   */

  var FileHeader = RigolDho8001000Bin.FileHeader = (function() {
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
      this.fileSize = this._io.readU8le();
      this.nWaveforms = this._io.readU4le();
    }

    /**
     * Magic bytes identifying a Rigol DHO .bin file.
     */

    /**
     * File format version string.
     */

    /**
     * Total file size in bytes.
     */

    /**
     * Number of waveform records (one per enabled channel).
     */

    return FileHeader;
  })();

  /**
   * Stream of calibrated float32 voltage samples for analog buffers.
   */

  var SampleData = RigolDho8001000Bin.SampleData = (function() {
    function SampleData(_io, _parent, _root) {
      this._io = _io;
      this._parent = _parent;
      this._root = _root;

      this._read();
    }
    SampleData.prototype._read = function() {
      this.values = [];
      var i = 0;
      while (!this._io.isEof()) {
        this.values.push(this._io.readF4le());
        i++;
      }
    }

    /**
     * Voltage at each sample point in volts.
     */

    return SampleData;
  })();

  /**
   * One waveform record: header, data header, and sample payload.
   */

  var Waveform = RigolDho8001000Bin.Waveform = (function() {
    function Waveform(_io, _parent, _root) {
      this._io = _io;
      this._parent = _parent;
      this._root = _root;

      this._read();
    }
    Waveform.prototype._read = function() {
      this.wfmHeader = new WaveformHeader(this._io, this, this._root);
      this.dataHeader = new DataHeader(this._io, this, this._root);
      this._raw_samples = this._io.readBytes(this.dataHeader.bufferSize);
      var _io__raw_samples = new KaitaiStream(this._raw_samples);
      this.samples = new SampleData(_io__raw_samples, this, this._root);
    }

    /**
     * Calibrated voltage values in volts (float32 LE).
     */

    return Waveform;
  })();

  /**
   * 140-byte per-waveform header (Table 19.3).
   * Describes acquisition settings and time-axis parameters for one channel.
   */

  var WaveformHeader = RigolDho8001000Bin.WaveformHeader = (function() {
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
      this.model = KaitaiStream.bytesToStr(KaitaiStream.bytesTerminate(this._io.readBytes(24), 0, false), "ASCII");
      this.channelName = KaitaiStream.bytesToStr(KaitaiStream.bytesTerminate(this._io.readBytes(16), 0, false), "ASCII");
      this.padding = this._io.readBytes(12);
    }

    /**
     * Sampling interval in seconds.
     */
    Object.defineProperty(WaveformHeader.prototype, 'secondsPerPoint', {
      get: function() {
        if (this._m_secondsPerPoint !== undefined)
          return this._m_secondsPerPoint;
        this._m_secondsPerPoint = this.xIncrement;
        return this._m_secondsPerPoint;
      }
    });

    /**
     * Empirical first-sample time used by the current analog parser.
     */
    Object.defineProperty(WaveformHeader.prototype, 't0', {
      get: function() {
        if (this._m_t0 !== undefined)
          return this._m_t0;
        this._m_t0 = -(this.xOrigin);
        return this._m_t0;
      }
    });

    /**
     * Size of this header in bytes (= 140).
     */

    /**
     * Acquisition mode.
     */

    /**
     * Number of data buffers (= 1).
     */

    /**
     * Number of sample points.
     */

    /**
     * Unused, always 0.
     */

    /**
     * Horizontal display range in seconds.
     */

    /**
     * Horizontal display origin.
     */

    /**
     * Time between consecutive samples in seconds.
     */

    /**
     * Manual: x-value of the first data point in seconds.
     * Empirical analog captures used by this repo behave as if this is a
     * positive trigger distance; downstream code therefore negates it:
     *   t[0] = -x_origin
     *   t[i] = -x_origin + i * x_increment
     */

    /**
     * X-axis unit.
     */

    /**
     * Y-axis unit.
     */

    /**
     * Capture date (null-terminated ASCII).
     */

    /**
     * Capture time (null-terminated ASCII).
     */

    /**
     * Model and serial number string "MODEL#:SERIAL#".
     */

    /**
     * Channel label, e.g. "CH1".
     */

    /**
     * Reserved, always zero.
     */

    return WaveformHeader;
  })();

  return RigolDho8001000Bin;
})();
RigolDho8001000Bin_.RigolDho8001000Bin = RigolDho8001000Bin;
});
