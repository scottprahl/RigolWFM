// This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild

(function (root, factory) {
  if (typeof define === 'function' && define.amd) {
    define(['exports', 'kaitai-struct/KaitaiStream'], factory);
  } else if (typeof exports === 'object' && exports !== null && typeof exports.nodeType !== 'number') {
    factory(exports, require('kaitai-struct/KaitaiStream'));
  } else {
    factory(root.Rigol6000Wfm || (root.Rigol6000Wfm = {}), root.KaitaiStream);
  }
})(typeof self !== 'undefined' ? self : this, function (Rigol6000Wfm_, KaitaiStream) {
/**
 * Rigol DS6000 waveform file format.
 * 
 * Sources used for this KSY binary format: document titled "WFM save format: FFalcon/Goshawk"
 * 
 * Tested file formats: synthetic DS6000 files generated in `tests/test_6.py`,
 * including normal two-channel captures and a zero-offset / missing-channel
 * case; no checked-in real DS6000 fixture is present yet.
 * 
 * Oscilloscope models this format may apply to: DS6000 family models currently
 * listed by the library, including `DS6062`, `DS6064`, `DS6102`, and
 * `DS6104`.
 */

var Rigol6000Wfm = (function() {
  Rigol6000Wfm.AcquisitionEnum = Object.freeze({
    NORMAL: 0,
    AVERAGE: 1,
    PEAK: 2,
    HIGH_RESOLUTION: 3,

    0: "NORMAL",
    1: "AVERAGE",
    2: "PEAK",
    3: "HIGH_RESOLUTION",
  });

  Rigol6000Wfm.BandwidthEnum = Object.freeze({
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

  Rigol6000Wfm.CouplingEnum = Object.freeze({
    DC: 0,
    AC: 1,
    GND: 2,

    0: "DC",
    1: "AC",
    2: "GND",
  });

  Rigol6000Wfm.FilterEnum = Object.freeze({
    LOW_PASS: 0,
    HIGH_PASS: 1,
    BAND_PASS: 2,
    BAND_REJECT: 3,

    0: "LOW_PASS",
    1: "HIGH_PASS",
    2: "BAND_PASS",
    3: "BAND_REJECT",
  });

  Rigol6000Wfm.ImpedanceEnum = Object.freeze({
    OHM_50: 0,
    OHM_1MEG: 1,

    0: "OHM_50",
    1: "OHM_1MEG",
  });

  Rigol6000Wfm.ProbeEnum = Object.freeze({
    SINGLE: 0,
    DIFF: 1,

    0: "SINGLE",
    1: "DIFF",
  });

  Rigol6000Wfm.ProbeRatioEnum = Object.freeze({
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

  Rigol6000Wfm.ProbeTypeEnum = Object.freeze({
    NORMAL_TYPE: 0,
    DIFFERENTIAL: 1,

    0: "NORMAL_TYPE",
    1: "DIFFERENTIAL",
  });

  Rigol6000Wfm.TimeEnum = Object.freeze({
    YT: 0,
    XY: 1,
    ROLL: 2,

    0: "YT",
    1: "XY",
    2: "ROLL",
  });

  Rigol6000Wfm.UnitEnum = Object.freeze({
    W: 0,
    A: 1,
    V: 2,
    U: 3,

    0: "W",
    1: "A",
    2: "V",
    3: "U",
  });

  function Rigol6000Wfm(_io, _parent, _root) {
    this._io = _io;
    this._parent = _parent;
    this._root = _root || this;

    this._read();
  }
  Rigol6000Wfm.prototype._read = function() {
  }

  var ChannelHeader = Rigol6000Wfm.ChannelHeader = (function() {
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
      this.invertVal = this._io.readU1();
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
        this._m_inverted = (this.invertVal != 0 ? true : false);
        return this._m_inverted;
      }
    });
    Object.defineProperty(ChannelHeader.prototype, 'probeValue', {
      get: function() {
        if (this._m_probeValue !== undefined)
          return this._m_probeValue;
        this._m_probeValue = (this.probeRatio == Rigol6000Wfm.ProbeRatioEnum.X0_01 ? 0.01 : (this.probeRatio == Rigol6000Wfm.ProbeRatioEnum.X0_02 ? 0.02 : (this.probeRatio == Rigol6000Wfm.ProbeRatioEnum.X0_05 ? 0.05 : (this.probeRatio == Rigol6000Wfm.ProbeRatioEnum.X0_1 ? 0.1 : (this.probeRatio == Rigol6000Wfm.ProbeRatioEnum.X0_2 ? 0.2 : (this.probeRatio == Rigol6000Wfm.ProbeRatioEnum.X0_5 ? 0.5 : (this.probeRatio == Rigol6000Wfm.ProbeRatioEnum.X1 ? 1.0 : (this.probeRatio == Rigol6000Wfm.ProbeRatioEnum.X2 ? 2.0 : (this.probeRatio == Rigol6000Wfm.ProbeRatioEnum.X5 ? 5.0 : (this.probeRatio == Rigol6000Wfm.ProbeRatioEnum.X10 ? 10.0 : (this.probeRatio == Rigol6000Wfm.ProbeRatioEnum.X20 ? 20.0 : (this.probeRatio == Rigol6000Wfm.ProbeRatioEnum.X50 ? 50.0 : (this.probeRatio == Rigol6000Wfm.ProbeRatioEnum.X100 ? 100.0 : (this.probeRatio == Rigol6000Wfm.ProbeRatioEnum.X200 ? 200.0 : (this.probeRatio == Rigol6000Wfm.ProbeRatioEnum.X500 ? 500.0 : 1000.0)))))))))))))));
        return this._m_probeValue;
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

    return ChannelHeader;
  })();

  var ChannelMask = Rigol6000Wfm.ChannelMask = (function() {
    function ChannelMask(_io, _parent, _root) {
      this._io = _io;
      this._parent = _parent;
      this._root = _root;

      this._read();
    }
    ChannelMask.prototype._read = function() {
      this.rawMask = this._io.readU2le();
    }
    Object.defineProperty(ChannelMask.prototype, 'channel1', {
      get: function() {
        if (this._m_channel1 !== undefined)
          return this._m_channel1;
        this._m_channel1 = (this.rawMask & 1) != 0;
        return this._m_channel1;
      }
    });
    Object.defineProperty(ChannelMask.prototype, 'channel2', {
      get: function() {
        if (this._m_channel2 !== undefined)
          return this._m_channel2;
        this._m_channel2 = (this.rawMask & 2) != 0;
        return this._m_channel2;
      }
    });
    Object.defineProperty(ChannelMask.prototype, 'channel3', {
      get: function() {
        if (this._m_channel3 !== undefined)
          return this._m_channel3;
        this._m_channel3 = (this.rawMask & 4) != 0;
        return this._m_channel3;
      }
    });
    Object.defineProperty(ChannelMask.prototype, 'channel4', {
      get: function() {
        if (this._m_channel4 !== undefined)
          return this._m_channel4;
        this._m_channel4 = (this.rawMask & 8) != 0;
        return this._m_channel4;
      }
    });

    return ChannelMask;
  })();

  var Header = Rigol6000Wfm.Header = (function() {
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
      this.blockNum = this._io.readU2le();
      this.fileVersion = this._io.readU2le();
      this.fileCrc = this._io.readU4le();
      this.reserved52 = this._io.readU2le();
      this.reserved54 = this._io.readU2le();
      this.wfmCrc = this._io.readU4le();
      this.structureSize = this._io.readU2le();
      this.structureVersion = this._io.readU2le();
      this.enabled = new ChannelMask(this._io, this, this._root);
      this.reserved66 = this._io.readBytes(2);
      this.channelOffset = [];
      for (var i = 0; i < 4; i++) {
        this.channelOffset.push(this._io.readU4le());
      }
      this.acquisitionMode = this._io.readU2le();
      this.averageTime = this._io.readU2le();
      this.sampleMode = this._io.readU2le();
      this.reserved90 = this._io.readBytes(2);
      this.memDepth = this._io.readU4le();
      this.sampleRateHz = this._io.readF4le();
      this.timeMode = this._io.readU2le();
      this.reserved102 = this._io.readBytes(2);
      this.timeScalePs = this._io.readU8le();
      this.timeOffsetPs = this._io.readS8le();
      this.ch = [];
      for (var i = 0; i < 4; i++) {
        this.ch.push(new ChannelHeader(this._io, this, this._root));
      }
      this.setupSize = this._io.readU4le();
      this.setupOffset = this._io.readU4le();
      this.wfmOffset = this._io.readU4le();
      this.storageDepth = this._io.readU4le();
      this.zPtOffset = this._io.readU4le();
      this.wfmLen = this._io.readU4le();
      this.memOffset = [];
      for (var i = 0; i < 2; i++) {
        this.memOffset.push(this._io.readU2le());
      }
      this.equCoarse = [];
      for (var i = 0; i < 2; i++) {
        this.equCoarse.push(this._io.readU2le());
      }
      this.equFine = [];
      for (var i = 0; i < 2; i++) {
        this.equFine.push(this._io.readU2le());
      }
      this.memLastAddr = [];
      for (var i = 0; i < 2; i++) {
        this.memLastAddr.push(this._io.readU4le());
      }
      this.memLength = [];
      for (var i = 0; i < 2; i++) {
        this.memLength.push(this._io.readU4le());
      }
      this.memStartAddr = [];
      for (var i = 0; i < 2; i++) {
        this.memStartAddr.push(this._io.readU4le());
      }
      this.bankSize = [];
      for (var i = 0; i < 2; i++) {
        this.bankSize.push(this._io.readU4le());
      }
      this.rollScrnWaveLength = this._io.readU2le();
      this.analogInterpEn = this._io.readU1();
      this.mainForceAnalogTrig = this._io.readU1();
      this.zoomForceAnalogTrig = this._io.readU1();
      this.horizSlowForceStopFrame = this._io.readU1();
      this.getSpuDigDataStatus = this._io.readU1();
      this.reserved307 = this._io.readBytes(1);
      this.mainMemOffset = this._io.readS8le();
      this.memViewOffset = this._io.readS8le();
      this.slowDetaWaveLength = this._io.readS8le();
      this.slowDetaWaveLengthNoDelay = this._io.readS8le();
      this.realSaDotPeriod = this._io.readU8le();
      this.trigTypeDetaDelay = this._io.readS4le();
      this.chnl12MaxDelay = this._io.readS4le();
      this.chnl34MaxDelay = this._io.readS4le();
      this.chnlDlyToMemLen = this._io.readU4le();
      this.spuMemDepthDeta = this._io.readU4le();
      this.spuMemDepthRema = this._io.readU4le();
      this.memOffsetBase = this._io.readU4le();
      this.spuMemBankSize = this._io.readU4le();
      this.s16Adc1ClockDelay = this._io.readS2le();
      this.s16Adc2ClockDelay = this._io.readS2le();
      this.maxMainScrnChnlDelay = this._io.readU2le();
      this.maxZoomScrnChnlDelay = this._io.readU2le();
      this.mainDgtlTrigDataOffset = this._io.readU2le();
      this.zoomDgtlTrigDataOffset = this._io.readU2le();
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
        this._m_lenRaw1 = (this.channelOffset[0] != 0 ? this.wfmLen : 0);
        return this._m_lenRaw1;
      }
    });
    Object.defineProperty(Header.prototype, 'lenRaw2', {
      get: function() {
        if (this._m_lenRaw2 !== undefined)
          return this._m_lenRaw2;
        this._m_lenRaw2 = (this.channelOffset[1] != 0 ? this.wfmLen : 0);
        return this._m_lenRaw2;
      }
    });
    Object.defineProperty(Header.prototype, 'lenRaw3', {
      get: function() {
        if (this._m_lenRaw3 !== undefined)
          return this._m_lenRaw3;
        this._m_lenRaw3 = (this.channelOffset[2] != 0 ? this.wfmLen : 0);
        return this._m_lenRaw3;
      }
    });
    Object.defineProperty(Header.prototype, 'lenRaw4', {
      get: function() {
        if (this._m_lenRaw4 !== undefined)
          return this._m_lenRaw4;
        this._m_lenRaw4 = (this.channelOffset[3] != 0 ? this.wfmLen : 0);
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
        if (this.channelOffset[0] != 0) {
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
        if (this.channelOffset[1] != 0) {
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
        if (this.channelOffset[2] != 0) {
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
        if (this.channelOffset[3] != 0) {
          var _pos = this._io.pos;
          this._io.seek(this.channelOffset[3] + this.zPtOffset);
          this._m_raw4 = this._io.readBytes(this.lenRaw4);
          this._io.seek(_pos);
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
     * average time 0-2048
     */

    /**
     * equ or real
     */

    /**
     * storage depth
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

    return Header;
  })();
  Object.defineProperty(Rigol6000Wfm.prototype, 'header', {
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

  return Rigol6000Wfm;
})();
Rigol6000Wfm_.Rigol6000Wfm = Rigol6000Wfm;
});
