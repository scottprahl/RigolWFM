// This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild

(function (root, factory) {
  if (typeof define === 'function' && define.amd) {
    define(['exports', 'kaitai-struct/KaitaiStream'], factory);
  } else if (typeof exports === 'object' && exports !== null && typeof exports.nodeType !== 'number') {
    factory(exports, require('kaitai-struct/KaitaiStream'));
  } else {
    factory(root.SiglentOldPlatform || (root.SiglentOldPlatform = {}), root.KaitaiStream);
  }
})(typeof self !== 'undefined' ? self : this, function (SiglentOldPlatform_, KaitaiStream) {
/**
 * Binary waveform layout documented by Siglent as "Binary Format in Old
 * Platform". This revision is used by older SDS1000X / SDS2000X families.
 * 
 * The file does not include an explicit format-version field or instrument
 * model identifier, so the surrounding Python adapter is responsible for any
 * remaining family-specific interpretation.
 */

var SiglentOldPlatform = (function() {
  function SiglentOldPlatform(_io, _parent, _root) {
    this._io = _io;
    this._parent = _parent;
    this._root = _root || this;

    this._read();
  }
  SiglentOldPlatform.prototype._read = function() {
  }

  var F4Array4 = SiglentOldPlatform.F4Array4 = (function() {
    function F4Array4(_io, _parent, _root) {
      this._io = _io;
      this._parent = _parent;
      this._root = _root;

      this._read();
    }
    F4Array4.prototype._read = function() {
      this.entries = [];
      for (var i = 0; i < 4; i++) {
        this.entries.push(this._io.readF4le());
      }
    }

    return F4Array4;
  })();

  var S4Array4 = SiglentOldPlatform.S4Array4 = (function() {
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

  var U1Array16 = SiglentOldPlatform.U1Array16 = (function() {
    function U1Array16(_io, _parent, _root) {
      this._io = _io;
      this._parent = _parent;
      this._root = _root;

      this._read();
    }
    U1Array16.prototype._read = function() {
      this.entries = [];
      for (var i = 0; i < 16; i++) {
        this.entries.push(this._io.readU1());
      }
    }

    return U1Array16;
  })();
  Object.defineProperty(SiglentOldPlatform.prototype, 'chOn', {
    get: function() {
      if (this._m_chOn !== undefined)
        return this._m_chOn;
      var _pos = this._io.pos;
      this._io.seek(256);
      this._m_chOn = new S4Array4(this._io, this, this._root);
      this._io.seek(_pos);
      return this._m_chOn;
    }
  });
  Object.defineProperty(SiglentOldPlatform.prototype, 'chVertOffsetPixels', {
    get: function() {
      if (this._m_chVertOffsetPixels !== undefined)
        return this._m_chVertOffsetPixels;
      var _pos = this._io.pos;
      this._io.seek(220);
      this._m_chVertOffsetPixels = new S4Array4(this._io, this, this._root);
      this._io.seek(_pos);
      return this._m_chVertOffsetPixels;
    }
  });
  Object.defineProperty(SiglentOldPlatform.prototype, 'chVoltDivMv', {
    get: function() {
      if (this._m_chVoltDivMv !== undefined)
        return this._m_chVoltDivMv;
      var _pos = this._io.pos;
      this._io.seek(188);
      this._m_chVoltDivMv = new F4Array4(this._io, this, this._root);
      this._io.seek(_pos);
      return this._m_chVoltDivMv;
    }
  });
  Object.defineProperty(SiglentOldPlatform.prototype, 'msoChOpenNum', {
    get: function() {
      if (this._m_msoChOpenNum !== undefined)
        return this._m_msoChOpenNum;
      var _pos = this._io.pos;
      this._io.seek(16);
      this._m_msoChOpenNum = this._io.readU4le();
      this._io.seek(_pos);
      return this._m_msoChOpenNum;
    }
  });
  Object.defineProperty(SiglentOldPlatform.prototype, 'msoChOpenStats', {
    get: function() {
      if (this._m_msoChOpenStats !== undefined)
        return this._m_msoChOpenStats;
      var _pos = this._io.pos;
      this._io.seek(20);
      this._m_msoChOpenStats = new U1Array16(this._io, this, this._root);
      this._io.seek(_pos);
      return this._m_msoChOpenStats;
    }
  });
  Object.defineProperty(SiglentOldPlatform.prototype, 'msoWaveLength', {
    get: function() {
      if (this._m_msoWaveLength !== undefined)
        return this._m_msoWaveLength;
      var _pos = this._io.pos;
      this._io.seek(4);
      this._m_msoWaveLength = this._io.readU4le();
      this._io.seek(_pos);
      return this._m_msoWaveLength;
    }
  });
  Object.defineProperty(SiglentOldPlatform.prototype, 'timeDelayPixels', {
    get: function() {
      if (this._m_timeDelayPixels !== undefined)
        return this._m_timeDelayPixels;
      var _pos = this._io.pos;
      this._io.seek(592);
      this._m_timeDelayPixels = this._io.readS4le();
      this._io.seek(_pos);
      return this._m_timeDelayPixels;
    }
  });
  Object.defineProperty(SiglentOldPlatform.prototype, 'timeDivIndex', {
    get: function() {
      if (this._m_timeDivIndex !== undefined)
        return this._m_timeDivIndex;
      var _pos = this._io.pos;
      this._io.seek(584);
      this._m_timeDivIndex = this._io.readS4le();
      this._io.seek(_pos);
      return this._m_timeDivIndex;
    }
  });
  Object.defineProperty(SiglentOldPlatform.prototype, 'waveData', {
    get: function() {
      if (this._m_waveData !== undefined)
        return this._m_waveData;
      var _pos = this._io.pos;
      this._io.seek(5232);
      this._m_waveData = this._io.readBytes(this._io.size - 5232);
      this._io.seek(_pos);
      return this._m_waveData;
    }
  });

  return SiglentOldPlatform;
})();
SiglentOldPlatform_.SiglentOldPlatform = SiglentOldPlatform;
});
