// This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild

(function (root, factory) {
  if (typeof define === 'function' && define.amd) {
    define(['exports', 'kaitai-struct/KaitaiStream'], factory);
  } else if (typeof exports === 'object' && exports !== null && typeof exports.nodeType !== 'number') {
    factory(exports, require('kaitai-struct/KaitaiStream'));
  } else {
    factory(root.SiglentV1Bin || (root.SiglentV1Bin = {}), root.KaitaiStream);
  }
})(typeof self !== 'undefined' ? self : this, function (SiglentV1Bin_, KaitaiStream) {
/**
 * Siglent waveform binary layout documented as "Binary Format V1.0".
 * 
 * V1.0 introduces a compact 2 KiB waveform header at the start of the file and
 * stores enabled analog channels first in the sample payload at offset 0x800.
 * 
 * Sources used for this KSY binary format: The binary waveform layout documented by
 * Siglent as "How to Extract Data from the Binary File of SIGLENT Oscilloscope".
 * 
 * Tested file formats: the synthetic `Binary Format V1.0` fixture in
 * `tests/test_siglent.py`, exercised through revision detection, low-level
 * Kaitai parsing, and normalized waveform loading.
 * 
 * Oscilloscope models this format may apply to: Siglent instruments that write
 * `Binary Format V1.0`; the checked-in tests do not yet narrow this revision to
 * a smaller verified model list.
 */

var SiglentV1Bin = (function() {
  function SiglentV1Bin(_io, _parent, _root) {
    this._io = _io;
    this._parent = _parent;
    this._root = _root || this;

    this._read();
  }
  SiglentV1Bin.prototype._read = function() {
  }

  var S4Array4 = SiglentV1Bin.S4Array4 = (function() {
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

  var ScaledValue16 = SiglentV1Bin.ScaledValue16 = (function() {
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

  var ScaledValue16Array4 = SiglentV1Bin.ScaledValue16Array4 = (function() {
    function ScaledValue16Array4(_io, _parent, _root) {
      this._io = _io;
      this._parent = _parent;
      this._root = _root;

      this._read();
    }
    ScaledValue16Array4.prototype._read = function() {
      this.entries = [];
      for (var i = 0; i < 4; i++) {
        this.entries.push(new ScaledValue16(this._io, this, this._root));
      }
    }

    return ScaledValue16Array4;
  })();

  var U4Array16 = SiglentV1Bin.U4Array16 = (function() {
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
  Object.defineProperty(SiglentV1Bin.prototype, 'chOn', {
    get: function() {
      if (this._m_chOn !== undefined)
        return this._m_chOn;
      var _pos = this._io.pos;
      this._io.seek(0);
      this._m_chOn = new S4Array4(this._io, this, this._root);
      this._io.seek(_pos);
      return this._m_chOn;
    }
  });
  Object.defineProperty(SiglentV1Bin.prototype, 'chVertOffset', {
    get: function() {
      if (this._m_chVertOffset !== undefined)
        return this._m_chVertOffset;
      var _pos = this._io.pos;
      this._io.seek(80);
      this._m_chVertOffset = new ScaledValue16Array4(this._io, this, this._root);
      this._io.seek(_pos);
      return this._m_chVertOffset;
    }
  });
  Object.defineProperty(SiglentV1Bin.prototype, 'chVoltDiv', {
    get: function() {
      if (this._m_chVoltDiv !== undefined)
        return this._m_chVoltDiv;
      var _pos = this._io.pos;
      this._io.seek(16);
      this._m_chVoltDiv = new ScaledValue16Array4(this._io, this, this._root);
      this._io.seek(_pos);
      return this._m_chVoltDiv;
    }
  });
  Object.defineProperty(SiglentV1Bin.prototype, 'digitalChOn', {
    get: function() {
      if (this._m_digitalChOn !== undefined)
        return this._m_digitalChOn;
      var _pos = this._io.pos;
      this._io.seek(148);
      this._m_digitalChOn = new U4Array16(this._io, this, this._root);
      this._io.seek(_pos);
      return this._m_digitalChOn;
    }
  });
  Object.defineProperty(SiglentV1Bin.prototype, 'digitalOn', {
    get: function() {
      if (this._m_digitalOn !== undefined)
        return this._m_digitalOn;
      var _pos = this._io.pos;
      this._io.seek(144);
      this._m_digitalOn = this._io.readU4le();
      this._io.seek(_pos);
      return this._m_digitalOn;
    }
  });
  Object.defineProperty(SiglentV1Bin.prototype, 'digitalSampleRate', {
    get: function() {
      if (this._m_digitalSampleRate !== undefined)
        return this._m_digitalSampleRate;
      var _pos = this._io.pos;
      this._io.seek(268);
      this._m_digitalSampleRate = new ScaledValue16(this._io, this, this._root);
      this._io.seek(_pos);
      return this._m_digitalSampleRate;
    }
  });
  Object.defineProperty(SiglentV1Bin.prototype, 'digitalWaveLength', {
    get: function() {
      if (this._m_digitalWaveLength !== undefined)
        return this._m_digitalWaveLength;
      var _pos = this._io.pos;
      this._io.seek(264);
      this._m_digitalWaveLength = this._io.readU4le();
      this._io.seek(_pos);
      return this._m_digitalWaveLength;
    }
  });
  Object.defineProperty(SiglentV1Bin.prototype, 'sampleRate', {
    get: function() {
      if (this._m_sampleRate !== undefined)
        return this._m_sampleRate;
      var _pos = this._io.pos;
      this._io.seek(248);
      this._m_sampleRate = new ScaledValue16(this._io, this, this._root);
      this._io.seek(_pos);
      return this._m_sampleRate;
    }
  });
  Object.defineProperty(SiglentV1Bin.prototype, 'timeDelay', {
    get: function() {
      if (this._m_timeDelay !== undefined)
        return this._m_timeDelay;
      var _pos = this._io.pos;
      this._io.seek(228);
      this._m_timeDelay = new ScaledValue16(this._io, this, this._root);
      this._io.seek(_pos);
      return this._m_timeDelay;
    }
  });
  Object.defineProperty(SiglentV1Bin.prototype, 'timeDiv', {
    get: function() {
      if (this._m_timeDiv !== undefined)
        return this._m_timeDiv;
      var _pos = this._io.pos;
      this._io.seek(212);
      this._m_timeDiv = new ScaledValue16(this._io, this, this._root);
      this._io.seek(_pos);
      return this._m_timeDiv;
    }
  });
  Object.defineProperty(SiglentV1Bin.prototype, 'waveData', {
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
  Object.defineProperty(SiglentV1Bin.prototype, 'waveLength', {
    get: function() {
      if (this._m_waveLength !== undefined)
        return this._m_waveLength;
      var _pos = this._io.pos;
      this._io.seek(244);
      this._m_waveLength = this._io.readU4le();
      this._io.seek(_pos);
      return this._m_waveLength;
    }
  });

  return SiglentV1Bin;
})();
SiglentV1Bin_.SiglentV1Bin = SiglentV1Bin;
});
