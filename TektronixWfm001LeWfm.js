// This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild

(function (root, factory) {
  if (typeof define === 'function' && define.amd) {
    define(['exports', 'kaitai-struct/KaitaiStream'], factory);
  } else if (typeof exports === 'object' && exports !== null && typeof exports.nodeType !== 'number') {
    factory(exports, require('kaitai-struct/KaitaiStream'));
  } else {
    factory(root.TektronixWfm001LeWfm || (root.TektronixWfm001LeWfm = {}), root.KaitaiStream);
  }
})(typeof self !== 'undefined' ? self : this, function (TektronixWfm001LeWfm_, KaitaiStream) {
/**
 * Tektronix WFM binary waveform format, version WFM#001, little-endian variant.
 * 
 * Applies to: TDS6000/B/C, TDS/CSA7000/B, and similar instruments with Intel
 * (PC-based) acquisition systems that produce WFM#001 files.
 * 
 * For WFM#002 files (TDS5000B), use tek_wfm_002_le/be.  For WFM#003 files
 * (DPO7000, DPO70000, DSA70000), use tek_wfm_002_le/be with caution — the
 * critical calibration fields (dim_scale, dim_offset) are identical in layout
 * but point_density in user-view sections is f8 instead of u4, shifting fields
 * that follow it.
 * 
 * Endianness detection (performed by caller before selecting this parser)::
 * 
 *   byte_order at offset 0 is 0x0F0F for little-endian (Intel);
 *   0xF0F0 for big-endian (PPC) — use tek_wfm_001_be in that case.
 * 
 * Version detection::
 * 
 *   version_number at offset 2 is "WFM#001" for this parser.
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
 * Valid user data starts at curve.data_start_offset bytes into the buffer.
 * 
 * Reference: Tektronix "Reference Waveform File Format" (001-1378-03).
 * 
 * Sources used for this KSY binary format:
 * `docs/vendors/tektronix/tek_docs.pdf` and the shared Tektronix adapter logic
 * in this repository.
 * 
 * Tested file formats: no checked-in `WFM#001` little-endian fixture currently
 * exercises this exact schema; current Tek regression tests cover synthetic
 * `WFM#002`, `WFM#003`, and legacy `LLWFM` files, so this variant is
 * document-backed rather than fixture-backed today.
 * 
 * Oscilloscope models this format may apply to: Tektronix `TDS6000` / `B` /
 * `C`, `TDS/CSA7000` / `B`, and similar Intel / PC-based instruments that
 * write little-endian `WFM#001` files.
 */

var TektronixWfm001LeWfm = (function() {
  TektronixWfm001LeWfm.BaseTypeEnum = Object.freeze({
    BASE_TIME: 0,
    BASE_SPECTRAL_MAG: 1,
    BASE_SPECTRAL_PHASE: 2,
    BASE_INVALID: 3,

    0: "BASE_TIME",
    1: "BASE_SPECTRAL_MAG",
    2: "BASE_SPECTRAL_PHASE",
    3: "BASE_INVALID",
  });

  TektronixWfm001LeWfm.ChecksumTypeEnum = Object.freeze({
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

  TektronixWfm001LeWfm.DataTypeEnum = Object.freeze({
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

  TektronixWfm001LeWfm.ExplicitFormatEnum = Object.freeze({
    EXPLICIT_INT16: 0,
    EXPLICIT_INT32: 1,
    EXPLICIT_UINT32: 2,
    EXPLICIT_UINT64: 3,
    EXPLICIT_FP32: 4,
    EXPLICIT_FP64: 5,
    EXPLICIT_INVALID_FORMAT: 6,

    0: "EXPLICIT_INT16",
    1: "EXPLICIT_INT32",
    2: "EXPLICIT_UINT32",
    3: "EXPLICIT_UINT64",
    4: "EXPLICIT_FP32",
    5: "EXPLICIT_FP64",
    6: "EXPLICIT_INVALID_FORMAT",
  });

  TektronixWfm001LeWfm.ExplicitStorageEnum = Object.freeze({
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

  TektronixWfm001LeWfm.PixMapFormatEnum = Object.freeze({
    DSY_FORMAT_INVALID: 0,
    DSY_FORMAT_YT: 1,
    DSY_FORMAT_XY: 2,
    DSY_FORMAT_XYZ: 3,

    0: "DSY_FORMAT_INVALID",
    1: "DSY_FORMAT_YT",
    2: "DSY_FORMAT_XY",
    3: "DSY_FORMAT_XYZ",
  });

  TektronixWfm001LeWfm.SetTypeEnum = Object.freeze({
    SINGLE_WAVEFORM: 0,
    FAST_FRAME: 1,

    0: "SINGLE_WAVEFORM",
    1: "FAST_FRAME",
  });

  TektronixWfm001LeWfm.SweepEnum = Object.freeze({
    SWEEP_ROLL: 0,
    SWEEP_SAMPLE: 1,
    SWEEP_ET: 2,
    SWEEP_INVALID: 3,

    0: "SWEEP_ROLL",
    1: "SWEEP_SAMPLE",
    2: "SWEEP_ET",
    3: "SWEEP_INVALID",
  });

  function TektronixWfm001LeWfm(_io, _parent, _root) {
    this._io = _io;
    this._parent = _parent;
    this._root = _root || this;

    this._read();
  }
  TektronixWfm001LeWfm.prototype._read = function() {
    this.staticFileInfo = new StaticFileInfo(this._io, this, this._root);
    this.wfmHeader = new WfmHeader(this._io, this, this._root);
  }

  /**
   * Explicit dimension: 100-byte description block followed by a 56-byte user-view
   * block, totalling 156 bytes.
   * 
   * For YT waveforms, explicit dimension 1 defines the voltage (Y) axis:
   *   volts[i] = dim_scale * adc[i] + dim_offset
   * 
   * where adc[i] is the signed integer or float value from the curve buffer.
   */

  var ExpDim = TektronixWfm001LeWfm.ExpDim = (function() {
    function ExpDim(_io, _parent, _root) {
      this._io = _io;
      this._parent = _parent;
      this._root = _root;

      this._read();
    }
    ExpDim.prototype._read = function() {
      this.dimScale = this._io.readF8le();
      this.dimOffset = this._io.readF8le();
      this.dimSize = this._io.readU4le();
      this.units = this._io.readBytes(20);
      this.dimExtentMin = this._io.readF8le();
      this.dimExtentMax = this._io.readF8le();
      this.dimResolution = this._io.readF8le();
      this.dimRefPoint = this._io.readF8le();
      this.format = this._io.readS4le();
      this.storageType = this._io.readS4le();
      this.nValue = this._io.readBytes(4);
      this.overRange = this._io.readBytes(4);
      this.underRange = this._io.readBytes(4);
      this.highRange = this._io.readBytes(4);
      this.lowRange = this._io.readBytes(4);
      this.userScale = this._io.readF8le();
      this.userUnits = this._io.readBytes(20);
      this.userOffset = this._io.readF8le();
      this.pointDensity = this._io.readU4le();
      this.hRef = this._io.readF8le();
      this.trigDelay = this._io.readF8le();
    }

    /**
     * Scale factor in physical units per ADC count (e.g. volts per LSB).
     * For float curve formats, dim_scale is 1.0 and the curve values are
     * already in physical units.
     */

    /**
     * Offset in physical units.  The ground-level distance from the dimension
     * zero to the true zero.
     * volts[i] = dim_scale * adc[i] + dim_offset.
     */

    /**
     * Storage element size for the explicit dimension.  For integer formats this
     * is the ADC full-scale count (e.g. 252 for 8-bit, 65532 for 16-bit).
     * For float formats this is 1.
     */

    /**
     * Null-terminated ASCII string naming the physical unit (e.g. "Volts").
     */

    /**
     * Minimum attainable value for this dimension (not available for user use).
     */

    /**
     * Maximum attainable value for this dimension (not available for user use).
     */

    /**
     * Smallest resolvable increment given the digitizer and acquisition mode —
     * the physical value of one digitizing level (DL).
     */

    /**
     * Ground-level reference value for the explicit (voltage) dimension.
     */

    /**
     * Data format (code type) of the values stored in the curve buffer.
     */

    /**
     * Storage layout of the curve buffer values.
     */

    /**
     * Raw 4-byte representation of the NULL (unacquired) data value.
     * Interpretation depends on format: s2, s4, or f4.
     */

    /**
     * Raw 4-byte value indicating an over-range (clipped high) sample.
     */

    /**
     * Raw 4-byte value indicating an under-range (clipped low) sample.
     */

    /**
     * Raw 4-byte largest signed value possible in this data (excluding special codes).
     */

    /**
     * Raw 4-byte smallest value possible in this data (excluding special codes).
     */

    /**
     * User display scale expressed in physical units per screen division.
     */

    /**
     * Null-terminated user display unit string (e.g. "Volts per Div").
     */

    /**
     * User display position offset in screen divisions.
     */

    /**
     * Screen-to-data ratio for the explicit dimension.  Always 1 for explicit
     * dimensions (each data point maps to one screen point).
     * Note: this field is f8 in WFM#003 files (DPO7000, DPO70000, DSA70000).
     */

    /**
     * Trigger horizontal position as a percentage of the waveform record (0–100%).
     */

    /**
     * Time delay in seconds from the trigger event to the HRef screen position.
     * Positive for pre-trigger; negative for post-trigger.
     */

    return ExpDim;
  })();

  /**
   * Implicit dimension: 76-byte description block followed by a 56-byte user-view
   * block, totalling 132 bytes.
   * 
   * For YT waveforms, implicit dimension 1 defines the time (X) axis.
   * The real time value at sample index i (0-based from start of curve buffer) is:
   *   t[i] = dim_offset + i * dim_scale
   * 
   * The first user-accessible sample is at:
   *   i_start = curve.data_start_offset / num_bytes_per_point
   */

  var ImpDim = TektronixWfm001LeWfm.ImpDim = (function() {
    function ImpDim(_io, _parent, _root) {
      this._io = _io;
      this._parent = _parent;
      this._root = _root;

      this._read();
    }
    ImpDim.prototype._read = function() {
      this.dimScale = this._io.readF8le();
      this.dimOffset = this._io.readF8le();
      this.dimSize = this._io.readU4le();
      this.units = this._io.readBytes(20);
      this.dimExtentMin = this._io.readF8le();
      this.dimExtentMax = this._io.readF8le();
      this.dimResolution = this._io.readF8le();
      this.dimRefPoint = this._io.readF8le();
      this.spacing = this._io.readU4le();
      this.userScale = this._io.readF8le();
      this.userUnits = this._io.readBytes(20);
      this.userOffset = this._io.readF8le();
      this.pointDensity = this._io.readU4le();
      this.hRef = this._io.readF8le();
      this.trigDelay = this._io.readF8le();
    }

    /**
     * Sample interval in seconds (time between consecutive samples).
     */

    /**
     * Trigger position: time in seconds of sample index 0 (the start of the
     * curve buffer, including pre-charge data) relative to the trigger event.
     * Typically negative because pre-charge data precedes the trigger.
     */

    /**
     * Record length in data points, including pre-charge and post-charge data.
     * Pre-charge and post-charge are normally 16 points each (used for display
     * interpolation); not all points are user-accessible.
     */

    /**
     * Null-terminated ASCII string naming the time unit (e.g. "s").
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
     * Real-time point spacing: integer count of the difference in points between
     * consecutive acquired points.  1 for non-interpolated waveforms.
     */

    /**
     * User display time scale.
     */

    /**
     * Null-terminated user display time unit string.
     */

    /**
     * Value of the horizontal center pixel column relative to the trigger,
     * in absolute horizontal user units (typically seconds).
     */

    /**
     * Number of data points compressed into a single pixel column at zoom=1.
     * Note: this field is f8 in WFM#003 files (DPO7000, DPO70000, DSA70000).
     */

    /**
     * Trigger horizontal position as a percentage of the waveform (0–100%).
     */

    /**
     * Time delay in seconds from the trigger to the HRef screen position.
     */

    return ImpDim;
  })();

  /**
   * 78-byte block of static waveform file information at the very start of the file.
   * This block is common to all WFM format versions and both endiannesses.
   */

  var StaticFileInfo = TektronixWfm001LeWfm.StaticFileInfo = (function() {
    function StaticFileInfo(_io, _parent, _root) {
      this._io = _io;
      this._parent = _parent;
      this._root = _root;

      this._read();
    }
    StaticFileInfo.prototype._read = function() {
      this.byteOrder = this._io.readU2le();
      this.versionNumber = this._io.readBytes(8);
      this.numDigitsByteCount = this._io.readU1();
      this.numBytesToEof = this._io.readS4le();
      this.numBytesPerPoint = this._io.readU1();
      this.byteOffsetToCurveBuffer = this._io.readS4le();
      this.horizZoomScaleFactor = this._io.readS4le();
      this.horizZoomPosition = this._io.readF4le();
      this.vertZoomScaleFactor = this._io.readF8le();
      this.vertZoomPosition = this._io.readF4le();
      this.waveformLabel = this._io.readBytes(32);
      this.nFastFramesMinus1 = this._io.readU4le();
      this.wfmHeaderSize = this._io.readU2le();
    }

    /**
     * Byte-order marker.  0x0F0F = little-endian (Intel / PC); 0xF0F0 = big-endian
     * (PPC / older TDS instruments).  Select parser variant before parsing.  Offset 0.
     */

    /**
     * Version identification string, null-padded to 8 bytes.
     * "WFM#001" for this parser.  Offset 2.
     */

    /**
     * Number of decimal digits in the byte-count field (0–9).  Offset 10.
     */

    /**
     * Number of bytes from this field to the end of file.  Offset 11.
     */

    /**
     * Bytes per curve data point — allows quick determination of total data size.
     * Typical values: 2 (INT16), 4 (INT32 or FP32), 8 (FP64).  Offset 15.
     */

    /**
     * Absolute byte offset from the start of file to the start of the curve buffer.
     * Offset 16.
     */

    /**
     * Horizontal zoom scale factor (display use only; not for data conversion).  Offset 20.
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
     * Number of FastFrame frames minus 1.  0 for single-waveform files.
     * N > 0 means there are N additional WfmUpdateSpec and WfmCurveObject
     * records immediately after the first curve object in the header.  Offset 72.
     */

    /**
     * Size in bytes of the waveform header that immediately follows this field.
     * Offset 76.
     */

    return StaticFileInfo;
  })();

  /**
   * 12-byte time-base information block describing how waveform data was acquired
   * and the meaning of the acquired points.
   */

  var TimeBaseInfo = TektronixWfm001LeWfm.TimeBaseInfo = (function() {
    function TimeBaseInfo(_io, _parent, _root) {
      this._io = _io;
      this._parent = _parent;
      this._root = _root;

      this._read();
    }
    TimeBaseInfo.prototype._read = function() {
      this.realPointSpacing = this._io.readU4le();
      this.sweep = this._io.readS4le();
      this.typeOfBase = this._io.readS4le();
    }

    /**
     * Integer count of the difference in points between consecutive acquired
     * points.  1 for waveforms not created by interpolation.
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
   * 30-byte curve object.  Contains byte offsets into the curve buffer that
   * delimit pre-charge, valid user data, post-charge, and roll-mode regions.
   * 
   * To extract valid waveform samples from the curve buffer:
   *   first_byte = data_start_offset
   *   last_byte  = postcharge_start_offset   (exclusive)
   * 
   * Convert byte offsets to sample indices by dividing by
   * _root.static_file_info.num_bytes_per_point.
   */

  var WfmCurveObject = TektronixWfm001LeWfm.WfmCurveObject = (function() {
    function WfmCurveObject(_io, _parent, _root) {
      this._io = _io;
      this._parent = _parent;
      this._root = _root;

      this._read();
    }
    WfmCurveObject.prototype._read = function() {
      this.stateFlags = this._io.readU4le();
      this.checksumType = this._io.readS4le();
      this.checksum = this._io.readS2le();
      this.prechargeStartOffset = this._io.readU4le();
      this.dataStartOffset = this._io.readU4le();
      this.postchargeStartOffset = this._io.readU4le();
      this.postchargeStopOffset = this._io.readU4le();
      this.endOfCurveBufferOffset = this._io.readU4le();
    }

    /**
     * Sample index (0-based from start of curve buffer) of the first
     * user-accessible data point.
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
     * Internal curve validity flags (flagOver, flagUnder, flagValid, flagNulls —
     * 2 bits each).  Not for user use.
     */

    /**
     * Algorithm used to calculate the curve checksum.
     */

    /**
     * Curve checksum value (currently not implemented; file checksum is used).
     */

    /**
     * Byte offset from the start of the curve buffer to the first pre-charge
     * data point.  Pre-charge data is intended for interpolation only.
     */

    /**
     * Byte offset from the start of the curve buffer to the first user-accessible
     * waveform data point.
     */

    /**
     * Byte offset from the start of the curve buffer to the first post-charge
     * data point.  Post-charge data is for interpolation only.
     */

    /**
     * Byte offset from the start of the curve buffer to just past the last valid
     * waveform point (inclusive of post-charge data).
     */

    /**
     * Byte offset to the end of the curve buffer allocation.  In non-roll-mode
     * acquisitions this equals postcharge_stop_offset.  In Roll mode it may be
     * larger to accommodate the roll buffer.
     */

    return WfmCurveObject;
  })();

  /**
   * Waveform header block containing reference file data, explicit and implicit
   * dimension descriptors, time-base information, and the first waveform update
   * specification and curve object.  Begins at byte 78 of the file.
   */

  var WfmHeader = TektronixWfm001LeWfm.WfmHeader = (function() {
    function WfmHeader(_io, _parent, _root) {
      this._io = _io;
      this._parent = _parent;
      this._root = _root;

      this._read();
    }
    WfmHeader.prototype._read = function() {
      this.setType = this._io.readS4le();
      this.wfmCnt = this._io.readU4le();
      this.acqCounter = this._io.readU8le();
      this.transactionCounter = this._io.readU8le();
      this.slotId = this._io.readS4le();
      this.isStaticFlag = this._io.readS4le();
      this.wfmUpdateSpecCount = this._io.readU4le();
      this.impDimRefCount = this._io.readU4le();
      this.expDimRefCount = this._io.readU4le();
      this.dataType = this._io.readS4le();
      this.genPurposeCounter = this._io.readU8le();
      this.accumWfmCount = this._io.readU4le();
      this.targetAccumCount = this._io.readU4le();
      this.curveRefCount = this._io.readU4le();
      this.numRequestedFastFrames = this._io.readU4le();
      this.numAcquiredFastFrames = this._io.readU4le();
      this.pixMapDisplayFormat = this._io.readS4le();
      this.pixMapMaxValue = this._io.readU8le();
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
     * Waveform set type.  0 = single waveform set; 1 = FastFrame set.  Offset 78.
     */

    /**
     * Number of waveforms in the set.  For FastFrame this is a special case
     * described by the num_frames fields below.  Offset 82.
     */

    /**
     * Internal acquisition counter used to match waveforms from the same
     * acquisition.  Not for user use.  Offset 86.
     */

    /**
     * Internal transaction timestamp.  Not for user use.  Offset 94.
     */

    /**
     * Instrument data-slot enumeration.  Not for user use.  Offset 102.
     */

    /**
     * Non-zero if this is a static (reference) waveform; 0 if live (channel/math).
     * Not for user use.  Offset 106.
     */

    /**
     * Number of waveform update specifications in this set.  FastFrame waveforms
     * have one per frame.  Offset 110.
     */

    /**
     * Number of implicit dimension references.  1 for vector YT/XY waveforms;
     * 0 for scalars.  Offset 114.
     */

    /**
     * Number of explicit dimension references.  1 for YT; 2 for XY/XYZ.
     * Pixel maps have two implicit dimensions.  Offset 118.
     */

    /**
     * Waveform data type.  Normal YT waveforms are WFMDATA_VECTOR (2).
     * Offset 122.
     */

    /**
     * General-purpose internal counter.  Not for user use.  Offset 126.
     */

    /**
     * Number of waveforms accumulated by the Math system so far.
     * Updated per acquisition.  Offset 134.
     */

    /**
     * Number of acquisitions requested for accumulation.  Offset 138.
     */

    /**
     * Number of curve objects for this waveform set.  Normally 1.  Offset 142.
     */

    /**
     * Number of FastFrame acquisitions requested.  Offset 146.
     */

    /**
     * Number of FastFrame frames actually acquired (≤ num_requested_fast_frames).
     * Offset 150.
     */

    /**
     * Pixel-map display format (display use only).  Offset 154.
     */

    /**
     * Maximum pixel-map value (display use only).  Offset 158.
     */

    /**
     * Explicit dimension 1 descriptor + user-view data (156 bytes).
     * For YT waveforms this defines the voltage axis.  Offset 166.
     */

    /**
     * Explicit dimension 2 (156 bytes).  Used for XY and XYZ waveforms.  Offset 322.
     */

    /**
     * Implicit dimension 1 descriptor + user-view data (132 bytes).
     * For YT waveforms this defines the time axis.  Offset 478.
     */

    /**
     * Implicit dimension 2 (132 bytes).  Used for XY and XYZ waveforms.  Offset 610.
     */

    /**
     * Time-base 1 acquisition information (12 bytes).  Offset 742.
     */

    /**
     * Time-base 2 acquisition information (12 bytes).  Offset 754.
     */

    /**
     * Update specification for the first (or only) waveform frame (24 bytes).
     * Contains trigger timing data.  Offset 766.
     */

    /**
     * Curve object for the first (or only) waveform frame (30 bytes).
     * Contains byte offsets into the curve buffer that delimit valid data.
     * Offset 790.
     */

    return WfmHeader;
  })();

  /**
   * 24-byte waveform update specification.  For FastFrame waveform sets there is
   * one of these per frame (the first is embedded in wfm_header; N–1 additional
   * records follow the first curve object).
   */

  var WfmUpdateSpec = TektronixWfm001LeWfm.WfmUpdateSpec = (function() {
    function WfmUpdateSpec(_io, _parent, _root) {
      this._io = _io;
      this._parent = _parent;
      this._root = _root;

      this._read();
    }
    WfmUpdateSpec.prototype._read = function() {
      this.realPointOffset = this._io.readU4le();
      this.ttOffset = this._io.readF8le();
      this.fracSec = this._io.readF8le();
      this.gmtSec = this._io.readS4le();
    }

    /**
     * Integer offset from the beginning of valid data (preChargeStart) to the
     * first acquired, non-interpolated point in the record.
     */

    /**
     * Time from the trigger occurrence to the next data point in the record.
     * Represents the sub-sample fraction of the sample interval.
     */

    /**
     * Fractional seconds within the current second at which the trigger occurred.
     * Used with gmt_sec to reconstruct the absolute trigger timestamp.
     */

    /**
     * Whole-second GMT time of the trigger event.
     */

    return WfmUpdateSpec;
  })();

  /**
   * Raw curve data bytes, inclusive of pre- and post-charge interpolation data.
   * For non-roll-mode waveforms, end_of_curve_buffer_offset equals
   * postcharge_stop_offset.  Valid user-accessible data occupies the byte range
   * [data_start_offset, postcharge_start_offset) within this buffer.
   */
  Object.defineProperty(TektronixWfm001LeWfm.prototype, 'curveBuffer', {
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
   * 78-byte static waveform file information header.
   */

  /**
   * Variable-length waveform header with dimension, time-base, and curve metadata.
   */

  return TektronixWfm001LeWfm;
})();
TektronixWfm001LeWfm_.TektronixWfm001LeWfm = TektronixWfm001LeWfm;
});
