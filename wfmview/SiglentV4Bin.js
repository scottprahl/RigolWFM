// This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild

(function (root, factory) {
  if (typeof define === 'function' && define.amd) {
    define(['exports', 'kaitai-struct/KaitaiStream'], factory);
  } else if (typeof exports === 'object' && exports !== null && typeof exports.nodeType !== 'number') {
    factory(exports, require('kaitai-struct/KaitaiStream'));
  } else {
    factory(root.SiglentV4Bin || (root.SiglentV4Bin = {}), root.KaitaiStream);
  }
})(typeof self !== 'undefined' ? self : this, function (SiglentV4Bin_, KaitaiStream) {
/**
 * Siglent waveform binary layout documented as "Binary Format V4.0".
 * 
 * V4.0 increases the header size to 4 KiB, adds a data-offset field, and
 * expands the analog channel metadata to support up to eight channels plus
 * additional memory/zoom parameters.
 * 
 * Sources used for this KSY binary format: The binary waveform layout documented by 
 * Siglent as "How to Extract Data from the Binary File of SIGLENT Oscilloscope". 
 * 
 * Tested file formats: the synthetic `Binary Format V4.0` fixture in
 * `tests/test_siglent.py`, exercised through revision detection, low-level
 * Kaitai parsing, and normalized waveform loading.
 * 
 * Oscilloscope models this format may apply to: Siglent instruments that write
 * `Binary Format V4.0`; the checked-in tests do not yet narrow this revision to
 * a smaller verified model list.
 */

var SiglentV4Bin = (function() {
  function SiglentV4Bin(_io, _parent, _root) {
    this._io = _io;
    this._parent = _parent;
    this._root = _root || this;

    this._read();
  }
  SiglentV4Bin.prototype._read = function() {
  }

  var DataWithUnit = SiglentV4Bin.DataWithUnit = (function() {
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

  var DataWithUnitArray4 = SiglentV4Bin.DataWithUnitArray4 = (function() {
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

  var F8Array4 = SiglentV4Bin.F8Array4 = (function() {
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

  var S4Array4 = SiglentV4Bin.S4Array4 = (function() {
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

  var U4Array16 = SiglentV4Bin.U4Array16 = (function() {
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

  var U4Array4 = SiglentV4Bin.U4Array4 = (function() {
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
  Object.defineProperty(SiglentV4Bin.prototype, 'byteOrder', {
    get: function() {
      if (this._m_byteOrder !== undefined)
        return this._m_byteOrder;
      var _pos = this._io.pos;
      this._io.seek(613);
      this._m_byteOrder = this._io.readU1();
      this._io.seek(_pos);
      return this._m_byteOrder;
    }
  });
  Object.defineProperty(SiglentV4Bin.prototype, 'chOn14', {
    get: function() {
      if (this._m_chOn14 !== undefined)
        return this._m_chOn14;
      var _pos = this._io.pos;
      this._io.seek(8);
      this._m_chOn14 = new S4Array4(this._io, this, this._root);
      this._io.seek(_pos);
      return this._m_chOn14;
    }
  });
  Object.defineProperty(SiglentV4Bin.prototype, 'chOn58', {
    get: function() {
      if (this._m_chOn58 !== undefined)
        return this._m_chOn58;
      var _pos = this._io.pos;
      this._io.seek(1028);
      this._m_chOn58 = new S4Array4(this._io, this, this._root);
      this._io.seek(_pos);
      return this._m_chOn58;
    }
  });
  Object.defineProperty(SiglentV4Bin.prototype, 'chProbe14', {
    get: function() {
      if (this._m_chProbe14 !== undefined)
        return this._m_chProbe14;
      var _pos = this._io.pos;
      this._io.seek(580);
      this._m_chProbe14 = new F8Array4(this._io, this, this._root);
      this._io.seek(_pos);
      return this._m_chProbe14;
    }
  });
  Object.defineProperty(SiglentV4Bin.prototype, 'chProbe58', {
    get: function() {
      if (this._m_chProbe58 !== undefined)
        return this._m_chProbe58;
      var _pos = this._io.pos;
      this._io.seek(1364);
      this._m_chProbe58 = new F8Array4(this._io, this, this._root);
      this._io.seek(_pos);
      return this._m_chProbe58;
    }
  });
  Object.defineProperty(SiglentV4Bin.prototype, 'chVertCodePerDiv14', {
    get: function() {
      if (this._m_chVertCodePerDiv14 !== undefined)
        return this._m_chVertCodePerDiv14;
      var _pos = this._io.pos;
      this._io.seek(624);
      this._m_chVertCodePerDiv14 = new S4Array4(this._io, this, this._root);
      this._io.seek(_pos);
      return this._m_chVertCodePerDiv14;
    }
  });
  Object.defineProperty(SiglentV4Bin.prototype, 'chVertCodePerDiv58', {
    get: function() {
      if (this._m_chVertCodePerDiv58 !== undefined)
        return this._m_chVertCodePerDiv58;
      var _pos = this._io.pos;
      this._io.seek(1396);
      this._m_chVertCodePerDiv58 = new S4Array4(this._io, this, this._root);
      this._io.seek(_pos);
      return this._m_chVertCodePerDiv58;
    }
  });
  Object.defineProperty(SiglentV4Bin.prototype, 'chVertOffset14', {
    get: function() {
      if (this._m_chVertOffset14 !== undefined)
        return this._m_chVertOffset14;
      var _pos = this._io.pos;
      this._io.seek(184);
      this._m_chVertOffset14 = new DataWithUnitArray4(this._io, this, this._root);
      this._io.seek(_pos);
      return this._m_chVertOffset14;
    }
  });
  Object.defineProperty(SiglentV4Bin.prototype, 'chVertOffset58', {
    get: function() {
      if (this._m_chVertOffset58 !== undefined)
        return this._m_chVertOffset58;
      var _pos = this._io.pos;
      this._io.seek(1204);
      this._m_chVertOffset58 = new DataWithUnitArray4(this._io, this, this._root);
      this._io.seek(_pos);
      return this._m_chVertOffset58;
    }
  });
  Object.defineProperty(SiglentV4Bin.prototype, 'chVoltDiv14', {
    get: function() {
      if (this._m_chVoltDiv14 !== undefined)
        return this._m_chVoltDiv14;
      var _pos = this._io.pos;
      this._io.seek(24);
      this._m_chVoltDiv14 = new DataWithUnitArray4(this._io, this, this._root);
      this._io.seek(_pos);
      return this._m_chVoltDiv14;
    }
  });
  Object.defineProperty(SiglentV4Bin.prototype, 'chVoltDiv58', {
    get: function() {
      if (this._m_chVoltDiv58 !== undefined)
        return this._m_chVoltDiv58;
      var _pos = this._io.pos;
      this._io.seek(1044);
      this._m_chVoltDiv58 = new DataWithUnitArray4(this._io, this, this._root);
      this._io.seek(_pos);
      return this._m_chVoltDiv58;
    }
  });
  Object.defineProperty(SiglentV4Bin.prototype, 'dataOffsetByte', {
    get: function() {
      if (this._m_dataOffsetByte !== undefined)
        return this._m_dataOffsetByte;
      var _pos = this._io.pos;
      this._io.seek(4);
      this._m_dataOffsetByte = this._io.readU4le();
      this._io.seek(_pos);
      return this._m_dataOffsetByte;
    }
  });
  Object.defineProperty(SiglentV4Bin.prototype, 'dataWidth', {
    get: function() {
      if (this._m_dataWidth !== undefined)
        return this._m_dataWidth;
      var _pos = this._io.pos;
      this._io.seek(612);
      this._m_dataWidth = this._io.readU1();
      this._io.seek(_pos);
      return this._m_dataWidth;
    }
  });
  Object.defineProperty(SiglentV4Bin.prototype, 'digitalChOn', {
    get: function() {
      if (this._m_digitalChOn !== undefined)
        return this._m_digitalChOn;
      var _pos = this._io.pos;
      this._io.seek(348);
      this._m_digitalChOn = new U4Array16(this._io, this, this._root);
      this._io.seek(_pos);
      return this._m_digitalChOn;
    }
  });
  Object.defineProperty(SiglentV4Bin.prototype, 'digitalOn', {
    get: function() {
      if (this._m_digitalOn !== undefined)
        return this._m_digitalOn;
      var _pos = this._io.pos;
      this._io.seek(344);
      this._m_digitalOn = this._io.readU4le();
      this._io.seek(_pos);
      return this._m_digitalOn;
    }
  });
  Object.defineProperty(SiglentV4Bin.prototype, 'digitalSampleRate', {
    get: function() {
      if (this._m_digitalSampleRate !== undefined)
        return this._m_digitalSampleRate;
      var _pos = this._io.pos;
      this._io.seek(540);
      this._m_digitalSampleRate = new DataWithUnit(this._io, this, this._root);
      this._io.seek(_pos);
      return this._m_digitalSampleRate;
    }
  });
  Object.defineProperty(SiglentV4Bin.prototype, 'digitalWaveLength', {
    get: function() {
      if (this._m_digitalWaveLength !== undefined)
        return this._m_digitalWaveLength;
      var _pos = this._io.pos;
      this._io.seek(536);
      this._m_digitalWaveLength = this._io.readU4le();
      this._io.seek(_pos);
      return this._m_digitalWaveLength;
    }
  });
  Object.defineProperty(SiglentV4Bin.prototype, 'horiDivNum', {
    get: function() {
      if (this._m_horiDivNum !== undefined)
        return this._m_horiDivNum;
      var _pos = this._io.pos;
      this._io.seek(620);
      this._m_horiDivNum = this._io.readS4le();
      this._io.seek(_pos);
      return this._m_horiDivNum;
    }
  });
  Object.defineProperty(SiglentV4Bin.prototype, 'mathFTime', {
    get: function() {
      if (this._m_mathFTime !== undefined)
        return this._m_mathFTime;
      var _pos = this._io.pos;
      this._io.seek(992);
      this._m_mathFTime = new F8Array4(this._io, this, this._root);
      this._io.seek(_pos);
      return this._m_mathFTime;
    }
  });
  Object.defineProperty(SiglentV4Bin.prototype, 'mathStoreLen', {
    get: function() {
      if (this._m_mathStoreLen !== undefined)
        return this._m_mathStoreLen;
      var _pos = this._io.pos;
      this._io.seek(976);
      this._m_mathStoreLen = new U4Array4(this._io, this, this._root);
      this._io.seek(_pos);
      return this._m_mathStoreLen;
    }
  });
  Object.defineProperty(SiglentV4Bin.prototype, 'mathSwitch', {
    get: function() {
      if (this._m_mathSwitch !== undefined)
        return this._m_mathSwitch;
      var _pos = this._io.pos;
      this._io.seek(640);
      this._m_mathSwitch = new S4Array4(this._io, this, this._root);
      this._io.seek(_pos);
      return this._m_mathSwitch;
    }
  });
  Object.defineProperty(SiglentV4Bin.prototype, 'mathVertCodePerDiv', {
    get: function() {
      if (this._m_mathVertCodePerDiv !== undefined)
        return this._m_mathVertCodePerDiv;
      var _pos = this._io.pos;
      this._io.seek(1024);
      this._m_mathVertCodePerDiv = this._io.readS4le();
      this._io.seek(_pos);
      return this._m_mathVertCodePerDiv;
    }
  });
  Object.defineProperty(SiglentV4Bin.prototype, 'sampleRate', {
    get: function() {
      if (this._m_sampleRate !== undefined)
        return this._m_sampleRate;
      var _pos = this._io.pos;
      this._io.seek(496);
      this._m_sampleRate = new DataWithUnit(this._io, this, this._root);
      this._io.seek(_pos);
      return this._m_sampleRate;
    }
  });
  Object.defineProperty(SiglentV4Bin.prototype, 'timeDelay', {
    get: function() {
      if (this._m_timeDelay !== undefined)
        return this._m_timeDelay;
      var _pos = this._io.pos;
      this._io.seek(452);
      this._m_timeDelay = new DataWithUnit(this._io, this, this._root);
      this._io.seek(_pos);
      return this._m_timeDelay;
    }
  });
  Object.defineProperty(SiglentV4Bin.prototype, 'timeDiv', {
    get: function() {
      if (this._m_timeDiv !== undefined)
        return this._m_timeDiv;
      var _pos = this._io.pos;
      this._io.seek(412);
      this._m_timeDiv = new DataWithUnit(this._io, this, this._root);
      this._io.seek(_pos);
      return this._m_timeDiv;
    }
  });
  Object.defineProperty(SiglentV4Bin.prototype, 'version', {
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
  Object.defineProperty(SiglentV4Bin.prototype, 'waveData', {
    get: function() {
      if (this._m_waveData !== undefined)
        return this._m_waveData;
      var _pos = this._io.pos;
      this._io.seek(this.dataOffsetByte);
      this._m_waveData = this._io.readBytes(this._io.size - this.dataOffsetByte);
      this._io.seek(_pos);
      return this._m_waveData;
    }
  });
  Object.defineProperty(SiglentV4Bin.prototype, 'waveLength', {
    get: function() {
      if (this._m_waveLength !== undefined)
        return this._m_waveLength;
      var _pos = this._io.pos;
      this._io.seek(492);
      this._m_waveLength = this._io.readU4le();
      this._io.seek(_pos);
      return this._m_waveLength;
    }
  });

  return SiglentV4Bin;
})();
SiglentV4Bin_.SiglentV4Bin = SiglentV4Bin;
});
