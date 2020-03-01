meta:
  id: wfm1000c
  title: Rigol DS1020C oscilloscope waveform file format
  file-extension: wfm
  endian: le

doc: |
  Rigol DS1020CD .wmf format abstracted from a Matlab script with the addition
  of a few fields found in a Pascal program.  Neither program really examines
  the header closely (meaning that they skip 26 bytes).

doc-ref: !
  The Matlab script is from
  https://www.mathworks.com/matlabcentral/fileexchange/18999-read-binary-rigol-waveforms
  The Pascal program is from
  https://sourceforge.net/projects/wfmreader/
  The DS4000 parser is from
  https://github.com/Cat-Ion/rigol-ds4000-wfm

instances:
  header:
    pos: 0
    type: header
  data:
    pos: 272
    type: raw_data

types:
  header:
    seq:
      - id: magic            # 00 (file pos)
        contents: [0xa5, 0xa5, 0x00, 0x00]
      - id: unknown_1        # 04
        type: u4
        repeat: expr
        repeat-expr: 6
      - id: points           # 28
        type: u4
      - id: active_channel   # 32
        type: u1
      - id: unknown_2        # 33
        size: 3
      - id: ch               # 36, 60
        type: channel_header
        repeat: expr
        repeat-expr: 2
      - id: time_scale       # 84
        type: u8
      - id: time_delay       # 92
        type: s8
      - id: sample_rate_hz   # 100
        type: f4
      - id: unknown_3        # 104
        type: u4
        repeat: expr
        repeat-expr: 9
      - id: unknown_4        # 140
        type: u2
      - id: trigger_mode     # 142
        type: u1
        enum: trigger_mode_enum
      - id: unknown_6        # 143
        size: 1
      - id: trigger_source   # 144
        type: u1
        enum: trigger_source_enum

    instances:
      seconds_per_point:
        value: 1.0/sample_rate_hz

  channel_header:   # 24 bytes total
    seq:
      - id: scale_display    # 36, 60
        type: s4
      - id: shift_display    # 40, 64
        type: s2
      - id: unknown_1        # 42, 66
        type: u1
      - id: unknown_2        # 43, 67
        type: u1
      - id: probe            # 44, 68
        type: f4
      - id: invert_disp_val  # 48, 72
        type: u1
      - id: enabled_val      # 49, 73
        type: u1
      - id: inverted_m_val   # 50, 74
        type: u1
      - id: unknown_3        # 51, 75
        size: 1
      - id: scale_orig       # 52, 76
        type: u4
      - id: position_orig    # 56, 80
        type: u4
      - id: scale_measured   # 52, 76
        type: s4
      - id: shift_measured   # 56, 80
        type: s2
    instances:
      inverted:
        value: "inverted_m_val != 0 ? true : false"
      enabled:
        value: "enabled_val != 0 ? true : false"
      volt_per_division:
        value: "inverted ?
                -1.0e-6 * scale_measured:
                +1.0e-6 * scale_measured"
      volt_scale:
        value: volt_per_division/25.0
      volt_offset:
        value: shift_measured * volt_scale

  raw_data:
    seq:
      - id: ch1
        type: u1
        repeat: expr
        repeat-expr: _root.header.points
        if: _root.header.ch[0].enabled

      - id: ch2
        type: u1
        repeat: expr
        repeat-expr: _root.header.points
        if: _root.header.ch[1].enabled

enums:
  trigger_source_enum:
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
