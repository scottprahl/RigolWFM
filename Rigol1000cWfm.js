// This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild

(function (root, factory) {
  if (typeof define === 'function' && define.amd) {
    define(['exports', 'kaitai-struct/KaitaiStream'], factory);
  } else if (typeof exports === 'object' && exports !== null && typeof exports.nodeType !== 'number') {
    factory(exports, require('kaitai-struct/KaitaiStream'));
  } else {
    factory(root.Rigol1000cWfm || (root.Rigol1000cWfm = {}), root.KaitaiStream);
  }
})(typeof self !== 'undefined' ? self : this, function (Rigol1000cWfm_, KaitaiStream) {
/**
 * Waveform format for DS1000C/CD/MD/M series scopes.  Related to but distinct
 * from DS1000D/E: the magic byte at offset 0 is 0xA1 (versus 0xA5 for DS1000D),
 * data starts at offset 256 (versus 276 for DS1000D/E), there is an optional
 * 16-byte padding block before the sample data when byte 0 is 0xA5, and
 * volt_per_division includes the probe_value factor (DS1000D/E firmware stores
 * scale_measured already probe-corrected).
 */

var Rigol1000cWfm = (function() {
  Rigol1000cWfm.MachineModeEnum = Object.freeze({
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

  Rigol1000cWfm.TriggerModeEnum = Object.freeze({
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

  Rigol1000cWfm.TriggerSourceEnum = Object.freeze({
    CH1: 0,
    CH2: 1,
    EXT: 2,
    EXT5: 3,
    AC_LINE: 5,
    DIG_CH: 7,

    0: "CH1",
    1: "CH2",
    2: "EXT",
    3: "EXT5",
    5: "AC_LINE",
    7: "DIG_CH",
  });

  Rigol1000cWfm.UnitEnum = Object.freeze({
    W: 0,
    A: 1,
    V: 2,
    U: 3,

    0: "W",
    1: "A",
    2: "V",
    3: "U",
  });

  function Rigol1000cWfm(_io, _parent, _root) {
    this._io = _io;
    this._parent = _parent;
    this._root = _root || this;

    this._read();
  }
  Rigol1000cWfm.prototype._read = function() {
  }

  var ChannelHeader = Rigol1000cWfm.ChannelHeader = (function() {
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
        this._m_unit = Rigol1000cWfm.UnitEnum.V;
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
        this._m_voltScale = this.voltPerDivision / 25.0;
        return this._m_voltScale;
      }
    });

    return ChannelHeader;
  })();

  var Header = Rigol1000cWfm.Header = (function() {
    function Header(_io, _parent, _root) {
      this._io = _io;
      this._parent = _parent;
      this._root = _root;

      this._read();
    }
    Header.prototype._read = function() {
      this.byte1 = this._io.readU1();
      this.magic = this._io.readBytes(3);
      if (!((KaitaiStream.byteArrayCompare(this.magic, new Uint8Array([165, 0, 0])) == 0))) {
        throw new KaitaiStream.ValidationNotEqualError(new Uint8Array([165, 0, 0]), this.magic, this._io, "/types/header/seq/1");
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
      this.unknown6 = this._io.readU1();
      this.triggerSource = this._io.readU1();
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

  var RawData = Rigol1000cWfm.RawData = (function() {
    function RawData(_io, _parent, _root) {
      this._io = _io;
      this._parent = _parent;
      this._root = _root;

      this._read();
    }
    RawData.prototype._read = function() {
      if (this._root.header.byte1 == 165) {
        this.unused55 = this._io.readBytes(16);
      }
      if (this._root.header.ch[0].enabled) {
        this.ch1 = this._io.readBytes(this._root.header.points);
      }
      if (this._root.header.ch[1].enabled) {
        this.ch2 = this._io.readBytes(this._root.header.points);
      }
    }

    return RawData;
  })();
  Object.defineProperty(Rigol1000cWfm.prototype, 'data', {
    get: function() {
      if (this._m_data !== undefined)
        return this._m_data;
      var _pos = this._io.pos;
      this._io.seek(256);
      this._m_data = new RawData(this._io, this, this._root);
      this._io.seek(_pos);
      return this._m_data;
    }
  });
  Object.defineProperty(Rigol1000cWfm.prototype, 'header', {
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

  return Rigol1000cWfm;
})();
Rigol1000cWfm_.Rigol1000cWfm = Rigol1000cWfm;
});
