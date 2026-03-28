meta:
  id: lecroy_1_0_be
  title: Teledyne LeCroy oscilloscope waveform file (LECROY_1_0, little-endian)
  file-extension: trc
  endian: be

doc: |
  Teledyne LeCroy LECROY_1_0 binary waveform format (.trc / .000 files) — big-endian variant.

  This older format has a 320-byte WAVEDESC (vs 346 bytes in LECROY_2_3) with a different
  field layout.  Key differences from LECROY_2_3:
    - wave_array_1_len is at offset 48 (not 60)
    - instrument_name is at offset 56 (not 76)
    - wave_array_count is at offset 92 (not 116)
    - vertical calibration: volts[i] = vertical_gain * adc[i] - acq_vert_offset
    - wave_source at offset 296 is 1-indexed (1=CH1, 2=CH2, …)
    - No ris_time_array field

  Endianness detection (performed by the caller before selecting this parser):
    COMM_ORDER is a u2 at offset 34.  byte 34 == 0 → HIFIRST (little-endian, use lecroy_1_0_le).

  Voltage reconstruction:
    volts[i] = vertical_gain * adc[i] - acq_vert_offset
  where adc[i] is signed 8-bit (COMM_TYPE == byte) or signed 16-bit (COMM_TYPE == word).

  Time axis:
    t[i] = horiz_offset + i * horiz_interval   (i = 0 … wave_array_count − 1)

seq:
  - id: wavedesc
    type: wavedesc
    doc: Main waveform descriptor block.

instances:
  user_text:
    pos: wavedesc.wave_descriptor
    size: wavedesc.user_text_len
    if: wavedesc.user_text_len > 0
    doc: Optional ASCII user text.

  trigtime_array:
    pos: wavedesc.wave_descriptor + wavedesc.user_text_len
    type: trigtime_entry
    repeat: expr
    repeat-expr: wavedesc.trigtime_array_len / 16
    if: wavedesc.trigtime_array_len > 0
    doc: Per-segment trigger-time entries for sequence acquisitions.

  wave_array_1:
    pos: >-
      wavedesc.wave_descriptor
      + wavedesc.user_text_len
      + wavedesc.trigtime_array_len
    size: wavedesc.wave_array_1_len
    doc: |
      Primary sample data as raw bytes.
      Interpret as s1 array (COMM_TYPE == byte) or s2 array (COMM_TYPE == word),
      big-endian byte order.
      Apply: volts[i] = vertical_gain * adc[i] - acq_vert_offset.

  wave_array_2:
    pos: >-
      wavedesc.wave_descriptor
      + wavedesc.user_text_len
      + wavedesc.trigtime_array_len
      + wavedesc.wave_array_1_len
    size: wavedesc.wave_array_2_len
    if: wavedesc.wave_array_2_len > 0
    doc: Secondary sample data as raw bytes.

