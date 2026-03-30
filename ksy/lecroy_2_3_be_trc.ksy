meta:
  id: lecroy_2_3_be
  title: LeCroy 2.3 TRC Binary Format (Big-Endian)
  file-extension: trc
  endian: be

doc: |
  Teledyne LeCroy LECROY_2_3 binary waveform format (.trc files) — big-endian variant.

  This parser handles files where byte 34 (the low byte of COMM_ORDER) equals 1,
  indicating LOFIRST (little-endian) byte order.  Use lecroy_2_3_be for big-endian
  files (byte 34 == 0).

  File layout:
    [WAVEDESC block:   346 bytes  — main waveform descriptor (WAVE_DESCRIPTOR field)]
    [USERTEXT block:   variable  — optional free-form text (USER_TEXT bytes; 0 if absent)]
    [TRIGTIME array:   variable  — segment trigger times for sequence acquisitions]
    [RIS_TIME array:   variable  — random-interleaved-sampling time array (0 if absent)]
    [WAVE_ARRAY_1:     variable  — primary sample data (WAVE_ARRAY_1 bytes)]
    [WAVE_ARRAY_2:     variable  — secondary sample data (0 if absent)]

  WAVEDESC always starts with the 8-byte ASCII marker "WAVEDESC", null-padded to
  16 bytes.  Normal .trc files written by the oscilloscope begin at byte 0.  Files
  transferred via SCPI may carry a short numeric prefix before WAVEDESC; those
  files are not supported directly by this parser.

  Endianness detection (performed by the caller before selecting this parser):
    COMM_ORDER is a u2 at offset 34.  Because COMM_ORDER can only be 0 or 1,
    the low byte at offset 34 is unambiguous in both byte orders:
      byte 34 == 0  →  HIFIRST (big-endian,    use lecroy_2_3_be)
      byte 34 == 1  →  LOFIRST (little-endian, use lecroy_2_3_be)

  Voltage reconstruction (single sweep):
    volts[i] = VERTICAL_GAIN * adc[i] - VERTICAL_OFFSET
  where adc[i] is signed 8-bit (COMM_TYPE == byte) or signed 16-bit (COMM_TYPE == word).

  Time axis:
    t[i] = HORIZ_OFFSET + i * HORIZ_INTERVAL   (i = 0 … WAVE_ARRAY_COUNT − 1)

  For sequence acquisitions (SUBARRAY_COUNT > 1), the time axis for segment k is:
    t[k,i] = (trigtime_array[k].trigger_time + trigtime_array[k].trigger_offset)
             + i * HORIZ_INTERVAL

seq:
  - id: wavedesc
    type: wavedesc
    doc: Main waveform descriptor block.

instances:
  user_text:
    pos: wavedesc.wave_descriptor
    size: wavedesc.user_text_len
    if: wavedesc.user_text_len > 0
    doc: Optional ASCII user text (up to 160 bytes).

  trigtime_array:
    pos: wavedesc.wave_descriptor + wavedesc.user_text_len
    type: trigtime_entry
    repeat: expr
    repeat-expr: wavedesc.trigtime_array_len / 16
    if: wavedesc.trigtime_array_len > 0
    doc: |
      Per-segment trigger-time entries for sequence acquisitions.
      Present only when SUBARRAY_COUNT > 1.  Each entry is 16 bytes
      (two f8 values: trigger_time, trigger_offset).

  wave_array_1:
    pos: >-
      wavedesc.wave_descriptor
      + wavedesc.user_text_len
      + wavedesc.trigtime_array_len
      + wavedesc.ris_time_array_len
    size: wavedesc.wave_array_1_len
    doc: |
      Primary sample data as raw bytes.
      Interpret as s1 array (COMM_TYPE == byte) or s2 array (COMM_TYPE == word),
      big-endian byte order.
      Apply: volts[i] = VERTICAL_GAIN * adc[i] - VERTICAL_OFFSET.

  wave_array_2:
    pos: >-
      wavedesc.wave_descriptor
      + wavedesc.user_text_len
      + wavedesc.trigtime_array_len
      + wavedesc.ris_time_array_len
      + wavedesc.wave_array_1_len
    size: wavedesc.wave_array_2_len
    if: wavedesc.wave_array_2_len > 0
    doc: |
      Secondary sample data as raw bytes (same format as wave_array_1).
      Interpretation depends on RECORD_TYPE:
        extrema (6)     — floor (minimum) trace
        complex (5)     — imaginary part of FFT
        peak_detect (9) — floor trace

