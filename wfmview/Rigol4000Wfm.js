// This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild

(function (root, factory) {
  if (typeof define === 'function' && define.amd) {
    define(['exports', 'kaitai-struct/KaitaiStream'], factory);
  } else if (typeof exports === 'object' && exports !== null && typeof exports.nodeType !== 'number') {
    factory(exports, require('kaitai-struct/KaitaiStream'));
  } else {
    factory(root.Rigol4000Wfm || (root.Rigol4000Wfm = {}), root.KaitaiStream);
  }
})(typeof self !== 'undefined' ? self : this, function (Rigol4000Wfm_, KaitaiStream) {
var Rigol4000Wfm = (function() {
  Rigol4000Wfm.AcquisitionEnum = Object.freeze({
    NORMAL: 0,
    AVERAGE: 1,
    PEAK: 2,
    HIGH_RESOLUTION: 3,

    0: "NORMAL",
    1: "AVERAGE",
    2: "PEAK",
    3: "HIGH_RESOLUTION",
  });

  Rigol4000Wfm.BandwidthEnum = Object.freeze({
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

  Rigol4000Wfm.CouplingEnum = Object.freeze({
    DC: 0,
    AC: 1,
    GND: 2,

    0: "DC",
    1: "AC",
    2: "GND",
  });

  Rigol4000Wfm.FilterEnum = Object.freeze({
    LOW_PASS: 0,
    HIGH_PASS: 1,
    BAND_PASS: 2,
    BAND_REJECT: 3,

    0: "LOW_PASS",
    1: "HIGH_PASS",
    2: "BAND_PASS",
    3: "BAND_REJECT",
  });

  Rigol4000Wfm.ImpedanceEnum = Object.freeze({
    OHM_50: 0,
    OHM_1MEG: 1,

    0: "OHM_50",
    1: "OHM_1MEG",
  });

  Rigol4000Wfm.MemDepthEnum = Object.freeze({
    AUTO: 0,
    P_7K: 1,
    P_70K: 2,
    P_700K: 3,
    P_7M: 4,
    P_70M: 5,
    P_14K: 6,
    P_140K: 7,
    P_1M4: 8,
    P_14M: 9,
    P_140M: 10,

    0: "AUTO",
    1: "P_7K",
    2: "P_70K",
    3: "P_700K",
    4: "P_7M",
    5: "P_70M",
    6: "P_14K",
    7: "P_140K",
    8: "P_1M4",
    9: "P_14M",
    10: "P_140M",
  });

  Rigol4000Wfm.ProbeEnum = Object.freeze({
    SINGLE: 0,
    DIFF: 1,

    0: "SINGLE",
    1: "DIFF",
  });

  Rigol4000Wfm.ProbeRatioEnum = Object.freeze({
    X0_01: 0,
    X0_02: 1,
    X0_05: 2,
    X0_1: 3,
    X0_2: 4,
    X0_5: 5,
    X1: 6,
    X2: 7,
    X5: 8,
    X10: 9,
    X20: 10,
    X50: 11,
    X100: 12,
    X200: 13,
    X500: 14,
    X1000: 15,

    0: "X0_01",
    1: "X0_02",
    2: "X0_05",
    3: "X0_1",
    4: "X0_2",
    5: "X0_5",
    6: "X1",
    7: "X2",
    8: "X5",
    9: "X10",
    10: "X20",
    11: "X50",
    12: "X100",
    13: "X200",
    14: "X500",
    15: "X1000",
  });

  Rigol4000Wfm.ProbeTypeEnum = Object.freeze({
    NORMAL_TYPE: 0,
    DIFFERENTIAL: 1,

    0: "NORMAL_TYPE",
    1: "DIFFERENTIAL",
  });

  Rigol4000Wfm.TimeEnum = Object.freeze({
    YT: 0,
    XY: 1,
    ROLL: 2,

    0: "YT",
    1: "XY",
    2: "ROLL",
  });

  Rigol4000Wfm.TriggerModeEnum = Object.freeze({
    EDGE: 3,
    VIDEO: 4,

    3: "EDGE",
    4: "VIDEO",
  });

  Rigol4000Wfm.TriggerSourceEnum = Object.freeze({
    CH1: 1,
    CH2: 2,
    CH3: 3,
    CH4: 4,
    EXT: 5,

    1: "CH1",
    2: "CH2",
    3: "CH3",
    4: "CH4",
    5: "EXT",
  });

  Rigol4000Wfm.UnitEnum = Object.freeze({
    W: 0,
    A: 1,
    V: 2,
    U: 3,

    0: "W",
    1: "A",
    2: "V",
    3: "U",
  });

  function Rigol4000Wfm(_io, _parent, _root) {
    this._io = _io;
    this._parent = _parent;
    this._root = _root || this;

    this._read();
  }
  Rigol4000Wfm.prototype._read = function() {
  }

  var ChannelHeader = Rigol4000Wfm.ChannelHeader = (function() {
    function ChannelHeader(_io, _parent, _root) {
      this._io = _io;
      this._parent = _parent;
      this._root = _root;

      this._read();
    }
    ChannelHeader.prototype._read = function() {
      this.enabledVal = this._io.readU1();
      this.coupling = this._io.readU1();
      this.bandwidthLimit = this._io.readU1();
      this.probeType = this._io.readU1();
      this.probeRatio = this._io.readU1();
      this.probeDiff = this._io.readU1();
      this.probeSignal = this._io.readU1();
      this.probeImpedance = this._io.readU1();
      this.voltPerDivision = this._io.readF4le();
      this.voltOffset = this._io.readF4le();
      this.invertedVal = this._io.readU1();
      this.unit = this._io.readU1();
      this.filterEnabled = this._io.readU1();
      this.filterType = this._io.readU1();
      this.filterHigh = this._io.readU4le();
      this.filterLow = this._io.readU4le();
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
        this._m_inverted = (this.invertedVal != 0 ? true : false);
        return this._m_inverted;
      }
    });
    Object.defineProperty(ChannelHeader.prototype, 'probeValue', {
      get: function() {
        if (this._m_probeValue !== undefined)
          return this._m_probeValue;
        this._m_probeValue = (this.probeRatio == Rigol4000Wfm.ProbeRatioEnum.X0_01 ? 0.01 : (this.probeRatio == Rigol4000Wfm.ProbeRatioEnum.X0_02 ? 0.02 : (this.probeRatio == Rigol4000Wfm.ProbeRatioEnum.X0_05 ? 0.05 : (this.probeRatio == Rigol4000Wfm.ProbeRatioEnum.X0_1 ? 0.1 : (this.probeRatio == Rigol4000Wfm.ProbeRatioEnum.X0_2 ? 0.2 : (this.probeRatio == Rigol4000Wfm.ProbeRatioEnum.X0_5 ? 0.5 : (this.probeRatio == Rigol4000Wfm.ProbeRatioEnum.X1 ? 1.0 : (this.probeRatio == Rigol4000Wfm.ProbeRatioEnum.X2 ? 2.0 : (this.probeRatio == Rigol4000Wfm.ProbeRatioEnum.X5 ? 5.0 : (this.probeRatio == Rigol4000Wfm.ProbeRatioEnum.X10 ? 10.0 : (this.probeRatio == Rigol4000Wfm.ProbeRatioEnum.X20 ? 20.0 : (this.probeRatio == Rigol4000Wfm.ProbeRatioEnum.X50 ? 50.0 : (this.probeRatio == Rigol4000Wfm.ProbeRatioEnum.X100 ? 100.0 : (this.probeRatio == Rigol4000Wfm.ProbeRatioEnum.X200 ? 200.0 : (this.probeRatio == Rigol4000Wfm.ProbeRatioEnum.X500 ? 500.0 : 1000.0)))))))))))))));
        return this._m_probeValue;
      }
    });
    Object.defineProperty(ChannelHeader.prototype, 'voltScale', {
      get: function() {
        if (this._m_voltScale !== undefined)
          return this._m_voltScale;
        this._m_voltScale = (this._root.header.modelNumber.substring(2, 3) == "2" ? this.voltSigned / 25.0 : this.voltSigned / 32.0);
        return this._m_voltScale;
      }
    });
    Object.defineProperty(ChannelHeader.prototype, 'voltSigned', {
      get: function() {
        if (this._m_voltSigned !== undefined)
          return this._m_voltSigned;
        this._m_voltSigned = (this.inverted ? -1.0 * this.voltPerDivision : 1.0 * this.voltPerDivision);
        return this._m_voltSigned;
      }
    });

    return ChannelHeader;
  })();

  var ChannelMask = Rigol4000Wfm.ChannelMask = (function() {
    function ChannelMask(_io, _parent, _root) {
      this._io = _io;
      this._parent = _parent;
      this._root = _root;

      this._read();
    }
    ChannelMask.prototype._read = function() {
      this.unused = this._io.readBitsIntBe(4);
      this.channel4 = this._io.readBitsIntBe(1) != 0;
      this.channel3 = this._io.readBitsIntBe(1) != 0;
      this.channel2 = this._io.readBitsIntBe(1) != 0;
      this.channel1 = this._io.readBitsIntBe(1) != 0;
    }

    return ChannelMask;
  })();

  var Header = Rigol4000Wfm.Header = (function() {
    function Header(_io, _parent, _root) {
      this._io = _io;
      this._parent = _parent;
      this._root = _root;

      this._read();
    }
    Header.prototype._read = function() {
      this.magic = this._io.readBytes(4);
      if (!((KaitaiStream.byteArrayCompare(this.magic, new Uint8Array([165, 165, 56, 0])) == 0))) {
        throw new KaitaiStream.ValidationNotEqualError(new Uint8Array([165, 165, 56, 0]), this.magic, this._io, "/types/header/seq/0");
      }
      this.modelNumber = KaitaiStream.bytesToStr(KaitaiStream.bytesTerminate(this._io.readBytes(20), 0, false), "ASCII");
      this.firmwareVersion = KaitaiStream.bytesToStr(KaitaiStream.bytesTerminate(this._io.readBytes(20), 0, false), "ASCII");
      this.unknown1 = [];
      for (var i = 0; i < 5; i++) {
        this.unknown1.push(this._io.readU4le());
      }
      this.enabled = new ChannelMask(this._io, this, this._root);
      this.unknown2 = this._io.readBytes(3);
      this.position = new PositionType(this._io, this, this._root);
      this.unknown3 = this._io.readU4le();
      this.unknown4 = this._io.readU4le();
      this.unknown5 = this._io.readU4le();
      this.memDepth1 = this._io.readU4le();
      this.sampleRateHz = this._io.readF4le();
      this.unknown8 = this._io.readU4le();
      this.timePerDivPs = this._io.readU8le();
      this.unknown9 = [];
      for (var i = 0; i < 2; i++) {
        this.unknown9.push(this._io.readU4le());
      }
      this.ch = [];
      for (var i = 0; i < 4; i++) {
        this.ch.push(new ChannelHeader(this._io, this, this._root));
      }
      this.unknown33 = [];
      for (var i = 0; i < 6; i++) {
        this.unknown33.push(this._io.readU4le());
      }
      this.memDepth2 = this._io.readU4le();
      this.unknown37 = this._io.readBytes(4);
      this.memDepth = this._io.readU4le();
      this.unknown38 = [];
      for (var i = 0; i < 9; i++) {
        this.unknown38.push(this._io.readU4le());
      }
      this.bytesPerChannel1 = this._io.readU4le();
      this.bytesPerChannel2 = this._io.readU4le();
      this.unknown42 = [];
      for (var i = 0; i < 41; i++) {
        this.unknown42.push(this._io.readU4le());
      }
      this.totalSamples = this._io.readU4le();
      this.unknown57 = [];
      for (var i = 0; i < 4; i++) {
        this.unknown57.push(this._io.readU4le());
      }
      this.memDepthType = this._io.readU1();
      this.unknown60 = this._io.readBytes(27);
      this.time = new TimeHeader(this._io, this, this._root);
    }
    Object.defineProperty(Header.prototype, 'dataStart', {
      get: function() {
        if (this._m_dataStart !== undefined)
          return this._m_dataStart;
        this._m_dataStart = (this.position.channel1 != 0 ? this.position.channel1 : (this.position.channel2 != 0 ? this.position.channel2 : (this.position.channel3 != 0 ? this.position.channel3 : this.position.channel4)));
        return this._m_dataStart;
      }
    });
    Object.defineProperty(Header.prototype, 'lenRaw1', {
      get: function() {
        if (this._m_lenRaw1 !== undefined)
          return this._m_lenRaw1;
        this._m_lenRaw1 = (this.enabled.channel1 ? this.memDepth : 0);
        return this._m_lenRaw1;
      }
    });
    Object.defineProperty(Header.prototype, 'lenRaw2', {
      get: function() {
        if (this._m_lenRaw2 !== undefined)
          return this._m_lenRaw2;
        this._m_lenRaw2 = (this.enabled.channel2 ? this.memDepth : 0);
        return this._m_lenRaw2;
      }
    });
    Object.defineProperty(Header.prototype, 'lenRaw3', {
      get: function() {
        if (this._m_lenRaw3 !== undefined)
          return this._m_lenRaw3;
        this._m_lenRaw3 = (this.enabled.channel3 ? this.memDepth : 0);
        return this._m_lenRaw3;
      }
    });
    Object.defineProperty(Header.prototype, 'lenRaw4', {
      get: function() {
        if (this._m_lenRaw4 !== undefined)
          return this._m_lenRaw4;
        this._m_lenRaw4 = (this.enabled.channel4 ? this.memDepth : 0);
        return this._m_lenRaw4;
      }
    });
    Object.defineProperty(Header.prototype, 'points', {
      get: function() {
        if (this._m_points !== undefined)
          return this._m_points;
        this._m_points = this.memDepth;
        return this._m_points;
      }
    });
    Object.defineProperty(Header.prototype, 'raw1', {
      get: function() {
        if (this._m_raw1 !== undefined)
          return this._m_raw1;
        if (this.enabled.channel1) {
          var io = this._root._io;
          var _pos = io.pos;
          io.seek(this.position.channel1);
          this._m_raw1 = io.readBytes(this.lenRaw1);
          io.seek(_pos);
        }
        return this._m_raw1;
      }
    });
    Object.defineProperty(Header.prototype, 'raw2', {
      get: function() {
        if (this._m_raw2 !== undefined)
          return this._m_raw2;
        if (this.enabled.channel2) {
          var io = this._root._io;
          var _pos = io.pos;
          io.seek(this.position.channel2);
          this._m_raw2 = io.readBytes(this.lenRaw2);
          io.seek(_pos);
        }
        return this._m_raw2;
      }
    });
    Object.defineProperty(Header.prototype, 'raw3', {
      get: function() {
        if (this._m_raw3 !== undefined)
          return this._m_raw3;
        if (this.enabled.channel3) {
          var io = this._root._io;
          var _pos = io.pos;
          io.seek(this.position.channel3);
          this._m_raw3 = io.readBytes(this.lenRaw3);
          io.seek(_pos);
        }
        return this._m_raw3;
      }
    });
    Object.defineProperty(Header.prototype, 'raw4', {
      get: function() {
        if (this._m_raw4 !== undefined)
          return this._m_raw4;
        if (this.enabled.channel4) {
          var io = this._root._io;
          var _pos = io.pos;
          io.seek(this.position.channel4);
          this._m_raw4 = io.readBytes(this.lenRaw4);
          io.seek(_pos);
        }
        return this._m_raw4;
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
    Object.defineProperty(Header.prototype, 'serialNumber', {
      get: function() {
        if (this._m_serialNumber !== undefined)
          return this._m_serialNumber;
        this._m_serialNumber = this.modelNumber;
        return this._m_serialNumber;
      }
    });
    Object.defineProperty(Header.prototype, 'setup', {
      get: function() {
        if (this._m_setup !== undefined)
          return this._m_setup;
        var _pos = this._io.pos;
        this._io.seek(597);
        this._raw__m_setup = this._io.readBytes(this.dataStart - 597);
        var _io__raw__m_setup = new KaitaiStream(this._raw__m_setup);
        this._m_setup = new SetupBlock(_io__raw__m_setup, this, this._root);
        this._io.seek(_pos);
        return this._m_setup;
      }
    });
    Object.defineProperty(Header.prototype, 'timeOffset', {
      get: function() {
        if (this._m_timeOffset !== undefined)
          return this._m_timeOffset;
        this._m_timeOffset = 1.0E-12 * this.time.actualOffsetPs;
        return this._m_timeOffset;
      }
    });
    Object.defineProperty(Header.prototype, 'timeScale', {
      get: function() {
        if (this._m_timeScale !== undefined)
          return this._m_timeScale;
        this._m_timeScale = 1.0E-12 * this.time.timePerDivPs;
        return this._m_timeScale;
      }
    });
    Object.defineProperty(Header.prototype, 'verticalScaleFactor', {
      get: function() {
        if (this._m_verticalScaleFactor !== undefined)
          return this._m_verticalScaleFactor;
        this._m_verticalScaleFactor = (this.modelNumber.substring(2, 3) == "2" ? 25 : 32);
        return this._m_verticalScaleFactor;
      }
    });

    /**
     * The last two bytes is the size of the header 0x38=56
     */

    /**
     * one byte with lower bits indicating which channels are active
     */

    return Header;
  })();

  var PositionType = Rigol4000Wfm.PositionType = (function() {
    function PositionType(_io, _parent, _root) {
      this._io = _io;
      this._parent = _parent;
      this._root = _root;

      this._read();
    }
    PositionType.prototype._read = function() {
      this.channel1 = this._io.readU4le();
      this.channel2 = this._io.readU4le();
      this.channel3 = this._io.readU4le();
      this.channel4 = this._io.readU4le();
    }

    return PositionType;
  })();

  var SetupBlock = Rigol4000Wfm.SetupBlock = (function() {
    function SetupBlock(_io, _parent, _root) {
      this._io = _io;
      this._parent = _parent;
      this._root = _root;

      this._read();
    }
    SetupBlock.prototype._read = function() {
    }
    Object.defineProperty(SetupBlock.prototype, 'legacyTriggerLevels', {
      get: function() {
        if (this._m_legacyTriggerLevels !== undefined)
          return this._m_legacyTriggerLevels;
        if (this._io.size >= 558) {
          var _pos = this._io.pos;
          this._io.seek(538);
          this._m_legacyTriggerLevels = new TriggerLevelBlock(this._io, this, this._root);
          this._io.seek(_pos);
        }
        return this._m_legacyTriggerLevels;
      }
    });
    Object.defineProperty(SetupBlock.prototype, 'modernTriggerLevels', {
      get: function() {
        if (this._m_modernTriggerLevels !== undefined)
          return this._m_modernTriggerLevels;
        if (this._io.size >= 606) {
          var _pos = this._io.pos;
          this._io.seek(586);
          this._m_modernTriggerLevels = new TriggerLevelBlock(this._io, this, this._root);
          this._io.seek(_pos);
        }
        return this._m_modernTriggerLevels;
      }
    });
    Object.defineProperty(SetupBlock.prototype, 'modernTriggerMode', {
      get: function() {
        if (this._m_modernTriggerMode !== undefined)
          return this._m_modernTriggerMode;
        if (this._io.size >= 611) {
          var _pos = this._io.pos;
          this._io.seek(610);
          this._m_modernTriggerMode = this._io.readU1();
          this._io.seek(_pos);
        }
        return this._m_modernTriggerMode;
      }
    });
    Object.defineProperty(SetupBlock.prototype, 'modernTriggerSource', {
      get: function() {
        if (this._m_modernTriggerSource !== undefined)
          return this._m_modernTriggerSource;
        if (this._io.size >= 624) {
          var _pos = this._io.pos;
          this._io.seek(623);
          this._m_modernTriggerSource = this._io.readU1();
          this._io.seek(_pos);
        }
        return this._m_modernTriggerSource;
      }
    });

    return SetupBlock;
  })();

  var TimeHeader = Rigol4000Wfm.TimeHeader = (function() {
    function TimeHeader(_io, _parent, _root) {
      this._io = _io;
      this._parent = _parent;
      this._root = _root;

      this._read();
    }
    TimeHeader.prototype._read = function() {
      this.unknown1 = this._io.readU2le();
      this.unknown2 = this._io.readBytes(10);
      this.index = this._io.readU4le();
      this.timePerDivPs = this._io.readU4le();
      this.unknown3a = this._io.readBytes(4);
      this.offsetPerDivPs = this._io.readU8le();
      this.unknown4Head = this._io.readBytes(8);
      this.actualOffsetPs = this._io.readS8le();
      this.offsetPs = this._io.readU8le();
      this.unknown5 = this._io.readBytes(16);
      this.unknown6 = this._io.readU2le();
      this.unknown7 = this._io.readU1();
    }

    return TimeHeader;
  })();

  var TriggerLevelBlock = Rigol4000Wfm.TriggerLevelBlock = (function() {
    function TriggerLevelBlock(_io, _parent, _root) {
      this._io = _io;
      this._parent = _parent;
      this._root = _root;

      this._read();
    }
    TriggerLevelBlock.prototype._read = function() {
      this.ch1LevelUv = this._io.readS4le();
      this.ch2LevelUv = this._io.readS4le();
      this.ch3LevelUv = this._io.readS4le();
      this.ch4LevelUv = this._io.readS4le();
      this.extLevelUv = this._io.readS4le();
    }

    return TriggerLevelBlock;
  })();
  Object.defineProperty(Rigol4000Wfm.prototype, 'header', {
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

  return Rigol4000Wfm;
})();
Rigol4000Wfm_.Rigol4000Wfm = Rigol4000Wfm;
});