types:
  wavedesc:
    doc: |
      320-byte WAVEDESC header block (LECROY_1_0 template).  All byte offsets are
      relative to the start of this struct.  Endianness is inherited from root (big-endian).
    seq:
      - id: descriptor_name
        size: 16
        doc: "ASCII \"WAVEDESC\" null-padded to 16 bytes.  Offset 0."
      - id: template_name
        size: 16
        doc: "Template version string, e.g. \"LECROY_1_0\".  Offset 16."
      - id: comm_type
        type: u2
        enum: comm_type_enum
        doc: "Sample width: 0 = byte (8-bit), 1 = word (16-bit).  Offset 32."
      - id: comm_order
        type: u2
        enum: comm_order_enum
        doc: "Byte order: 0 = HIFIRST (big-endian), 1 = LOFIRST (little-endian, use lecroy_1_0_le).  Offset 34."
      - id: wave_descriptor
        type: s4
        doc: "Length in bytes of this WAVEDESC block (320).  Offset 36."
      - id: user_text_len
        type: s4
        doc: "Length in bytes of the USERTEXT block; 0 if absent.  Offset 40."
      - id: trigtime_array_len
        type: s4
        doc: "Length in bytes of the TRIGTIME array; 0 if absent.  Offset 44."
      - id: wave_array_1_len
        type: s4
        doc: "Length in bytes of the primary waveform data array.  Offset 48."
      - id: wave_array_2_len
        type: s4
        doc: "Length in bytes of the secondary waveform data array; 0 if absent.  Offset 52."
      - id: instrument_name
        size: 16
        doc: "Null-terminated ASCII instrument identifier.  Offset 56."
      - id: instrument_number
        type: s4
        doc: "Instrument model number.  Offset 72."
      - id: trace_label
        size: 16
        doc: "User-defined waveform label string.  Offset 76."
      - id: wave_array_count
        type: s4
        doc: "Total number of samples in the waveform.  Offset 92."
      - id: points_per_screen
        type: s4
        doc: "Nominal number of samples visible on screen.  Offset 96."
      - id: first_valid_pnt
        type: s4
        doc: "Index of the first valid sample.  Offset 100."
      - id: last_valid_pnt
        type: s4
        doc: "Index of the last valid sample.  Offset 104."
      - id: subarray_count
        type: s4
        doc: "Number of acquired segments.  Offset 108."
      - id: nom_subarray_count
        type: s4
        doc: "Nominal number of segments.  Offset 112."
      - id: sweeps_per_acq
        type: s4
        doc: "Number of sweeps accumulated.  Offset 116."
      - id: vertical_gain
        type: f4
        doc: "Volts per ADC count.  Offset 120."
      - id: vertical_offset
        type: f4
        doc: "Voltage offset (display use; calibration uses acq_vert_offset).  Offset 124."
      - id: max_value
        type: s2
        doc: "Maximum ADC count (e.g. 32512 for 16-bit).  Offset 128."
      - id: min_value
        type: s2
        doc: "Minimum ADC count (e.g. -32768 for 16-bit).  Offset 130."
      - id: nominal_bits
        type: s2
        doc: "Nominal ADC resolution in bits.  Offset 132."
      - id: horiz_interval
        type: f4
        doc: "Sampling interval in seconds.  Offset 134."
      - id: horiz_offset
        type: f8
        doc: "Time of the first sample relative to the trigger, in seconds.  Offset 138."
      - id: pixel_offset
        type: f8
        doc: "Horizontal display pixel offset (display use only).  Offset 146."
      - id: vert_unit
        size: 48
        doc: "Null-terminated ASCII unit string for the voltage axis.  Offset 154."
      - id: hor_unit
        size: 48
        doc: "Null-terminated ASCII unit string for the time axis.  Offset 202."
      - id: trigger_time
        type: trigger_timestamp
        doc: "Absolute date and time of the trigger event (16 bytes).  Offset 250."
      - id: acq_duration
        type: f4
        doc: "Total acquisition duration in seconds.  Offset 266."
      - id: record_type
        type: s2
        doc: "Waveform record type.  Offset 270."
      - id: processing_done
        type: s2
        doc: "Post-acquisition processing applied.  Offset 272."
      - id: timebase
        type: u2
        doc: "Encoded horizontal time-per-division setting.  Offset 274."
      - id: vert_coupling
        type: u2
        enum: vert_coupling_enum
        doc: "Vertical input coupling.  Offset 276."
      - id: probe_att
        type: f4
        doc: "Probe attenuation factor.  Offset 278."
      - id: fixed_vert_gain
        type: u2
        doc: "Encoded nominal vertical scale setting.  Offset 282."
      - id: bandwidth_limit
        type: u2
        enum: bandwidth_limit_enum
        doc: "Bandwidth-limiting filter state.  Offset 284."
      - id: vert_vernier
        type: f4
        doc: "Fine vertical scale adjustment factor.  Offset 286."
      - id: acq_vert_offset
        type: f4
        doc: |
          Acquisition vertical offset in volts.
          Calibration: volts[i] = vertical_gain * adc[i] - acq_vert_offset.  Offset 290.
      - id: wave_source_plugin
        type: s2
        doc: "Plugin slot of the source channel.  Offset 294."
      - id: wave_source
        type: s2
        doc: "Source channel number, 1-indexed (1=CH1, 2=CH2, 3=CH3, 4=CH4).  Offset 296."
      - id: trigger_source
        type: s2
        doc: "Trigger source channel.  Offset 298."
      - id: trigger_coupling
        type: s2
        doc: "Trigger coupling mode.  Offset 300."
      - id: trigger_slope
        type: s2
        doc: "Trigger slope.  Offset 302."
      - id: smart_trigger
        type: s2
        doc: "Smart trigger mode.  Offset 304."
      - id: trigger_level
        type: f4
        doc: "Trigger level in volts.  Offset 306."
      - id: sweeps_array_1
        type: s4
        doc: "Sweeps in array 1.  Offset 310."
      - id: sweeps_array_2
        type: s4
        doc: "Sweeps in array 2.  Offset 314."
      - id: reserved_end
        size: 2
        doc: "Reserved padding to 320 bytes.  Offset 318."

    instances:
      seconds_per_point:
        value: horiz_interval
        doc: Alias for horiz_interval.
      volt_per_division:
        value: (max_value - min_value) * vertical_gain / 8.0
        doc: |
          Vertical scale in volts per division, computed from the full ADC count
          range scaled by vertical_gain and divided by 8 display divisions.
      is_sequence:
        value: subarray_count > 1
        doc: True when this is a sequence-mode acquisition.
      is_16bit:
        value: comm_type == comm_type_enum::word
        doc: True when samples are 16-bit words; false for 8-bit bytes.

  trigger_timestamp:
    doc: 16-byte absolute trigger timestamp.
    seq:
      - id: seconds
        type: f8
        doc: Fractional seconds within the current minute.
      - id: minutes
        type: u1
      - id: hours
        type: u1
      - id: days
        type: u1
      - id: months
        type: u1
      - id: year
        type: s2
      - id: unused
        type: s2

  trigtime_entry:
    doc: One 16-byte record in the TRIGTIME array.
    seq:
      - id: trigger_time
        type: f8
      - id: trigger_offset
        type: f8

enums:
  comm_type_enum:
    0: byte
    1: word

  comm_order_enum:
    0: big_endian
    1: little_endian

  vert_coupling_enum:
    0: dc_50_ohm
    1: ground
    2: dc_1m_ohm
    3: ground_b
    4: ac_1m_ohm

  bandwidth_limit_enum:
    0: bw_full
    1: bw_limited