types:
  wavedesc:
    doc: |
      346-byte WAVEDESC header block (LECROY_2_3 template).  All byte offsets in the
      original LeCroy template documentation are relative to the start of this struct.
      Endianness is inherited from the root type (big-endian).
    seq:
      - id: descriptor_name
        size: 16
        doc: "ASCII \"WAVEDESC\" null-padded to 16 bytes.  Offset 0."
      - id: template_name
        size: 16
        doc: "Template version string, e.g. \"LECROY_2_3\".  Offset 16."
      - id: comm_type
        type: u2
        enum: comm_type_enum
        doc: "Sample width: 0 = byte (8-bit), 1 = word (16-bit).  Offset 32."
      - id: comm_order
        type: u2
        enum: comm_order_enum
        doc: "Byte order: 0 = HIFIRST (big-endian), 1 = LOFIRST (little-endian).  Offset 34."
      - id: wave_descriptor
        type: s4
        doc: "Length in bytes of this WAVEDESC block (typically 346).  Offset 36."
      - id: user_text_len
        type: s4
        doc: "Length in bytes of the USERTEXT block; 0 if absent.  Offset 40."
      - id: res_desc1
        type: s4
        doc: "Reserved.  Offset 44."
      - id: trigtime_array_len
        type: s4
        doc: "Length in bytes of the TRIGTIME array; 0 if absent.  Offset 48."
      - id: ris_time_array_len
        type: s4
        doc: "Length in bytes of the RIS_TIME array; 0 if absent.  Offset 52."
      - id: res_array1
        type: s4
        doc: "Reserved.  Offset 56."
      - id: wave_array_1_len
        type: s4
        doc: "Length in bytes of the primary waveform data array.  Offset 60."
      - id: wave_array_2_len
        type: s4
        doc: "Length in bytes of the secondary waveform data array; 0 if absent.  Offset 64."
      - id: res_array2
        type: s4
        doc: "Reserved.  Offset 68."
      - id: res_array3
        type: s4
        doc: "Reserved.  Offset 72."
      - id: instrument_name
        size: 16
        doc: "Null-terminated ASCII instrument identifier (e.g. \"WAVERUNNER\").  Offset 76."
      - id: instrument_number
        type: s4
        doc: "Instrument serial number.  Offset 92."
      - id: trace_label
        size: 16
        doc: "User-defined waveform label string.  Offset 96."
      - id: reserved1
        type: s2
        doc: "Reserved.  Offset 112."
      - id: reserved2
        type: s2
        doc: "Reserved.  Offset 114."
      - id: wave_array_count
        type: s4
        doc: "Total number of samples in the waveform.  Offset 116."
      - id: pnts_per_screen
        type: s4
        doc: "Nominal number of samples visible on the oscilloscope screen.  Offset 120."
      - id: first_valid_pnt
        type: s4
        doc: "Index of the first valid sample.  Offset 124."
      - id: last_valid_pnt
        type: s4
        doc: "Index of the last valid sample.  Offset 128."
      - id: first_point
        type: s4
        doc: "Byte offset of the first transmitted point relative to start of trace.  Offset 132."
      - id: sparsing_factor
        type: s4
        doc: "Sparsing factor applied to the transmitted data.  Offset 136."
      - id: segment_index
        type: s4
        doc: "Index of the transmitted segment (for sequence acquisitions).  Offset 140."
      - id: subarray_count
        type: s4
        doc: |
          Number of acquired segments.  1 = single sweep, >1 = sequence mode.
          When > 1, trigtime_array at the root level holds per-segment time info.
          Offset 144.
      - id: sweeps_per_acq
        type: s4
        doc: "Number of sweeps accumulated (average/envelope modes).  Offset 148."
      - id: points_per_pair
        type: s2
        doc: "Data points per min/max pair (peak-detect waveforms only).  Offset 152."
      - id: pair_offset
        type: s2
        doc: "Offset to the data pairs (peak-detect waveforms only).  Offset 154."
      - id: vertical_gain
        type: f4
        doc: |
          Volts per ADC count.
          volts[i] = vertical_gain * adc[i] - vertical_offset.  Offset 156.
      - id: vertical_offset
        type: f4
        doc: |
          Voltage offset subtracted after scaling.
          volts[i] = vertical_gain * adc[i] - vertical_offset.  Offset 160.
      - id: max_value
        type: f4
        doc: "Maximum ADC output voltage (top of the displayed grid).  Offset 164."
      - id: min_value
        type: f4
        doc: "Minimum ADC output voltage (bottom of the displayed grid).  Offset 168."
      - id: nominal_bits
        type: s2
        doc: "ADC resolution in bits (e.g. 8 or 16).  Offset 172."
      - id: nom_subarray_count
        type: s2
        doc: "Nominal number of segments (requested; may differ from subarray_count).  Offset 174."
      - id: horiz_interval
        type: f4
        doc: "Sampling interval in seconds (time between consecutive samples).  Offset 176."
      - id: horiz_offset
        type: f8
        doc: "Time of the first sample relative to the trigger, in seconds.  Offset 180."
      - id: pixel_offset
        type: f8
        doc: "Horizontal display pixel offset (for display use only).  Offset 188."
      - id: vert_unit
        size: 48
        doc: "Null-terminated ASCII unit string for the voltage axis (e.g. \"V\").  Offset 196."
      - id: hor_unit
        size: 48
        doc: "Null-terminated ASCII unit string for the time axis (e.g. \"s\").  Offset 244."
      - id: horiz_uncertainty
        type: f4
        doc: "Estimated uncertainty of horiz_offset, in seconds.  Offset 292."
      - id: trigger_time
        type: trigger_timestamp
        doc: "Absolute date and time of the trigger event (16 bytes).  Offset 296."
      - id: acq_duration
        type: f4
        doc: "Total acquisition duration, in seconds.  Offset 312."
      - id: record_type
        type: u2
        enum: record_type_enum
        doc: "Waveform record type; governs interpretation of wave_array_2.  Offset 316."
      - id: processing_done
        type: u2
        enum: processing_done_enum
        doc: "Post-acquisition processing applied to the data.  Offset 318."
      - id: reserved5
        type: s2
        doc: "Reserved.  Offset 320."
      - id: ris_sweeps
        type: s2
        doc: "Number of sweeps in a RIS acquisition; 1 for all other record types.  Offset 322."
      - id: timebase
        type: u2
        doc: |
          Encoded horizontal time-per-division setting.
          Values 0–47 follow a 1/2/5 × 10^n sequence (index 0 = 1 ps/div, …,
          index 47 = 5 ks/div).  Value 100 = EXTERNAL clock.
          Decode: mant = [1,2,5][index % 3]; exp = index // 3 − 12; t = mant × 10^exp s/div.
          Offset 324.
      - id: vert_coupling
        type: u2
        enum: vert_coupling_enum
        doc: "Vertical input coupling.  Offset 326."
      - id: probe_att
        type: f4
        doc: "Probe attenuation factor (e.g. 10.0 for a 10× probe).  Offset 328."
      - id: fixed_vert_gain
        type: u2
        doc: |
          Encoded nominal vertical scale setting (V/div, before probe attenuation).
          Values 0–27 follow a 1/2/5 × 10^n sequence:
            index 0 = 1 µV/div, index 9 = 10 mV/div, index 18 = 100 mV/div, etc.
          Decode: mant = [1,2,5][index % 3]; exp = index // 3 − 6; V/div = mant × 10^exp.
          Offset 332.
      - id: bandwidth_limit
        type: u2
        enum: bandwidth_limit_enum
        doc: "Bandwidth-limiting filter state (bw_full = no limit, bw_limited = on).  Offset 334."
      - id: vertical_vernier
        type: f4
        doc: "Fine vertical scale adjustment factor.  Offset 336."
      - id: acq_vert_offset
        type: f4
        doc: "Acquisition vertical offset in volts.  Offset 340."
      - id: wave_source
        type: u2
        enum: wave_source_enum
        doc: "Oscilloscope channel that produced this waveform.  Offset 344."

    instances:
      seconds_per_point:
        value: horiz_interval
        doc: Alias for horiz_interval; seconds between consecutive ADC samples.
      volt_per_division:
        value: (max_value - min_value) * vertical_gain / 8.0
        doc: |
          Vertical scale in volts per division.  MAX_VALUE and MIN_VALUE are ADC
          counts; multiply by vertical_gain to convert to volts, then divide by
          the standard 8-division display height.
      is_sequence:
        value: subarray_count > 1
        doc: True when this is a sequence-mode (multi-segment) acquisition.
      is_16bit:
        value: comm_type == comm_type_enum::word
        doc: True when samples are 16-bit words; false for 8-bit bytes.

  trigger_timestamp:
    doc: |
      16-byte absolute trigger timestamp embedded in WAVEDESC at offset 296.
      Endianness is inherited from the root type.
    seq:
      - id: seconds
        type: f8
        doc: Fractional seconds within the current minute (0.0 to 59.999…).
      - id: minutes
        type: u1
        doc: Minutes component of the trigger time (0–59).
      - id: hours
        type: u1
        doc: Hours component of the trigger time (0–23).
      - id: days
        type: u1
        doc: Day of month (1–31).
      - id: months
        type: u1
        doc: Month (1–12).
      - id: year
        type: s2
        doc: Full year (e.g. 2024).
      - id: unused
        type: s2
        doc: Padding; always 0.

  trigtime_entry:
    doc: |
      One 16-byte record in the TRIGTIME array.  Present only for sequence-mode
      acquisitions (SUBARRAY_COUNT > 1).  Endianness is inherited from the root type.

      Time axis for segment k (0-based):
        t[k,i] = (trigger_time + trigger_offset) + i * HORIZ_INTERVAL
    seq:
      - id: trigger_time
        type: f8
        doc: Absolute trigger timestamp for this segment, in seconds.
      - id: trigger_offset
        type: f8
        doc: Horizontal offset for this segment (time from trigger to first sample), in seconds.

enums:
  comm_type_enum:
    0: byte
    1: word

  comm_order_enum:
    0: big_endian
    1: little_endian

  record_type_enum:
    0: single_sweep
    1: interleaved
    2: histogram
    3: graph
    4: filter_coefficient
    5: complex
    6: extrema
    7: sequence_obsolete
    8: centered_ris
    9: peak_detect

  processing_done_enum:
    0: no_processing
    1: fir_filter
    2: interpolated
    3: sparsed
    4: autoscaled
    5: no_result
    6: rolling
    7: cumulative

  vert_coupling_enum:
    0: dc_50_ohm
    1: ground
    2: dc_1m_ohm
    3: ground_b
    4: ac_1m_ohm

  bandwidth_limit_enum:
    0: bw_full
    1: bw_limited

  wave_source_enum:
    0: channel_1
    1: channel_2
    2: channel_3
    3: channel_4
    4: unknown
