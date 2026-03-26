// This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild

(function (root, factory) {
  if (typeof define === 'function' && define.amd) {
    define(['exports', 'kaitai-struct/KaitaiStream'], factory);
  } else if (typeof exports === 'object' && exports !== null && typeof exports.nodeType !== 'number') {
    factory(exports, require('kaitai-struct/KaitaiStream'));
  } else {
    factory(root.Wfm1000d || (root.Wfm1000d = {}), root.KaitaiStream);
  }
})(typeof self !== 'undefined' ? self : this, function (Wfm1000d_, KaitaiStream) {
/**
 * Rigol DS1102D .wmf format abstracted from a Matlab script with the addition
 * of a few fields found in a Pascal program.  Neither program really examines
 * the header closely (meaning that they skip 26 bytes).
 * @see The Matlab script is from https://www.mathworks.com/matlabcentral/fileexchange/18999-read-binary-rigol-waveforms The Pascal program is from https://sourceforge.net/projects/wfmreader/
 */

var Wfm1000d = (function() {
  Wfm1000d.MachineModeEnum = Object.freeze({
    DS1000B: 0,
    DS1000C: 1,
    DS1000E: 2,
    DS1000Z: 3,
    DS2000: 4,
    DS4000: 5,
    DS6000: 6,

    0: "DS1000B",
    1: "DS1000C",
    2: "DS1000E",
    3: "DS1000Z",
    4: "DS2000",
    5: "DS4000",
    6: "DS6000",
  });

  Wfm1000d.SourceEnum = Object.freeze({
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

  Wfm1000d.TriggerModeEnum = Object.freeze({
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

  Wfm1000d.UnitEnum = Object.freeze({
    W: 0,
    A: 1,
    V: 2,
    U: 3,

    0: "W",
    1: "A",
    2: "V",
    3: "U",
  });

  function Wfm1000d(_io, _parent, _root) {
    this._io = _io;
    this._parent = _parent;
    this._root = _root || this;

    this._read();
  }
  Wfm1000d.prototype._read = function() {
  }

  var ChannelHeader = Wfm1000d.ChannelHeader = (function() {
    function ChannelHeader(_io, _parent, _root) {
      this._io = _io;
      this._parent = _parent;
      this._root = _root;

      this._read();
    }
    ChannelHeader.prototype._read = function() {
      this.scaleDisplay = this._io.readS4le();
      this.shiftDisplay = this._io.readS2le();
      this.unknown1 = this._io.readU1();
      this.unknown2 = this._io.readU1();
      this.probeValue = this._io.readF4le();
      this.invertDispVal = this._io.readU1();
      this.enabledVal = this._io.readU1();
      this.invertMVal = this._io.readU1();
      this.unknown3 = this._io.readU1();
      this.scaleMeasured = this._io.readS4le();
      this.shiftMeasured = this._io.readS2le();
      this.unknown3a = this._io.readU2le();
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
        this._m_inverted = (this.invertMVal != 0 ? true : false);
        return this._m_inverted;
      }
    });
    Object.defineProperty(ChannelHeader.prototype, 'timeOffset', {
      get: function() {
        if (this._m_timeOffset !== undefined)
          return this._m_timeOffset;
        this._m_timeOffset = this._root.header.timeOffset;
        return this._m_timeOffset;
      }
    });
    Object.defineProperty(ChannelHeader.prototype, 'timeScale', {
      get: function() {
        if (this._m_timeScale !== undefined)
          return this._m_timeScale;
        this._m_timeScale = this._root.header.timeScale;
        return this._m_timeScale;
      }
    });
    Object.defineProperty(ChannelHeader.prototype, 'unit', {
      get: function() {
        if (this._m_unit !== undefined)
          return this._m_unit;
        this._m_unit = Wfm1000d.UnitEnum.V;
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
        this._m_voltPerDivision = (this.inverted ? -0.0000010 * this.scaleMeasured : 0.0000010 * this.scaleMeasured);
        return this._m_voltPerDivision;
      }
    });
    Object.defineProperty(ChannelHeader.prototype, 'voltScale', {
      get: function() {
        if (this._m_voltScale !== undefined)
          return this._m_voltScale;
        this._m_voltScale = this.voltPerDivision / 25.0;
        return this._m_voltScale;
      }
    });

    return ChannelHeader;
  })();

  var Header = Wfm1000d.Header = (function() {
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
      this.unknown1 = [];
      for (var i = 0; i < 6; i++) {
        this.unknown1.push(this._io.readU4le());
      }
      this.points = this._io.readU4le();
      this.activeChannel = this._io.readU1();
      this.unknown2a = this._io.readBytes(3);
      this.ch = [];
      for (var i = 0; i < 2; i++) {
        this.ch.push(new ChannelHeader(this._io, this, this._root));
      }
      this.timeScale = this._io.readU8le();
      this.timeOffset = this._io.readS8le();
      this.sampleRateHz = this._io.readF4le();
      this.unknown3 = [];
      for (var i = 0; i < 9; i++) {
        this.unknown3.push(this._io.readU4le());
      }
      this.unknown4 = this._io.readU2le();
      this.triggerMode = this._io.readU1();
      this.trigger1 = new TriggerHeader(this._io, this, this._root);
      this.trigger2 = new TriggerHeader(this._io, this, this._root);
    }
    Object.defineProperty(Header.prototype, 'secondsPerPoint', {
      get: function() {
        if (this._m_secondsPerPoint !== undefined)
          return this._m_secondsPerPoint;
        this._m_secondsPerPoint = 1.0 / this.sampleRateHz;
        return this._m_secondsPerPoint;
      }
    });

    return Header;
  })();

  var RawData = Wfm1000d.RawData = (function() {
    function RawData(_io, _parent, _root) {
      this._io = _io;
      this._parent = _parent;
      this._root = _root;

      this._read();
    }
    RawData.prototype._read = function() {
      if (this._root.header.ch[0].enabled) {
        this.ch1 = this._io.readBytes(this._root.header.points);
      }
      if (this._root.header.ch[1].enabled) {
        this.ch2 = this._io.readBytes(this._root.header.points);
      }
    }

    return RawData;
  })();

  var TriggerHeader = Wfm1000d.TriggerHeader = (function() {
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
  Object.defineProperty(Wfm1000d.prototype, 'data', {
    get: function() {
      if (this._m_data !== undefined)
        return this._m_data;
      var _pos = this._io.pos;
      this._io.seek(272);
      this._m_data = new RawData(this._io, this, this._root);
      this._io.seek(_pos);
      return this._m_data;
    }
  });
  Object.defineProperty(Wfm1000d.prototype, 'header', {
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

  return Wfm1000d;
})();
Wfm1000d_.Wfm1000d = Wfm1000d;
});
