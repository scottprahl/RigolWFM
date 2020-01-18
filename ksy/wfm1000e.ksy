meta:
  id: wfm1102e
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
    type: raw_data

types:
  header:
    seq:
      - id: magic
        contents: [0xa5,0xa5]
      - id: blank_1
        contents: [0x00,0x00]
      - id: unused_1
        contents: [0x00,0x00,0x00,0x00]
      - id: unused_2
        contents: [0x00,0x00,0x00,0x00]
      - id: unused_3
        contents: [0x00,0x00,0x00,0x00]
      - id: adc_mode
        type: u1
      - id: padding_2
        contents: [0x00,0x00,0x00]
      - id: roll_stop
        type: u4
      - id: unused_4
        contents: [0x00,0x00,0x00,0x00]
      - id: npts_1
        type: u4
      - id: active_channel
        type: u1
      - id: padding_3
        contents: [0x00,0x00,0x00]
      - id: ch1
        type: channel_header
      - id: padding_4
        contents: [0x00,0x00]
      - id: ch2
        type: channel_header
      - id: time_delay
        type: u1
      - id: padding_5
        contents: [0x00]
      - id: time1
        type: time_header
      - id: logic
        type: logic_analyzer_header
      - id: trigger_mode
        type: u1
      - id: trigger1
        type: trigger_header
      - id: trigger2
        type: trigger_header
      - id: padding_6
        contents: [0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00]
      - id: npts_2
        type: u4
      - id: time2
        type: time_header
      - id: la_sample_rate
        doc: This does not exist in early file formats, unsure how to detect if missing
        type: f4
        repeat: expr
        repeat-expr: 1

  channel_header:
    seq:
      - id: scale_d
        type: s4
      - id: shift_d
        type: s2
      - id: unknown_1
        size: 2
      - id: probe
        type: f4
      - id: invert_d
        type: u1
      - id: enabled
        type: u1
      - id: invert_m
        type: u1
      - id: unknown_2
        size: 1
      - id: scale_m
        type: s4
      - id: shift_m
        type: s2

  time_header:
    seq:
      - id: scale_d
        type: s8
      - id: delay_d
        type: s8
      - id: sample_rate
        type: f4
      - id: scale_m
        type: s8
      - id: delay_m
        type: s8

  trigger_header:
    seq:
      - id: mode
        type: u1
      - id: source
        type: u1
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
        contents: [0x00,0x00]
      - id: pulse_width
        type: f4
      - id: slope_type
        type: u1
      - id: padding_3
        contents: [0x00,0x00,0x00]
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
      - id: enabled
        doc: Should be 0 or 1
        type: u1
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
        type: u1
        if: _root.header.ch1.enabled > 0
        repeat: expr
        repeat-expr: _root.header.ch1.enabled

      - id: ch2
        doc: Sometimes npts_2 is not written, use npts_1 in this case.
        type: u1
        if: _root.header.ch2.enabled > 0
        repeat: expr
        repeat-expr: '_root.header.npts_2 > 0 ? _root.header.npts_2 : _root.header.npts_1'
        
      - id: logic
        doc: Not clear where the LA length is stored assume same as npts_1
        type: u1
        repeat: expr
        repeat-expr: '_root.header.logic.enabled>0 ? _root.header.npts_1 : 0'

enums:
  probe_attenuation:
    0x3F80: x1
    0x4120: x10
    0x42C8: x100
    0x43FA: x500
    0x447A: x1000

  source:
    0 : ch1
    1 : ch2
    2 : ext
    3 : ext5
    5 : ac_line
    7 : dig_ch

  mode:
    0 : edge
    1 : pulse
    2 : slope
    3 : video
    4 : alt
    5 : pattern
    6 : duration
