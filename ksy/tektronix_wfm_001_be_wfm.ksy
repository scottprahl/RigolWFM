meta:
  id: tektronix_wfm_001_be_wfm
  title: Tektronix WFM 001 File Format (Big-Endian)
  file-extension: wfm
  endian: be

doc: |
  Tektronix WFM binary waveform format, version WFM#001, big-endian variant.

  Applies to: TDS6000/B/C, TDS/CSA7000/B, and similar instruments with Intel
  (PC-based) acquisition systems that produce WFM#001 files.

  Endianness detection (performed by caller before selecting this parser)::

    byte_order at offset 0 is 0x0F0F for little-endian (Intel);
    0xF0F0 for big-endian (PPC) — use tek_wfm_001_le in that case.

  Version detection::

    version_number at offset 2 is "WFM#001" for this parser.

  Voltage reconstruction (explicit dimension 1)::

    volts[i] = exp_dim1.dim_scale * adc[i] + exp_dim1.dim_offset

  Time axis (implicit dimension 1)::

    t[i] = imp_dim1.dim_offset + i * imp_dim1.dim_scale

  where i = 0 corresponds to the first sample in the curve buffer.
  Valid user data starts at curve.data_start_offset bytes into the buffer.

  Sources used for this KSY binary format: Tektronix "Reference Waveform File Format"
  (001-1378-03).

  Tested file formats: no checked-in `WFM#001` big-endian fixture currently
  exercises this exact schema; current Tek regression tests cover synthetic
  `WFM#002`, `WFM#003`, and legacy `LLWFM` files, so this variant is
  document-backed rather than fixture-backed today.

  Oscilloscope models this format may apply to: Tektronix `TDS6000` / `B` /
  `C`, `TDS/CSA7000` / `B`, and similar PPC-based instruments that write
  big-endian `WFM#001` files.

seq:
  - id: static_file_info
    type: static_file_info
    doc: 78-byte static waveform file information header.

  - id: wfm_header
    type: wfm_header
    doc: Variable-length waveform header with dimension, time-base, and curve metadata.

instances:
  curve_buffer:
    pos: static_file_info.byte_offset_to_curve_buffer
    size: wfm_header.curve.end_of_curve_buffer_offset
    doc: |
      Raw curve data bytes, inclusive of pre- and post-charge interpolation data.
      For non-roll-mode waveforms, end_of_curve_buffer_offset equals
      postcharge_stop_offset.  Valid user-accessible data occupies the byte range
      [data_start_offset, postcharge_start_offset) within this buffer.

