// This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild

(function (root, factory) {
  if (typeof define === 'function' && define.amd) {
    define(['exports', 'kaitai-struct/KaitaiStream'], factory);
  } else if (typeof exports === 'object' && exports !== null && typeof exports.nodeType !== 'number') {
    factory(exports, require('kaitai-struct/KaitaiStream'));
  } else {
    factory(root.SiglentV02Bin || (root.SiglentV02Bin = {}), root.KaitaiStream);
  }
})(typeof self !== 'undefined' ? self : this, function (SiglentV02Bin_, KaitaiStream) {
/**
 * Siglent waveform binary layout documented as "Binary Format V0.2".
 * 
 * V0.2 keeps the V0.1 analog-only sample packing but moves the horizontal
 * timing metadata to later offsets in the file.
 */

var SiglentV02Bin = (function() {
  function SiglentV02Bin(_io, _parent, _root) {
    this._io = _io;
    this._parent = _parent;
    this._root = _root || this;

    this._read();
  }
  SiglentV02Bin.prototype._read = function() {
  }

  var ScaledValue16 = SiglentV02Bin.ScaledValue16 = (function() {
    function ScaledValue16(_io, _parent, _root) {
      this._io = _io;
      this._parent = _parent;
      this._root = _root;

      this._read();
    }
    ScaledValue16.prototype._read = function() {
      this.value = this._io.readF8le();
      this.magnitude = this._io.readU4le();
      this.unit = this._io.readU4le();
    }

    return ScaledValue16;
  })();
  Object.defineProperty(SiglentV02Bin.prototype, 'ch1On', {
    get: function() {
      if (this._m_ch1On !== undefined)
        return this._m_ch1On;
      var _pos = this._io.pos;
      this._io.seek(68);
      this._m_ch1On = this._io.readS4le();
      this._io.seek(_pos);
      return this._m_ch1On;
    }
  });
  Object.defineProperty(SiglentV02Bin.prototype, 'ch1VertOffset', {
    get: function() {
      if (this._m_ch1VertOffset !== undefined)
        return this._m_ch1VertOffset;
      var _pos = this._io.pos;
      this._io.seek(196);
      this._m_ch1VertOffset = new ScaledValue16(this._io, this, this._root);
      this._io.seek(_pos);
      return this._m_ch1VertOffset;
    }
  });
  Object.defineProperty(SiglentV02Bin.prototype, 'ch1VoltDiv', {
    get: function() {
      if (this._m_ch1VoltDiv !== undefined)
        return this._m_ch1VoltDiv;
      var _pos = this._io.pos;
      this._io.seek(180);
      this._m_ch1VoltDiv = new ScaledValue16(this._io, this, this._root);
      this._io.seek(_pos);
      return this._m_ch1VoltDiv;
    }
  });
  Object.defineProperty(SiglentV02Bin.prototype, 'ch2On', {
    get: function() {
      if (this._m_ch2On !== undefined)
        return this._m_ch2On;
      var _pos = this._io.pos;
      this._io.seek(232);
      this._m_ch2On = this._io.readS4le();
      this._io.seek(_pos);
      return this._m_ch2On;
    }
  });
  Object.defineProperty(SiglentV02Bin.prototype, 'ch2VertOffset', {
    get: function() {
      if (this._m_ch2VertOffset !== undefined)
        return this._m_ch2VertOffset;
      var _pos = this._io.pos;
      this._io.seek(360);
      this._m_ch2VertOffset = new ScaledValue16(this._io, this, this._root);
      this._io.seek(_pos);
      return this._m_ch2VertOffset;
    }
  });
  Object.defineProperty(SiglentV02Bin.prototype, 'ch2VoltDiv', {
    get: function() {
      if (this._m_ch2VoltDiv !== undefined)
        return this._m_ch2VoltDiv;
      var _pos = this._io.pos;
      this._io.seek(344);
      this._m_ch2VoltDiv = new ScaledValue16(this._io, this, this._root);
      this._io.seek(_pos);
      return this._m_ch2VoltDiv;
    }
  });
  Object.defineProperty(SiglentV02Bin.prototype, 'ch3On', {
    get: function() {
      if (this._m_ch3On !== undefined)
        return this._m_ch3On;
      var _pos = this._io.pos;
      this._io.seek(396);
      this._m_ch3On = this._io.readS4le();
      this._io.seek(_pos);
      return this._m_ch3On;
    }
  });
  Object.defineProperty(SiglentV02Bin.prototype, 'ch3VertOffset', {
    get: function() {
      if (this._m_ch3VertOffset !== undefined)
        return this._m_ch3VertOffset;
      var _pos = this._io.pos;
      this._io.seek(524);
      this._m_ch3VertOffset = new ScaledValue16(this._io, this, this._root);
      this._io.seek(_pos);
      return this._m_ch3VertOffset;
    }
  });
  Object.defineProperty(SiglentV02Bin.prototype, 'ch3VoltDiv', {
    get: function() {
      if (this._m_ch3VoltDiv !== undefined)
        return this._m_ch3VoltDiv;
      var _pos = this._io.pos;
      this._io.seek(508);
      this._m_ch3VoltDiv = new ScaledValue16(this._io, this, this._root);
      this._io.seek(_pos);
      return this._m_ch3VoltDiv;
    }
  });
  Object.defineProperty(SiglentV02Bin.prototype, 'ch4On', {
    get: function() {
      if (this._m_ch4On !== undefined)
        return this._m_ch4On;
      var _pos = this._io.pos;
      this._io.seek(560);
      this._m_ch4On = this._io.readS4le();
      this._io.seek(_pos);
      return this._m_ch4On;
    }
  });
  Object.defineProperty(SiglentV02Bin.prototype, 'ch4VertOffset', {
    get: function() {
      if (this._m_ch4VertOffset !== undefined)
        return this._m_ch4VertOffset;
      var _pos = this._io.pos;
      this._io.seek(688);
      this._m_ch4VertOffset = new ScaledValue16(this._io, this, this._root);
      this._io.seek(_pos);
      return this._m_ch4VertOffset;
    }
  });
  Object.defineProperty(SiglentV02Bin.prototype, 'ch4VoltDiv', {
    get: function() {
      if (this._m_ch4VoltDiv !== undefined)
        return this._m_ch4VoltDiv;
      var _pos = this._io.pos;
      this._io.seek(672);
      this._m_ch4VoltDiv = new ScaledValue16(this._io, this, this._root);
      this._io.seek(_pos);
      return this._m_ch4VoltDiv;
    }
  });
  Object.defineProperty(SiglentV02Bin.prototype, 'sampleRate', {
    get: function() {
      if (this._m_sampleRate !== undefined)
        return this._m_sampleRate;
      var _pos = this._io.pos;
      this._io.seek(3548);
      this._m_sampleRate = new ScaledValue16(this._io, this, this._root);
      this._io.seek(_pos);
      return this._m_sampleRate;
    }
  });
  Object.defineProperty(SiglentV02Bin.prototype, 'timeDelay', {
    get: function() {
      if (this._m_timeDelay !== undefined)
        return this._m_timeDelay;
      var _pos = this._io.pos;
      this._io.seek(3528);
      this._m_timeDelay = new ScaledValue16(this._io, this, this._root);
      this._io.seek(_pos);
      return this._m_timeDelay;
    }
  });
  Object.defineProperty(SiglentV02Bin.prototype, 'timeDiv', {
    get: function() {
      if (this._m_timeDiv !== undefined)
        return this._m_timeDiv;
      var _pos = this._io.pos;
      this._io.seek(3512);
      this._m_timeDiv = new ScaledValue16(this._io, this, this._root);
      this._io.seek(_pos);
      return this._m_timeDiv;
    }
  });
  Object.defineProperty(SiglentV02Bin.prototype, 'waveData', {
    get: function() {
      if (this._m_waveData !== undefined)
        return this._m_waveData;
      var _pos = this._io.pos;
      this._io.seek(37676);
      this._m_waveData = this._io.readBytes(this._io.size - 37676);
      this._io.seek(_pos);
      return this._m_waveData;
    }
  });
  Object.defineProperty(SiglentV02Bin.prototype, 'waveLength', {
    get: function() {
      if (this._m_waveLength !== undefined)
        return this._m_waveLength;
      var _pos = this._io.pos;
      this._io.seek(3544);
      this._m_waveLength = this._io.readU4le();
      this._io.seek(_pos);
      return this._m_waveLength;
    }
  });

  return SiglentV02Bin;
})();
SiglentV02Bin_.SiglentV02Bin = SiglentV02Bin;
});
