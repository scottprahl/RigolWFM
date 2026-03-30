// This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild

(function (root, factory) {
  if (typeof define === 'function' && define.amd) {
    define(['exports', 'kaitai-struct/KaitaiStream'], factory);
  } else if (typeof exports === 'object' && exports !== null && typeof exports.nodeType !== 'number') {
    factory(exports, require('kaitai-struct/KaitaiStream'));
  } else {
    factory(root.SiglentV3 || (root.SiglentV3 = {}), root.KaitaiStream);
  }
})(typeof self !== 'undefined' ? self : this, function (SiglentV3_, KaitaiStream) {
/**
 * Siglent waveform binary layout documented as "Binary Format V3.0".
 * 
 * V3.0 retains the V2.0 2 KiB header but adds byte order, horizontal grid
 * count, per-channel code-per-division values, and math-wave metadata.
 */

var SiglentV3 = (function() {
  function SiglentV3(_io, _parent, _root) {
    this._io = _io;
    this._parent = _parent;
    this._root = _root || this;

    this._read();
  }
  SiglentV3.prototype._read = function() {
  }

  var DataWithUnit = SiglentV3.DataWithUnit = (function() {
    function DataWithUnit(_io, _parent, _root) {
      this._io = _io;
      this._parent = _parent;
      this._root = _root;

      this._read();
    }
    DataWithUnit.prototype._read = function() {
      this.value = this._io.readF8le();
      this.magnitude = this._io.readU4le();
      this.unitWords = [];
      for (var i = 0; i < 7; i++) {
        this.unitWords.push(this._io.readU4le());
      }
    }

    return DataWithUnit;
  })();

  var DataWithUnitArray4 = SiglentV3.DataWithUnitArray4 = (function() {
    function DataWithUnitArray4(_io, _parent, _root) {
      this._io = _io;
      this._parent = _parent;
      this._root = _root;

      this._read();
    }
    DataWithUnitArray4.prototype._read = function() {
      this.entries = [];
      for (var i = 0; i < 4; i++) {
        this.entries.push(new DataWithUnit(this._io, this, this._root));
      }
    }

    return DataWithUnitArray4;
  })();

  var F8Array4 = SiglentV3.F8Array4 = (function() {
    function F8Array4(_io, _parent, _root) {
      this._io = _io;
      this._parent = _parent;
      this._root = _root;

      this._read();
    }
    F8Array4.prototype._read = function() {
      this.entries = [];
      for (var i = 0; i < 4; i++) {
        this.entries.push(this._io.readF8le());
      }
    }

    return F8Array4;
  })();

  var S4Array4 = SiglentV3.S4Array4 = (function() {
    function S4Array4(_io, _parent, _root) {
      this._io = _io;
      this._parent = _parent;
      this._root = _root;

      this._read();
    }
    S4Array4.prototype._read = function() {
      this.entries = [];
      for (var i = 0; i < 4; i++) {
        this.entries.push(this._io.readS4le());
      }
    }

    return S4Array4;
  })();

  var U4Array16 = SiglentV3.U4Array16 = (function() {
    function U4Array16(_io, _parent, _root) {
      this._io = _io;
      this._parent = _parent;
      this._root = _root;

      this._read();
    }
    U4Array16.prototype._read = function() {
      this.entries = [];
      for (var i = 0; i < 16; i++) {
        this.entries.push(this._io.readU4le());
      }
    }

    return U4Array16;
  })();

  var U4Array4 = SiglentV3.U4Array4 = (function() {
    function U4Array4(_io, _parent, _root) {
      this._io = _io;
      this._parent = _parent;
      this._root = _root;

      this._read();
    }
    U4Array4.prototype._read = function() {
      this.entries = [];
      for (var i = 0; i < 4; i++) {
        this.entries.push(this._io.readU4le());
      }
    }

    return U4Array4;
  })();
  Object.defineProperty(SiglentV3.prototype, 'byteOrder', {
    get: function() {
      if (this._m_byteOrder !== undefined)
        return this._m_byteOrder;
      var _pos = this._io.pos;
      this._io.seek(609);
      this._m_byteOrder = this._io.readU1();
      this._io.seek(_pos);
      return this._m_byteOrder;
    }
  });
  Object.defineProperty(SiglentV3.prototype, 'chOn', {
    get: function() {
      if (this._m_chOn !== undefined)
        return this._m_chOn;
      var _pos = this._io.pos;
      this._io.seek(4);
      this._m_chOn = new S4Array4(this._io, this, this._root);
      this._io.seek(_pos);
      return this._m_chOn;
    }
  });
  Object.defineProperty(SiglentV3.prototype, 'chProbe', {
    get: function() {
      if (this._m_chProbe !== undefined)
        return this._m_chProbe;
      var _pos = this._io.pos;
      this._io.seek(576);
      this._m_chProbe = new F8Array4(this._io, this, this._root);
      this._io.seek(_pos);
      return this._m_chProbe;
    }
  });
  Object.defineProperty(SiglentV3.prototype, 'chVertCodePerDiv', {
    get: function() {
      if (this._m_chVertCodePerDiv !== undefined)
        return this._m_chVertCodePerDiv;
      var _pos = this._io.pos;
      this._io.seek(620);
      this._m_chVertCodePerDiv = new S4Array4(this._io, this, this._root);
      this._io.seek(_pos);
      return this._m_chVertCodePerDiv;
    }
  });
  Object.defineProperty(SiglentV3.prototype, 'chVertOffset', {
    get: function() {
      if (this._m_chVertOffset !== undefined)
        return this._m_chVertOffset;
      var _pos = this._io.pos;
      this._io.seek(180);
      this._m_chVertOffset = new DataWithUnitArray4(this._io, this, this._root);
      this._io.seek(_pos);
      return this._m_chVertOffset;
    }
  });
  Object.defineProperty(SiglentV3.prototype, 'chVoltDiv', {
    get: function() {
      if (this._m_chVoltDiv !== undefined)
        return this._m_chVoltDiv;
      var _pos = this._io.pos;
      this._io.seek(20);
      this._m_chVoltDiv = new DataWithUnitArray4(this._io, this, this._root);
      this._io.seek(_pos);
      return this._m_chVoltDiv;
    }
  });
  Object.defineProperty(SiglentV3.prototype, 'dataWidth', {
    get: function() {
      if (this._m_dataWidth !== undefined)
        return this._m_dataWidth;
      var _pos = this._io.pos;
      this._io.seek(608);
      this._m_dataWidth = this._io.readU1();
      this._io.seek(_pos);
      return this._m_dataWidth;
    }
  });
  Object.defineProperty(SiglentV3.prototype, 'digitalChOn', {
    get: function() {
      if (this._m_digitalChOn !== undefined)
        return this._m_digitalChOn;
      var _pos = this._io.pos;
      this._io.seek(344);
      this._m_digitalChOn = new U4Array16(this._io, this, this._root);
      this._io.seek(_pos);
      return this._m_digitalChOn;
    }
  });
  Object.defineProperty(SiglentV3.prototype, 'digitalOn', {
    get: function() {
      if (this._m_digitalOn !== undefined)
        return this._m_digitalOn;
      var _pos = this._io.pos;
      this._io.seek(340);
      this._m_digitalOn = this._io.readU4le();
      this._io.seek(_pos);
      return this._m_digitalOn;
    }
  });
  Object.defineProperty(SiglentV3.prototype, 'digitalSampleRate', {
    get: function() {
      if (this._m_digitalSampleRate !== undefined)
        return this._m_digitalSampleRate;
      var _pos = this._io.pos;
      this._io.seek(536);
      this._m_digitalSampleRate = new DataWithUnit(this._io, this, this._root);
      this._io.seek(_pos);
      return this._m_digitalSampleRate;
    }
  });
  Object.defineProperty(SiglentV3.prototype, 'digitalWaveLength', {
    get: function() {
      if (this._m_digitalWaveLength !== undefined)
        return this._m_digitalWaveLength;
      var _pos = this._io.pos;
      this._io.seek(532);
      this._m_digitalWaveLength = this._io.readU4le();
      this._io.seek(_pos);
      return this._m_digitalWaveLength;
    }
  });
  Object.defineProperty(SiglentV3.prototype, 'horiDivNum', {
    get: function() {
      if (this._m_horiDivNum !== undefined)
        return this._m_horiDivNum;
      var _pos = this._io.pos;
      this._io.seek(616);
      this._m_horiDivNum = this._io.readS4le();
      this._io.seek(_pos);
      return this._m_horiDivNum;
    }
  });
  Object.defineProperty(SiglentV3.prototype, 'mathFTime', {
    get: function() {
      if (this._m_mathFTime !== undefined)
        return this._m_mathFTime;
      var _pos = this._io.pos;
      this._io.seek(988);
      this._m_mathFTime = new F8Array4(this._io, this, this._root);
      this._io.seek(_pos);
      return this._m_mathFTime;
    }
  });
  Object.defineProperty(SiglentV3.prototype, 'mathStoreLen', {
    get: function() {
      if (this._m_mathStoreLen !== undefined)
        return this._m_mathStoreLen;
      var _pos = this._io.pos;
      this._io.seek(972);
      this._m_mathStoreLen = new U4Array4(this._io, this, this._root);
      this._io.seek(_pos);
      return this._m_mathStoreLen;
    }
  });
  Object.defineProperty(SiglentV3.prototype, 'mathSwitch', {
    get: function() {
      if (this._m_mathSwitch !== undefined)
        return this._m_mathSwitch;
      var _pos = this._io.pos;
      this._io.seek(636);
      this._m_mathSwitch = new S4Array4(this._io, this, this._root);
      this._io.seek(_pos);
      return this._m_mathSwitch;
    }
  });
  Object.defineProperty(SiglentV3.prototype, 'mathVertCodePerDiv', {
    get: function() {
      if (this._m_mathVertCodePerDiv !== undefined)
        return this._m_mathVertCodePerDiv;
      var _pos = this._io.pos;
      this._io.seek(1020);
      this._m_mathVertCodePerDiv = this._io.readS4le();
      this._io.seek(_pos);
      return this._m_mathVertCodePerDiv;
    }
  });
  Object.defineProperty(SiglentV3.prototype, 'sampleRate', {
    get: function() {
      if (this._m_sampleRate !== undefined)
        return this._m_sampleRate;
      var _pos = this._io.pos;
      this._io.seek(492);
      this._m_sampleRate = new DataWithUnit(this._io, this, this._root);
      this._io.seek(_pos);
      return this._m_sampleRate;
    }
  });
  Object.defineProperty(SiglentV3.prototype, 'timeDelay', {
    get: function() {
      if (this._m_timeDelay !== undefined)
        return this._m_timeDelay;
      var _pos = this._io.pos;
      this._io.seek(448);
      this._m_timeDelay = new DataWithUnit(this._io, this, this._root);
      this._io.seek(_pos);
      return this._m_timeDelay;
    }
  });
  Object.defineProperty(SiglentV3.prototype, 'timeDiv', {
    get: function() {
      if (this._m_timeDiv !== undefined)
        return this._m_timeDiv;
      var _pos = this._io.pos;
      this._io.seek(408);
      this._m_timeDiv = new DataWithUnit(this._io, this, this._root);
      this._io.seek(_pos);
      return this._m_timeDiv;
    }
  });
  Object.defineProperty(SiglentV3.prototype, 'version', {
    get: function() {
      if (this._m_version !== undefined)
        return this._m_version;
      var _pos = this._io.pos;
      this._io.seek(0);
      this._m_version = this._io.readU4le();
      this._io.seek(_pos);
      return this._m_version;
    }
  });
  Object.defineProperty(SiglentV3.prototype, 'waveData', {
    get: function() {
      if (this._m_waveData !== undefined)
        return this._m_waveData;
      var _pos = this._io.pos;
      this._io.seek(2048);
      this._m_waveData = this._io.readBytes(this._io.size - 2048);
      this._io.seek(_pos);
      return this._m_waveData;
    }
  });
  Object.defineProperty(SiglentV3.prototype, 'waveLength', {
    get: function() {
      if (this._m_waveLength !== undefined)
        return this._m_waveLength;
      var _pos = this._io.pos;
      this._io.seek(488);
      this._m_waveLength = this._io.readU4le();
      this._io.seek(_pos);
      return this._m_waveLength;
    }
  });

  return SiglentV3;
})();
SiglentV3_.SiglentV3 = SiglentV3;
});