types:
  static_file_info:
    doc: |
      78-byte block of static waveform file information at the very start of the file.
      This block is common to all WFM format versions and both endiannesses.
    seq:
      - id: byte_order
        type: u2
        doc: |
          Byte-order marker.  0x0F0F = little-endian (Intel / PC); 0xF0F0 = big-endian
          (PPC / older TDS instruments).  Select parser variant before parsing.  Offset 0.
      - id: version_number
        size: 8
        doc: |
          Version identification string, null-padded to 8 bytes.
          "WFM#001" for this parser.  Offset 2.
      - id: num_digits_byte_count
        type: u1
        doc: Number of decimal digits in the byte-count field (0–9).  Offset 10.
      - id: num_bytes_to_eof
        type: s4
        doc: Number of bytes from this field to the end of file.  Offset 11.
      - id: num_bytes_per_point
        type: u1
        doc: |
          Bytes per curve data point — allows quick determination of total data size.
          Typical values: 2 (INT16), 4 (INT32 or FP32), 8 (FP64).  Offset 15.
      - id: byte_offset_to_curve_buffer
        type: s4
        doc: |
          Absolute byte offset from the start of file to the start of the curve buffer.
          Offset 16.
      - id: horiz_zoom_scale_factor
        type: s4
        doc: Horizontal zoom scale factor (display use only; not for data conversion).  Offset 20.
      - id: horiz_zoom_position
        type: f4
        doc: Horizontal zoom position (display use only).  Offset 24.
      - id: vert_zoom_scale_factor
        type: f8
        doc: Vertical zoom scale factor (display use only).  Offset 28.
      - id: vert_zoom_position
        type: f4
        doc: Vertical zoom position (display use only).  Offset 36.
      - id: waveform_label
        size: 32
        doc: User-defined null-padded ASCII label for this waveform.  Offset 40.
      - id: n_fast_frames_minus_1
        type: u4
        doc: |
          Number of FastFrame frames minus 1.  0 for single-waveform files.
          N > 0 means there are N additional WfmUpdateSpec and WfmCurveObject
          records immediately after the first curve object in the header.  Offset 72.
      - id: wfm_header_size
        type: u2
        doc: |
          Size in bytes of the waveform header that immediately follows this field.
          Offset 76.

  wfm_header:
    doc: |
      Waveform header block containing reference file data, explicit and implicit
      dimension descriptors, time-base information, and the first waveform update
      specification and curve object.  Begins at byte 78 of the file.
    seq:
      - id: set_type
        type: s4
        enum: set_type_enum
        doc: |
          Waveform set type.  0 = single waveform set; 1 = FastFrame set.  Offset 78.
      - id: wfm_cnt
        type: u4
        doc: |
          Number of waveforms in the set.  For FastFrame this is a special case
          described by the num_frames fields below.  Offset 82.
      - id: acq_counter
        type: u8
        doc: |
          Internal acquisition counter used to match waveforms from the same
          acquisition.  Not for user use.  Offset 86.
      - id: transaction_counter
        type: u8
        doc: Internal transaction timestamp.  Not for user use.  Offset 94.
      - id: slot_id
        type: s4
        doc: Instrument data-slot enumeration.  Not for user use.  Offset 102.
      - id: is_static_flag
        type: s4
        doc: |
          Non-zero if this is a static (reference) waveform; 0 if live (channel/math).
          Not for user use.  Offset 106.
      - id: wfm_update_spec_count
        type: u4
        doc: |
          Number of waveform update specifications in this set.  FastFrame waveforms
          have one per frame.  Offset 110.
      - id: imp_dim_ref_count
        type: u4
        doc: |
          Number of implicit dimension references.  1 for vector YT/XY waveforms;
          0 for scalars.  Offset 114.
      - id: exp_dim_ref_count
        type: u4
        doc: |
          Number of explicit dimension references.  1 for YT; 2 for XY/XYZ.
          Pixel maps have two implicit dimensions.  Offset 118.
      - id: data_type
        type: s4
        enum: data_type_enum
        doc: |
          Waveform data type.  Normal YT waveforms are WFMDATA_VECTOR (2).
          Offset 122.
      - id: gen_purpose_counter
        type: u8
        doc: General-purpose internal counter.  Not for user use.  Offset 126.
      - id: accum_wfm_count
        type: u4
        doc: |
          Number of waveforms accumulated by the Math system so far.
          Updated per acquisition.  Offset 134.
      - id: target_accum_count
        type: u4
        doc: Number of acquisitions requested for accumulation.  Offset 138.
      - id: curve_ref_count
        type: u4
        doc: Number of curve objects for this waveform set.  Normally 1.  Offset 142.
      - id: num_requested_fast_frames
        type: u4
        doc: Number of FastFrame acquisitions requested.  Offset 146.
      - id: num_acquired_fast_frames
        type: u4
        doc: |
          Number of FastFrame frames actually acquired (≤ num_requested_fast_frames).
          Offset 150.
      - id: pix_map_display_format
        type: s4
        enum: pix_map_format_enum
        doc: Pixel-map display format (display use only).  Offset 154.
      - id: pix_map_max_value
        type: u8
        doc: Maximum pixel-map value (display use only).  Offset 158.
      - id: exp_dim1
        type: exp_dim
        doc: |
          Explicit dimension 1 descriptor + user-view data (156 bytes).
          For YT waveforms this defines the voltage axis.  Offset 166.
      - id: exp_dim2
        type: exp_dim
        doc: Explicit dimension 2 (156 bytes).  Used for XY and XYZ waveforms.  Offset 322.
      - id: imp_dim1
        type: imp_dim
        doc: |
          Implicit dimension 1 descriptor + user-view data (132 bytes).
          For YT waveforms this defines the time axis.  Offset 478.
      - id: imp_dim2
        type: imp_dim
        doc: Implicit dimension 2 (132 bytes).  Used for XY and XYZ waveforms.  Offset 610.
      - id: time_base1
        type: time_base_info
        doc: Time-base 1 acquisition information (12 bytes).  Offset 742.
      - id: time_base2
        type: time_base_info
        doc: Time-base 2 acquisition information (12 bytes).  Offset 754.
      - id: update_spec
        type: wfm_update_spec
        doc: |
          Update specification for the first (or only) waveform frame (24 bytes).
          Contains trigger timing data.  Offset 766.
      - id: curve
        type: wfm_curve_object
        doc: |
          Curve object for the first (or only) waveform frame (30 bytes).
          Contains byte offsets into the curve buffer that delimit valid data.
          Offset 790.

  exp_dim:
    doc: |
      Explicit dimension: 100-byte description block followed by a 56-byte user-view
      block, totalling 156 bytes.

      For YT waveforms, explicit dimension 1 defines the voltage (Y) axis:
        volts[i] = dim_scale * adc[i] + dim_offset

      where adc[i] is the signed integer or float value from the curve buffer.
    seq:
      - id: dim_scale
        type: f8
        doc: |
          Scale factor in physical units per ADC count (e.g. volts per LSB).
          For float curve formats, dim_scale is 1.0 and the curve values are
          already in physical units.
      - id: dim_offset
        type: f8
        doc: |
          Offset in physical units.  The ground-level distance from the dimension
          zero to the true zero.
          volts[i] = dim_scale * adc[i] + dim_offset.
      - id: dim_size
        type: u4
        doc: |
          Storage element size for the explicit dimension.  For integer formats this
          is the ADC full-scale count (e.g. 252 for 8-bit, 65532 for 16-bit).
          For float formats this is 1.
      - id: units
        size: 20
        doc: Null-terminated ASCII string naming the physical unit (e.g. "Volts").
      - id: dim_extent_min
        type: f8
        doc: Minimum attainable value for this dimension (not available for user use).
      - id: dim_extent_max
        type: f8
        doc: Maximum attainable value for this dimension (not available for user use).
      - id: dim_resolution
        type: f8
        doc: |
          Smallest resolvable increment given the digitizer and acquisition mode —
          the physical value of one digitizing level (DL).
      - id: dim_ref_point
        type: f8
        doc: Ground-level reference value for the explicit (voltage) dimension.
      - id: format
        type: s4
        enum: explicit_format_enum
        doc: Data format (code type) of the values stored in the curve buffer.
      - id: storage_type
        type: s4
        enum: explicit_storage_enum
        doc: Storage layout of the curve buffer values.
      - id: n_value
        size: 4
        doc: |
          Raw 4-byte representation of the NULL (unacquired) data value.
          Interpretation depends on format: s2, s4, or f4.
      - id: over_range
        size: 4
        doc: Raw 4-byte value indicating an over-range (clipped high) sample.
      - id: under_range
        size: 4
        doc: Raw 4-byte value indicating an under-range (clipped low) sample.
      - id: high_range
        size: 4
        doc: Raw 4-byte largest signed value possible in this data (excluding special codes).
      - id: low_range
        size: 4
        doc: Raw 4-byte smallest value possible in this data (excluding special codes).
      # User-view data (56 bytes)
      - id: user_scale
        type: f8
        doc: User display scale expressed in physical units per screen division.
      - id: user_units
        size: 20
        doc: Null-terminated user display unit string (e.g. "Volts per Div").
      - id: user_offset
        type: f8
        doc: User display position offset in screen divisions.
      - id: point_density
        type: u4
        doc: |
          Screen-to-data ratio for the explicit dimension.  Always 1 for explicit
          dimensions (each data point maps to one screen point).
          Note: this field is f8 in WFM#003 files (DPO7000, DPO70000, DSA70000).
      - id: h_ref
        type: f8
        doc: |
          Trigger horizontal position as a percentage of the waveform record (0–100%).
      - id: trig_delay
        type: f8
        doc: |
          Time delay in seconds from the trigger event to the HRef screen position.
          Positive for pre-trigger; negative for post-trigger.

  imp_dim:
    doc: |
      Implicit dimension: 76-byte description block followed by a 56-byte user-view
      block, totalling 132 bytes.

      For YT waveforms, implicit dimension 1 defines the time (X) axis.
      The real time value at sample index i (0-based from start of curve buffer) is:
        t[i] = dim_offset + i * dim_scale

      The first user-accessible sample is at:
        i_start = curve.data_start_offset / num_bytes_per_point
    seq:
      - id: dim_scale
        type: f8
        doc: Sample interval in seconds (time between consecutive samples).
      - id: dim_offset
        type: f8
        doc: |
          Trigger position: time in seconds of sample index 0 (the start of the
          curve buffer, including pre-charge data) relative to the trigger event.
          Typically negative because pre-charge data precedes the trigger.
      - id: dim_size
        type: u4
        doc: |
          Record length in data points, including pre-charge and post-charge data.
          Pre-charge and post-charge are normally 16 points each (used for display
          interpolation); not all points are user-accessible.
      - id: units
        size: 20
        doc: Null-terminated ASCII string naming the time unit (e.g. "s").
      - id: dim_extent_min
        type: f8
        doc: Not available for user use.
      - id: dim_extent_max
        type: f8
        doc: Not available for user use.
      - id: dim_resolution
        type: f8
        doc: Time axis resolution.
      - id: dim_ref_point
        type: f8
        doc: Horizontal reference point of the time base.
      - id: spacing
        type: u4
        doc: |
          Real-time point spacing: integer count of the difference in points between
          consecutive acquired points.  1 for non-interpolated waveforms.
      # User-view data (56 bytes)
      - id: user_scale
        type: f8
        doc: User display time scale.
      - id: user_units
        size: 20
        doc: Null-terminated user display time unit string.
      - id: user_offset
        type: f8
        doc: |
          Value of the horizontal center pixel column relative to the trigger,
          in absolute horizontal user units (typically seconds).
      - id: point_density
        type: u4
        doc: |
          Number of data points compressed into a single pixel column at zoom=1.
          Note: this field is f8 in WFM#003 files (DPO7000, DPO70000, DSA70000).
      - id: h_ref
        type: f8
        doc: Trigger horizontal position as a percentage of the waveform (0–100%).
      - id: trig_delay
        type: f8
        doc: |
          Time delay in seconds from the trigger to the HRef screen position.

  time_base_info:
    doc: |
      12-byte time-base information block describing how waveform data was acquired
      and the meaning of the acquired points.
    seq:
      - id: real_point_spacing
        type: u4
        doc: |
          Integer count of the difference in points between consecutive acquired
          points.  1 for waveforms not created by interpolation.
      - id: sweep
        type: s4
        enum: sweep_enum
        doc: "Sweep/acquisition mode."
      - id: type_of_base
        type: s4
        enum: base_type_enum
        doc: "Domain of the horizontal axis."

  wfm_update_spec:
    doc: |
      24-byte waveform update specification.  For FastFrame waveform sets there is
      one of these per frame (the first is embedded in wfm_header; N–1 additional
      records follow the first curve object).
    seq:
      - id: real_point_offset
        type: u4
        doc: |
          Integer offset from the beginning of valid data (preChargeStart) to the
          first acquired, non-interpolated point in the record.
      - id: tt_offset
        type: f8
        doc: |
          Time from the trigger occurrence to the next data point in the record.
          Represents the sub-sample fraction of the sample interval.
      - id: frac_sec
        type: f8
        doc: |
          Fractional seconds within the current second at which the trigger occurred.
          Used with gmt_sec to reconstruct the absolute trigger timestamp.
      - id: gmt_sec
        type: s4
        doc: Whole-second GMT time of the trigger event.

  wfm_curve_object:
    doc: |
      30-byte curve object.  Contains byte offsets into the curve buffer that
      delimit pre-charge, valid user data, post-charge, and roll-mode regions.

      To extract valid waveform samples from the curve buffer:
        first_byte = data_start_offset
        last_byte  = postcharge_start_offset   (exclusive)

      Convert byte offsets to sample indices by dividing by
      _root.static_file_info.num_bytes_per_point.
    seq:
      - id: state_flags
        type: u4
        doc: |
          Internal curve validity flags (flagOver, flagUnder, flagValid, flagNulls —
          2 bits each).  Not for user use.
      - id: checksum_type
        type: s4
        enum: checksum_type_enum
        doc: Algorithm used to calculate the curve checksum.
      - id: checksum
        type: s2
        doc: Curve checksum value (currently not implemented; file checksum is used).
      - id: precharge_start_offset
        type: u4
        doc: |
          Byte offset from the start of the curve buffer to the first pre-charge
          data point.  Pre-charge data is intended for interpolation only.
      - id: data_start_offset
        type: u4
        doc: |
          Byte offset from the start of the curve buffer to the first user-accessible
          waveform data point.
      - id: postcharge_start_offset
        type: u4
        doc: |
          Byte offset from the start of the curve buffer to the first post-charge
          data point.  Post-charge data is for interpolation only.
      - id: postcharge_stop_offset
        type: u4
        doc: |
          Byte offset from the start of the curve buffer to just past the last valid
          waveform point (inclusive of post-charge data).
      - id: end_of_curve_buffer_offset
        type: u4
        doc: |
          Byte offset to the end of the curve buffer allocation.  In non-roll-mode
          acquisitions this equals postcharge_stop_offset.  In Roll mode it may be
          larger to accommodate the roll buffer.

    instances:
      first_valid_sample:
        value: data_start_offset / _root.static_file_info.num_bytes_per_point
        doc: |
          Sample index (0-based from start of curve buffer) of the first
          user-accessible data point.
      num_valid_samples:
        value: >-
          postcharge_start_offset / _root.static_file_info.num_bytes_per_point
          - data_start_offset / _root.static_file_info.num_bytes_per_point
        doc: Number of user-accessible waveform samples.

