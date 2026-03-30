// This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild

(function (root, factory) {
  if (typeof define === 'function' && define.amd) {
    define(['exports', 'kaitai-struct/KaitaiStream'], factory);
  } else if (typeof exports === 'object' && exports !== null && typeof exports.nodeType !== 'number') {
    factory(exports, require('kaitai-struct/KaitaiStream'));
  } else {
    factory(root.RohdeSchwarzRtpWfm || (root.RohdeSchwarzRtpWfm = {}), root.KaitaiStream);
  }
})(typeof self !== 'undefined' ? self : this, function (RohdeSchwarzRtpWfm_, KaitaiStream) {
/**
 * Rohde & Schwarz oscilloscope waveform payload file used alongside an XML
 * metadata file with the same basename and a `.bin` extension.
 * 
 * The binary file starts with an 8-byte little-endian header followed by the
 * raw waveform payload. The companion XML file describes the signal format,
 * channel layout, acquisition count, scaling, and timing needed to interpret
 * the payload.
 */

var RohdeSchwarzRtpWfm = (function() {
  RohdeSchwarzRtpWfm.FormatCodeEnum = Object.freeze({
    INT8BIT: 0,
    INT16BIT: 1,
    FLOAT32: 4,
    XYDOUBLEFLOAT: 6,

    0: "INT8BIT",
    1: "INT16BIT",
    4: "FLOAT32",
    6: "XYDOUBLEFLOAT",
  });

  function RohdeSchwarzRtpWfm(_io, _parent, _root) {
    this._io = _io;
    this._parent = _parent;
    this._root = _root || this;

    this._read();
  }
  RohdeSchwarzRtpWfm.prototype._read = function() {
    this.formatCode = this._io.readU4le();
    this.recordLength = this._io.readU4le();
    this.payload = this._io.readBytesFull();
  }

  /**
   * Number of raw waveform bytes stored after the 8-byte file header.
   */
  Object.defineProperty(RohdeSchwarzRtpWfm.prototype, 'payloadSize', {
    get: function() {
      if (this._m_payloadSize !== undefined)
        return this._m_payloadSize;
      this._m_payloadSize = this.payload.length;
      return this._m_payloadSize;
    }
  });

  /**
   * R&S waveform format code observed in vendor fixtures.
   * 0 = int8 raw ADC samples
   * 1 = int16 raw ADC samples
   * 4 = float32 voltage samples
   * 6 = XYDOUBLEFLOAT records (float64 time + float32 channel values)
   */

  /**
   * Hardware record length reported in the payload file header. In vendor
   * samples this matches the XML `SignalHardwareRecordLength` value.
   */

  /**
   * Raw waveform bytes; interpretation depends on the XML metadata.
   */

  return RohdeSchwarzRtpWfm;
})();
RohdeSchwarzRtpWfm_.RohdeSchwarzRtpWfm = RohdeSchwarzRtpWfm;
});
