// This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild

(function (root, factory) {
  if (typeof define === 'function' && define.amd) {
    define(['exports', 'kaitai-struct/KaitaiStream'], factory);
  } else if (typeof exports === 'object' && exports !== null && typeof exports.nodeType !== 'number') {
    factory(exports, require('kaitai-struct/KaitaiStream'));
  } else {
    factory(root.Rigol2000Wfm || (root.Rigol2000Wfm = {}), root.KaitaiStream);
  }
})(typeof self !== 'undefined' ? self : this, function (Rigol2000Wfm_, KaitaiStream) {
/**
 * Rigol DS2000 / MSO2000 waveform file format.
 * 
 * Sources used for this KSY binary format: a document titled "WFM save format: Secretary Bird"
 * 
 * Tested file formats: real repo fixtures `DS2000-A.wfm`, `DS2000-B.wfm`, and
 * `DS2072A-1.wfm` through `DS2072A-9.wfm`, plus small header-window mutation
 * regressions built from those files.
 * 
 * Oscilloscope models this format may apply to: DS2000 family models c
 * `DS2072A`, `DS2102A`, `MSO2102A`,
 * `MSO2102A-S`, `DS2202A`, `MSO2202A`, `MSO2202A-S`, `DS2302A`, `MSO2302A`,
 * and `MSO2302A-S`.
 */

var Rigol2000Wfm = (function() {
  Rigol2000Wfm.AcquisitionEnum = Object.freeze({
    NORMAL: 0,
    AVERAGE: 1,
    PEAK: 2,
    HIGH_RESOLUTION: 3,

    0: "NORMAL",
    1: "AVERAGE",
    2: "PEAK",
    3: "HIGH_RESOLUTION",
  });

  Rigol2000Wfm.BandwidthEnum = Object.freeze({
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

  Rigol2000Wfm.CouplingEnum = Object.freeze({
    DC: 0,
    AC: 1,
    GND: 2,

    0: "DC",
    1: "AC",
    2: "GND",
  });

  Rigol2000Wfm.FilterEnum = Object.freeze({
    LOW_PASS: 0,
    HIGH_PASS: 1,
    BAND_PASS: 2,
    BAND_REJECT: 3,

    0: "LOW_PASS",
    1: "HIGH_PASS",
    2: "BAND_PASS",
    3: "BAND_REJECT",
  });

  Rigol2000Wfm.ImpedanceEnum = Object.freeze({
    OHM_50: 0,
    OHM_1MEG: 1,

    0: "OHM_50",
    1: "OHM_1MEG",
  });

  Rigol2000Wfm.ProbeEnum = Object.freeze({
    SINGLE: 0,
    DIFF: 1,

    0: "SINGLE",
    1: "DIFF",
  });

  Rigol2000Wfm.ProbeRatioEnum = Object.freeze({
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

  Rigol2000Wfm.ProbeTypeEnum = Object.freeze({
    NORMAL_TYPE: 0,
    DIFFERENTIAL: 1,

    0: "NORMAL_TYPE",
    1: "DIFFERENTIAL",
  });

  Rigol2000Wfm.SetupTriggerSourceEnum = Object.freeze({
    CH1: 0,
    CH2: 1,
    EXT: 2,
    AC_LINE: 3,

    0: "CH1",
    1: "CH2",
    2: "EXT",
    3: "AC_LINE",
  });

  Rigol2000Wfm.TimeEnum = Object.freeze({
    YT: 0,
    XY: 1,
    ROLL: 2,

    0: "YT",
    1: "XY",
    2: "ROLL",
  });

  Rigol2000Wfm.UnitEnum = Object.freeze({
    W: 0,
    A: 1,
    V: 2,
    U: 3,

    0: "W",
    1: "A",
    2: "V",
    3: "U",
  });

  function Rigol2000Wfm(_io, _parent, _root) {
    this._io = _io;
    this._parent = _parent;
    this._root = _root || this;

    this._read();
  }
  Rigol2000Wfm.prototype._read = function() {
  }

  var ChannelHeader = Rigol2000Wfm.ChannelHeader = (function() {
    function ChannelHeader(_io, _parent, _root) {
      this._io = _io;
      this._parent = _parent;
      this._root = _root;

      this._read();
    }
    ChannelHeader.prototype._read = function() {
      this.enabledTemp = this._io.readU1();
      this.couplingRaw = this._io.readU1();
      this.bandwidthLimit = this._io.readU1();
      this.probeType = this._io.readU1();
      this.probeRatioRaw = this._io.readU1();
      this.probeDiff = this._io.readU1();
      this.probeSignal = this._io.readU1();
      this.probeImpedanceRaw = this._io.readU1();
      this.voltPerDivision = this._io.readF4le();
      this.voltOffset = this._io.readF4le();
      this.invertedTemp = this._io.readU1();
      this.unitTemp = this._io.readU1();
      this.filterEnabled = this._io.readU1();
      this.filterType = this._io.readU1();
      this.filterHigh = this._io.readU4le();
      this.filterLow = this._io.readU4le();
    }
    Object.defineProperty(ChannelHeader.prototype, 'coupling', {
      get: function() {
        if (this._m_coupling !== undefined)
          return this._m_coupling;
        this._m_coupling = (this.couplingRaw >>> 6 == 0 ? Rigol2000Wfm.CouplingEnum.DC : (this.couplingRaw >>> 6 == 1 ? Rigol2000Wfm.CouplingEnum.AC : Rigol2000Wfm.CouplingEnum.GND));
        return this._m_coupling;
      }
    });
    Object.defineProperty(ChannelHeader.prototype, 'enabled', {
      get: function() {
        if (this._m_enabled !== undefined)
          return this._m_enabled;
        this._m_enabled = (this.enabledTemp != 0 ? true : false);
        return this._m_enabled;
      }
    });
    Object.defineProperty(ChannelHeader.prototype, 'inverted', {
      get: function() {
        if (this._m_inverted !== undefined)
          return this._m_inverted;
        this._m_inverted = (this.invertedActual == 1 ? true : false);
        return this._m_inverted;
      }
    });
    Object.defineProperty(ChannelHeader.prototype, 'invertedActual', {
      get: function() {
        if (this._m_invertedActual !== undefined)
          return this._m_invertedActual;
        this._m_invertedActual = (this.legacyVerticalLayout ? this.invertedTemp : this.unitTemp);
        return this._m_invertedActual;
      }
    });

    /**
     * The older DS2000 captures in this repo store invert/unit in the
     * documented order when bChanEn is 1.  The DS2072A captures instead
     * store unit first and use zeroed probe fields, so a small compatibility
     * shim is needed to recover the visible settings.
     */
    Object.defineProperty(ChannelHeader.prototype, 'legacyVerticalLayout', {
      get: function() {
        if (this._m_legacyVerticalLayout !== undefined)
          return this._m_legacyVerticalLayout;
        this._m_legacyVerticalLayout = (this.enabledTemp == 1 ? true : false);
        return this._m_legacyVerticalLayout;
      }
    });
    Object.defineProperty(ChannelHeader.prototype, 'probeImpedance', {
      get: function() {
        if (this._m_probeImpedance !== undefined)
          return this._m_probeImpedance;
        this._m_probeImpedance = ( ((!(this.legacyVerticalLayout)) && (this.probeRatioRaw == Rigol2000Wfm.ProbeRatioEnum.X0_01) && (this.probeImpedanceRaw == Rigol2000Wfm.ImpedanceEnum.OHM_50))  ? Rigol2000Wfm.ImpedanceEnum.OHM_1MEG : this.probeImpedanceRaw);
        return this._m_probeImpedance;
      }
    });
    Object.defineProperty(ChannelHeader.prototype, 'probeRatio', {
      get: function() {
        if (this._m_probeRatio !== undefined)
          return this._m_probeRatio;
        this._m_probeRatio = ( ((!(this.legacyVerticalLayout)) && (this.probeRatioRaw == Rigol2000Wfm.ProbeRatioEnum.X0_01) && (this.probeImpedanceRaw == Rigol2000Wfm.ImpedanceEnum.OHM_50))  ? Rigol2000Wfm.ProbeRatioEnum.X1 : this.probeRatioRaw);
        return this._m_probeRatio;
      }
    });
    Object.defineProperty(ChannelHeader.prototype, 'probeValue', {
      get: function() {
        if (this._m_probeValue !== undefined)
          return this._m_probeValue;
        this._m_probeValue = (this.probeRatio == Rigol2000Wfm.ProbeRatioEnum.X0_01 ? 0.01 : (this.probeRatio == Rigol2000Wfm.ProbeRatioEnum.X0_02 ? 0.02 : (this.probeRatio == Rigol2000Wfm.ProbeRatioEnum.X0_05 ? 0.05 : (this.probeRatio == Rigol2000Wfm.ProbeRatioEnum.X0_1 ? 0.1 : (this.probeRatio == Rigol2000Wfm.ProbeRatioEnum.X0_2 ? 0.2 : (this.probeRatio == Rigol2000Wfm.ProbeRatioEnum.X0_5 ? 0.5 : (this.probeRatio == Rigol2000Wfm.ProbeRatioEnum.X1 ? 1.0 : (this.probeRatio == Rigol2000Wfm.ProbeRatioEnum.X2 ? 2.0 : (this.probeRatio == Rigol2000Wfm.ProbeRatioEnum.X5 ? 5.0 : (this.probeRatio == Rigol2000Wfm.ProbeRatioEnum.X10 ? 10.0 : (this.probeRatio == Rigol2000Wfm.ProbeRatioEnum.X20 ? 20.0 : (this.probeRatio == Rigol2000Wfm.ProbeRatioEnum.X50 ? 50.0 : (this.probeRatio == Rigol2000Wfm.ProbeRatioEnum.X100 ? 100.0 : (this.probeRatio == Rigol2000Wfm.ProbeRatioEnum.X200 ? 200.0 : (this.probeRatio == Rigol2000Wfm.ProbeRatioEnum.X500 ? 500.0 : 1000.0)))))))))))))));
        return this._m_probeValue;
      }
    });
    Object.defineProperty(ChannelHeader.prototype, 'unit', {
      get: function() {
        if (this._m_unit !== undefined)
          return this._m_unit;
        this._m_unit = this.unitActual;
        return this._m_unit;
      }
    });
    Object.defineProperty(ChannelHeader.prototype, 'unitActual', {
      get: function() {
        if (this._m_unitActual !== undefined)
          return this._m_unitActual;
        this._m_unitActual = (this.legacyVerticalLayout ? this.unitTemp : this.invertedTemp);
        return this._m_unitActual;
      }
    });
    Object.defineProperty(ChannelHeader.prototype, 'voltScale', {
      get: function() {
        if (this._m_voltScale !== undefined)
          return this._m_voltScale;
        this._m_voltScale = this.voltSigned / 25.0;
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

    /**
     * Older DS2000 captures use 1 for enabled channels.  The shipped
     * DS2072A fixtures use 8 instead, so the parser treats any non-zero
     * value as enabled.
     */

    /**
     * The format note documents this as a byte, but the newer DS2072A
     * captures only use the upper bits for the published coupling mode.
     */

    return ChannelHeader;
  })();

  var ChannelMask = Rigol2000Wfm.ChannelMask = (function() {
    function ChannelMask(_io, _parent, _root) {
      this._io = _io;
      this._parent = _parent;
      this._root = _root;

      this._read();
    }
    ChannelMask.prototype._read = function() {
      this.unused1 = this._io.readBitsIntBe(4);
      this.channel4 = this._io.readBitsIntBe(1) != 0;
      this.channel3 = this._io.readBitsIntBe(1) != 0;
      this.channel2 = this._io.readBitsIntBe(1) != 0;
      this.channel1 = this._io.readBitsIntBe(1) != 0;
      this.unused2 = this._io.readBitsIntBe(7);
      this.interwoven = this._io.readBitsIntBe(1) != 0;
    }

    return ChannelMask;
  })();

  var Header = Rigol2000Wfm.Header = (function() {
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
      this.blockNum = this._io.readBytes(2);
      if (!((KaitaiStream.byteArrayCompare(this.blockNum, new Uint8Array([1, 0])) == 0))) {
        throw new KaitaiStream.ValidationNotEqualError(new Uint8Array([1, 0]), this.blockNum, this._io, "/types/header/seq/3");
      }
      this.fileVersion = this._io.readU2le();
      this.unused1 = this._io.readBytes(8);
      this.crc = this._io.readU4le();
      this.structureSize = this._io.readU2le();
      this.structureVersion = this._io.readU2le();
      this.enabled = new ChannelMask(this._io, this, this._root);
      this.extra1a = this._io.readBytes(2);
      this.channelOffset = [];
      for (var i = 0; i < 4; i++) {
        this.channelOffset.push(this._io.readU4le());
      }
      this.acquisitionMode = this._io.readU2le();
      this.averageTime = this._io.readU2le();
      this.sampleMode = this._io.readU2le();
      this.extra1b = this._io.readBytes(2);
      this.memDepth = this._io.readU4le();
      this.sampleRateHz = this._io.readF4le();
      this.extra1c = this._io.readBytes(2);
      this.timeMode = this._io.readU2le();
      this.timeScalePs = this._io.readU8le();
      this.timeOffsetPs = this._io.readS8le();
      this.ch = [];
      for (var i = 0; i < 4; i++) {
        this.ch.push(new ChannelHeader(this._io, this, this._root));
      }
      this.lenSetup = this._io.readU4le();
      this.setupOffset = this._io.readU4le();
      this.wfmOffset = this._io.readU4le();
      this.storageDepth = this._io.readU4le();
      this.zPtOffset = this._io.readU4le();
      this.wfmLen = this._io.readU4le();
      this.equCoarse = this._io.readU2le();
      this.equFine = this._io.readU2le();
      this.memStartAddr = [];
      for (var i = 0; i < 2; i++) {
        this.memStartAddr.push(this._io.readU4le());
      }
      this.memLastAddr = this._io.readU4le();
      this.memLength = this._io.readU4le();
      this.channelDepth = this._io.readU4le();
      this.bankSize = this._io.readU4le();
      this.bankOffset = this._io.readU4le();
      this.realOffset = this._io.readU4le();
      this.realChOffset = this._io.readU4le();
      this.horizSlowForceStopFrameBoolean = this._io.readU1();
      this.getSpuDigDataStatusBoolean = this._io.readU1();
      this.spuLoadDataStatusBoolean = this._io.readU1();
      this.reserved243 = this._io.readBytes(1);
      this.trigDelayMemOffset = this._io.readS8le();
      this.trigDelayViewOffset = this._io.readS8le();
      this.memOffsetCompensate = this._io.readS8le();
      this.slowDeltaWaveLength = this._io.readS8le();
      this.channelPosMaxDelay = this._io.readS8le();
      this.channelNegMinDelay = this._io.readS8le();
      this.realSaDotPeriod = this._io.readU8le();
      this.memOffsetBase = this._io.readU8le();
      this.trigTypeDeltaDelay = this._io.readS4le();
      this.ch1Delay = this._io.readS4le();
      this.ch2Delay = this._io.readS4le();
      this.channelDelayToMemLen = this._io.readU4le();
      this.spuMemBankSize = this._io.readU4le();
      this.rollScrnWaveLength = this._io.readU2le();
      this.triggerSource = this._io.readU1();
      this.calIndex = this._io.readU1();
      this.recordFrameIndex = this._io.readU4le();
      this.frameCur = this._io.readU4le();
      this.private = [];
      for (var i = 0; i < 4; i++) {
        this.private.push(this._io.readU4le());
      }
    }
    Object.defineProperty(Header.prototype, 'lenRaw1', {
      get: function() {
        if (this._m_lenRaw1 !== undefined)
          return this._m_lenRaw1;
        this._m_lenRaw1 = (this.channelOffset[0] > 0 ? this.rawDepth : 0);
        return this._m_lenRaw1;
      }
    });
    Object.defineProperty(Header.prototype, 'lenRaw2', {
      get: function() {
        if (this._m_lenRaw2 !== undefined)
          return this._m_lenRaw2;
        this._m_lenRaw2 = (this.channelOffset[1] > 0 ? this.rawDepth : 0);
        return this._m_lenRaw2;
      }
    });
    Object.defineProperty(Header.prototype, 'lenRaw3', {
      get: function() {
        if (this._m_lenRaw3 !== undefined)
          return this._m_lenRaw3;
        this._m_lenRaw3 = (this.channelOffset[2] > 0 ? this.rawDepth : 0);
        return this._m_lenRaw3;
      }
    });
    Object.defineProperty(Header.prototype, 'lenRaw4', {
      get: function() {
        if (this._m_lenRaw4 !== undefined)
          return this._m_lenRaw4;
        this._m_lenRaw4 = (this.channelOffset[3] > 0 ? this.rawDepth : 0);
        return this._m_lenRaw4;
      }
    });
    Object.defineProperty(Header.prototype, 'points', {
      get: function() {
        if (this._m_points !== undefined)
          return this._m_points;
        this._m_points = this.wfmLen;
        return this._m_points;
      }
    });
    Object.defineProperty(Header.prototype, 'raw1', {
      get: function() {
        if (this._m_raw1 !== undefined)
          return this._m_raw1;
        if (this.channelOffset[0] > 0) {
          var _pos = this._io.pos;
          this._io.seek(this.channelOffset[0] + this.zPtOffset);
          this._m_raw1 = this._io.readBytes(this.lenRaw1);
          this._io.seek(_pos);
        }
        return this._m_raw1;
      }
    });
    Object.defineProperty(Header.prototype, 'raw2', {
      get: function() {
        if (this._m_raw2 !== undefined)
          return this._m_raw2;
        if (this.channelOffset[1] > 0) {
          var _pos = this._io.pos;
          this._io.seek(this.channelOffset[1] + this.zPtOffset);
          this._m_raw2 = this._io.readBytes(this.lenRaw2);
          this._io.seek(_pos);
        }
        return this._m_raw2;
      }
    });
    Object.defineProperty(Header.prototype, 'raw3', {
      get: function() {
        if (this._m_raw3 !== undefined)
          return this._m_raw3;
        if (this.channelOffset[2] > 0) {
          var _pos = this._io.pos;
          this._io.seek(this.channelOffset[2] + this.zPtOffset);
          this._m_raw3 = this._io.readBytes(this.lenRaw3);
          this._io.seek(_pos);
        }
        return this._m_raw3;
      }
    });
    Object.defineProperty(Header.prototype, 'raw4', {
      get: function() {
        if (this._m_raw4 !== undefined)
          return this._m_raw4;
        if (this.channelOffset[3] > 0) {
          var _pos = this._io.pos;
          this._io.seek(this.channelOffset[3] + this.zPtOffset);
          this._m_raw4 = this._io.readBytes(this.lenRaw4);
          this._io.seek(_pos);
        }
        return this._m_raw4;
      }
    });
    Object.defineProperty(Header.prototype, 'rawDepth', {
      get: function() {
        if (this._m_rawDepth !== undefined)
          return this._m_rawDepth;
        this._m_rawDepth = (this.enabled.interwoven ? Math.floor(this.wfmLen / 2) : this.wfmLen);
        return this._m_rawDepth;
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
        this._io.seek(this.setupOffset - 56);
        this._raw__m_setup = this._io.readBytes(this.lenSetup);
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
        this._m_timeOffset = 1.0E-12 * this.timeOffsetPs;
        return this._m_timeOffset;
      }
    });
    Object.defineProperty(Header.prototype, 'timeScale', {
      get: function() {
        if (this._m_timeScale !== undefined)
          return this._m_timeScale;
        this._m_timeScale = 1.0E-12 * this.timeScalePs;
        return this._m_timeScale;
      }
    });

    /**
     * The last two bytes is the size of the header 0x38=56
     */

    /**
     * not in pdf specification
     */

    /**
     * average time 2-8192
     */

    /**
     * equ or real
     */

    /**
     * not in pdf specification
     */

    /**
     * storage depth
     */

    /**
     * not in pdf specification
     */

    /**
     * horizontal timebase in picoseconds
     */

    /**
     * horizontal offset in picoseconds
     */

    /**
     * offset of valid waveform relative to start of storage waveform
     */

    /**
     * real waveform storage depth
     */

    /**
     * padding byte present before the delay fields in shipped captures
     */

    return Header;
  })();

  var SetupBlock = Rigol2000Wfm.SetupBlock = (function() {
    function SetupBlock(_io, _parent, _root) {
      this._io = _io;
      this._parent = _parent;
      this._root = _root;

      this._read();
    }
    SetupBlock.prototype._read = function() {
    }
    Object.defineProperty(SetupBlock.prototype, 'triggerHoldoffNs', {
      get: function() {
        if (this._m_triggerHoldoffNs !== undefined)
          return this._m_triggerHoldoffNs;
        if (this._io.size >= 543) {
          var _pos = this._io.pos;
          this._io.seek(539);
          this._m_triggerHoldoffNs = this._io.readU4le();
          this._io.seek(_pos);
        }
        return this._m_triggerHoldoffNs;
      }
    });
    Object.defineProperty(SetupBlock.prototype, 'triggerLevels', {
      get: function() {
        if (this._m_triggerLevels !== undefined)
          return this._m_triggerLevels;
        if (this._io.size >= 559) {
          var _pos = this._io.pos;
          this._io.seek(547);
          this._m_triggerLevels = new TriggerLevelBlock(this._io, this, this._root);
          this._io.seek(_pos);
        }
        return this._m_triggerLevels;
      }
    });
    Object.defineProperty(SetupBlock.prototype, 'triggerModeCode', {
      get: function() {
        if (this._m_triggerModeCode !== undefined)
          return this._m_triggerModeCode;
        if (this._io.size >= 539) {
          var _pos = this._io.pos;
          this._io.seek(535);
          this._m_triggerModeCode = this._io.readU4le();
          this._io.seek(_pos);
        }
        return this._m_triggerModeCode;
      }
    });
    Object.defineProperty(SetupBlock.prototype, 'triggerSourcePrimary', {
      get: function() {
        if (this._m_triggerSourcePrimary !== undefined)
          return this._m_triggerSourcePrimary;
        if (this._io.size >= 520) {
          var _pos = this._io.pos;
          this._io.seek(519);
          this._m_triggerSourcePrimary = this._io.readU1();
          this._io.seek(_pos);
        }
        return this._m_triggerSourcePrimary;
      }
    });
    Object.defineProperty(SetupBlock.prototype, 'triggerSourceShadow', {
      get: function() {
        if (this._m_triggerSourceShadow !== undefined)
          return this._m_triggerSourceShadow;
        if (this._io.size >= 524) {
          var _pos = this._io.pos;
          this._io.seek(523);
          this._m_triggerSourceShadow = this._io.readU1();
          this._io.seek(_pos);
        }
        return this._m_triggerSourceShadow;
      }
    });

    return SetupBlock;
  })();

  var TriggerLevelBlock = Rigol2000Wfm.TriggerLevelBlock = (function() {
    function TriggerLevelBlock(_io, _parent, _root) {
      this._io = _io;
      this._parent = _parent;
      this._root = _root;

      this._read();
    }
    TriggerLevelBlock.prototype._read = function() {
      this.ch1LevelUv = this._io.readS4le();
      this.ch2LevelUv = this._io.readS4le();
      this.extLevelUv = this._io.readS4le();
    }

    return TriggerLevelBlock;
  })();
  Object.defineProperty(Rigol2000Wfm.prototype, 'header', {
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

  return Rigol2000Wfm;
})();
Rigol2000Wfm_.Rigol2000Wfm = Rigol2000Wfm;
});
