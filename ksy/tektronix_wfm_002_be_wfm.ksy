meta:
  id: tektronix_wfm_002_be_wfm
  title: Tektronix WFM002/WFM003 Binary Format (Big-Endian)
  file-extension: wfm
  endian: be

doc: |
  Tektronix WFM binary waveform format, version WFM#002 and WFM#003,
  big-endian variant.

  WFM#002 applies to: TDS5000B Series.
  WFM#003 applies to: DPO7000, DPO70000, DSA70000 Series.

  Difference from WFM#001: a 2-byte summary_frame_type field is inserted at
  offset 0x9a (154) between num_acquired_fast_frames and pix_map_display_format,
  shifting all subsequent fields by 2 bytes.

  WFM#003 additional difference: point_density in the user-view sections of each
  dimension (exp_dim1, exp_dim2, imp_dim1, imp_dim2) changes from u4 (4 bytes) to
  f8 (8 bytes).  This parser handles that layout difference explicitly, so the
  downstream time-base, update-spec, and curve offsets are correct for both
  WFM#002 and WFM#003 files.

  Endianness detection: byte_order at offset 0 is 0xF0F0 for big-endian (PPC).
  Version string at offset 2 is "WFM#002" or "WFM#003".

  Voltage reconstruction (explicit dimension 1):
    volts[i] = exp_dim1.dim_scale * adc[i] + exp_dim1.dim_offset

  Time axis (implicit dimension 1):
    t[i] = imp_dim1.dim_offset + i * imp_dim1.dim_scale
  where i = 0 corresponds to the first sample in the curve buffer.

  Reference: Tektronix "Reference Waveform File Format" (001-1378-03), version notes.

seq:
  - id: static_file_info
    type: static_file_info
    doc: 78-byte static waveform file information header.

  - id: wfm_header
    type: wfm_header
    doc: Variable-length waveform header with dimension, time-base, and curve metadata.

instances:
  is_wfm003:
    value: static_file_info.version_number == "WFM#003"
    doc: True when this file uses the WFM#003 layout.
  curve_buffer:
    pos: static_file_info.byte_offset_to_curve_buffer
    size: wfm_header.curve.end_of_curve_buffer_offset
    doc: |
      Raw curve data bytes, inclusive of pre- and post-charge interpolation data.
      Valid user-accessible data occupies the byte range
      [data_start_offset, postcharge_start_offset) within this buffer.

