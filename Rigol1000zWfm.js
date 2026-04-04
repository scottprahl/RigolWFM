// This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild

(function (root, factory) {
  if (typeof define === 'function' && define.amd) {
    define(['exports', 'kaitai-struct/KaitaiStream'], factory);
  } else if (typeof exports === 'object' && exports !== null && typeof exports.nodeType !== 'number') {
    factory(exports, require('kaitai-struct/KaitaiStream'));
  } else {
    factory(root.Rigol1000zWfm || (root.Rigol1000zWfm = {}), root.KaitaiStream);
  }
})(typeof self !== 'undefined' ? self : this, function (Rigol1000zWfm_, KaitaiStream) {
/**
 * Rigol DS1000Z scope .wmf file format.
 * 
 * Sources used for this KSY binary format. An document titled
 * "DS1000Z Waveform Storage Structure" and the Github repository
 * <https://github.com/michal-szkutnik/pyRigolWfm1000Z>,
 * 
 * Tested file formats: real repo fixtures `DS1202Z-E.wfm`, `DS1054Z-A.wfm`
 * through `DS1054Z-D.wfm`, `DS1074Z-A.wfm` through `DS1074Z-C.wfm`,
 * `MSO1104.wfm`, and the two-channel SP3 fixtures
 * `DS1054Z-ch1SquareCH2Uart.wfm` and `DS1054Z-ch1SquareCH4Uart.wfm`.
 * 
 * Oscilloscope models this format may apply to: DS1000Z family models
 * currently listed by the library, including `DS1202Z`, `DS1054Z`, `MSO1054Z`,
 * `DS1074Z`, `MSO1074Z`, `DS1074Z-S`, `DS1104Z`, `MSO1104Z`, and
 * `DS1104Z-S`.
 */

var Rigol1000zWfm = (function() {
  Rigol1000zWfm.AcquistionEnum = Object.freeze({
    NORMAL: 0,
    PEAK: 1,
    AVERAGE: 2,
    HIGH_RESOLUTION: 3,

    0: "NORMAL",
    1: "PEAK",
    2: "AVERAGE",
    3: "HIGH_RESOLUTION",
  });

  Rigol1000zWfm.BandwidthEnum = Object.freeze({
    MHZ_20: 0,
    NO_LIMIT: 1,

    0: "MHZ_20",
    1: "NO_LIMIT",
  });

  Rigol1000zWfm.CouplingEnum = Object.freeze({
    DC: 0,
    AC: 1,
    GND: 2,

    0: "DC",
    1: "AC",
    2: "GND",
  });

  Rigol1000zWfm.ProbeEnum = Object.freeze({
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

  Rigol1000zWfm.TimeModeEnum = Object.freeze({
    YT: 0,
    XY: 1,
    ROLL: 2,

    0: "YT",
    1: "XY",
    2: "ROLL",
  });

  Rigol1000zWfm.UnitEnum = Object.freeze({
    W: 0,
    A: 1,
    V: 2,
    U: 3,

    0: "W",
    1: "A",
    2: "V",
    3: "U",
  });

  function Rigol1000zWfm(_io, _parent, _root) {
    this._io = _io;
    this._parent = _parent;
    this._root = _root || this;

    this._read();
  }
  Rigol1000zWfm.prototype._read = function() {
  }

  var ChannelHead = Rigol1000zWfm.ChannelHead = (function() {
    function ChannelHead(_io, _parent, _root) {
      this._io = _io;
      this._parent = _parent;
      this._root = _root;

      this._read();
    }
    ChannelHead.prototype._read = function() {
      this.enabledVal = this._io.readU1();
      this.coupling = this._io.readU1();
      this.bandwidthLimit = this._io.readU1();
      this.probeType = this._io.readU1();
      this.probeRatio = this._io.readU1();
      this.unused = this._io.readBytes(3);
      this.scale = this._io.readF4le();
      this.shift = this._io.readF4le();
      this.invertedVal = this._io.readU1();
      this.unit = this._io.readU1();
      this.unknown2 = this._io.readBytes(10);
    }
    Object.defineProperty(ChannelHead.prototype, 'enabled', {
      get: function() {
        if (this._m_enabled !== undefined)
          return this._m_enabled;
        this._m_enabled = (this.enabledVal != 0 ? true : false);
        return this._m_enabled;
      }
    });
    Object.defineProperty(ChannelHead.prototype, 'inverted', {
      get: function() {
        if (this._m_inverted !== undefined)
          return this._m_inverted;
        this._m_inverted = (this.invertedVal != 0 ? true : false);
        return this._m_inverted;
      }
    });
    Object.defineProperty(ChannelHead.prototype, 'probeValue', {
      get: function() {
        if (this._m_probeValue !== undefined)
          return this._m_probeValue;
        this._m_probeValue = (this.probeRatio == Rigol1000zWfm.ProbeEnum.X0_01 ? 0.01 : (this.probeRatio == Rigol1000zWfm.ProbeEnum.X0_02 ? 0.02 : (this.probeRatio == Rigol1000zWfm.ProbeEnum.X0_05 ? 0.05 : (this.probeRatio == Rigol1000zWfm.ProbeEnum.X0_1 ? 0.1 : (this.probeRatio == Rigol1000zWfm.ProbeEnum.X0_2 ? 0.2 : (this.probeRatio == Rigol1000zWfm.ProbeEnum.X0_5 ? 0.5 : (this.probeRatio == Rigol1000zWfm.ProbeEnum.X1 ? 1.0 : (this.probeRatio == Rigol1000zWfm.ProbeEnum.X2 ? 2.0 : (this.probeRatio == Rigol1000zWfm.ProbeEnum.X5 ? 5.0 : (this.probeRatio == Rigol1000zWfm.ProbeEnum.X10 ? 10.0 : (this.probeRatio == Rigol1000zWfm.ProbeEnum.X20 ? 20.0 : (this.probeRatio == Rigol1000zWfm.ProbeEnum.X50 ? 50.0 : (this.probeRatio == Rigol1000zWfm.ProbeEnum.X100 ? 100.0 : (this.probeRatio == Rigol1000zWfm.ProbeEnum.X200 ? 200.0 : (this.probeRatio == Rigol1000zWfm.ProbeEnum.X500 ? 500.0 : 1000.0)))))))))))))));
        return this._m_probeValue;
      }
    });
    Object.defineProperty(ChannelHead.prototype, 'timeOffset', {
      get: function() {
        if (this._m_timeOffset !== undefined)
          return this._m_timeOffset;
        this._m_timeOffset = this._root.header.timeOffset;
        return this._m_timeOffset;
      }
    });
    Object.defineProperty(ChannelHead.prototype, 'timeScale', {
      get: function() {
        if (this._m_timeScale !== undefined)
          return this._m_timeScale;
        this._m_timeScale = this._root.header.timeScale;
        return this._m_timeScale;
      }
    });

    /**
     * Most DS1000Z captures line up with the existing `+1 div` bias that the
     * project has used for years.  The older 00.04.04.SP3 firmware is an
     * exception for two-channel captures: the sparse CH1+CH2 and CH1+CH4
     * fixtures only match their same-rate CSV exports when negative-offset
     * channels use a much smaller +0.2 div bias and zero-offset channels use
     * no extra bias at all.
     */
    Object.defineProperty(ChannelHead.prototype, 'verticalBias', {
      get: function() {
        if (this._m_verticalBias !== undefined)
          return this._m_verticalBias;
        this._m_verticalBias = ( ((this._root.preheader.firmwareVersion == "00.04.04.SP3") && (this._root.header.totalChannels == 2))  ? (this.shift < 0 ? this.voltPerDivision / 5.0 : 0.0) : this.voltPerDivision);
        return this._m_verticalBias;
      }
    });
    Object.defineProperty(ChannelHead.prototype, 'voltOffset', {
      get: function() {
        if (this._m_voltOffset !== undefined)
          return this._m_voltOffset;
        this._m_voltOffset = this.shift;
        return this._m_voltOffset;
      }
    });
    Object.defineProperty(ChannelHead.prototype, 'voltPerDivision', {
      get: function() {
        if (this._m_voltPerDivision !== undefined)
          return this._m_voltPerDivision;
        this._m_voltPerDivision = (this.inverted ? -1.0 * this.scale : 1.0 * this.scale);
        return this._m_voltPerDivision;
      }
    });
    Object.defineProperty(ChannelHead.prototype, 'voltScale', {
      get: function() {
        if (this._m_voltScale !== undefined)
          return this._m_voltScale;
        this._m_voltScale = this.voltPerDivision / 25.0;
        return this._m_voltScale;
      }
    });
    Object.defineProperty(ChannelHead.prototype, 'yOffset', {
      get: function() {
        if (this._m_yOffset !== undefined)
          return this._m_yOffset;
        this._m_yOffset = this.shift - this.verticalBias;
        return this._m_yOffset;
      }
    });
    Object.defineProperty(ChannelHead.prototype, 'yScale', {
      get: function() {
        if (this._m_yScale !== undefined)
          return this._m_yScale;
        this._m_yScale = -(this.voltPerDivision) / 20.0;
        return this._m_yScale;
      }
    });

    return ChannelHead;
  })();

  var ChannelSubhead = Rigol1000zWfm.ChannelSubhead = (function() {
    function ChannelSubhead(_io, _parent, _root) {
      this._io = _io;
      this._parent = _parent;
      this._root = _root;

      this._read();
    }
    ChannelSubhead.prototype._read = function() {
      this.unknown1 = this._io.readBytes(3);
      this.unusedBits1 = this._io.readBitsIntBe(7);
      this.enabled = this._io.readBitsIntBe(1) != 0;
      this._io.alignToByte();
      this.unknown2 = this._io.readBytes(7);
      this.unusedBits2 = this._io.readBitsIntBe(7);
      this.inverted = this._io.readBitsIntBe(1) != 0;
      this._io.alignToByte();
      this.unknown3 = this._io.readBytes(10);
      this.probeAttenuation = this._io.readS8le();
      this.unknown4 = this._io.readBytes(16);
      this.label = KaitaiStream.bytesToStr(KaitaiStream.bytesTerminate(this._io.readBytes(4), 0, false), "UTF-8");
      this.unknown5 = this._io.readBytes(10);
    }

    return ChannelSubhead;
  })();

  var FileHeader = Rigol1000zWfm.FileHeader = (function() {
    function FileHeader(_io, _parent, _root) {
      this._io = _io;
      this._parent = _parent;
      this._root = _root;

      this._read();
    }
    FileHeader.prototype._read = function() {
      this.magic = this._io.readBytes(4);
      if (!((KaitaiStream.byteArrayCompare(this.magic, new Uint8Array([1, 255, 255, 255])) == 0))) {
        throw new KaitaiStream.ValidationNotEqualError(new Uint8Array([1, 255, 255, 255]), this.magic, this._io, "/types/file_header/seq/0");
      }
      this.magic2 = this._io.readU2le();
      this.structureSize = this._io.readU2le();
      this.modelNumber = KaitaiStream.bytesToStr(KaitaiStream.bytesTerminate(this._io.readBytes(20), 0, false), "ASCII");
      this.firmwareVersion = KaitaiStream.bytesToStr(KaitaiStream.bytesTerminate(this._io.readBytes(20), 0, false), "ASCII");
      this.block = this._io.readBytes(2);
      if (!((KaitaiStream.byteArrayCompare(this.block, new Uint8Array([1, 0])) == 0))) {
        throw new KaitaiStream.ValidationNotEqualError(new Uint8Array([1, 0]), this.block, this._io, "/types/file_header/seq/5");
      }
      this.fileVersion = this._io.readU2le();
    }

    /**
     * should be [0xa5, 0xa5] or [0xa5, 0xa6]
     */

    /**
     * should be 0x38
     */

    return FileHeader;
  })();

  /**
   * The DS1000Z horizontal metadata block contains a duplicated 64-byte table
   * of normalized channel settings at offsets 0x000 and 0x1c0.  These values
   * mirror the float scale/shift fields from the waveform header after
   * applying a 10/probe normalization; they do not appear to be separate
   * calibration data.
   */

  var HorizontalBlock = Rigol1000zWfm.HorizontalBlock = (function() {
    function HorizontalBlock(_io, _parent, _root) {
      this._io = _io;
      this._parent = _parent;
      this._root = _root;

      this._read();
    }
    HorizontalBlock.prototype._read = function() {
      this.raw = this._io.readBytesFull();
    }
    Object.defineProperty(HorizontalBlock.prototype, 'normalizedA', {
      get: function() {
        if (this._m_normalizedA !== undefined)
          return this._m_normalizedA;
        var _pos = this._io.pos;
        this._io.seek(0);
        this._m_normalizedA = new NormalizedChannelTable(this._io, this, this._root);
        this._io.seek(_pos);
        return this._m_normalizedA;
      }
    });
    Object.defineProperty(HorizontalBlock.prototype, 'normalizedB', {
      get: function() {
        if (this._m_normalizedB !== undefined)
          return this._m_normalizedB;
        var _pos = this._io.pos;
        this._io.seek(448);
        this._m_normalizedB = new NormalizedChannelTable(this._io, this, this._root);
        this._io.seek(_pos);
        return this._m_normalizedB;
      }
    });

    return HorizontalBlock;
  })();

  var NormalizedChannelTable = Rigol1000zWfm.NormalizedChannelTable = (function() {
    function NormalizedChannelTable(_io, _parent, _root) {
      this._io = _io;
      this._parent = _parent;
      this._root = _root;

      this._read();
    }
    NormalizedChannelTable.prototype._read = function() {
      this.rangeNorm = [];
      for (var i = 0; i < 4; i++) {
        this.rangeNorm.push(this._io.readU4le());
      }
      this.shiftNorm = [];
      for (var i = 0; i < 4; i++) {
        this.shiftNorm.push(this._io.readS8le());
      }
      this.enabledNorm = [];
      for (var i = 0; i < 4; i++) {
        this.enabledNorm.push(this._io.readU4le());
      }
    }

    return NormalizedChannelTable;
  })();

  var RawData = Rigol1000zWfm.RawData = (function() {
    function RawData(_io, _parent, _root) {
      this._io = _io;
      this._parent = _parent;
      this._root = _root;

      this._read();
    }
    RawData.prototype._read = function() {
      this.raw = this._io.readBytes(this._root.header.points * this._root.header.stride);
    }

    return RawData;
  })();

  var WfmHeader = Rigol1000zWfm.WfmHeader = (function() {
    function WfmHeader(_io, _parent, _root) {
      this._io = _io;
      this._parent = _parent;
      this._root = _root;

      this._read();
    }
    WfmHeader.prototype._read = function() {
      this.picosecondsPerDivision = this._io.readU8le();
      this.picosecondsOffset = this._io.readS8le();
      this.crc = this._io.readU4le();
      this.structureSize = this._io.readBytes(2);
      if (!((KaitaiStream.byteArrayCompare(this.structureSize, new Uint8Array([216, 0])) == 0))) {
        throw new KaitaiStream.ValidationNotEqualError(new Uint8Array([216, 0]), this.structureSize, this._io, "/types/wfm_header/seq/3");
      }
      this.structureVersion = this._io.readU2le();
      this.unusedBits1 = this._io.readBitsIntBe(4);
      this.ch4Enabled = this._io.readBitsIntBe(1) != 0;
      this.ch3Enabled = this._io.readBitsIntBe(1) != 0;
      this.ch2Enabled = this._io.readBitsIntBe(1) != 0;
      this.ch1Enabled = this._io.readBitsIntBe(1) != 0;
      this._io.alignToByte();
      this.unusedMaskBytes = this._io.readBytes(3);
      this.ch1FileOffset = this._io.readU4le();
      this.ch2FileOffset = this._io.readU4le();
      this.ch3FileOffset = this._io.readU4le();
      this.ch4FileOffset = this._io.readU4le();
      this.laOffset = this._io.readU4le();
      this.acqMode = this._io.readU1();
      this.averageTime = this._io.readU1();
      this.sampleMode = this._io.readBytes(1);
      if (!((KaitaiStream.byteArrayCompare(this.sampleMode, new Uint8Array([0])) == 0))) {
        throw new KaitaiStream.ValidationNotEqualError(new Uint8Array([0]), this.sampleMode, this._io, "/types/wfm_header/seq/18");
      }
      this.timeMode = this._io.readU1();
      this.memoryDepth = this._io.readU4le();
      this.sampleRateGhz = this._io.readF4le();
      this.ch = [];
      for (var i = 0; i < 4; i++) {
        this.ch.push(new ChannelHead(this._io, this, this._root));
      }
      this.laParameters = this._io.readBytes(12);
      this.setupSize = this._io.readU4le();
      this.setupOffset = this._io.readU4le();
      this.horizontalSize = this._io.readU4le();
      this.horizontalOffset = this._io.readU4le();
      this.displayDelay = this._io.readU4le();
      this.displayAddress = this._io.readU4le();
      this.displayFine = this._io.readU4le();
      this.memoryAddress = this._io.readU4le();
    }
    Object.defineProperty(WfmHeader.prototype, 'ch1Int', {
      get: function() {
        if (this._m_ch1Int !== undefined)
          return this._m_ch1Int;
        this._m_ch1Int = (this.ch1Enabled ? 1 : 0);
        return this._m_ch1Int;
      }
    });
    Object.defineProperty(WfmHeader.prototype, 'ch2Int', {
      get: function() {
        if (this._m_ch2Int !== undefined)
          return this._m_ch2Int;
        this._m_ch2Int = (this.ch2Enabled ? 1 : 0);
        return this._m_ch2Int;
      }
    });
    Object.defineProperty(WfmHeader.prototype, 'ch3Int', {
      get: function() {
        if (this._m_ch3Int !== undefined)
          return this._m_ch3Int;
        this._m_ch3Int = (this.ch3Enabled ? 1 : 0);
        return this._m_ch3Int;
      }
    });
    Object.defineProperty(WfmHeader.prototype, 'ch4Int', {
      get: function() {
        if (this._m_ch4Int !== undefined)
          return this._m_ch4Int;
        this._m_ch4Int = (this.ch4Enabled ? 1 : 0);
        return this._m_ch4Int;
      }
    });
    Object.defineProperty(WfmHeader.prototype, 'points', {
      get: function() {
        if (this._m_points !== undefined)
          return this._m_points;
        this._m_points = Math.floor(this.memoryDepth / this.stride);
        return this._m_points;
      }
    });
    Object.defineProperty(WfmHeader.prototype, 'sampleRateHz', {
      get: function() {
        if (this._m_sampleRateHz !== undefined)
          return this._m_sampleRateHz;
        this._m_sampleRateHz = this.sampleRateGhz * 1E+9;
        return this._m_sampleRateHz;
      }
    });
    Object.defineProperty(WfmHeader.prototype, 'secondsPerPoint', {
      get: function() {
        if (this._m_secondsPerPoint !== undefined)
          return this._m_secondsPerPoint;
        this._m_secondsPerPoint = 1 / this.sampleRateHz;
        return this._m_secondsPerPoint;
      }
    });
    Object.defineProperty(WfmHeader.prototype, 'stride', {
      get: function() {
        if (this._m_stride !== undefined)
          return this._m_stride;
        this._m_stride = (this.totalChannels == 3 ? 4 : this.totalChannels);
        return this._m_stride;
      }
    });
    Object.defineProperty(WfmHeader.prototype, 'timeOffset', {
      get: function() {
        if (this._m_timeOffset !== undefined)
          return this._m_timeOffset;
        this._m_timeOffset = this.picosecondsOffset * 1E-12;
        return this._m_timeOffset;
      }
    });
    Object.defineProperty(WfmHeader.prototype, 'timeScale', {
      get: function() {
        if (this._m_timeScale !== undefined)
          return this._m_timeScale;
        this._m_timeScale = this.picosecondsPerDivision * 1E-12;
        return this._m_timeScale;
      }
    });
    Object.defineProperty(WfmHeader.prototype, 'totalChannels', {
      get: function() {
        if (this._m_totalChannels !== undefined)
          return this._m_totalChannels;
        this._m_totalChannels = (this.totalCount == 0 ? 1 : this.totalCount);
        return this._m_totalChannels;
      }
    });
    Object.defineProperty(WfmHeader.prototype, 'totalCount', {
      get: function() {
        if (this._m_totalCount !== undefined)
          return this._m_totalCount;
        this._m_totalCount = ((this.ch1Int + this.ch2Int) + this.ch3Int) + this.ch4Int;
        return this._m_totalCount;
      }
    });

    return WfmHeader;
  })();
  Object.defineProperty(Rigol1000zWfm.prototype, 'data', {
    get: function() {
      if (this._m_data !== undefined)
        return this._m_data;
      var _pos = this._io.pos;
      this._io.seek(this._root.header.horizontalOffset + this._root.header.horizontalSize);
      this._m_data = new RawData(this._io, this, this._root);
      this._io.seek(_pos);
      return this._m_data;
    }
  });
  Object.defineProperty(Rigol1000zWfm.prototype, 'header', {
    get: function() {
      if (this._m_header !== undefined)
        return this._m_header;
      var _pos = this._io.pos;
      this._io.seek(64);
      this._m_header = new WfmHeader(this._io, this, this._root);
      this._io.seek(_pos);
      return this._m_header;
    }
  });
  Object.defineProperty(Rigol1000zWfm.prototype, 'horizontal', {
    get: function() {
      if (this._m_horizontal !== undefined)
        return this._m_horizontal;
      var _pos = this._io.pos;
      this._io.seek(this._root.header.horizontalOffset);
      this._raw__m_horizontal = this._io.readBytes(this._root.header.horizontalSize);
      var _io__raw__m_horizontal = new KaitaiStream(this._raw__m_horizontal);
      this._m_horizontal = new HorizontalBlock(_io__raw__m_horizontal, this, this._root);
      this._io.seek(_pos);
      return this._m_horizontal;
    }
  });
  Object.defineProperty(Rigol1000zWfm.prototype, 'preheader', {
    get: function() {
      if (this._m_preheader !== undefined)
        return this._m_preheader;
      var _pos = this._io.pos;
      this._io.seek(0);
      this._m_preheader = new FileHeader(this._io, this, this._root);
      this._io.seek(_pos);
      return this._m_preheader;
    }
  });

  return Rigol1000zWfm;
})();
Rigol1000zWfm_.Rigol1000zWfm = Rigol1000zWfm;
});