enums:
  set_type_enum:
    0: single_waveform
    1: fast_frame

  data_type_enum:
    0: wfmdata_scalar_meas
    1: wfmdata_scalar_const
    2: wfmdata_vector
    3: wfmdata_pixmap
    4: wfmdata_invalid
    5: wfmdata_wfmdb

  explicit_format_enum:
    0: explicit_int16
    1: explicit_int32
    2: explicit_uint32
    3: explicit_uint64
    4: explicit_fp32
    5: explicit_fp64
    6: explicit_invalid_format

  explicit_storage_enum:
    0: explicit_sample
    1: explicit_min_max
    2: explicit_vert_hist
    3: explicit_hor_hist
    4: explicit_row_order
    5: explicit_column_order
    6: explicit_invalid_storage

  pix_map_format_enum:
    0: dsy_format_invalid
    1: dsy_format_yt
    2: dsy_format_xy
    3: dsy_format_xyz

  sweep_enum:
    0: sweep_roll
    1: sweep_sample
    2: sweep_et
    3: sweep_invalid

  base_type_enum:
    0: base_time
    1: base_spectral_mag
    2: base_spectral_phase
    3: base_invalid

  checksum_type_enum:
    0: no_checksum
    1: ctype_crc16
    2: ctype_sum16
    3: ctype_crc32
    4: ctype_sum32
