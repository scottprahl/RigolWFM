// This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild

(function (root, factory) {
  if (typeof define === 'function' && define.amd) {
    define(['exports', 'kaitai-struct/KaitaiStream'], factory);
  } else if (typeof exports === 'object' && exports !== null && typeof exports.nodeType !== 'number') {
    factory(exports, require('kaitai-struct/KaitaiStream'));
  } else {
    factory(root.YokogawaWvf || (root.YokogawaWvf = {}), root.KaitaiStream);
  }
})(typeof self !== 'undefined' ? self : this, function (YokogawaWvf_, KaitaiStream) {
/**
 * Binary waveform data (.wvf) produced by Yokogawa DL-series oscilloscopes
 * (DL750, DL1600, DL716, DL7440, etc.).
 * 
 * Two-file format
 * ---------------
 * Every capture produces a PAIR of files that share the same base name:
 * 
 *   <name>.hdr   — ASCII text, key/value metadata (parsed separately)
 *   <name>.wvf   — this file: flat binary sample data
 * 
 * ALL structural metadata (data type, sample count, voltage scaling, time
 * axis, data layout) lives in the .hdr file.  The .wvf file is a plain byte
 * array with no self-describing framing.  The companion .hdr MUST be parsed
 * first; its fields supply the params used to interpret the binary data here.
 * 
 * Companion .hdr file format
 * --------------------------
 * The .hdr file is an ASCII key/value text file.  Relevant fields:
 * 
 * Global section ($PublicInfo):
 *   FormatVersion   Version string (e.g. "1.11")
 *   Model           Oscilloscope model (e.g. "DL750", "DL1600")
 *   Endian          "Big" = big-endian (Motorola 68k)
 *                   "Ltl" = little-endian (Intel x86)
 *   DataFormat      "TRACE" or "BLOCK" — layout of the binary data (see below)
 *   GroupNumber     Number of data groups in the file
 *   TraceTotalNumber  Total number of traces across all groups
 *   DataOffset      Leading unused bytes at the start of the .wvf file;
 *                   the first sample byte is at this file offset.
 * 
 * Per-group section ($Group<N>, one section per group):
 *   TraceNumber     Number of traces in this group
 *   BlockNumber     Number of time blocks captured in this group
 * 
 * Per-trace entries (all on one line, space-separated, one value per trace):
 *   TraceName       Channel labels, e.g. "CH1 CH2 CH3 CH4"
 *   BlockSize       Number of samples per block per trace
 *   VResolution     Vertical scale factor (physical units per ADC count)
 *   VOffset         Vertical DC offset in physical units
 *   VDataType       ADC format code for each trace (see below)
 *   VUnit           Physical unit string, e.g. "V" or "A"
 *   VPlusOverData   Raw value for upper-overrange marker (optional)
 *   VMinusOverData  Raw value for lower-overrange marker (optional)
 *   VIllegalData    Raw value for illegal/invalid sample (optional)
 *   VMaxData        Maximum valid raw ADC value
 *   VMinData        Minimum valid raw ADC value
 *   HResolution     Time between samples (seconds/sample)
 *   HOffset         Time of the first sample relative to trigger (seconds)
 *   HUnit           Time unit string (typically "s")
 *   Date / Date<N>  Recording date per block (YYYY/MM/DD)
 *   Time / Time<N>  Recording time per block (HH:MM:SS)
 * 
 * VDataType codes
 * ---------------
 * Each trace carries one code describing its binary sample format:
 * 
 *   IS<n>   Signed integer,   n bytes per sample  (e.g. IS2 = int16)
 *   IU<n>   Unsigned integer, n bytes per sample  (e.g. IU1 = uint8)
 *   FS<n>   Signed IEEE 754 float, n bytes per sample  (FS4 = float32, FS8 = float64)
 *   FU<n>   Unsigned float (treated identically to FS<n> by parsers)
 *   B<m>    Raw binary (logic signals), m bytes per sample  (B16 = 16-byte words,
 *           DL750 only; individual bits represent digital channels)
 * 
 * Supported sample widths (n/m):  1, 2, 4, 8
 * 
 * Data layout in .wvf
 * -------------------
 * After the DataOffset-byte preamble the samples are laid out in one of two
 * orders depending on the .hdr DataFormat field.
 * 
 * Let:
 *   G     = total number of groups
 *   T[g]  = number of traces in group g  (g = 1..G)
 *   B[g]  = number of blocks in group g
 *   S[g,t] = BlockSize (samples/block) for trace t in group g
 *   W[g,t] = VDataType byte-width for trace t in group g
 * 
 * TRACE format  (DataFormat = "TRACE"):
 *   All blocks of a given trace are contiguous; traces are sorted by group:
 * 
 *   for g = 1..G:
 *     for t = 1..T[g]:
 *       for b = 1..B[g]:
 *         S[g,t] × W[g,t]  raw bytes
 * 
 *   Byte offset of (group g, trace t, block b):
 *     DataOffset
 *     + sum_{g'<g} sum_{t'=1}^{T[g']}  S[g',t'] × B[g'] × W[g',t']
 *     + sum_{t'<t}  S[g,t'] × B[g] × W[g,t']
 *     + (b-1) × S[g,t] × W[g,t]
 * 
 * BLOCK format  (DataFormat = "BLOCK"):
 *   All traces within a block are contiguous; blocks are sorted by group:
 * 
 *   for g = 1..G:
 *     for b = 1..B[g]:
 *       for t = 1..T[g]:
 *         S[g,t] × W[g,t]  raw bytes
 * 
 *   Byte offset of (group g, trace t, block b):
 *     DataOffset
 *     + sum_{g'<g} sum_{b'=1}^{B[g']} sum_{t'=1}^{T[g']}  S[g',t'] × W[g',t']
 *     + sum_{b'<b} sum_{t'=1}^{T[g]}  S[g,t'] × W[g,t']
 *     + sum_{t'<t}  S[g,t'] × W[g,t']
 * 
 * Voltage calibration
 * --------------------
 *   volts[i] = VOffset + VResolution * raw[i]
 * 
 * Time axis
 * ---------
 *   t[i] = HOffset + HResolution * (i - 1)     (i = 1 .. BlockSize)
 * 
 *   Note: the MATLAB reference implementation uses 1-based sample indexing, so
 *   the first sample at i=1 gives t = HOffset.  Python adapters that use
 *   0-based indexing should use:
 *   t[i] = HOffset + HResolution * i            (i = 0 .. BlockSize-1)
 * 
 * Endianness
 * ----------
 * The Endian field in the .hdr controls byte order for all multi-byte samples:
 *   "Big"  — big-endian (Motorola 68000 byte order)
 *   "Ltl"  — little-endian (Intel x86 byte order)
 * 
 * Logic (B-type) traces
 * ----------------------
 * DL750 logic channels use 16-byte (128-bit) words per sample.  Each bit
 * represents one digital channel.  The MATLAB reference extracts individual
 * bits with bitget(raw_value, bit_position).  These traces are not converted
 * to physical units; the raw integer is returned directly.
 * 
 * References
 * ----------
 * Erik Benkler, "wvfread v1.7", Physikalisch-Technische Bundesanstalt, 2011.
 * Yokogawa Technical Information TI 7000-21 E, 1998 (3rd edition).
 * Yokogawa DL 1640 User Manual, Appendix 3.
 */

var YokogawaWvf = (function() {
  function YokogawaWvf(_io, _parent, _root, dataOffset) {
    this._io = _io;
    this._parent = _parent;
    this._root = _root || this;
    this.dataOffset = dataOffset;

    this._read();
  }
  YokogawaWvf.prototype._read = function() {
    this.leadingUnused = this._io.readBytes(this.dataOffset);
    this.samplesRaw = this._io.readBytesFull();
  }

  /**
   * Unused padding at the beginning of the file.  Size is given by the
   * DataOffset entry in the companion .hdr file.
   */

  /**
   * Raw packed sample bytes for all groups, traces, and blocks, laid out
   * according to the DataFormat, TraceNumber, BlockNumber, BlockSize, and
   * VDataType fields from the companion .hdr file.
   * 
   * The caller must parse the .hdr file to determine:
   *   - Byte order (Endian)
   *   - Data layout (DataFormat: "TRACE" or "BLOCK")
   *   - Per-trace byte widths (W[g,t] from VDataType)
   *   - Per-trace sample counts (S[g,t] from BlockSize)
   * 
   * See the top-level doc section for the exact offset formulas and
   * calibration equations.
   */

  /**
   * Leading unused bytes before the first sample.  Read from the DataOffset
   * field in the companion .hdr file.  Pass 0 if DataOffset is absent or zero.
   */

  return YokogawaWvf;
})();
YokogawaWvf_.YokogawaWvf = YokogawaWvf;
});