types:
  static_file_info:
    doc: |
      78-byte block of static waveform file information at the very start of the file.
      Identical in layout to WFM#001.
    seq:
      - id: byte_order
        type: u2
        doc: |
          Byte-order marker.  0xF0F0 = big-endian (PPC); 0x0F0F = little-endian (Intel / PC)
          (PPC).  Offset 0.
      - id: version_number
        type: str
        size: 7
        encoding: ASCII
        doc: |
          Version identification string.
          "WFM#002" or "WFM#003" for this parser.  Offset 2.
      - id: version_pad
        size: 1
        doc: Null terminator / padding byte after version_number.  Offset 9.
      - id: num_digits_byte_count
        type: u1
        doc: Number of decimal digits in the byte-count field (0–9).  Offset 10.
      - id: num_bytes_to_eof
        type: s4
        doc: Number of bytes from this field to the end of file.  Offset 11.
      - id: num_bytes_per_point
        type: u1
        doc: Bytes per curve data point (2, 4, or 8).  Offset 15.
      - id: byte_offset_to_curve_buffer
        type: s4
        doc: |
          Absolute byte offset from the start of file to the start of the curve buffer.
          Offset 16.
      - id: horiz_zoom_scale_factor
        type: s4
        doc: Horizontal zoom scale factor (display use only).  Offset 20.
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
        doc: Number of FastFrame frames minus 1 (0 for single-waveform files).  Offset 72.
      - id: wfm_header_size
        type: u2
        doc: Size in bytes of the waveform header.  Offset 76.

  wfm_header:
    doc: |
      Waveform header block.  Differs from WFM#001 by the 2-byte summary_frame_type
      field inserted after num_acquired_fast_frames.

      WFM#002 uses 4-byte point_density values in the user-view sections:
        exp_dim1 @ 168, exp_dim2 @ 324, imp_dim1 @ 480, imp_dim2 @ 612,
        time_base1 @ 744, time_base2 @ 756, update_spec @ 768, curve @ 792.

      WFM#003 uses 8-byte point_density values in the same sections:
        exp_dim1 @ 168, exp_dim2 @ 328, imp_dim1 @ 488, imp_dim2 @ 624,
        time_base1 @ 760, time_base2 @ 772, update_spec @ 784, curve @ 808.
    seq:
      - id: set_type
        type: s4
        enum: set_type_enum
        doc: Waveform set type.  0 = single; 1 = FastFrame.  Offset 78.
      - id: wfm_cnt
        type: u4
        doc: Number of waveforms in the set.  Offset 82.
      - id: acq_counter
        type: u8
        doc: Internal acquisition counter.  Not for user use.  Offset 86.
      - id: transaction_counter
        type: u8
        doc: Internal transaction timestamp.  Not for user use.  Offset 94.
      - id: slot_id
        type: s4
        doc: Instrument data-slot enumeration.  Not for user use.  Offset 102.
      - id: is_static_flag
        type: s4
        doc: Non-zero = static reference; 0 = live channel/math.  Offset 106.
      - id: wfm_update_spec_count
        type: u4
        doc: Number of waveform update specifications.  Offset 110.
      - id: imp_dim_ref_count
        type: u4
        doc: Number of implicit dimension references.  Offset 114.
      - id: exp_dim_ref_count
        type: u4
        doc: Number of explicit dimension references.  Offset 118.
      - id: data_type
        type: s4
        enum: data_type_enum
        doc: Waveform data type.  2 = vector (normal YT).  Offset 122.
      - id: gen_purpose_counter
        type: u8
        doc: General-purpose internal counter.  Offset 126.
      - id: accum_wfm_count
        type: u4
        doc: Accumulated waveform count.  Offset 134.
      - id: target_accum_count
        type: u4
        doc: Target accumulation count.  Offset 138.
      - id: curve_ref_count
        type: u4
        doc: Number of curve objects.  Normally 1.  Offset 142.
      - id: num_requested_fast_frames
        type: u4
        doc: Number of FastFrame acquisitions requested.  Offset 146.
      - id: num_acquired_fast_frames
        type: u4
        doc: Number of FastFrame frames actually acquired.  Offset 150.
      - id: summary_frame_type
        type: u2
        enum: summary_frame_enum
        doc: |
          FastFrame summary frame type (WFM#002/003 addition at offset 154).
          0 = off; 1 = average; 2 = envelope.
      - id: pix_map_display_format
        type: s4
        enum: pix_map_format_enum
        doc: Pixel-map display format (display use only).  Offset 156.
      - id: pix_map_max_value
        type: u8
        doc: Maximum pixel-map value (display use only).  Offset 160.
      - id: exp_dim1
        type: exp_dim
        doc: |
          Explicit dimension 1 (156 bytes in WFM#002, 160 bytes in WFM#003;
          voltage axis for YT).  Offset 168.
      - id: exp_dim2
        type: exp_dim
        doc: |
          Explicit dimension 2 (156 bytes in WFM#002, 160 bytes in WFM#003).
          Offset 324 in WFM#002, 328 in WFM#003.
      - id: imp_dim1
        type: imp_dim
        doc: |
          Implicit dimension 1 (132 bytes in WFM#002, 136 bytes in WFM#003;
          time axis for YT).  Offset 480 in WFM#002, 488 in WFM#003.
      - id: imp_dim2
        type: imp_dim
        doc: |
          Implicit dimension 2 (132 bytes in WFM#002, 136 bytes in WFM#003).
          Offset 612 in WFM#002, 624 in WFM#003.
      - id: time_base1
        type: time_base_info
        doc: Time-base 1 information (12 bytes).  Offset 744 in WFM#002, 760 in WFM#003.
      - id: time_base2
        type: time_base_info
        doc: Time-base 2 information (12 bytes).  Offset 756 in WFM#002, 772 in WFM#003.
      - id: update_spec
        type: wfm_update_spec
        doc: |
          Update specification for the first waveform frame (24 bytes).
          Offset 768 in WFM#002, 784 in WFM#003.
      - id: curve
        type: wfm_curve_object
        doc: |
          Curve object for the first waveform frame (30 bytes).
          Offset 792 in WFM#002, 808 in WFM#003.

  exp_dim:
    doc: |
      Explicit dimension: 100-byte description block plus a version-dependent
      user-view section.

      Total size:
        WFM#002 = 156 bytes (56-byte user-view)
        WFM#003 = 160 bytes (60-byte user-view)

      For YT waveforms, explicit dimension 1 defines the voltage (Y) axis:
        volts[i] = dim_scale * adc[i] + dim_offset
    seq:
      - id: dim_scale
        type: f8
        doc: Scale factor in physical units per ADC count (volts per LSB).
      - id: dim_offset
        type: f8
        doc: |
          Offset in physical units.
          volts[i] = dim_scale * adc[i] + dim_offset.
      - id: dim_size
        type: u4
        doc: |
          Storage element size (e.g. 252 for 8-bit, 65532 for 16-bit; 1 for float).
      - id: units
        size: 20
        doc: Null-terminated ASCII unit string (e.g. "Volts").
      - id: dim_extent_min
        type: f8
        doc: Minimum attainable value (not for user use).
      - id: dim_extent_max
        type: f8
        doc: Maximum attainable value (not for user use).
      - id: dim_resolution
        type: f8
        doc: Smallest resolvable voltage increment (value of one digitizing level).
      - id: dim_ref_point
        type: f8
        doc: Ground-level reference value.
      - id: format
        type: s4
        enum: explicit_format_enum
        doc: Data format of curve buffer values.
      - id: storage_type
        type: s4
        enum: explicit_storage_enum
        doc: Storage layout of curve buffer values.
      - id: n_value
        size: 4
        doc: Raw 4-byte unacquired (NULL) value representation.
      - id: over_range
        size: 4
        doc: Raw 4-byte over-range value.
      - id: under_range
        size: 4
        doc: Raw 4-byte under-range value.
      - id: high_range
        size: 4
        doc: Raw 4-byte maximum signed value.
      - id: low_range
        size: 4
        doc: Raw 4-byte minimum value.
      # User-view data
      - id: user_scale
        type: f8
        doc: User display scale in physical units per screen division.
      - id: user_units
        size: 20
        doc: Null-terminated user display unit string.
      - id: user_offset
        type: f8
        doc: User display position offset in screen divisions.
      - id: point_density_u4
        type: u4
        if: not _root.is_wfm003
        doc: |
          Screen-to-data ratio in WFM#002 files.  Always 1 for explicit dimensions.
      - id: point_density_f8
        type: f8
        if: _root.is_wfm003
        doc: |
          Screen-to-data ratio in WFM#003 files.  Always 1 for explicit dimensions.
      - id: h_ref
        type: f8
        doc: Trigger horizontal position as a percentage of the waveform (0–100%).
      - id: trig_delay
        type: f8
        doc: Time delay in seconds from trigger to HRef screen position.

    instances:
      point_density:
        value: "_root.is_wfm003 ? point_density_f8 : point_density_u4"
        doc: Version-normalized point_density value.

  imp_dim:
    doc: |
      Implicit dimension: 76-byte description block plus a version-dependent
      user-view section.

      Total size:
        WFM#002 = 132 bytes (56-byte user-view)
        WFM#003 = 136 bytes (60-byte user-view)

      For YT waveforms, implicit dimension 1 defines the time (X) axis:
        t[i] = dim_offset + i * dim_scale
      where i = 0 is the first sample in the curve buffer.
    seq:
      - id: dim_scale
        type: f8
        doc: Sample interval in seconds (time per point).
      - id: dim_offset
        type: f8
        doc: |
          Time in seconds of sample index 0 relative to the trigger.
          Typically negative (pre-charge data precedes the trigger).
      - id: dim_size
        type: u4
        doc: Record length in samples, including pre- and post-charge data.
      - id: units
        size: 20
        doc: Null-terminated ASCII unit string (e.g. "s").
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
        doc: Real-time point spacing; 1 for non-interpolated waveforms.
      # User-view data
      - id: user_scale
        type: f8
        doc: User display time scale.
      - id: user_units
        size: 20
        doc: Null-terminated user display time unit string.
      - id: user_offset
        type: f8
        doc: Horizontal center pixel column position relative to trigger (absolute time units).
      - id: point_density_u4
        type: u4
        if: not _root.is_wfm003
        doc: |
          Data points compressed into one pixel column at zoom = 1 for WFM#002 files.
      - id: point_density_f8
        type: f8
        if: _root.is_wfm003
        doc: |
          Data points compressed into one pixel column at zoom = 1 for WFM#003 files.
      - id: h_ref
        type: f8
        doc: Trigger horizontal position as a percentage of the waveform (0–100%).
      - id: trig_delay
        type: f8
        doc: Time delay in seconds from trigger to HRef screen position.

    instances:
      point_density:
        value: "_root.is_wfm003 ? point_density_f8 : point_density_u4"
        doc: Version-normalized point_density value.

  time_base_info:
    doc: 12-byte time-base acquisition information block.
    seq:
      - id: real_point_spacing
        type: u4
        doc: Integer point spacing between consecutive acquired points.
      - id: sweep
        type: s4
        enum: sweep_enum
        doc: Sweep/acquisition mode.
      - id: type_of_base
        type: s4
        enum: base_type_enum
        doc: Domain of the horizontal axis.

  wfm_update_spec:
    doc: |
      24-byte waveform update specification containing per-frame trigger timing data.
    seq:
      - id: real_point_offset
        type: u4
        doc: Offset to the first non-interpolated point from the start of valid data.
      - id: tt_offset
        type: f8
        doc: Sub-sample time fraction from trigger to next data point.
      - id: frac_sec
        type: f8
        doc: Fractional-second component of trigger timestamp.
      - id: gmt_sec
        type: s4
        doc: Whole-second GMT time of trigger.

  wfm_curve_object:
    doc: |
      30-byte curve object containing byte offsets that bound the curve data regions.
      To extract valid waveform samples:
        first_byte = data_start_offset
        last_byte  = postcharge_start_offset   (exclusive)
    seq:
      - id: state_flags
        type: u4
        doc: Internal curve validity flags.
      - id: checksum_type
        type: s4
        enum: checksum_type_enum
        doc: Checksum algorithm for this curve.
      - id: checksum
        type: s2
        doc: Curve checksum value.
      - id: precharge_start_offset
        type: u4
        doc: Byte offset from curve buffer start to first pre-charge data point.
      - id: data_start_offset
        type: u4
        doc: Byte offset from curve buffer start to first user-accessible data point.
      - id: postcharge_start_offset
        type: u4
        doc: Byte offset from curve buffer start to first post-charge data point.
      - id: postcharge_stop_offset
        type: u4
        doc: Byte offset just past the last valid waveform point.
      - id: end_of_curve_buffer_offset
        type: u4
        doc: |
          Byte offset to the end of the curve buffer.  Equals postcharge_stop_offset
          for non-roll-mode acquisitions.

    instances:
      first_valid_sample:
        value: data_start_offset / _root.static_file_info.num_bytes_per_point
        doc: Index of the first user-accessible sample in the curve buffer.
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
    7: explicit_uint8
    8: explicit_int8

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

  summary_frame_enum:
    0: summary_frame_off
    1: summary_frame_average
    2: summary_frame_envelope

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
