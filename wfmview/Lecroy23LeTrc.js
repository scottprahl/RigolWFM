// This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild

(function (root, factory) {
  if (typeof define === 'function' && define.amd) {
    define(['exports', 'kaitai-struct/KaitaiStream'], factory);
  } else if (typeof exports === 'object' && exports !== null && typeof exports.nodeType !== 'number') {
    factory(exports, require('kaitai-struct/KaitaiStream'));
  } else {
    factory(root.Lecroy23LeTrc || (root.Lecroy23LeTrc = {}), root.KaitaiStream);
  }
})(typeof self !== 'undefined' ? self : this, function (Lecroy23LeTrc_, KaitaiStream) {
/**
 * Teledyne LeCroy LECROY_2_3 binary waveform format (.trc files) — little-endian variant.
 * 
 * This parser handles files where byte 34 (the low byte of COMM_ORDER) equals 1,
 * indicating LOFIRST (little-endian) byte order.  Use lecroy_2_3_be for big-endian
 * files (byte 34 == 0).
 * 
 * File layout::
 * 
 *   [WAVEDESC block:   346 bytes  — main waveform descriptor (WAVE_DESCRIPTOR field)]
 *   [USERTEXT block:   variable  — optional free-form text (USER_TEXT bytes; 0 if absent)]
 *   [TRIGTIME array:   variable  — segment trigger times for sequence acquisitions]
 *   [RIS_TIME array:   variable  — random-interleaved-sampling time array (0 if absent)]
 *   [WAVE_ARRAY_1:     variable  — primary sample data (WAVE_ARRAY_1 bytes)]
 *   [WAVE_ARRAY_2:     variable  — secondary sample data (0 if absent)]
 * 
 * WAVEDESC always starts with the 8-byte ASCII marker "WAVEDESC", null-padded to
 * 16 bytes.  Normal .trc files written by the oscilloscope begin at byte 0.  Files
 * transferred via SCPI may carry a short numeric prefix before WAVEDESC; those
 * files are not supported directly by this parser.
 * 
 * Endianness detection (performed by the caller before selecting this parser)::
 * 
 *   COMM_ORDER is a u2 at offset 34.  Because COMM_ORDER can only be 0 or 1,
 *   the low byte at offset 34 is unambiguous in both byte orders:
 *     byte 34 == 0  →  HIFIRST (big-endian,    use lecroy_2_3_be)
 *     byte 34 == 1  →  LOFIRST (little-endian, use lecroy_2_3_le)
 * 
 * Voltage reconstruction (single sweep)::
 * 
 *   volts[i] = VERTICAL_GAIN * adc[i] - VERTICAL_OFFSET
 * 
 * where adc[i] is signed 8-bit (COMM_TYPE == byte) or signed 16-bit (COMM_TYPE == word).
 * 
 * Time axis::
 * 
 *   t[i] = HORIZ_OFFSET + i * HORIZ_INTERVAL   (i = 0 … WAVE_ARRAY_COUNT − 1)
 * 
 * For sequence acquisitions (SUBARRAY_COUNT > 1), the time axis for segment k is::
 * 
 *   t[k,i] = (trigtime_array[k].trigger_time + trigtime_array[k].trigger_offset)
 *            + i * HORIZ_INTERVAL
 * 
 * Sources used for this KSY binary format:
 * `docs/vendors/lecroy/LeCroyWaveformTemplate_2_3.pdf`.  Github repos: 
 * <https://github.com/bennomeier/leCroyParser>, and 
 * <https://github.com/lobis/lecroy-scope> were used for verification.
 * 
 * Tested file formats: synthetic little-endian `LECROY_2_3` files with 8-bit
 * and 16-bit sample payloads, SCPI-prefixed fixtures, and long-prefix
 * autodetect cases, plus the checked-in real `lecroy_1.trc` through
 * `lecroy_4.trc` SCPI-prefixed captures.
 * 
 * Oscilloscope models this format may apply to: Teledyne LeCroy oscilloscopes
 * that write the `LECROY_2_3` template in little-endian form, including many
 * WaveRunner, WavePro, WaveSurfer, and later Teledyne LeCroy families.
 */

var Lecroy23LeTrc = (function() {
  Lecroy23LeTrc.BandwidthLimitEnum = Object.freeze({
    BW_FULL: 0,
    BW_LIMITED: 1,

    0: "BW_FULL",
    1: "BW_LIMITED",
  });

  Lecroy23LeTrc.CommOrderEnum = Object.freeze({
    BIG_ENDIAN: 0,
    LITTLE_ENDIAN: 1,

    0: "BIG_ENDIAN",
    1: "LITTLE_ENDIAN",
  });

  Lecroy23LeTrc.CommTypeEnum = Object.freeze({
    BYTE: 0,
    WORD: 1,

    0: "BYTE",
    1: "WORD",
  });

  Lecroy23LeTrc.ProcessingDoneEnum = Object.freeze({
    NO_PROCESSING: 0,
    FIR_FILTER: 1,
    INTERPOLATED: 2,
    SPARSED: 3,
    AUTOSCALED: 4,
    NO_RESULT: 5,
    ROLLING: 6,
    CUMULATIVE: 7,

    0: "NO_PROCESSING",
    1: "FIR_FILTER",
    2: "INTERPOLATED",
    3: "SPARSED",
    4: "AUTOSCALED",
    5: "NO_RESULT",
    6: "ROLLING",
    7: "CUMULATIVE",
  });

  Lecroy23LeTrc.RecordTypeEnum = Object.freeze({
    SINGLE_SWEEP: 0,
    INTERLEAVED: 1,
    HISTOGRAM: 2,
    GRAPH: 3,
    FILTER_COEFFICIENT: 4,
    COMPLEX: 5,
    EXTREMA: 6,
    SEQUENCE_OBSOLETE: 7,
    CENTERED_RIS: 8,
    PEAK_DETECT: 9,

    0: "SINGLE_SWEEP",
    1: "INTERLEAVED",
    2: "HISTOGRAM",
    3: "GRAPH",
    4: "FILTER_COEFFICIENT",
    5: "COMPLEX",
    6: "EXTREMA",
    7: "SEQUENCE_OBSOLETE",
    8: "CENTERED_RIS",
    9: "PEAK_DETECT",
  });

  Lecroy23LeTrc.VertCouplingEnum = Object.freeze({
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

  Lecroy23LeTrc.WaveSourceEnum = Object.freeze({
    CHANNEL_1: 0,
    CHANNEL_2: 1,
    CHANNEL_3: 2,
    CHANNEL_4: 3,
    UNKNOWN: 4,

    0: "CHANNEL_1",
    1: "CHANNEL_2",
    2: "CHANNEL_3",
    3: "CHANNEL_4",
    4: "UNKNOWN",
  });

  function Lecroy23LeTrc(_io, _parent, _root) {
    this._io = _io;
    this._parent = _parent;
    this._root = _root || this;

    this._read();
  }
  Lecroy23LeTrc.prototype._read = function() {
    this.wavedesc = new Wavedesc(this._io, this, this._root);
  }

  /**
   * 16-byte absolute trigger timestamp embedded in WAVEDESC at offset 296.
   * Endianness is inherited from the root type.
   */

  var TriggerTimestamp = Lecroy23LeTrc.TriggerTimestamp = (function() {
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
     * Fractional seconds within the current minute (0.0 to 59.999…).
     */

    /**
     * Minutes component of the trigger time (0–59).
     */

    /**
     * Hours component of the trigger time (0–23).
     */

    /**
     * Day of month (1–31).
     */

    /**
     * Month (1–12).
     */

    /**
     * Full year (e.g. 2024).
     */

    /**
     * Padding; always 0.
     */

    return TriggerTimestamp;
  })();

  /**
   * One 16-byte record in the TRIGTIME array.  Present only for sequence-mode
   * acquisitions (SUBARRAY_COUNT > 1).  Endianness is inherited from the root type.
   * 
   * Time axis for segment k (0-based):
   *   t[k,i] = (trigger_time + trigger_offset) + i * HORIZ_INTERVAL
   */

  var TrigtimeEntry = Lecroy23LeTrc.TrigtimeEntry = (function() {
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

    /**
     * Absolute trigger timestamp for this segment, in seconds.
     */

    /**
     * Horizontal offset for this segment (time from trigger to first sample), in seconds.
     */

    return TrigtimeEntry;
  })();

  /**
   * 346-byte WAVEDESC header block (LECROY_2_3 template).  All byte offsets in the
   * original LeCroy template documentation are relative to the start of this struct.
   * Endianness is inherited from the root type (little-endian).
   */

  var Wavedesc = Lecroy23LeTrc.Wavedesc = (function() {
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
      this.resDesc1 = this._io.readS4le();
      this.trigtimeArrayLen = this._io.readS4le();
      this.risTimeArrayLen = this._io.readS4le();
      this.resArray1 = this._io.readS4le();
      this.waveArray1Len = this._io.readS4le();
      this.waveArray2Len = this._io.readS4le();
      this.resArray2 = this._io.readS4le();
      this.resArray3 = this._io.readS4le();
      this.instrumentName = this._io.readBytes(16);
      this.instrumentNumber = this._io.readS4le();
      this.traceLabel = this._io.readBytes(16);
      this.reserved1 = this._io.readS2le();
      this.reserved2 = this._io.readS2le();
      this.waveArrayCount = this._io.readS4le();
      this.pntsPerScreen = this._io.readS4le();
      this.firstValidPnt = this._io.readS4le();
      this.lastValidPnt = this._io.readS4le();
      this.firstPoint = this._io.readS4le();
      this.sparsingFactor = this._io.readS4le();
      this.segmentIndex = this._io.readS4le();
      this.subarrayCount = this._io.readS4le();
      this.sweepsPerAcq = this._io.readS4le();
      this.pointsPerPair = this._io.readS2le();
      this.pairOffset = this._io.readS2le();
      this.verticalGain = this._io.readF4le();
      this.verticalOffset = this._io.readF4le();
      this.maxValue = this._io.readF4le();
      this.minValue = this._io.readF4le();
      this.nominalBits = this._io.readS2le();
      this.nomSubarrayCount = this._io.readS2le();
      this.horizInterval = this._io.readF4le();
      this.horizOffset = this._io.readF8le();
      this.pixelOffset = this._io.readF8le();
      this.vertUnit = this._io.readBytes(48);
      this.horUnit = this._io.readBytes(48);
      this.horizUncertainty = this._io.readF4le();
      this.triggerTime = new TriggerTimestamp(this._io, this, this._root);
      this.acqDuration = this._io.readF4le();
      this.recordType = this._io.readU2le();
      this.processingDone = this._io.readU2le();
      this.reserved5 = this._io.readS2le();
      this.risSweeps = this._io.readS2le();
      this.timebase = this._io.readU2le();
      this.vertCoupling = this._io.readU2le();
      this.probeAtt = this._io.readF4le();
      this.fixedVertGain = this._io.readU2le();
      this.bandwidthLimit = this._io.readU2le();
      this.verticalVernier = this._io.readF4le();
      this.acqVertOffset = this._io.readF4le();
      this.waveSource = this._io.readU2le();
    }

    /**
     * True when samples are 16-bit words; false for 8-bit bytes.
     */
    Object.defineProperty(Wavedesc.prototype, 'is16bit', {
      get: function() {
        if (this._m_is16bit !== undefined)
          return this._m_is16bit;
        this._m_is16bit = this.commType == Lecroy23LeTrc.CommTypeEnum.WORD;
        return this._m_is16bit;
      }
    });

    /**
     * True when this is a sequence-mode (multi-segment) acquisition.
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
     * Alias for horiz_interval; seconds between consecutive ADC samples.
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
     * Vertical scale in volts per division.  MAX_VALUE and MIN_VALUE are ADC
     * counts; multiply by vertical_gain to convert to volts, then divide by
     * the standard 8-division display height.
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
     * Template version string, e.g. "LECROY_2_3".  Offset 16.
     */

    /**
     * Sample width: 0 = byte (8-bit), 1 = word (16-bit).  Offset 32.
     */

    /**
     * Byte order: 0 = HIFIRST (big-endian), 1 = LOFIRST (little-endian).  Offset 34.
     */

    /**
     * Length in bytes of this WAVEDESC block (typically 346).  Offset 36.
     */

    /**
     * Length in bytes of the USERTEXT block; 0 if absent.  Offset 40.
     */

    /**
     * Reserved.  Offset 44.
     */

    /**
     * Length in bytes of the TRIGTIME array; 0 if absent.  Offset 48.
     */

    /**
     * Length in bytes of the RIS_TIME array; 0 if absent.  Offset 52.
     */

    /**
     * Reserved.  Offset 56.
     */

    /**
     * Length in bytes of the primary waveform data array.  Offset 60.
     */

    /**
     * Length in bytes of the secondary waveform data array; 0 if absent.  Offset 64.
     */

    /**
     * Reserved.  Offset 68.
     */

    /**
     * Reserved.  Offset 72.
     */

    /**
     * Null-terminated ASCII instrument identifier (e.g. "WAVERUNNER").  Offset 76.
     */

    /**
     * Instrument serial number.  Offset 92.
     */

    /**
     * User-defined waveform label string.  Offset 96.
     */

    /**
     * Reserved.  Offset 112.
     */

    /**
     * Reserved.  Offset 114.
     */

    /**
     * Total number of samples in the waveform.  Offset 116.
     */

    /**
     * Nominal number of samples visible on the oscilloscope screen.  Offset 120.
     */

    /**
     * Index of the first valid sample.  Offset 124.
     */

    /**
     * Index of the last valid sample.  Offset 128.
     */

    /**
     * Byte offset of the first transmitted point relative to start of trace.  Offset 132.
     */

    /**
     * Sparsing factor applied to the transmitted data.  Offset 136.
     */

    /**
     * Index of the transmitted segment (for sequence acquisitions).  Offset 140.
     */

    /**
     * Number of acquired segments.  1 = single sweep, >1 = sequence mode.
     * When > 1, trigtime_array at the root level holds per-segment time info.
     * Offset 144.
     */

    /**
     * Number of sweeps accumulated (average/envelope modes).  Offset 148.
     */

    /**
     * Data points per min/max pair (peak-detect waveforms only).  Offset 152.
     */

    /**
     * Offset to the data pairs (peak-detect waveforms only).  Offset 154.
     */

    /**
     * Volts per ADC count.
     * volts[i] = vertical_gain * adc[i] - vertical_offset.  Offset 156.
     */

    /**
     * Voltage offset subtracted after scaling.
     * volts[i] = vertical_gain * adc[i] - vertical_offset.  Offset 160.
     */

    /**
     * Maximum ADC output voltage (top of the displayed grid).  Offset 164.
     */

    /**
     * Minimum ADC output voltage (bottom of the displayed grid).  Offset 168.
     */

    /**
     * ADC resolution in bits (e.g. 8 or 16).  Offset 172.
     */

    /**
     * Nominal number of segments (requested; may differ from subarray_count).  Offset 174.
     */

    /**
     * Sampling interval in seconds (time between consecutive samples).  Offset 176.
     */

    /**
     * Time of the first sample relative to the trigger, in seconds.  Offset 180.
     */

    /**
     * Horizontal display pixel offset (for display use only).  Offset 188.
     */

    /**
     * Null-terminated ASCII unit string for the voltage axis (e.g. "V").  Offset 196.
     */

    /**
     * Null-terminated ASCII unit string for the time axis (e.g. "s").  Offset 244.
     */

    /**
     * Estimated uncertainty of horiz_offset, in seconds.  Offset 292.
     */

    /**
     * Absolute date and time of the trigger event (16 bytes).  Offset 296.
     */

    /**
     * Total acquisition duration, in seconds.  Offset 312.
     */

    /**
     * Waveform record type; governs interpretation of wave_array_2.  Offset 316.
     */

    /**
     * Post-acquisition processing applied to the data.  Offset 318.
     */

    /**
     * Reserved.  Offset 320.
     */

    /**
     * Number of sweeps in a RIS acquisition; 1 for all other record types.  Offset 322.
     */

    /**
     * Encoded horizontal time-per-division setting.
     * Values 0–47 follow a 1/2/5 × 10^n sequence (index 0 = 1 ps/div, …,
     * index 47 = 5 ks/div).  Value 100 = EXTERNAL clock.
     * Decode: mant = [1,2,5][index % 3]; exp = index // 3 − 12; t = mant × 10^exp s/div.
     * Offset 324.
     */

    /**
     * Vertical input coupling.  Offset 326.
     */

    /**
     * Probe attenuation factor (e.g. 10.0 for a 10× probe).  Offset 328.
     */

    /**
     * Encoded nominal vertical scale setting (V/div, before probe attenuation).
     * Values 0–27 follow a 1/2/5 × 10^n sequence:
     *   index 0 = 1 µV/div, index 9 = 10 mV/div, index 18 = 100 mV/div, etc.
     * Decode: mant = [1,2,5][index % 3]; exp = index // 3 − 6; V/div = mant × 10^exp.
     * Offset 332.
     */

    /**
     * Bandwidth-limiting filter state (bw_full = no limit, bw_limited = on).  Offset 334.
     */

    /**
     * Fine vertical scale adjustment factor.  Offset 336.
     */

    /**
     * Acquisition vertical offset in volts.  Offset 340.
     */

    /**
     * Oscilloscope channel that produced this waveform.  Offset 344.
     */

    return Wavedesc;
  })();

  /**
   * Per-segment trigger-time entries for sequence acquisitions.
   * Present only when SUBARRAY_COUNT > 1.  Each entry is 16 bytes
   * (two f8 values: trigger_time, trigger_offset).
   */
  Object.defineProperty(Lecroy23LeTrc.prototype, 'trigtimeArray', {
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
   * Optional ASCII user text (up to 160 bytes).
   */
  Object.defineProperty(Lecroy23LeTrc.prototype, 'userText', {
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
   * Apply: volts[i] = VERTICAL_GAIN * adc[i] - VERTICAL_OFFSET.
   */
  Object.defineProperty(Lecroy23LeTrc.prototype, 'waveArray1', {
    get: function() {
      if (this._m_waveArray1 !== undefined)
        return this._m_waveArray1;
      var _pos = this._io.pos;
      this._io.seek(((this.wavedesc.waveDescriptor + this.wavedesc.userTextLen) + this.wavedesc.trigtimeArrayLen) + this.wavedesc.risTimeArrayLen);
      this._m_waveArray1 = this._io.readBytes(this.wavedesc.waveArray1Len);
      this._io.seek(_pos);
      return this._m_waveArray1;
    }
  });

  /**
   * Secondary sample data as raw bytes (same format as wave_array_1).
   * Interpretation depends on RECORD_TYPE:
   *   extrema (6)     — floor (minimum) trace
   *   complex (5)     — imaginary part of FFT
   *   peak_detect (9) — floor trace
   */
  Object.defineProperty(Lecroy23LeTrc.prototype, 'waveArray2', {
    get: function() {
      if (this._m_waveArray2 !== undefined)
        return this._m_waveArray2;
      if (this.wavedesc.waveArray2Len > 0) {
        var _pos = this._io.pos;
        this._io.seek((((this.wavedesc.waveDescriptor + this.wavedesc.userTextLen) + this.wavedesc.trigtimeArrayLen) + this.wavedesc.risTimeArrayLen) + this.wavedesc.waveArray1Len);
        this._m_waveArray2 = this._io.readBytes(this.wavedesc.waveArray2Len);
        this._io.seek(_pos);
      }
      return this._m_waveArray2;
    }
  });

  /**
   * Main waveform descriptor block.
   */

  return Lecroy23LeTrc;
})();
Lecroy23LeTrc_.Lecroy23LeTrc = Lecroy23LeTrc;
});
