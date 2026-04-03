// This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild

(function (root, factory) {
  if (typeof define === 'function' && define.amd) {
    define(['exports', 'kaitai-struct/KaitaiStream'], factory);
  } else if (typeof exports === 'object' && exports !== null && typeof exports.nodeType !== 'number') {
    factory(exports, require('kaitai-struct/KaitaiStream'));
  } else {
    factory(root.SiglentV01Bin || (root.SiglentV01Bin = {}), root.KaitaiStream);
  }
})(typeof self !== 'undefined' ? self : this, function (SiglentV01Bin_, KaitaiStream) {
/**
 * Siglent waveform binary layout documented as "Binary Format V0.1".
 * 
 * This revision predates the explicit top-level version field used by later
 * layouts. It stores four analog channels with 16-byte value/unit structures
 * and places waveform samples after a large fixed metadata block.
 * 
 * Sources used for this KSY binary format: The binary waveform layout documented by 
 * Siglent as "How to Extract Data from the Binary File of SIGLENT Oscilloscope". 
 * 
 * Tested file formats: the synthetic `Binary Format V0.1` fixture in
 * `tests/test_siglent.py`, exercised through revision detection, low-level
 * Kaitai parsing, and normalized waveform loading.
 * 
 * Oscilloscope models this format may apply to: Siglent instruments that write
 * `Binary Format V0.1`; the checked-in tests do not yet narrow this revision to
 * a smaller verified model list.
 */

var SiglentV01Bin = (function() {
  function SiglentV01Bin(_io, _parent, _root) {
    this._io = _io;
    this._parent = _parent;
    this._root = _root || this;

    this._read();
  }
  SiglentV01Bin.prototype._read = function() {
  }

  var ScaledValue16 = SiglentV01Bin.ScaledValue16 = (function() {
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
  Object.defineProperty(SiglentV01Bin.prototype, 'ch1On', {
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
  Object.defineProperty(SiglentV01Bin.prototype, 'ch1VertOffset', {
    get: function() {
      if (this._m_ch1VertOffset !== undefined)
        return this._m_ch1VertOffset;
      var _pos = this._io.pos;
      this._io.seek(160);
      this._m_ch1VertOffset = new ScaledValue16(this._io, this, this._root);
      this._io.seek(_pos);
      return this._m_ch1VertOffset;
    }
  });
  Object.defineProperty(SiglentV01Bin.prototype, 'ch1VoltDiv', {
    get: function() {
      if (this._m_ch1VoltDiv !== undefined)
        return this._m_ch1VoltDiv;
      var _pos = this._io.pos;
      this._io.seek(144);
      this._m_ch1VoltDiv = new ScaledValue16(this._io, this, this._root);
      this._io.seek(_pos);
      return this._m_ch1VoltDiv;
    }
  });
  Object.defineProperty(SiglentV01Bin.prototype, 'ch2On', {
    get: function() {
      if (this._m_ch2On !== undefined)
        return this._m_ch2On;
      var _pos = this._io.pos;
      this._io.seek(192);
      this._m_ch2On = this._io.readS4le();
      this._io.seek(_pos);
      return this._m_ch2On;
    }
  });
  Object.defineProperty(SiglentV01Bin.prototype, 'ch2VertOffset', {
    get: function() {
      if (this._m_ch2VertOffset !== undefined)
        return this._m_ch2VertOffset;
      var _pos = this._io.pos;
      this._io.seek(284);
      this._m_ch2VertOffset = new ScaledValue16(this._io, this, this._root);
      this._io.seek(_pos);
      return this._m_ch2VertOffset;
    }
  });
  Object.defineProperty(SiglentV01Bin.prototype, 'ch2VoltDiv', {
    get: function() {
      if (this._m_ch2VoltDiv !== undefined)
        return this._m_ch2VoltDiv;
      var _pos = this._io.pos;
      this._io.seek(268);
      this._m_ch2VoltDiv = new ScaledValue16(this._io, this, this._root);
      this._io.seek(_pos);
      return this._m_ch2VoltDiv;
    }
  });
  Object.defineProperty(SiglentV01Bin.prototype, 'ch3On', {
    get: function() {
      if (this._m_ch3On !== undefined)
        return this._m_ch3On;
      var _pos = this._io.pos;
      this._io.seek(316);
      this._m_ch3On = this._io.readS4le();
      this._io.seek(_pos);
      return this._m_ch3On;
    }
  });
  Object.defineProperty(SiglentV01Bin.prototype, 'ch3VertOffset', {
    get: function() {
      if (this._m_ch3VertOffset !== undefined)
        return this._m_ch3VertOffset;
      var _pos = this._io.pos;
      this._io.seek(408);
      this._m_ch3VertOffset = new ScaledValue16(this._io, this, this._root);
      this._io.seek(_pos);
      return this._m_ch3VertOffset;
    }
  });
  Object.defineProperty(SiglentV01Bin.prototype, 'ch3VoltDiv', {
    get: function() {
      if (this._m_ch3VoltDiv !== undefined)
        return this._m_ch3VoltDiv;
      var _pos = this._io.pos;
      this._io.seek(392);
      this._m_ch3VoltDiv = new ScaledValue16(this._io, this, this._root);
      this._io.seek(_pos);
      return this._m_ch3VoltDiv;
    }
  });
  Object.defineProperty(SiglentV01Bin.prototype, 'ch4On', {
    get: function() {
      if (this._m_ch4On !== undefined)
        return this._m_ch4On;
      var _pos = this._io.pos;
      this._io.seek(440);
      this._m_ch4On = this._io.readS4le();
      this._io.seek(_pos);
      return this._m_ch4On;
    }
  });
  Object.defineProperty(SiglentV01Bin.prototype, 'ch4VertOffset', {
    get: function() {
      if (this._m_ch4VertOffset !== undefined)
        return this._m_ch4VertOffset;
      var _pos = this._io.pos;
      this._io.seek(532);
      this._m_ch4VertOffset = new ScaledValue16(this._io, this, this._root);
      this._io.seek(_pos);
      return this._m_ch4VertOffset;
    }
  });
  Object.defineProperty(SiglentV01Bin.prototype, 'ch4VoltDiv', {
    get: function() {
      if (this._m_ch4VoltDiv !== undefined)
        return this._m_ch4VoltDiv;
      var _pos = this._io.pos;
      this._io.seek(516);
      this._m_ch4VoltDiv = new ScaledValue16(this._io, this, this._root);
      this._io.seek(_pos);
      return this._m_ch4VoltDiv;
    }
  });
  Object.defineProperty(SiglentV01Bin.prototype, 'sampleRate', {
    get: function() {
      if (this._m_sampleRate !== undefined)
        return this._m_sampleRate;
      var _pos = this._io.pos;
      this._io.seek(2728);
      this._m_sampleRate = new ScaledValue16(this._io, this, this._root);
      this._io.seek(_pos);
      return this._m_sampleRate;
    }
  });
  Object.defineProperty(SiglentV01Bin.prototype, 'timeDelay', {
    get: function() {
      if (this._m_timeDelay !== undefined)
        return this._m_timeDelay;
      var _pos = this._io.pos;
      this._io.seek(2708);
      this._m_timeDelay = new ScaledValue16(this._io, this, this._root);
      this._io.seek(_pos);
      return this._m_timeDelay;
    }
  });
  Object.defineProperty(SiglentV01Bin.prototype, 'timeDiv', {
    get: function() {
      if (this._m_timeDiv !== undefined)
        return this._m_timeDiv;
      var _pos = this._io.pos;
      this._io.seek(2692);
      this._m_timeDiv = new ScaledValue16(this._io, this, this._root);
      this._io.seek(_pos);
      return this._m_timeDiv;
    }
  });
  Object.defineProperty(SiglentV01Bin.prototype, 'waveData', {
    get: function() {
      if (this._m_waveData !== undefined)
        return this._m_waveData;
      var _pos = this._io.pos;
      this._io.seek(35424);
      this._m_waveData = this._io.readBytes(this._io.size - 35424);
      this._io.seek(_pos);
      return this._m_waveData;
    }
  });
  Object.defineProperty(SiglentV01Bin.prototype, 'waveLength', {
    get: function() {
      if (this._m_waveLength !== undefined)
        return this._m_waveLength;
      var _pos = this._io.pos;
      this._io.seek(2724);
      this._m_waveLength = this._io.readU4le();
      this._io.seek(_pos);
      return this._m_waveLength;
    }
  });

  return SiglentV01Bin;
})();
SiglentV01Bin_.SiglentV01Bin = SiglentV01Bin;
});
