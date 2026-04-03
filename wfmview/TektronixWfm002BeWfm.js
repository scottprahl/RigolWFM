// This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild

(function (root, factory) {
  if (typeof define === 'function' && define.amd) {
    define(['exports', 'kaitai-struct/KaitaiStream'], factory);
  } else if (typeof exports === 'object' && exports !== null && typeof exports.nodeType !== 'number') {
    factory(exports, require('kaitai-struct/KaitaiStream'));
  } else {
    factory(root.TektronixWfm002BeWfm || (root.TektronixWfm002BeWfm = {}), root.KaitaiStream);
  }
})(typeof self !== 'undefined' ? self : this, function (TektronixWfm002BeWfm_, KaitaiStream) {
/**
 * Tektronix WFM binary waveform format, version WFM#002 and WFM#003,
 * big-endian variant.
 * 
 * WFM#002 applies to: TDS5000B Series.
 * WFM#003 applies to: DPO7000, DPO70000, DSA70000 Series.
 * 
 * WFM#003 additional difference: point_density in the user-view sections of each
 * dimension (exp_dim1, exp_dim2, imp_dim1, imp_dim2) changes from u4 (4 bytes) to
 * f8 (8 bytes).  This parser handles that layout difference explicitly, so the
 * downstream time-base, update-spec, and curve offsets are correct for both
 * WFM#002 and WFM#003 files.
 * 
 * Endianness and version detection::
 * 
 *   byte_order at offset 0 is 0xF0F0 for big-endian (PPC).
 *   version_number at offset 2 is "WFM#002" or "WFM#003".
 * 
 * Voltage reconstruction (explicit dimension 1)::
 * 
 *   volts[i] = exp_dim1.dim_scale * adc[i] + exp_dim1.dim_offset
 * 
 * Time axis (implicit dimension 1)::
 * 
 *   t[i] = imp_dim1.dim_offset + i * imp_dim1.dim_scale
 * 
 * where i = 0 corresponds to the first sample in the curve buffer.
 * 
 * Sources used for this KSY binary format: Tektronix "Reference Waveform File Format" 
 * (001-1378-03).
 * 
 * Tested file formats: no checked-in big-endian `WFM#002` / `WFM#003` fixture
 * currently exercises this exact schema; the little-endian sibling is covered
 * by synthetic `WFM#002` / `WFM#003` regressions and this variant is the
 * byte-swapped counterpart from the same Tektronix reference manual.
 * 
 * Oscilloscope models this format may apply to: big-endian Tektronix scopes
 * that write `WFM#002` or `WFM#003`, especially older PPC-based variants of
 * the `TDS5000B`, `DPO7000`, `DPO70000`, and `DSA70000` families.
 */

var TektronixWfm002BeWfm = (function() {
  TektronixWfm002BeWfm.BaseTypeEnum = Object.freeze({
    BASE_TIME: 0,
    BASE_SPECTRAL_MAG: 1,
    BASE_SPECTRAL_PHASE: 2,
    BASE_INVALID: 3,

    0: "BASE_TIME",
    1: "BASE_SPECTRAL_MAG",
    2: "BASE_SPECTRAL_PHASE",
    3: "BASE_INVALID",
  });

  TektronixWfm002BeWfm.ChecksumTypeEnum = Object.freeze({
    NO_CHECKSUM: 0,
    CTYPE_CRC16: 1,
    CTYPE_SUM16: 2,
    CTYPE_CRC32: 3,
    CTYPE_SUM32: 4,

    0: "NO_CHECKSUM",
    1: "CTYPE_CRC16",
    2: "CTYPE_SUM16",
    3: "CTYPE_CRC32",
    4: "CTYPE_SUM32",
  });

  TektronixWfm002BeWfm.DataTypeEnum = Object.freeze({
    WFMDATA_SCALAR_MEAS: 0,
    WFMDATA_SCALAR_CONST: 1,
    WFMDATA_VECTOR: 2,
    WFMDATA_PIXMAP: 3,
    WFMDATA_INVALID: 4,
    WFMDATA_WFMDB: 5,

    0: "WFMDATA_SCALAR_MEAS",
    1: "WFMDATA_SCALAR_CONST",
    2: "WFMDATA_VECTOR",
    3: "WFMDATA_PIXMAP",
    4: "WFMDATA_INVALID",
    5: "WFMDATA_WFMDB",
  });

  TektronixWfm002BeWfm.ExplicitFormatEnum = Object.freeze({
    EXPLICIT_INT16: 0,
    EXPLICIT_INT32: 1,
    EXPLICIT_UINT32: 2,
    EXPLICIT_UINT64: 3,
    EXPLICIT_FP32: 4,
    EXPLICIT_FP64: 5,
    EXPLICIT_INVALID_FORMAT: 6,
    EXPLICIT_UINT8: 7,
    EXPLICIT_INT8: 8,

    0: "EXPLICIT_INT16",
    1: "EXPLICIT_INT32",
    2: "EXPLICIT_UINT32",
    3: "EXPLICIT_UINT64",
    4: "EXPLICIT_FP32",
    5: "EXPLICIT_FP64",
    6: "EXPLICIT_INVALID_FORMAT",
    7: "EXPLICIT_UINT8",
    8: "EXPLICIT_INT8",
  });

  TektronixWfm002BeWfm.ExplicitStorageEnum = Object.freeze({
    EXPLICIT_SAMPLE: 0,
    EXPLICIT_MIN_MAX: 1,
    EXPLICIT_VERT_HIST: 2,
    EXPLICIT_HOR_HIST: 3,
    EXPLICIT_ROW_ORDER: 4,
    EXPLICIT_COLUMN_ORDER: 5,
    EXPLICIT_INVALID_STORAGE: 6,

    0: "EXPLICIT_SAMPLE",
    1: "EXPLICIT_MIN_MAX",
    2: "EXPLICIT_VERT_HIST",
    3: "EXPLICIT_HOR_HIST",
    4: "EXPLICIT_ROW_ORDER",
    5: "EXPLICIT_COLUMN_ORDER",
    6: "EXPLICIT_INVALID_STORAGE",
  });

  TektronixWfm002BeWfm.PixMapFormatEnum = Object.freeze({
    DSY_FORMAT_INVALID: 0,
    DSY_FORMAT_YT: 1,
    DSY_FORMAT_XY: 2,
    DSY_FORMAT_XYZ: 3,

    0: "DSY_FORMAT_INVALID",
    1: "DSY_FORMAT_YT",
    2: "DSY_FORMAT_XY",
    3: "DSY_FORMAT_XYZ",
  });

  TektronixWfm002BeWfm.SetTypeEnum = Object.freeze({
    SINGLE_WAVEFORM: 0,
    FAST_FRAME: 1,

    0: "SINGLE_WAVEFORM",
    1: "FAST_FRAME",
  });

  TektronixWfm002BeWfm.SummaryFrameEnum = Object.freeze({
    SUMMARY_FRAME_OFF: 0,
    SUMMARY_FRAME_AVERAGE: 1,
    SUMMARY_FRAME_ENVELOPE: 2,

    0: "SUMMARY_FRAME_OFF",
    1: "SUMMARY_FRAME_AVERAGE",
    2: "SUMMARY_FRAME_ENVELOPE",
  });

  TektronixWfm002BeWfm.SweepEnum = Object.freeze({
    SWEEP_ROLL: 0,
    SWEEP_SAMPLE: 1,
    SWEEP_ET: 2,
    SWEEP_INVALID: 3,

    0: "SWEEP_ROLL",
    1: "SWEEP_SAMPLE",
    2: "SWEEP_ET",
    3: "SWEEP_INVALID",
  });

  function TektronixWfm002BeWfm(_io, _parent, _root) {
    this._io = _io;
    this._parent = _parent;
    this._root = _root || this;

    this._read();
  }
  TektronixWfm002BeWfm.prototype._read = function() {
    this.staticFileInfo = new StaticFileInfo(this._io, this, this._root);
    this.wfmHeader = new WfmHeader(this._io, this, this._root);
  }

  /**
   * Explicit dimension: 100-byte description block plus a version-dependent
   * user-view section.
   * 
   * Total size:
   *   WFM#002 = 156 bytes (56-byte user-view)
   *   WFM#003 = 160 bytes (60-byte user-view)
   * 
   * For YT waveforms, explicit dimension 1 defines the voltage (Y) axis:
   *   volts[i] = dim_scale * adc[i] + dim_offset
   */

  var ExpDim = TektronixWfm002BeWfm.ExpDim = (function() {
    function ExpDim(_io, _parent, _root) {
      this._io = _io;
      this._parent = _parent;
      this._root = _root;

      this._read();
    }
    ExpDim.prototype._read = function() {
      this.dimScale = this._io.readF8be();
      this.dimOffset = this._io.readF8be();
      this.dimSize = this._io.readU4be();
      this.units = this._io.readBytes(20);
      this.dimExtentMin = this._io.readF8be();
      this.dimExtentMax = this._io.readF8be();
      this.dimResolution = this._io.readF8be();
      this.dimRefPoint = this._io.readF8be();
      this.format = this._io.readS4be();
      this.storageType = this._io.readS4be();
      this.nValue = this._io.readBytes(4);
      this.overRange = this._io.readBytes(4);
      this.underRange = this._io.readBytes(4);
      this.highRange = this._io.readBytes(4);
      this.lowRange = this._io.readBytes(4);
      this.userScale = this._io.readF8be();
      this.userUnits = this._io.readBytes(20);
      this.userOffset = this._io.readF8be();
      if (!(this._root.isWfm003)) {
        this.pointDensityU4 = this._io.readU4be();
      }
      if (this._root.isWfm003) {
        this.pointDensityF8 = this._io.readF8be();
      }
      this.hRef = this._io.readF8be();
      this.trigDelay = this._io.readF8be();
    }

    /**
     * Version-normalized point_density value.
     */
    Object.defineProperty(ExpDim.prototype, 'pointDensity', {
      get: function() {
        if (this._m_pointDensity !== undefined)
          return this._m_pointDensity;
        this._m_pointDensity = (this._root.isWfm003 ? this.pointDensityF8 : this.pointDensityU4);
        return this._m_pointDensity;
      }
    });

    /**
     * Scale factor in physical units per ADC count (volts per LSB).
     */

    /**
     * Offset in physical units.
     * volts[i] = dim_scale * adc[i] + dim_offset.
     */

    /**
     * Storage element size (e.g. 252 for 8-bit, 65532 for 16-bit; 1 for float).
     */

    /**
     * Null-terminated ASCII unit string (e.g. "Volts").
     */

    /**
     * Minimum attainable value (not for user use).
     */

    /**
     * Maximum attainable value (not for user use).
     */

    /**
     * Smallest resolvable voltage increment (value of one digitizing level).
     */

    /**
     * Ground-level reference value.
     */

    /**
     * Data format of curve buffer values.
     */

    /**
     * Storage layout of curve buffer values.
     */

    /**
     * Raw 4-byte unacquired (NULL) value representation.
     */

    /**
     * Raw 4-byte over-range value.
     */

    /**
     * Raw 4-byte under-range value.
     */

    /**
     * Raw 4-byte maximum signed value.
     */

    /**
     * Raw 4-byte minimum value.
     */

    /**
     * User display scale in physical units per screen division.
     */

    /**
     * Null-terminated user display unit string.
     */

    /**
     * User display position offset in screen divisions.
     */

    /**
     * Screen-to-data ratio in WFM#002 files.  Always 1 for explicit dimensions.
     */

    /**
     * Screen-to-data ratio in WFM#003 files.  Always 1 for explicit dimensions.
     */

    /**
     * Trigger horizontal position as a percentage of the waveform (0–100%).
     */

    /**
     * Time delay in seconds from trigger to HRef screen position.
     */

    return ExpDim;
  })();

  /**
   * Implicit dimension: 76-byte description block plus a version-dependent
   * user-view section.
   * 
   * Total size:
   *   WFM#002 = 132 bytes (56-byte user-view)
   *   WFM#003 = 136 bytes (60-byte user-view)
   * 
   * For YT waveforms, implicit dimension 1 defines the time (X) axis:
   *   t[i] = dim_offset + i * dim_scale
   * where i = 0 is the first sample in the curve buffer.
   */

  var ImpDim = TektronixWfm002BeWfm.ImpDim = (function() {
    function ImpDim(_io, _parent, _root) {
      this._io = _io;
      this._parent = _parent;
      this._root = _root;

      this._read();
    }
    ImpDim.prototype._read = function() {
      this.dimScale = this._io.readF8be();
      this.dimOffset = this._io.readF8be();
      this.dimSize = this._io.readU4be();
      this.units = this._io.readBytes(20);
      this.dimExtentMin = this._io.readF8be();
      this.dimExtentMax = this._io.readF8be();
      this.dimResolution = this._io.readF8be();
      this.dimRefPoint = this._io.readF8be();
      this.spacing = this._io.readU4be();
      this.userScale = this._io.readF8be();
      this.userUnits = this._io.readBytes(20);
      this.userOffset = this._io.readF8be();
      if (!(this._root.isWfm003)) {
        this.pointDensityU4 = this._io.readU4be();
      }
      if (this._root.isWfm003) {
        this.pointDensityF8 = this._io.readF8be();
      }
      this.hRef = this._io.readF8be();
      this.trigDelay = this._io.readF8be();
    }

    /**
     * Version-normalized point_density value.
     */
    Object.defineProperty(ImpDim.prototype, 'pointDensity', {
      get: function() {
        if (this._m_pointDensity !== undefined)
          return this._m_pointDensity;
        this._m_pointDensity = (this._root.isWfm003 ? this.pointDensityF8 : this.pointDensityU4);
        return this._m_pointDensity;
      }
    });

    /**
     * Sample interval in seconds (time per point).
     */

    /**
     * Time in seconds of sample index 0 relative to the trigger.
     * Typically negative (pre-charge data precedes the trigger).
     */

    /**
     * Record length in samples, including pre- and post-charge data.
     */

    /**
     * Null-terminated ASCII unit string (e.g. "s").
     */

    /**
     * Not available for user use.
     */

    /**
     * Not available for user use.
     */

    /**
     * Time axis resolution.
     */

    /**
     * Horizontal reference point of the time base.
     */

    /**
     * Real-time point spacing; 1 for non-interpolated waveforms.
     */

    /**
     * User display time scale.
     */

    /**
     * Null-terminated user display time unit string.
     */

    /**
     * Horizontal center pixel column position relative to trigger (absolute time units).
     */

    /**
     * Data points compressed into one pixel column at zoom = 1 for WFM#002 files.
     */

    /**
     * Data points compressed into one pixel column at zoom = 1 for WFM#003 files.
     */

    /**
     * Trigger horizontal position as a percentage of the waveform (0–100%).
     */

    /**
     * Time delay in seconds from trigger to HRef screen position.
     */

    return ImpDim;
  })();

  /**
   * 78-byte block of static waveform file information at the very start of the file.
   * Identical in layout to WFM#001.
   */

  var StaticFileInfo = TektronixWfm002BeWfm.StaticFileInfo = (function() {
    function StaticFileInfo(_io, _parent, _root) {
      this._io = _io;
      this._parent = _parent;
      this._root = _root;

      this._read();
    }
    StaticFileInfo.prototype._read = function() {
      this.byteOrder = this._io.readU2be();
      this.versionNumber = KaitaiStream.bytesToStr(this._io.readBytes(7), "ASCII");
      this.versionPad = this._io.readBytes(1);
      this.numDigitsByteCount = this._io.readU1();
      this.numBytesToEof = this._io.readS4be();
      this.numBytesPerPoint = this._io.readU1();
      this.byteOffsetToCurveBuffer = this._io.readS4be();
      this.horizZoomScaleFactor = this._io.readS4be();
      this.horizZoomPosition = this._io.readF4be();
      this.vertZoomScaleFactor = this._io.readF8be();
      this.vertZoomPosition = this._io.readF4be();
      this.waveformLabel = this._io.readBytes(32);
      this.nFastFramesMinus1 = this._io.readU4be();
      this.wfmHeaderSize = this._io.readU2be();
    }

    /**
     * Byte-order marker.  0xF0F0 = big-endian (PPC); 0x0F0F = little-endian (Intel / PC)
     * (PPC).  Offset 0.
     */

    /**
     * Version identification string.
     * "WFM#002" or "WFM#003" for this parser.  Offset 2.
     */

    /**
     * Null terminator / padding byte after version_number.  Offset 9.
     */

    /**
     * Number of decimal digits in the byte-count field (0–9).  Offset 10.
     */

    /**
     * Number of bytes from this field to the end of file.  Offset 11.
     */

    /**
     * Bytes per curve data point (2, 4, or 8).  Offset 15.
     */

    /**
     * Absolute byte offset from the start of file to the start of the curve buffer.
     * Offset 16.
     */

    /**
     * Horizontal zoom scale factor (display use only).  Offset 20.
     */

    /**
     * Horizontal zoom position (display use only).  Offset 24.
     */

    /**
     * Vertical zoom scale factor (display use only).  Offset 28.
     */

    /**
     * Vertical zoom position (display use only).  Offset 36.
     */

    /**
     * User-defined null-padded ASCII label for this waveform.  Offset 40.
     */

    /**
     * Number of FastFrame frames minus 1 (0 for single-waveform files).  Offset 72.
     */

    /**
     * Size in bytes of the waveform header.  Offset 76.
     */

    return StaticFileInfo;
  })();

  /**
   * 12-byte time-base acquisition information block.
   */

  var TimeBaseInfo = TektronixWfm002BeWfm.TimeBaseInfo = (function() {
    function TimeBaseInfo(_io, _parent, _root) {
      this._io = _io;
      this._parent = _parent;
      this._root = _root;

      this._read();
    }
    TimeBaseInfo.prototype._read = function() {
      this.realPointSpacing = this._io.readU4be();
      this.sweep = this._io.readS4be();
      this.typeOfBase = this._io.readS4be();
    }

    /**
     * Integer point spacing between consecutive acquired points.
     */

    /**
     * Sweep/acquisition mode.
     */

    /**
     * Domain of the horizontal axis.
     */

    return TimeBaseInfo;
  })();

  /**
   * 30-byte curve object containing byte offsets that bound the curve data regions.
   * To extract valid waveform samples:
   *   first_byte = data_start_offset
   *   last_byte  = postcharge_start_offset   (exclusive)
   */

  var WfmCurveObject = TektronixWfm002BeWfm.WfmCurveObject = (function() {
    function WfmCurveObject(_io, _parent, _root) {
      this._io = _io;
      this._parent = _parent;
      this._root = _root;

      this._read();
    }
    WfmCurveObject.prototype._read = function() {
      this.stateFlags = this._io.readU4be();
      this.checksumType = this._io.readS4be();
      this.checksum = this._io.readS2be();
      this.prechargeStartOffset = this._io.readU4be();
      this.dataStartOffset = this._io.readU4be();
      this.postchargeStartOffset = this._io.readU4be();
      this.postchargeStopOffset = this._io.readU4be();
      this.endOfCurveBufferOffset = this._io.readU4be();
    }

    /**
     * Index of the first user-accessible sample in the curve buffer.
     */
    Object.defineProperty(WfmCurveObject.prototype, 'firstValidSample', {
      get: function() {
        if (this._m_firstValidSample !== undefined)
          return this._m_firstValidSample;
        this._m_firstValidSample = Math.floor(this.dataStartOffset / this._root.staticFileInfo.numBytesPerPoint);
        return this._m_firstValidSample;
      }
    });

    /**
     * Number of user-accessible waveform samples.
     */
    Object.defineProperty(WfmCurveObject.prototype, 'numValidSamples', {
      get: function() {
        if (this._m_numValidSamples !== undefined)
          return this._m_numValidSamples;
        this._m_numValidSamples = Math.floor(this.postchargeStartOffset / this._root.staticFileInfo.numBytesPerPoint) - Math.floor(this.dataStartOffset / this._root.staticFileInfo.numBytesPerPoint);
        return this._m_numValidSamples;
      }
    });

    /**
     * Internal curve validity flags.
     */

    /**
     * Checksum algorithm for this curve.
     */

    /**
     * Curve checksum value.
     */

    /**
     * Byte offset from curve buffer start to first pre-charge data point.
     */

    /**
     * Byte offset from curve buffer start to first user-accessible data point.
     */

    /**
     * Byte offset from curve buffer start to first post-charge data point.
     */

    /**
     * Byte offset just past the last valid waveform point.
     */

    /**
     * Byte offset to the end of the curve buffer.  Equals postcharge_stop_offset
     * for non-roll-mode acquisitions.
     */

    return WfmCurveObject;
  })();

  /**
   * Waveform header block.  Differs from WFM#001 by the 2-byte summary_frame_type
   * field inserted after num_acquired_fast_frames.
   * 
   * WFM#002 uses 4-byte point_density values in the user-view sections:
   *   exp_dim1 @ 168, exp_dim2 @ 324, imp_dim1 @ 480, imp_dim2 @ 612,
   *   time_base1 @ 744, time_base2 @ 756, update_spec @ 768, curve @ 792.
   * 
   * WFM#003 uses 8-byte point_density values in the same sections:
   *   exp_dim1 @ 168, exp_dim2 @ 328, imp_dim1 @ 488, imp_dim2 @ 624,
   *   time_base1 @ 760, time_base2 @ 772, update_spec @ 784, curve @ 808.
   */

  var WfmHeader = TektronixWfm002BeWfm.WfmHeader = (function() {
    function WfmHeader(_io, _parent, _root) {
      this._io = _io;
      this._parent = _parent;
      this._root = _root;

      this._read();
    }
    WfmHeader.prototype._read = function() {
      this.setType = this._io.readS4be();
      this.wfmCnt = this._io.readU4be();
      this.acqCounter = this._io.readU8be();
      this.transactionCounter = this._io.readU8be();
      this.slotId = this._io.readS4be();
      this.isStaticFlag = this._io.readS4be();
      this.wfmUpdateSpecCount = this._io.readU4be();
      this.impDimRefCount = this._io.readU4be();
      this.expDimRefCount = this._io.readU4be();
      this.dataType = this._io.readS4be();
      this.genPurposeCounter = this._io.readU8be();
      this.accumWfmCount = this._io.readU4be();
      this.targetAccumCount = this._io.readU4be();
      this.curveRefCount = this._io.readU4be();
      this.numRequestedFastFrames = this._io.readU4be();
      this.numAcquiredFastFrames = this._io.readU4be();
      this.summaryFrameType = this._io.readU2be();
      this.pixMapDisplayFormat = this._io.readS4be();
      this.pixMapMaxValue = this._io.readU8be();
      this.expDim1 = new ExpDim(this._io, this, this._root);
      this.expDim2 = new ExpDim(this._io, this, this._root);
      this.impDim1 = new ImpDim(this._io, this, this._root);
      this.impDim2 = new ImpDim(this._io, this, this._root);
      this.timeBase1 = new TimeBaseInfo(this._io, this, this._root);
      this.timeBase2 = new TimeBaseInfo(this._io, this, this._root);
      this.updateSpec = new WfmUpdateSpec(this._io, this, this._root);
      this.curve = new WfmCurveObject(this._io, this, this._root);
    }

    /**
     * Waveform set type.  0 = single; 1 = FastFrame.  Offset 78.
     */

    /**
     * Number of waveforms in the set.  Offset 82.
     */

    /**
     * Internal acquisition counter.  Not for user use.  Offset 86.
     */

    /**
     * Internal transaction timestamp.  Not for user use.  Offset 94.
     */

    /**
     * Instrument data-slot enumeration.  Not for user use.  Offset 102.
     */

    /**
     * Non-zero = static reference; 0 = live channel/math.  Offset 106.
     */

    /**
     * Number of waveform update specifications.  Offset 110.
     */

    /**
     * Number of implicit dimension references.  Offset 114.
     */

    /**
     * Number of explicit dimension references.  Offset 118.
     */

    /**
     * Waveform data type.  2 = vector (normal YT).  Offset 122.
     */

    /**
     * General-purpose internal counter.  Offset 126.
     */

    /**
     * Accumulated waveform count.  Offset 134.
     */

    /**
     * Target accumulation count.  Offset 138.
     */

    /**
     * Number of curve objects.  Normally 1.  Offset 142.
     */

    /**
     * Number of FastFrame acquisitions requested.  Offset 146.
     */

    /**
     * Number of FastFrame frames actually acquired.  Offset 150.
     */

    /**
     * FastFrame summary frame type (WFM#002/003 addition at offset 154).
     * 0 = off; 1 = average; 2 = envelope.
     */

    /**
     * Pixel-map display format (display use only).  Offset 156.
     */

    /**
     * Maximum pixel-map value (display use only).  Offset 160.
     */

    /**
     * Explicit dimension 1 (156 bytes in WFM#002, 160 bytes in WFM#003;
     * voltage axis for YT).  Offset 168.
     */

    /**
     * Explicit dimension 2 (156 bytes in WFM#002, 160 bytes in WFM#003).
     * Offset 324 in WFM#002, 328 in WFM#003.
     */

    /**
     * Implicit dimension 1 (132 bytes in WFM#002, 136 bytes in WFM#003;
     * time axis for YT).  Offset 480 in WFM#002, 488 in WFM#003.
     */

    /**
     * Implicit dimension 2 (132 bytes in WFM#002, 136 bytes in WFM#003).
     * Offset 612 in WFM#002, 624 in WFM#003.
     */

    /**
     * Time-base 1 information (12 bytes).  Offset 744 in WFM#002, 760 in WFM#003.
     */

    /**
     * Time-base 2 information (12 bytes).  Offset 756 in WFM#002, 772 in WFM#003.
     */

    /**
     * Update specification for the first waveform frame (24 bytes).
     * Offset 768 in WFM#002, 784 in WFM#003.
     */

    /**
     * Curve object for the first waveform frame (30 bytes).
     * Offset 792 in WFM#002, 808 in WFM#003.
     */

    return WfmHeader;
  })();

  /**
   * 24-byte waveform update specification containing per-frame trigger timing data.
   */

  var WfmUpdateSpec = TektronixWfm002BeWfm.WfmUpdateSpec = (function() {
    function WfmUpdateSpec(_io, _parent, _root) {
      this._io = _io;
      this._parent = _parent;
      this._root = _root;

      this._read();
    }
    WfmUpdateSpec.prototype._read = function() {
      this.realPointOffset = this._io.readU4be();
      this.ttOffset = this._io.readF8be();
      this.fracSec = this._io.readF8be();
      this.gmtSec = this._io.readS4be();
    }

    /**
     * Offset to the first non-interpolated point from the start of valid data.
     */

    /**
     * Sub-sample time fraction from trigger to next data point.
     */

    /**
     * Fractional-second component of trigger timestamp.
     */

    /**
     * Whole-second GMT time of trigger.
     */

    return WfmUpdateSpec;
  })();

  /**
   * Raw curve data bytes, inclusive of pre- and post-charge interpolation data.
   * Valid user-accessible data occupies the byte range
   * [data_start_offset, postcharge_start_offset) within this buffer.
   */
  Object.defineProperty(TektronixWfm002BeWfm.prototype, 'curveBuffer', {
    get: function() {
      if (this._m_curveBuffer !== undefined)
        return this._m_curveBuffer;
      var _pos = this._io.pos;
      this._io.seek(this.staticFileInfo.byteOffsetToCurveBuffer);
      this._m_curveBuffer = this._io.readBytes(this.wfmHeader.curve.endOfCurveBufferOffset);
      this._io.seek(_pos);
      return this._m_curveBuffer;
    }
  });

  /**
   * True when this file uses the WFM#003 layout.
   */
  Object.defineProperty(TektronixWfm002BeWfm.prototype, 'isWfm003', {
    get: function() {
      if (this._m_isWfm003 !== undefined)
        return this._m_isWfm003;
      this._m_isWfm003 = this.staticFileInfo.versionNumber == "WFM#003";
      return this._m_isWfm003;
    }
  });

  /**
   * 78-byte static waveform file information header.
   */

  /**
   * Variable-length waveform header with dimension, time-base, and curve metadata.
   */

  return TektronixWfm002BeWfm;
})();
TektronixWfm002BeWfm_.TektronixWfm002BeWfm = TektronixWfm002BeWfm;
});
