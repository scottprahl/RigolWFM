meta:
  id: wfm1000b
  title: Rigol DS1024B oscilloscope waveform file format
  file-extension: wfm
  endian: le

doc: |
  This was put together based on an excel header list of unknown provenance.
  It has been tested with a handful of different files.  The offset to the
  data seems correct and the channel coupling is untested.

instances:
  header:
    pos: 0
    type: header

types:
  header:
    seq:
      - id: magic            # 00 => file offset in decimal
        contents: [0xa5, 0xa5, 0xa4, 0x01]
      - id: scopetype        # 04
        type: str
        size: 8
        terminator: 0
        encoding: UTF-8
      - id: unknown_1        # 08
        size: 44
      - id: adcmode          # 52
        type: u1
      - id: unknown_2        # 53
        size: 3
      - id: points           # 56
        type: u4
      - id: active_channel   # 64
        type: u1
      - id: unknown_3        # 65
        size: 3
      - id: ch               # 68, 92, 116, 140
        type: channel_header
        repeat: expr
        repeat-expr: 4
      - id: time_scale       # 164 (in picoseconds)
        type: u8
      - id: time_offset      # 172 (in picoseconds)
        type: s8
      - id: sample_rate_hz   # 180
        type: f4
      - id: time_scale_stop  # 184
        type: u8
      - id: time_scale_offset  # 192
        type: s8
      - id: unknown_4        # 200
        type: u4
        repeat: expr
        repeat-expr: 4
      - id: coupling_ch12    # 212
        type: u1
      - id: coupling_ch34    # 213
        type: u1
      - id: unknown_5        # 216
        size: 4
      - id: trigger_mode     # 222
        type: u1
        enum: trigger_mode_enum
      - id: unknown_6        # 221
        type: u1
      - id: trigger_source   # 222
        type: u1
        enum: trigger_source_enum

    instances:
      seconds_per_point:
        value: 1.0/sample_rate_hz
      ch1:
        io: _root._io
        pos: 420
        size: points
        if: ch[0].enabled
      ch2:
        io: _root._io
        pos: 420 + _root.header.points
        size: points
        if: ch[1].enabled
      ch3:
        io: _root._io
        pos: 420 + _root.header.points * 2
        size: points
        if: ch[2].enabled
      ch4:
        io: _root._io
        pos: 420 + _root.header.points * 3
        size: points
        if: ch[3].enabled


  channel_header:   # 24 bytes total
    seq:
      - id: scale_display    # 68, 92, 116
        type: s4
      - id: shift_display    # 72, 96, 120
        type: s2
      - id: unknown1         # 74, 98
        size: 2
      - id: probe_value      # 76, 100
        type: f4
      - id: probe_type       # 80, 104
        type: s1
      - id: invert_disp_val  # 81, 105
        type: u1
      - id: enabled_val      # 82, 106
        type: u1
      - id: invert_m_val     # 83, 107
        type: u1
      - id: scale_measured   # 84, 108
        type: s4
      - id: shift_measured   # 88, 112
        type: s2
      - id: time_delayed     # 90, 114
        type: u1
      - id: unknown2         # 91, 114
        size: 1
    instances:
      inverted:
        value: "invert_m_val != 0 ? true : false"
      enabled:
        value: "enabled_val != 0 ? true : false"
      volt_per_division:
        value: "inverted ?
                -1.0e-6 * scale_measured * probe_value:
                +1.0e-6 * scale_measured * probe_value"
      volt_scale:
        value: volt_per_division/25.0
      volt_offset:
        value: shift_measured * volt_scale
      time_scale:
        value: _root.header.time_scale
      time_offset:
        value: _root.header.time_offset
      unit:
        value: "unit_enum::v"

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

  machine_mode_enum:
    0: ds1000b
    1: ds1000c
    2: ds1000e
    3: ds1000z
    4: ds2000
    5: ds4000
    6: ds6000

  unit_enum:
    0: w
    1: a
    2: v
    3: u
