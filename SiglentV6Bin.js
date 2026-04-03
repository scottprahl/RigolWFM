// This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild

(function (root, factory) {
  if (typeof define === 'function' && define.amd) {
    define(['exports', 'kaitai-struct/KaitaiStream'], factory);
  } else if (typeof exports === 'object' && exports !== null && typeof exports.nodeType !== 'number') {
    factory(exports, require('kaitai-struct/KaitaiStream'));
  } else {
    factory(root.SiglentV6Bin || (root.SiglentV6Bin = {}), root.KaitaiStream);
  }
})(typeof self !== 'undefined' ? self : this, function (SiglentV6Bin_, KaitaiStream) {
/**
 * Siglent waveform binary layout documented as "Binary Format V6.0".
 * 
 * V6.0 stores a top-level file header followed by one or more waveform records.
 * Each waveform contains a fixed shared header, optional extension bytes, an
 * optional additional-information block, and then the sample payload.
 * 
 * Sources used for this KSY binary format:
 * `docs/vendors/siglent/siglent-binaries.pdf` plus the synthetic regression
 * builder in `tests/test_siglent.py`.
 * 
 * Tested file formats: the synthetic `Binary Format V6.0` fixture in
 * `tests/test_siglent.py`, exercised through revision detection, low-level
 * Kaitai parsing, and normalized waveform loading with an `SDS1002X-E` module
 * string.
 * 
 * Oscilloscope models this format may apply to: `SDS1002X-E` is the checked-in
 * reference model, and other Siglent instruments that write `Binary Format
 * V6.0` may share this layout.
 */

var SiglentV6Bin = (function() {
  function SiglentV6Bin(_io, _parent, _root) {
    this._io = _io;
    this._parent = _parent;
    this._root = _root || this;

    this._read();
  }
  SiglentV6Bin.prototype._read = function() {
    this.fileHeader = new FileHeader(this._io, this, this._root);
    this.waveforms = [];
    for (var i = 0; i < this.fileHeader.waveNumber; i++) {
      this.waveforms.push(new Waveform(this._io, this, this._root));
    }
  }

  var FileHeader = SiglentV6Bin.FileHeader = (function() {
    function FileHeader(_io, _parent, _root) {
      this._io = _io;
      this._parent = _parent;
      this._root = _root;

      this._read();
    }
    FileHeader.prototype._read = function() {
      this.version = this._io.readU4le();
      this.headerBytes = this._io.readU2le();
      this.endianMarker = this._io.readU2le();
      this.module = KaitaiStream.bytesToStr(KaitaiStream.bytesTerminate(this._io.readBytes(32), 0, false), "ASCII");
      this.serial = KaitaiStream.bytesToStr(KaitaiStream.bytesTerminate(this._io.readBytes(32), 0, false), "ASCII");
      this.softwareVersion = KaitaiStream.bytesToStr(KaitaiStream.bytesTerminate(this._io.readBytes(32), 0, false), "ASCII");
      this.waveNumber = this._io.readU4le();
      if (this.headerBytes > 108) {
        this.headerExtra = this._io.readBytes(this.headerBytes - 108);
      }
    }

    return FileHeader;
  })();

  var Waveform = SiglentV6Bin.Waveform = (function() {
    function Waveform(_io, _parent, _root) {
      this._io = _io;
      this._parent = _parent;
      this._root = _root;

      this._read();
    }
    Waveform.prototype._read = function() {
      this.header = new WaveformHeader(this._io, this, this._root);
      this.addInfo = this._io.readBytes(this.header.addInfoBytes);
      this.dataRaw = this._io.readBytes(this.header.dataBytes);
    }

    return Waveform;
  })();

  var WaveformHeader = SiglentV6Bin.WaveformHeader = (function() {
    function WaveformHeader(_io, _parent, _root) {
      this._io = _io;
      this._parent = _parent;
      this._root = _root;

      this._read();
    }
    WaveformHeader.prototype._read = function() {
      this.baseHeaderType = this._io.readU4le();
      this.baseHeaderBytes = this._io.readU4le();
      this.waveType = this._io.readU4le();
      this.channelType = this._io.readU2le();
      this.channelIndex = this._io.readU2le();
      this.label = KaitaiStream.bytesToStr(KaitaiStream.bytesTerminate(this._io.readBytes(16), 0, false), "ASCII");
      this.date = KaitaiStream.bytesToStr(KaitaiStream.bytesTerminate(this._io.readBytes(16), 0, false), "ASCII");
      this.timeStr = KaitaiStream.bytesToStr(KaitaiStream.bytesTerminate(this._io.readBytes(32), 0, false), "ASCII");
      this.horiScale = this._io.readF8le();
      this.horiPos = this._io.readF8le();
      this.horiOriginPos = this._io.readF8le();
      this.horiInterval = this._io.readF8le();
      this.horiUnit = [];
      for (var i = 0; i < 8; i++) {
        this.horiUnit.push(this._io.readU4le());
      }
      this.horiUnitStr = KaitaiStream.bytesToStr(KaitaiStream.bytesTerminate(this._io.readBytes(16), 0, false), "ASCII");
      this.vertScale = this._io.readF8le();
      this.vertPos = this._io.readF8le();
      this.vertOriginPos = this._io.readF8le();
      this.vertInterval = this._io.readF8le();
      this.vertUnit = [];
      for (var i = 0; i < 8; i++) {
        this.vertUnit.push(this._io.readU4le());
      }
      this.vertUnitStr = KaitaiStream.bytesToStr(KaitaiStream.bytesTerminate(this._io.readBytes(16), 0, false), "ASCII");
      this.addInfoBytes = this._io.readU4le();
      this.dataType = this._io.readU4le();
      this.dataNumber = this._io.readU8le();
      this.dataBytes = this._io.readU8le();
      if (this.baseHeaderBytes > 264) {
        this.baseHeaderExtra = this._io.readBytes(this.baseHeaderBytes - 264);
      }
    }

    return WaveformHeader;
  })();

  return SiglentV6Bin;
})();
SiglentV6Bin_.SiglentV6Bin = SiglentV6Bin;
});
