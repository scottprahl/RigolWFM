// This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild

(function (root, factory) {
  if (typeof define === 'function' && define.amd) {
    define(['exports', 'kaitai-struct/KaitaiStream'], factory);
  } else if (typeof exports === 'object' && exports !== null && typeof exports.nodeType !== 'number') {
    factory(exports, require('kaitai-struct/KaitaiStream'));
  } else {
    factory(root.Lecroy10LeTrc || (root.Lecroy10LeTrc = {}), root.KaitaiStream);
  }
})(typeof self !== 'undefined' ? self : this, function (Lecroy10LeTrc_, KaitaiStream) {
/**
 * Teledyne LeCroy LECROY_1_0 binary waveform format (.trc / .000 files) — little-endian variant.
 * 
 * This older format has a 320-byte WAVEDESC (vs 346 bytes in LECROY_2_3) with a different
 * field layout.  Key differences from LECROY_2_3:
 * 
 *   - wave_array_1_len is at offset 48 (not 60)
 *   - instrument_name is at offset 56 (not 76)
 *   - wave_array_count is at offset 92 (not 116)
 *   - vertical calibration: volts[i] = vertical_gain * adc[i] - acq_vert_offset
 *   - wave_source at offset 296 is 1-indexed (1=CH1, 2=CH2, …)
 *   - No ris_time_array field
 * 
 * Endianness detection (performed by the caller before selecting this parser)::
 * 
 *   COMM_ORDER is a u2 at offset 34.  byte 34 == 1 → LOFIRST (little-endian).
 * 
 * Voltage reconstruction::
 * 
 *   volts[i] = vertical_gain * adc[i] - acq_vert_offset
 * 
 * where adc[i] is signed 8-bit (COMM_TYPE == byte) or signed 16-bit (COMM_TYPE == word).
 * 
 * Time axis::
 * 
 *   t[i] = horiz_offset + i * horiz_interval   (i = 0 … wave_array_count − 1)
 * 
 * Primary source used for this KSY binary format
 * <https://github.com/jonathanschilling/LeCroy7200A/blob/master/template.txt>.  The
 * Github repos <https://github.com/jonathanschilling/LeCroy7200A> and
 * <https://github.com/dgua/lecroy> were used for verification.
 * 
 * Tested file formats: synthetic little-endian `LECROY_1_0` files with both
 * 8-bit and 16-bit sample payloads, plus the checked-in real
 * `trace1.000` through `trace4.000` fixtures used for parse, scaling, time-axis,
 * and autodetect coverage.
 * 
 * Oscilloscope models this format may apply to: Teledyne LeCroy oscilloscopes
 * that write the `LECROY_1_0` template, including older 7200-series /
 * WaveRunner-era instruments and related scopes that store `.trc` or `.000`
 * waveform files in little-endian form.
 */

var Lecroy10LeTrc = (function() {
  Lecroy10LeTrc.BandwidthLimitEnum = Object.freeze({
    BW_FULL: 0,
    BW_LIMITED: 1,

    0: "BW_FULL",
    1: "BW_LIMITED",
  });

  Lecroy10LeTrc.CommOrderEnum = Object.freeze({
    BIG_ENDIAN: 0,
    LITTLE_ENDIAN: 1,

    0: "BIG_ENDIAN",
    1: "LITTLE_ENDIAN",
  });

  Lecroy10LeTrc.CommTypeEnum = Object.freeze({
    BYTE: 0,
    WORD: 1,

    0: "BYTE",
    1: "WORD",
  });

  Lecroy10LeTrc.VertCouplingEnum = Object.freeze({
    DC_50_OHM: 0,
    GROUND: 1,
    DC_1M_OHM: 2,
    GROUND_B: 3,
    AC_1M_OHM: 4,

    0: "DC_50_OHM",
    1: "GROUND",
    2: "DC_1M_OHM",
    3: "GROUND_B",
    4: "AC_1M_OHM",
  });

  function Lecroy10LeTrc(_io, _parent, _root) {
    this._io = _io;
    this._parent = _parent;
    this._root = _root || this;

    this._read();
  }
  Lecroy10LeTrc.prototype._read = function() {
    this.wavedesc = new Wavedesc(this._io, this, this._root);
  }

  /**
   * 16-byte absolute trigger timestamp.
   */

  var TriggerTimestamp = Lecroy10LeTrc.TriggerTimestamp = (function() {
    function TriggerTimestamp(_io, _parent, _root) {
      this._io = _io;
      this._parent = _parent;
      this._root = _root;

      this._read();
    }
    TriggerTimestamp.prototype._read = function() {
      this.seconds = this._io.readF8le();
      this.minutes = this._io.readU1();
      this.hours = this._io.readU1();
      this.days = this._io.readU1();
      this.months = this._io.readU1();
      this.year = this._io.readS2le();
      this.unused = this._io.readS2le();
    }

    /**
     * Fractional seconds within the current minute.
     */

    return TriggerTimestamp;
  })();

  /**
   * One 16-byte record in the TRIGTIME array.
   */

  var TrigtimeEntry = Lecroy10LeTrc.TrigtimeEntry = (function() {
    function TrigtimeEntry(_io, _parent, _root) {
      this._io = _io;
      this._parent = _parent;
      this._root = _root;

      this._read();
    }
    TrigtimeEntry.prototype._read = function() {
      this.triggerTime = this._io.readF8le();
      this.triggerOffset = this._io.readF8le();
    }

    return TrigtimeEntry;
  })();

  /**
   * 320-byte WAVEDESC header block (LECROY_1_0 template).  All byte offsets are
   * relative to the start of this struct.  Endianness is inherited from root (little-endian).
   */

  var Wavedesc = Lecroy10LeTrc.Wavedesc = (function() {
    function Wavedesc(_io, _parent, _root) {
      this._io = _io;
      this._parent = _parent;
      this._root = _root;

      this._read();
    }
    Wavedesc.prototype._read = function() {
      this.descriptorName = this._io.readBytes(16);
      this.templateName = this._io.readBytes(16);
      this.commType = this._io.readU2le();
      this.commOrder = this._io.readU2le();
      this.waveDescriptor = this._io.readS4le();
      this.userTextLen = this._io.readS4le();
      this.trigtimeArrayLen = this._io.readS4le();
      this.waveArray1Len = this._io.readS4le();
      this.waveArray2Len = this._io.readS4le();
      this.instrumentName = this._io.readBytes(16);
      this.instrumentNumber = this._io.readS4le();
      this.traceLabel = this._io.readBytes(16);
      this.waveArrayCount = this._io.readS4le();
      this.pointsPerScreen = this._io.readS4le();
      this.firstValidPnt = this._io.readS4le();
      this.lastValidPnt = this._io.readS4le();
      this.subarrayCount = this._io.readS4le();
      this.nomSubarrayCount = this._io.readS4le();
      this.sweepsPerAcq = this._io.readS4le();
      this.verticalGain = this._io.readF4le();
      this.verticalOffset = this._io.readF4le();
      this.maxValue = this._io.readS2le();
      this.minValue = this._io.readS2le();
      this.nominalBits = this._io.readS2le();
      this.horizInterval = this._io.readF4le();
      this.horizOffset = this._io.readF8le();
      this.pixelOffset = this._io.readF8le();
      this.vertUnit = this._io.readBytes(48);
      this.horUnit = this._io.readBytes(48);
      this.triggerTime = new TriggerTimestamp(this._io, this, this._root);
      this.acqDuration = this._io.readF4le();
      this.recordType = this._io.readS2le();
      this.processingDone = this._io.readS2le();
      this.timebase = this._io.readU2le();
      this.vertCoupling = this._io.readU2le();
      this.probeAtt = this._io.readF4le();
      this.fixedVertGain = this._io.readU2le();
      this.bandwidthLimit = this._io.readU2le();
      this.vertVernier = this._io.readF4le();
      this.acqVertOffset = this._io.readF4le();
      this.waveSourcePlugin = this._io.readS2le();
      this.waveSource = this._io.readS2le();
      this.triggerSource = this._io.readS2le();
      this.triggerCoupling = this._io.readS2le();
      this.triggerSlope = this._io.readS2le();
      this.smartTrigger = this._io.readS2le();
      this.triggerLevel = this._io.readF4le();
      this.sweepsArray1 = this._io.readS4le();
      this.sweepsArray2 = this._io.readS4le();
      this.reservedEnd = this._io.readBytes(2);
    }

    /**
     * True when samples are 16-bit words; false for 8-bit bytes.
     */
    Object.defineProperty(Wavedesc.prototype, 'is16bit', {
      get: function() {
        if (this._m_is16bit !== undefined)
          return this._m_is16bit;
        this._m_is16bit = this.commType == Lecroy10LeTrc.CommTypeEnum.WORD;
        return this._m_is16bit;
      }
    });

    /**
     * True when this is a sequence-mode acquisition.
     */
    Object.defineProperty(Wavedesc.prototype, 'isSequence', {
      get: function() {
        if (this._m_isSequence !== undefined)
          return this._m_isSequence;
        this._m_isSequence = this.subarrayCount > 1;
        return this._m_isSequence;
      }
    });

    /**
     * Alias for horiz_interval.
     */
    Object.defineProperty(Wavedesc.prototype, 'secondsPerPoint', {
      get: function() {
        if (this._m_secondsPerPoint !== undefined)
          return this._m_secondsPerPoint;
        this._m_secondsPerPoint = this.horizInterval;
        return this._m_secondsPerPoint;
      }
    });

    /**
     * Vertical scale in volts per division, computed from the full ADC count
     * range scaled by vertical_gain and divided by 8 display divisions.
     */
    Object.defineProperty(Wavedesc.prototype, 'voltPerDivision', {
      get: function() {
        if (this._m_voltPerDivision !== undefined)
          return this._m_voltPerDivision;
        this._m_voltPerDivision = ((this.maxValue - this.minValue) * this.verticalGain) / 8.0;
        return this._m_voltPerDivision;
      }
    });

    /**
     * ASCII "WAVEDESC" null-padded to 16 bytes.  Offset 0.
     */

    /**
     * Template version string, e.g. "LECROY_1_0".  Offset 16.
     */

    /**
     * Sample width: 0 = byte (8-bit), 1 = word (16-bit).  Offset 32.
     */

    /**
     * Byte order: 0 = HIFIRST (big-endian), 1 = LOFIRST (little-endian).  Offset 34.
     */

    /**
     * Length in bytes of this WAVEDESC block (320).  Offset 36.
     */

    /**
     * Length in bytes of the USERTEXT block; 0 if absent.  Offset 40.
     */

    /**
     * Length in bytes of the TRIGTIME array; 0 if absent.  Offset 44.
     */

    /**
     * Length in bytes of the primary waveform data array.  Offset 48.
     */

    /**
     * Length in bytes of the secondary waveform data array; 0 if absent.  Offset 52.
     */

    /**
     * Null-terminated ASCII instrument identifier.  Offset 56.
     */

    /**
     * Instrument model number.  Offset 72.
     */

    /**
     * User-defined waveform label string.  Offset 76.
     */

    /**
     * Total number of samples in the waveform.  Offset 92.
     */

    /**
     * Nominal number of samples visible on screen.  Offset 96.
     */

    /**
     * Index of the first valid sample.  Offset 100.
     */

    /**
     * Index of the last valid sample.  Offset 104.
     */

    /**
     * Number of acquired segments.  Offset 108.
     */

    /**
     * Nominal number of segments.  Offset 112.
     */

    /**
     * Number of sweeps accumulated.  Offset 116.
     */

    /**
     * Volts per ADC count.  Offset 120.
     */

    /**
     * Voltage offset (display use; calibration uses acq_vert_offset).  Offset 124.
     */

    /**
     * Maximum ADC count (e.g. 32512 for 16-bit).  Offset 128.
     */

    /**
     * Minimum ADC count (e.g. -32768 for 16-bit).  Offset 130.
     */

    /**
     * Nominal ADC resolution in bits.  Offset 132.
     */

    /**
     * Sampling interval in seconds.  Offset 134.
     */

    /**
     * Time of the first sample relative to the trigger, in seconds.  Offset 138.
     */

    /**
     * Horizontal display pixel offset (display use only).  Offset 146.
     */

    /**
     * Null-terminated ASCII unit string for the voltage axis.  Offset 154.
     */

    /**
     * Null-terminated ASCII unit string for the time axis.  Offset 202.
     */

    /**
     * Absolute date and time of the trigger event (16 bytes).  Offset 250.
     */

    /**
     * Total acquisition duration in seconds.  Offset 266.
     */

    /**
     * Waveform record type.  Offset 270.
     */

    /**
     * Post-acquisition processing applied.  Offset 272.
     */

    /**
     * Encoded horizontal time-per-division setting.  Offset 274.
     */

    /**
     * Vertical input coupling.  Offset 276.
     */

    /**
     * Probe attenuation factor.  Offset 278.
     */

    /**
     * Encoded nominal vertical scale setting.  Offset 282.
     */

    /**
     * Bandwidth-limiting filter state.  Offset 284.
     */

    /**
     * Fine vertical scale adjustment factor.  Offset 286.
     */

    /**
     * Acquisition vertical offset in volts.
     * Calibration: volts[i] = vertical_gain * adc[i] - acq_vert_offset.  Offset 290.
     */

    /**
     * Plugin slot of the source channel.  Offset 294.
     */

    /**
     * Source channel number, 1-indexed (1=CH1, 2=CH2, 3=CH3, 4=CH4).  Offset 296.
     */

    /**
     * Trigger source channel.  Offset 298.
     */

    /**
     * Trigger coupling mode.  Offset 300.
     */

    /**
     * Trigger slope.  Offset 302.
     */

    /**
     * Smart trigger mode.  Offset 304.
     */

    /**
     * Trigger level in volts.  Offset 306.
     */

    /**
     * Sweeps in array 1.  Offset 310.
     */

    /**
     * Sweeps in array 2.  Offset 314.
     */

    /**
     * Reserved padding to 320 bytes.  Offset 318.
     */

    return Wavedesc;
  })();

  /**
   * Per-segment trigger-time entries for sequence acquisitions.
   */
  Object.defineProperty(Lecroy10LeTrc.prototype, 'trigtimeArray', {
    get: function() {
      if (this._m_trigtimeArray !== undefined)
        return this._m_trigtimeArray;
      if (this.wavedesc.trigtimeArrayLen > 0) {
        var _pos = this._io.pos;
        this._io.seek(this.wavedesc.waveDescriptor + this.wavedesc.userTextLen);
        this._m_trigtimeArray = [];
        for (var i = 0; i < Math.floor(this.wavedesc.trigtimeArrayLen / 16); i++) {
          this._m_trigtimeArray.push(new TrigtimeEntry(this._io, this, this._root));
        }
        this._io.seek(_pos);
      }
      return this._m_trigtimeArray;
    }
  });

  /**
   * Optional ASCII user text.
   */
  Object.defineProperty(Lecroy10LeTrc.prototype, 'userText', {
    get: function() {
      if (this._m_userText !== undefined)
        return this._m_userText;
      if (this.wavedesc.userTextLen > 0) {
        var _pos = this._io.pos;
        this._io.seek(this.wavedesc.waveDescriptor);
        this._m_userText = this._io.readBytes(this.wavedesc.userTextLen);
        this._io.seek(_pos);
      }
      return this._m_userText;
    }
  });

  /**
   * Primary sample data as raw bytes.
   * Interpret as s1 array (COMM_TYPE == byte) or s2 array (COMM_TYPE == word),
   * little-endian byte order.
   * Apply: volts[i] = vertical_gain * adc[i] - acq_vert_offset.
   */
  Object.defineProperty(Lecroy10LeTrc.prototype, 'waveArray1', {
    get: function() {
      if (this._m_waveArray1 !== undefined)
        return this._m_waveArray1;
      var _pos = this._io.pos;
      this._io.seek((this.wavedesc.waveDescriptor + this.wavedesc.userTextLen) + this.wavedesc.trigtimeArrayLen);
      this._m_waveArray1 = this._io.readBytes(this.wavedesc.waveArray1Len);
      this._io.seek(_pos);
      return this._m_waveArray1;
    }
  });

  /**
   * Secondary sample data as raw bytes.
   */
  Object.defineProperty(Lecroy10LeTrc.prototype, 'waveArray2', {
    get: function() {
      if (this._m_waveArray2 !== undefined)
        return this._m_waveArray2;
      if (this.wavedesc.waveArray2Len > 0) {
        var _pos = this._io.pos;
        this._io.seek(((this.wavedesc.waveDescriptor + this.wavedesc.userTextLen) + this.wavedesc.trigtimeArrayLen) + this.wavedesc.waveArray1Len);
        this._m_waveArray2 = this._io.readBytes(this.wavedesc.waveArray2Len);
        this._io.seek(_pos);
      }
      return this._m_waveArray2;
    }
  });

  /**
   * Main waveform descriptor block.
   */

  return Lecroy10LeTrc;
})();
Lecroy10LeTrc_.Lecroy10LeTrc = Lecroy10LeTrc;
});
