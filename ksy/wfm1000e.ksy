meta:
  id: wfm1000e
  title: Rigol DS1102E oscilloscope waveform file format
  file-extension: wfm
  endian: le

doc: |
  Rigol DS1102E scope .wmf format abstracted from a python script

instances:
  header:
    pos: 0
    type: header
  data:
    pos: 276
    type: raw_data

types:
  header:
    seq:
      - id: magic
        contents: [0xa5, 0xa5, 0x00, 0x00]
      - id: blank_12
        contents: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
      - id: adc_mode
        type: u1
      - id: padding_2
        contents: [0, 0, 0]
      - id: roll_stop
        type: u4
      - id: unused_4
        contents: [0, 0, 0, 0]
      - id: ch1_points_tmp
        type: u4
      - id: active_channel
        type: u1
      - id: padding_3
        contents: [0]
      - id: ch
        type: channel_header
        repeat: expr
        repeat-expr: 2
      - id: time_offset
        type: u1
      - id: padding_4
        contents: [0x00]
      - id: time
        type: time_header
      - id: logic
        type: logic_analyzer_header
      - id: trigger_mode
        type: u1
        enum: trigger_mode_enum
      - id: trigger1
        type: trigger_header
      - id: trigger2
        type: trigger_header
      - id: padding_6
        contents: [0, 0, 0, 0, 0, 0, 0, 0, 0]
      - id: ch2_points_tmp
        type: u4
      - id: time2
        type: time_header
      - id: la_sample_rate
        doc: Does not exist in early formats, unsure how to detect if missing
        type: f4

    instances:
      ch1_points:
        value: "roll_stop == 0 ? ch1_points_tmp - 4: ch1_points_tmp-roll_stop-6"
        doc: In rolling mode, change the number of valid samples

      ch1_skip:
        value: "roll_stop == 0 ? 0 : roll_stop + 2"
        doc: In rolling mode, skip invalid points

      sample_rate_hz:
        value: time.sample_rate_hz

      seconds_per_point:
        value: 1/sample_rate_hz

      ch2_points:
        value: "ch[1].enabled and ch2_points_tmp==0 ?
                ch1_points : ch2_points_tmp"
        doc: Use ch1_points when ch2_points is not written

      ch1_volt_length:
        value: ch1_points - roll_stop
        doc: In rolling mode, skip invalid samples

      ch2_volt_length:
        value: ch2_points - roll_stop
        doc: In rolling mode, skip invalid samples

      ch1_time_scale:
        value: 1.0e-12 * time.scale_measured
      ch1_time_offset:
        value: 1.0e-12 * time.offset_measured
      ch2_time_scale:
        value: "trigger_mode == trigger_mode_enum::alt ?
                 1.0e-12 * time2.scale_measured:
                 ch1_time_scale"
      ch2_time_offset:
        value: "trigger_mode == trigger_mode_enum::alt ?
                 1.0e-12 * time2.offset_measured:
                 ch1_time_offset"

  channel_header:   # 24 bytes total
    seq:
      - id: unknown_0
        type: u2
      - id: scale_display
        type: s4
      - id: shift_display
        type: s2
      - id: unknown_1
        type: u1
      - id: unknown_2
        type: u1
      - id: probe_value
        type: f4
      - id: invert_disp_val
        type: u1
      - id: enabled_val
        type: u1
      - id: inverted_m_val
        type: u1
      - id: unknown_3
        type: u1
      - id: scale_measured
        type: s4
      - id: shift_measured
        type: s2

    instances:
      inverted:
        value: "inverted_m_val != 0 ? true : false"
      enabled:
        value: "enabled_val != 0 ? true : false"
      volt_per_division:
        value: "inverted ?
                -1.0e-6 * scale_measured * probe_value:
                +1.0e-6 * scale_measured * probe_value"
      volt_scale:
        value: 1.0e-6 * scale_measured * probe_value / 25.0
      volt_offset:
        value: shift_measured * volt_scale
      unit:
        value: "unit_enum::v"


  time_header:
    seq:
      - id: scale_display
        type: s8
      - id: offset_display
        type: s8
      - id: sample_rate_hz
        type: f4
      - id: scale_measured
        type: s8
      - id: offset_measured
        type: s8

  trigger_header:
    seq:
      - id: mode
        type: u1
        enum: trigger_mode_enum
      - id: source
        type: u1
        enum: source_enum
      - id: coupling
        type: u1
      - id: sweep
        type: u1
      - id: padding_1
        contents: [0x00]
      - id: sens
        type: f4
      - id: holdoff
        type: f4
      - id: level
        type: f4
      - id: direct
        type: u1
      - id: pulse_type
        type: u1
      - id: padding_2
        contents: [0x00, 0x00]
      - id: pulse_width
        type: f4
      - id: slope_type
        type: u1
      - id: padding_3
        contents: [0x00, 0x00, 0x00]
      - id: lower
        type: f4
      - id: slope_width
        type: f4
      - id: video_pol
        type: u1
      - id: video_sync
        type: u1
      - id: video_std
        type: u1

  logic_analyzer_header:
    seq:
      - id: unused
        type: b7
      - id: enabled
        type: b1
      - id: active_channel
        doc: Should be 0 to 16
        type: u1
      - id: enabled_channels
        doc: Each bit corresponds to one enabled channel
        type: u2
      - id: position
        size: 16
      - id: group8to15size
        doc: Should be 7-15
        type: u1
      - id: group0to7size
        doc: Should be 7-15
        type: u1

  raw_data:
    seq:
      - id: ch1
        size: _root.header.ch1_points
        if: _root.header.ch[0].enabled

      - id: roll_stop_padding1
        size: _root.header.ch1_skip
        if: _root.header.ch[0].enabled

      - id: sentinel_between_datasets
        type: u4
        doc: "[0x04, 0x00, 0x04, 0x00]"
        if: _root.header.ch[0].enabled

      - id: ch2
        size: _root.header.ch2_points
        if: _root.header.ch[1].enabled

      - id: roll_stop_padding2
        size: _root.header.ch1_skip
        if: _root.header.ch[1].enabled

      - id: logic
        doc: Not clear where the LA length is stored assume same as ch1_points
        type: u2
        repeat: expr
        repeat-expr: "_root.header.logic.enabled ? _root.header.ch1_points: 0"


enums:
  bandwidth_enum:
    0: no_limit
    1: mhz_20
    2: mhz_100
    3: mhz_200
    4: mhz_250

  coupling_enum:
    0: dc
    1: ac
    2: gnd

  filter_enum:
    0: low_pass
    1: high_pass
    2: band_pass
    3: band_reject

  source_enum:
    0: ch1
    1: ch2
    2: ext
    3: ext5
    5: ac_line
    7: dig_ch

  trigger_mode_enum:
    0: edge
    1: pulse
    2: slope
    3: video
    4: alt
    5: pattern
    6: duration

  unit_enum:
    0: w
    1: a
    2: v
    3: u
