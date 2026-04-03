// This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild

(function (root, factory) {
  if (typeof define === 'function' && define.amd) {
    define(['exports', 'kaitai-struct/KaitaiStream'], factory);
  } else if (typeof exports === 'object' && exports !== null && typeof exports.nodeType !== 'number') {
    factory(exports, require('kaitai-struct/KaitaiStream'));
  } else {
    factory(root.Rigol1000bWfm || (root.Rigol1000bWfm = {}), root.KaitaiStream);
  }
})(typeof self !== 'undefined' ? self : this, function (Rigol1000bWfm_, KaitaiStream) {
/**
 * This was put together based on an excel header list of unknown provenance.
 * It has been tested with a handful of different files.  The offset to the
 * data seems correct but the channel coupling is untested.
 */

var Rigol1000bWfm = (function() {
  Rigol1000bWfm.MachineModeEnum = Object.freeze({
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

  Rigol1000bWfm.TriggerModeEnum = Object.freeze({
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

  Rigol1000bWfm.TriggerSourceEnum = Object.freeze({
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

  Rigol1000bWfm.UnitEnum = Object.freeze({
    W: 0,
    A: 1,
    V: 2,
    U: 3,

    0: "W",
    1: "A",
    2: "V",
    3: "U",
  });

  function Rigol1000bWfm(_io, _parent, _root) {
    this._io = _io;
    this._parent = _parent;
    this._root = _root || this;

    this._read();
  }
  Rigol1000bWfm.prototype._read = function() {
  }

  var ChannelHeader = Rigol1000bWfm.ChannelHeader = (function() {
    function ChannelHeader(_io, _parent, _root) {
      this._io = _io;
      this._parent = _parent;
      this._root = _root;

      this._read();
    }
    ChannelHeader.prototype._read = function() {
      this.scaleDisplay = this._io.readS4le();
      this.shiftDisplay = this._io.readS2le();
      this.unknown1 = this._io.readBytes(2);
      this.probeValue = this._io.readF4le();
      this.probeType = this._io.readS1();
      this.invertDispVal = this._io.readU1();
      this.enabledVal = this._io.readU1();
      this.invertMVal = this._io.readU1();
      this.scaleMeasured = this._io.readS4le();
      this.shiftMeasured = this._io.readS2le();
      this.timeDelayed = this._io.readU1();
      this.unknown2 = this._io.readBytes(1);
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
        this._m_unit = Rigol1000bWfm.UnitEnum.V;
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

  var Header = Rigol1000bWfm.Header = (function() {
    function Header(_io, _parent, _root) {
      this._io = _io;
      this._parent = _parent;
      this._root = _root;

      this._read();
    }
    Header.prototype._read = function() {
      this.magic = this._io.readBytes(4);
      if (!((KaitaiStream.byteArrayCompare(this.magic, new Uint8Array([165, 165, 164, 1])) == 0))) {
        throw new KaitaiStream.ValidationNotEqualError(new Uint8Array([165, 165, 164, 1]), this.magic, this._io, "/types/header/seq/0");
      }
      this.scopetype = KaitaiStream.bytesToStr(KaitaiStream.bytesTerminate(this._io.readBytes(8), 0, false), "UTF-8");
      this.unknown1 = this._io.readBytes(44);
      this.adcmode = this._io.readU1();
      this.unknown2 = this._io.readBytes(3);
      this.points = this._io.readU4le();
      this.activeChannel = this._io.readU1();
      this.unknown3 = this._io.readBytes(3);
      this.ch = [];
      for (var i = 0; i < 4; i++) {
        this.ch.push(new ChannelHeader(this._io, this, this._root));
      }
      this.timeScale = this._io.readU8le();
      this.timeOffset = this._io.readS8le();
      this.sampleRateHz = this._io.readF4le();
      this.timeScaleStop = this._io.readU8le();
      this.timeScaleOffset = this._io.readS8le();
      this.unknown4 = [];
      for (var i = 0; i < 4; i++) {
        this.unknown4.push(this._io.readU4le());
      }
      this.couplingCh12 = this._io.readU1();
      this.couplingCh34 = this._io.readU1();
      this.unknown5 = this._io.readBytes(4);
      this.triggerMode = this._io.readU1();
      this.unknown6 = this._io.readU1();
      this.triggerSource = this._io.readU1();
    }
    Object.defineProperty(Header.prototype, 'ch1', {
      get: function() {
        if (this._m_ch1 !== undefined)
          return this._m_ch1;
        if (this.ch[0].enabled) {
          var io = this._root._io;
          var _pos = io.pos;
          io.seek(420);
          this._m_ch1 = io.readBytes(this.lenCh1);
          io.seek(_pos);
        }
        return this._m_ch1;
      }
    });
    Object.defineProperty(Header.prototype, 'ch2', {
      get: function() {
        if (this._m_ch2 !== undefined)
          return this._m_ch2;
        if (this.ch[1].enabled) {
          var io = this._root._io;
          var _pos = io.pos;
          io.seek(420 + this._root.header.points);
          this._m_ch2 = io.readBytes(this.lenCh2);
          io.seek(_pos);
        }
        return this._m_ch2;
      }
    });
    Object.defineProperty(Header.prototype, 'ch3', {
      get: function() {
        if (this._m_ch3 !== undefined)
          return this._m_ch3;
        if (this.ch[2].enabled) {
          var io = this._root._io;
          var _pos = io.pos;
          io.seek(420 + this._root.header.points * 2);
          this._m_ch3 = io.readBytes(this.lenCh3);
          io.seek(_pos);
        }
        return this._m_ch3;
      }
    });
    Object.defineProperty(Header.prototype, 'ch4', {
      get: function() {
        if (this._m_ch4 !== undefined)
          return this._m_ch4;
        if (this.ch[3].enabled) {
          var io = this._root._io;
          var _pos = io.pos;
          io.seek(420 + this._root.header.points * 3);
          this._m_ch4 = io.readBytes(this.lenCh4);
          io.seek(_pos);
        }
        return this._m_ch4;
      }
    });
    Object.defineProperty(Header.prototype, 'lenCh1', {
      get: function() {
        if (this._m_lenCh1 !== undefined)
          return this._m_lenCh1;
        this._m_lenCh1 = (this.ch[0].enabled ? this.points : 0);
        return this._m_lenCh1;
      }
    });
    Object.defineProperty(Header.prototype, 'lenCh2', {
      get: function() {
        if (this._m_lenCh2 !== undefined)
          return this._m_lenCh2;
        this._m_lenCh2 = (this.ch[1].enabled ? this.points : 0);
        return this._m_lenCh2;
      }
    });
    Object.defineProperty(Header.prototype, 'lenCh3', {
      get: function() {
        if (this._m_lenCh3 !== undefined)
          return this._m_lenCh3;
        this._m_lenCh3 = (this.ch[2].enabled ? this.points : 0);
        return this._m_lenCh3;
      }
    });
    Object.defineProperty(Header.prototype, 'lenCh4', {
      get: function() {
        if (this._m_lenCh4 !== undefined)
          return this._m_lenCh4;
        this._m_lenCh4 = (this.ch[3].enabled ? this.points : 0);
        return this._m_lenCh4;
      }
    });
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
  Object.defineProperty(Rigol1000bWfm.prototype, 'header', {
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

  return Rigol1000bWfm;
})();
Rigol1000bWfm_.Rigol1000bWfm = Rigol1000bWfm;
});
