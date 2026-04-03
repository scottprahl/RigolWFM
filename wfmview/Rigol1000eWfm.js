// This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild

(function (root, factory) {
  if (typeof define === 'function' && define.amd) {
    define(['exports', 'kaitai-struct/KaitaiStream'], factory);
  } else if (typeof exports === 'object' && exports !== null && typeof exports.nodeType !== 'number') {
    factory(exports, require('kaitai-struct/KaitaiStream'));
  } else {
    factory(root.Rigol1000eWfm || (root.Rigol1000eWfm = {}), root.KaitaiStream);
  }
})(typeof self !== 'undefined' ? self : this, function (Rigol1000eWfm_, KaitaiStream) {
/**
 * Rigol DS1102E scope .wmf format abstracted from a python script
 * 
 * Sources used for this KSY binary format were a PDF document titled,
 * "DS1000E/D WFM structure instruction" written by Rigol and the Github repository
 * <https://github.com/mabl/pyRigolWFM>.
 * 
 * Tested file formats: real repo fixtures `DS1102E-A.wfm` through
 * `DS1102E-G.wfm`, `DS1052E.wfm`, and `DS1000E-A.wfm` through
 * `DS1000E-D.wfm`.
 * 
 * Oscilloscope models this format may apply to: DS1000E family models
 * currently listed by the library, including `DS1102E`, `DS1052E`, and closely
 * related DS1000E-series scopes.
 */

var Rigol1000eWfm = (function() {
  Rigol1000eWfm.BandwidthEnum = Object.freeze({
    NO_LIMIT: 0,
    MHZ_20: 1,
    MHZ_100: 2,
    MHZ_200: 3,
    MHZ_250: 4,

    0: "NO_LIMIT",
    1: "MHZ_20",
    2: "MHZ_100",
    3: "MHZ_200",
    4: "MHZ_250",
  });

  Rigol1000eWfm.CouplingEnum = Object.freeze({
    DC: 0,
    AC: 1,
    GND: 2,

    0: "DC",
    1: "AC",
    2: "GND",
  });

  Rigol1000eWfm.FilterEnum = Object.freeze({
    LOW_PASS: 0,
    HIGH_PASS: 1,
    BAND_PASS: 2,
    BAND_REJECT: 3,

    0: "LOW_PASS",
    1: "HIGH_PASS",
    2: "BAND_PASS",
    3: "BAND_REJECT",
  });

  Rigol1000eWfm.SourceEnum = Object.freeze({
    CH1: 0,
    CH2: 1,
    EXT: 2,
    AC_LINE: 3,
    D0: 4,
    D1: 5,
    D2: 6,
    D3: 7,
    D4: 8,
    D5: 9,
    D6: 10,
    D7: 11,
    D8: 12,
    D9: 13,
    D10: 14,
    D11: 15,
    D12: 16,
    D13: 17,
    D14: 18,
    D15: 19,

    0: "CH1",
    1: "CH2",
    2: "EXT",
    3: "AC_LINE",
    4: "D0",
    5: "D1",
    6: "D2",
    7: "D3",
    8: "D4",
    9: "D5",
    10: "D6",
    11: "D7",
    12: "D8",
    13: "D9",
    14: "D10",
    15: "D11",
    16: "D12",
    17: "D13",
    18: "D14",
    19: "D15",
  });

  Rigol1000eWfm.TriggerModeEnum = Object.freeze({
    EDGE: 0,
    PULSE: 1,
    SLOPE: 2,
    VIDEO: 3,
    ALT: 4,
    PATTERN: 5,
    DURATION: 6,

    0: "EDGE",
    1: "PULSE",
    2: "SLOPE",
    3: "VIDEO",
    4: "ALT",
    5: "PATTERN",
    6: "DURATION",
  });

  Rigol1000eWfm.UnitEnum = Object.freeze({
    W: 0,
    A: 1,
    V: 2,
    U: 3,

    0: "W",
    1: "A",
    2: "V",
    3: "U",
  });

  function Rigol1000eWfm(_io, _parent, _root) {
    this._io = _io;
    this._parent = _parent;
    this._root = _root || this;

    this._read();
  }
  Rigol1000eWfm.prototype._read = function() {
  }

  var ChannelHeader = Rigol1000eWfm.ChannelHeader = (function() {
    function ChannelHeader(_io, _parent, _root) {
      this._io = _io;
      this._parent = _parent;
      this._root = _root;

      this._read();
    }
    ChannelHeader.prototype._read = function() {
      this.unknown0 = this._io.readU2le();
      this.scaleDisplay = this._io.readS4le();
      this.shiftDisplay = this._io.readS2le();
      this.unknown1 = this._io.readU1();
      this.unknown2 = this._io.readU1();
      this.probeValue = this._io.readF4le();
      this.invertDispVal = this._io.readU1();
      this.enabledVal = this._io.readU1();
      this.invertedMVal = this._io.readU1();
      this.unknown3 = this._io.readU1();
      this.scaleMeasured = this._io.readS4le();
      this.shiftMeasured = this._io.readS2le();
    }
    Object.defineProperty(ChannelHeader.prototype, 'enabled', {
      get: function() {
        if (this._m_enabled !== undefined)
          return this._m_enabled;
        this._m_enabled = (this.enabledVal != 0 ? true : false);
        return this._m_enabled;
      }
    });
    Object.defineProperty(ChannelHeader.prototype, 'inverted', {
      get: function() {
        if (this._m_inverted !== undefined)
          return this._m_inverted;
        this._m_inverted = (this.invertedMVal != 0 ? true : false);
        return this._m_inverted;
      }
    });
    Object.defineProperty(ChannelHeader.prototype, 'unit', {
      get: function() {
        if (this._m_unit !== undefined)
          return this._m_unit;
        this._m_unit = Rigol1000eWfm.UnitEnum.V;
        return this._m_unit;
      }
    });
    Object.defineProperty(ChannelHeader.prototype, 'voltOffset', {
      get: function() {
        if (this._m_voltOffset !== undefined)
          return this._m_voltOffset;
        this._m_voltOffset = this.shiftMeasured * this.voltScale;
        return this._m_voltOffset;
      }
    });
    Object.defineProperty(ChannelHeader.prototype, 'voltPerDivision', {
      get: function() {
        if (this._m_voltPerDivision !== undefined)
          return this._m_voltPerDivision;
        this._m_voltPerDivision = (this.inverted ? (-0.0000010 * this.scaleMeasured) * this.probeValue : (0.0000010 * this.scaleMeasured) * this.probeValue);
        return this._m_voltPerDivision;
      }
    });
    Object.defineProperty(ChannelHeader.prototype, 'voltScale', {
      get: function() {
        if (this._m_voltScale !== undefined)
          return this._m_voltScale;
        this._m_voltScale = ((0.0000010 * this.scaleMeasured) * this.probeValue) / 25.0;
        return this._m_voltScale;
      }
    });

    return ChannelHeader;
  })();

  var Header = Rigol1000eWfm.Header = (function() {
    function Header(_io, _parent, _root) {
      this._io = _io;
      this._parent = _parent;
      this._root = _root;

      this._read();
    }
    Header.prototype._read = function() {
      this.magic = this._io.readBytes(4);
      if (!((KaitaiStream.byteArrayCompare(this.magic, new Uint8Array([165, 165, 0, 0])) == 0))) {
        throw new KaitaiStream.ValidationNotEqualError(new Uint8Array([165, 165, 0, 0]), this.magic, this._io, "/types/header/seq/0");
      }
      this.unused1 = this._io.readU2le();
      this.blank10 = this._io.readBytes(10);
      if (!((KaitaiStream.byteArrayCompare(this.blank10, new Uint8Array([0, 0, 0, 0, 0, 0, 0, 0, 0, 0])) == 0))) {
        throw new KaitaiStream.ValidationNotEqualError(new Uint8Array([0, 0, 0, 0, 0, 0, 0, 0, 0, 0]), this.blank10, this._io, "/types/header/seq/2");
      }
      this.adcMode = this._io.readU1();
      this.padding2 = this._io.readBytes(3);
      if (!((KaitaiStream.byteArrayCompare(this.padding2, new Uint8Array([0, 0, 0])) == 0))) {
        throw new KaitaiStream.ValidationNotEqualError(new Uint8Array([0, 0, 0]), this.padding2, this._io, "/types/header/seq/4");
      }
      this.rollStop = this._io.readU4le();
      this.unused4 = this._io.readBytes(4);
      if (!((KaitaiStream.byteArrayCompare(this.unused4, new Uint8Array([0, 0, 0, 0])) == 0))) {
        throw new KaitaiStream.ValidationNotEqualError(new Uint8Array([0, 0, 0, 0]), this.unused4, this._io, "/types/header/seq/6");
      }
      this.ch1PointsTmp = this._io.readU4le();
      this.activeChannel = this._io.readU1();
      this.padding3 = this._io.readBytes(1);
      if (!((KaitaiStream.byteArrayCompare(this.padding3, new Uint8Array([0])) == 0))) {
        throw new KaitaiStream.ValidationNotEqualError(new Uint8Array([0]), this.padding3, this._io, "/types/header/seq/9");
      }
      this.ch = [];
      for (var i = 0; i < 2; i++) {
        this.ch.push(new ChannelHeader(this._io, this, this._root));
      }
      this.timeOffset = this._io.readU1();
      this.padding4 = this._io.readBytes(1);
      if (!((KaitaiStream.byteArrayCompare(this.padding4, new Uint8Array([0])) == 0))) {
        throw new KaitaiStream.ValidationNotEqualError(new Uint8Array([0]), this.padding4, this._io, "/types/header/seq/12");
      }
      this.time = new TimeHeader(this._io, this, this._root);
      this.logic = new LogicAnalyzerHeader(this._io, this, this._root);
      this.triggerMode = this._io.readU1();
      this.trigger1 = new TriggerHeader(this._io, this, this._root);
      this.trigger2 = new TriggerHeader(this._io, this, this._root);
      this.padding6 = this._io.readBytes(9);
      if (!((KaitaiStream.byteArrayCompare(this.padding6, new Uint8Array([0, 0, 0, 0, 0, 0, 0, 0, 0])) == 0))) {
        throw new KaitaiStream.ValidationNotEqualError(new Uint8Array([0, 0, 0, 0, 0, 0, 0, 0, 0]), this.padding6, this._io, "/types/header/seq/18");
      }
      this.ch2PointsTmp = this._io.readU4le();
      this.time2 = new TimeHeader(this._io, this, this._root);
      this.laSampleRate = this._io.readF4le();
    }

    /**
     * Analog acquisition depth stored for channel 1.
     */
    Object.defineProperty(Header.prototype, 'ch1MemoryDepth', {
      get: function() {
        if (this._m_ch1MemoryDepth !== undefined)
          return this._m_ch1MemoryDepth;
        this._m_ch1MemoryDepth = this.ch1PointsTmp;
        return this._m_ch1MemoryDepth;
      }
    });

    /**
     * Valid channel 1 samples after trimming rolling-mode padding.
     */
    Object.defineProperty(Header.prototype, 'ch1Points', {
      get: function() {
        if (this._m_ch1Points !== undefined)
          return this._m_ch1Points;
        this._m_ch1Points = this.ch1MemoryDepth - this.ch1Skip;
        return this._m_ch1Points;
      }
    });

    /**
     * In rolling mode, firmware keeps invalid bytes after the valid samples.
     */
    Object.defineProperty(Header.prototype, 'ch1Skip', {
      get: function() {
        if (this._m_ch1Skip !== undefined)
          return this._m_ch1Skip;
        this._m_ch1Skip = (this.rollStop == 0 ? 0 : this.rollStop + 2);
        return this._m_ch1Skip;
      }
    });
    Object.defineProperty(Header.prototype, 'ch1TimeOffset', {
      get: function() {
        if (this._m_ch1TimeOffset !== undefined)
          return this._m_ch1TimeOffset;
        this._m_ch1TimeOffset = 1.0E-12 * this.time.offsetMeasured;
        return this._m_ch1TimeOffset;
      }
    });
    Object.defineProperty(Header.prototype, 'ch1TimeScale', {
      get: function() {
        if (this._m_ch1TimeScale !== undefined)
          return this._m_ch1TimeScale;
        this._m_ch1TimeScale = 1.0E-12 * this.time.scaleMeasured;
        return this._m_ch1TimeScale;
      }
    });

    /**
     * Channel 2 depth is omitted by some files and then matches channel 1.
     */
    Object.defineProperty(Header.prototype, 'ch2MemoryDepth', {
      get: function() {
        if (this._m_ch2MemoryDepth !== undefined)
          return this._m_ch2MemoryDepth;
        this._m_ch2MemoryDepth = ( ((this.ch[1].enabled) && (this.ch2PointsTmp == 0))  ? this.ch1PointsTmp : this.ch2PointsTmp);
        return this._m_ch2MemoryDepth;
      }
    });

    /**
     * Valid channel 2 samples after trimming rolling-mode padding.
     */
    Object.defineProperty(Header.prototype, 'ch2Points', {
      get: function() {
        if (this._m_ch2Points !== undefined)
          return this._m_ch2Points;
        this._m_ch2Points = this.ch2MemoryDepth - this.ch1Skip;
        return this._m_ch2Points;
      }
    });
    Object.defineProperty(Header.prototype, 'ch2TimeOffset', {
      get: function() {
        if (this._m_ch2TimeOffset !== undefined)
          return this._m_ch2TimeOffset;
        this._m_ch2TimeOffset = (this.triggerMode == Rigol1000eWfm.TriggerModeEnum.ALT ? 1.0E-12 * this.time2.offsetMeasured : this.ch1TimeOffset);
        return this._m_ch2TimeOffset;
      }
    });
    Object.defineProperty(Header.prototype, 'ch2TimeScale', {
      get: function() {
        if (this._m_ch2TimeScale !== undefined)
          return this._m_ch2TimeScale;
        this._m_ch2TimeScale = (this.triggerMode == Rigol1000eWfm.TriggerModeEnum.ALT ? 1.0E-12 * this.time2.scaleMeasured : this.ch1TimeScale);
        return this._m_ch2TimeScale;
      }
    });

    /**
     * Logic samples are stored as `u2` values. The format note lists a
     * 16K logic block for an 8K analog depth and a 1M block for a 512K
     * analog depth, so the logic section is `2 * ch1_memory_depth` bytes.
     */
    Object.defineProperty(Header.prototype, 'logicWords', {
      get: function() {
        if (this._m_logicWords !== undefined)
          return this._m_logicWords;
        this._m_logicWords = (this.logic.enabled ? this.ch1MemoryDepth : 0);
        return this._m_logicWords;
      }
    });
    Object.defineProperty(Header.prototype, 'sampleRateHz', {
      get: function() {
        if (this._m_sampleRateHz !== undefined)
          return this._m_sampleRateHz;
        this._m_sampleRateHz = this.time.sampleRateHz;
        return this._m_sampleRateHz;
      }
    });
    Object.defineProperty(Header.prototype, 'secondsPerPoint', {
      get: function() {
        if (this._m_secondsPerPoint !== undefined)
          return this._m_secondsPerPoint;
        this._m_secondsPerPoint = 1 / this.sampleRateHz;
        return this._m_secondsPerPoint;
      }
    });

    /**
     * Does not exist in early formats, unsure how to detect if missing
     */

    return Header;
  })();

  var LogicAnalyzerHeader = Rigol1000eWfm.LogicAnalyzerHeader = (function() {
    function LogicAnalyzerHeader(_io, _parent, _root) {
      this._io = _io;
      this._parent = _parent;
      this._root = _root;

      this._read();
    }
    LogicAnalyzerHeader.prototype._read = function() {
      this.unused = this._io.readBitsIntBe(7);
      this.enabled = this._io.readBitsIntBe(1) != 0;
      this._io.alignToByte();
      this.activeChannel = this._io.readU1();
      this.enabledChannels = this._io.readU2le();
      this.position = this._io.readBytes(16);
      this.group8to15size = this._io.readU1();
      this.group0to7size = this._io.readU1();
    }

    /**
     * Should be 0 to 16
     */

    /**
     * Each bit corresponds to one enabled channel
     */

    /**
     * Should be 7-15
     */

    /**
     * Should be 7-15
     */

    return LogicAnalyzerHeader;
  })();

  var RawData = Rigol1000eWfm.RawData = (function() {
    function RawData(_io, _parent, _root) {
      this._io = _io;
      this._parent = _parent;
      this._root = _root;

      this._read();
    }
    RawData.prototype._read = function() {
      if (this._root.header.ch[0].enabled) {
        this.ch1 = this._io.readBytes(this._root.header.ch1Points);
      }
      if (this._root.header.ch[0].enabled) {
        this.rollStopPadding1 = this._io.readBytes(this._root.header.ch1Skip);
      }
      if (this._root.header.ch[1].enabled) {
        this.ch2 = this._io.readBytes(this._root.header.ch2Points);
      }
      if (this._root.header.ch[1].enabled) {
        this.rollStopPadding2 = this._io.readBytes(this._root.header.ch1Skip);
      }
      this.logic = [];
      for (var i = 0; i < this._root.header.logicWords; i++) {
        this.logic.push(this._io.readU2le());
      }
    }

    /**
     * Logic analyzer samples follow the analog blocks as u2 values.
     */

    return RawData;
  })();

  var TimeHeader = Rigol1000eWfm.TimeHeader = (function() {
    function TimeHeader(_io, _parent, _root) {
      this._io = _io;
      this._parent = _parent;
      this._root = _root;

      this._read();
    }
    TimeHeader.prototype._read = function() {
      this.scaleDisplay = this._io.readS8le();
      this.offsetDisplay = this._io.readS8le();
      this.sampleRateHz = this._io.readF4le();
      this.scaleMeasured = this._io.readS8le();
      this.offsetMeasured = this._io.readS8le();
    }

    return TimeHeader;
  })();

  var TriggerHeader = Rigol1000eWfm.TriggerHeader = (function() {
    function TriggerHeader(_io, _parent, _root) {
      this._io = _io;
      this._parent = _parent;
      this._root = _root;

      this._read();
    }
    TriggerHeader.prototype._read = function() {
      this.mode = this._io.readU1();
      this.source = this._io.readU1();
      this.coupling = this._io.readU1();
      this.sweep = this._io.readU1();
      this.padding1 = this._io.readBytes(1);
      if (!((KaitaiStream.byteArrayCompare(this.padding1, new Uint8Array([0])) == 0))) {
        throw new KaitaiStream.ValidationNotEqualError(new Uint8Array([0]), this.padding1, this._io, "/types/trigger_header/seq/4");
      }
      this.sens = this._io.readF4le();
      this.holdoff = this._io.readF4le();
      this.level = this._io.readF4le();
      this.direct = this._io.readU1();
      this.pulseType = this._io.readU1();
      this.padding2 = this._io.readBytes(2);
      if (!((KaitaiStream.byteArrayCompare(this.padding2, new Uint8Array([0, 0])) == 0))) {
        throw new KaitaiStream.ValidationNotEqualError(new Uint8Array([0, 0]), this.padding2, this._io, "/types/trigger_header/seq/10");
      }
      this.pulseWidth = this._io.readF4le();
      this.slopeType = this._io.readU1();
      this.padding3 = this._io.readBytes(3);
      if (!((KaitaiStream.byteArrayCompare(this.padding3, new Uint8Array([0, 0, 0])) == 0))) {
        throw new KaitaiStream.ValidationNotEqualError(new Uint8Array([0, 0, 0]), this.padding3, this._io, "/types/trigger_header/seq/13");
      }
      this.lower = this._io.readF4le();
      this.slopeWidth = this._io.readF4le();
      this.videoPol = this._io.readU1();
      this.videoSync = this._io.readU1();
      this.videoStd = this._io.readU1();
    }

    return TriggerHeader;
  })();
  Object.defineProperty(Rigol1000eWfm.prototype, 'data', {
    get: function() {
      if (this._m_data !== undefined)
        return this._m_data;
      var _pos = this._io.pos;
      this._io.seek(276);
      this._m_data = new RawData(this._io, this, this._root);
      this._io.seek(_pos);
      return this._m_data;
    }
  });
  Object.defineProperty(Rigol1000eWfm.prototype, 'header', {
    get: function() {
      if (this._m_header !== undefined)
        return this._m_header;
      var _pos = this._io.pos;
      this._io.seek(0);
      this._m_header = new Header(this._io, this, this._root);
      this._io.seek(_pos);
      return this._m_header;
    }
  });

  return Rigol1000eWfm;
})();
Rigol1000eWfm_.Rigol1000eWfm = Rigol1000eWfm;
});
