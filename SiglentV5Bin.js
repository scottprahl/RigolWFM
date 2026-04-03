// This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild

(function (root, factory) {
  if (typeof define === 'function' && define.amd) {
    define(['exports', 'kaitai-struct/KaitaiStream'], factory);
  } else if (typeof exports === 'object' && exports !== null && typeof exports.nodeType !== 'number') {
    factory(exports, require('kaitai-struct/KaitaiStream'));
  } else {
    factory(root.SiglentV5Bin || (root.SiglentV5Bin = {}), root.KaitaiStream);
  }
})(typeof self !== 'undefined' ? self : this, function (SiglentV5Bin_, KaitaiStream) {
/**
 * Siglent waveform binary layout documented as "Binary Format V5.0".
 * 
 * This revision is documented for later SDS1002X-E firmware and keeps the
 * analog waveform data at offset 0x800 while moving the channel and timing
 * metadata into a different fixed layout.
 * 
 * Sources used for this KSY binary format:
 * `docs/vendors/siglent/siglent-binaries.pdf` plus the synthetic regression
 * builder in `tests/test_siglent.py`.
 * 
 * Tested file formats: the synthetic `Binary Format V5.0` fixture in
 * `tests/test_siglent.py`, exercised through revision detection, low-level
 * Kaitai parsing, and normalized waveform loading.
 * 
 * Oscilloscope models this format may apply to: later `SDS1002X-E` firmware and
 * other Siglent instruments that write `Binary Format V5.0`.
 */

var SiglentV5Bin = (function() {
  function SiglentV5Bin(_io, _parent, _root) {
    this._io = _io;
    this._parent = _parent;
    this._root = _root || this;

    this._read();
  }
  SiglentV5Bin.prototype._read = function() {
  }

  var ScaledValue16 = SiglentV5Bin.ScaledValue16 = (function() {
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
  Object.defineProperty(SiglentV5Bin.prototype, 'ch1On', {
    get: function() {
      if (this._m_ch1On !== undefined)
        return this._m_ch1On;
      var _pos = this._io.pos;
      this._io.seek(118);
      this._m_ch1On = this._io.readS4le();
      this._io.seek(_pos);
      return this._m_ch1On;
    }
  });
  Object.defineProperty(SiglentV5Bin.prototype, 'ch1VertOffset', {
    get: function() {
      if (this._m_ch1VertOffset !== undefined)
        return this._m_ch1VertOffset;
      var _pos = this._io.pos;
      this._io.seek(188);
      this._m_ch1VertOffset = new ScaledValue16(this._io, this, this._root);
      this._io.seek(_pos);
      return this._m_ch1VertOffset;
    }
  });
  Object.defineProperty(SiglentV5Bin.prototype, 'ch1VoltDiv', {
    get: function() {
      if (this._m_ch1VoltDiv !== undefined)
        return this._m_ch1VoltDiv;
      var _pos = this._io.pos;
      this._io.seek(171);
      this._m_ch1VoltDiv = new ScaledValue16(this._io, this, this._root);
      this._io.seek(_pos);
      return this._m_ch1VoltDiv;
    }
  });
  Object.defineProperty(SiglentV5Bin.prototype, 'ch2On', {
    get: function() {
      if (this._m_ch2On !== undefined)
        return this._m_ch2On;
      var _pos = this._io.pos;
      this._io.seek(240);
      this._m_ch2On = this._io.readS4le();
      this._io.seek(_pos);
      return this._m_ch2On;
    }
  });
  Object.defineProperty(SiglentV5Bin.prototype, 'ch2VertOffset', {
    get: function() {
      if (this._m_ch2VertOffset !== undefined)
        return this._m_ch2VertOffset;
      var _pos = this._io.pos;
      this._io.seek(368);
      this._m_ch2VertOffset = new ScaledValue16(this._io, this, this._root);
      this._io.seek(_pos);
      return this._m_ch2VertOffset;
    }
  });
  Object.defineProperty(SiglentV5Bin.prototype, 'ch2VoltDiv', {
    get: function() {
      if (this._m_ch2VoltDiv !== undefined)
        return this._m_ch2VoltDiv;
      var _pos = this._io.pos;
      this._io.seek(352);
      this._m_ch2VoltDiv = new ScaledValue16(this._io, this, this._root);
      this._io.seek(_pos);
      return this._m_ch2VoltDiv;
    }
  });
  Object.defineProperty(SiglentV5Bin.prototype, 'ch3On', {
    get: function() {
      if (this._m_ch3On !== undefined)
        return this._m_ch3On;
      var _pos = this._io.pos;
      this._io.seek(404);
      this._m_ch3On = this._io.readS4le();
      this._io.seek(_pos);
      return this._m_ch3On;
    }
  });
  Object.defineProperty(SiglentV5Bin.prototype, 'ch3VertOffset', {
    get: function() {
      if (this._m_ch3VertOffset !== undefined)
        return this._m_ch3VertOffset;
      var _pos = this._io.pos;
      this._io.seek(532);
      this._m_ch3VertOffset = new ScaledValue16(this._io, this, this._root);
      this._io.seek(_pos);
      return this._m_ch3VertOffset;
    }
  });
  Object.defineProperty(SiglentV5Bin.prototype, 'ch3VoltDiv', {
    get: function() {
      if (this._m_ch3VoltDiv !== undefined)
        return this._m_ch3VoltDiv;
      var _pos = this._io.pos;
      this._io.seek(516);
      this._m_ch3VoltDiv = new ScaledValue16(this._io, this, this._root);
      this._io.seek(_pos);
      return this._m_ch3VoltDiv;
    }
  });
  Object.defineProperty(SiglentV5Bin.prototype, 'ch4On', {
    get: function() {
      if (this._m_ch4On !== undefined)
        return this._m_ch4On;
      var _pos = this._io.pos;
      this._io.seek(568);
      this._m_ch4On = this._io.readS4le();
      this._io.seek(_pos);
      return this._m_ch4On;
    }
  });
  Object.defineProperty(SiglentV5Bin.prototype, 'ch4VertOffset', {
    get: function() {
      if (this._m_ch4VertOffset !== undefined)
        return this._m_ch4VertOffset;
      var _pos = this._io.pos;
      this._io.seek(696);
      this._m_ch4VertOffset = new ScaledValue16(this._io, this, this._root);
      this._io.seek(_pos);
      return this._m_ch4VertOffset;
    }
  });
  Object.defineProperty(SiglentV5Bin.prototype, 'ch4VoltDiv', {
    get: function() {
      if (this._m_ch4VoltDiv !== undefined)
        return this._m_ch4VoltDiv;
      var _pos = this._io.pos;
      this._io.seek(680);
      this._m_ch4VoltDiv = new ScaledValue16(this._io, this, this._root);
      this._io.seek(_pos);
      return this._m_ch4VoltDiv;
    }
  });
  Object.defineProperty(SiglentV5Bin.prototype, 'sampleRate', {
    get: function() {
      if (this._m_sampleRate !== undefined)
        return this._m_sampleRate;
      var _pos = this._io.pos;
      this._io.seek(7058);
      this._m_sampleRate = new ScaledValue16(this._io, this, this._root);
      this._io.seek(_pos);
      return this._m_sampleRate;
    }
  });
  Object.defineProperty(SiglentV5Bin.prototype, 'timeDelay', {
    get: function() {
      if (this._m_timeDelay !== undefined)
        return this._m_timeDelay;
      var _pos = this._io.pos;
      this._io.seek(7032);
      this._m_timeDelay = new ScaledValue16(this._io, this, this._root);
      this._io.seek(_pos);
      return this._m_timeDelay;
    }
  });
  Object.defineProperty(SiglentV5Bin.prototype, 'timeDiv', {
    get: function() {
      if (this._m_timeDiv !== undefined)
        return this._m_timeDiv;
      var _pos = this._io.pos;
      this._io.seek(7016);
      this._m_timeDiv = new ScaledValue16(this._io, this, this._root);
      this._io.seek(_pos);
      return this._m_timeDiv;
    }
  });
  Object.defineProperty(SiglentV5Bin.prototype, 'version', {
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
  Object.defineProperty(SiglentV5Bin.prototype, 'waveData', {
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
  Object.defineProperty(SiglentV5Bin.prototype, 'waveLength', {
    get: function() {
      if (this._m_waveLength !== undefined)
        return this._m_waveLength;
      var _pos = this._io.pos;
      this._io.seek(7048);
      this._m_waveLength = this._io.readU4le();
      this._io.seek(_pos);
      return this._m_waveLength;
    }
  });

  return SiglentV5Bin;
})();
SiglentV5Bin_.SiglentV5Bin = SiglentV5Bin;
});
