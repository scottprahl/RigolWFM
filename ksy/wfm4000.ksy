meta:
  id: wfm4000
  file-extension: wfm
  endian: le

instances:
  header:
    pos: 0
    type: header

types:
  header:
    seq:
      - id: magic
        contents: [0xa5, 0xa5, 0x38, 0x00]
        doc: The last two bytes is the size of the header 0x38=56

      - id: serial_number
        size: 20
        type: str
        terminator: 0
        encoding: ascii

      - id: firmware_version
        size: 20
        type: str
        terminator: 0
        encoding: ascii

      - id: unknown_1
        type: u4
        repeat: expr
        repeat-expr: 5

      - id: enabled
        type: channel_mask
        doc: one byte with lower bits indicating which channels are active

      - id: unknown_2
        size: 3

      - id: position
        type: position_type

      - id: unknown_3
        type: u4

      - id: unknown_4
        type: u4

      - id: unknown_5
        type: u4

      - id: mem_depth_1
        type: u4

      - id: sample_rate_hz
        type: f4

      - id: unknown_8
        type: u4

      - id: time_per_div_ps
        type: u8

      - id: unknown_9
        type: u4
        repeat: expr
        repeat-expr: 4

      - id: channel_subhead
        type: channel_subheader
        repeat: expr
        repeat-expr: 4

      - id: unknown_33
        type: u4
        repeat: expr
        repeat-expr: 4

      - id: mem_depth_2
        type: u4
      - id: unknown_37
        size: 4
        doc: "[0x00, 0x00, 0x00, 0x00]"
      - id: mem_depth
        type: u4

      - id: unknown_38
        type: u4
        repeat: expr
        repeat-expr: 7
      - id: unknown_40_data_len_p
        type: u4
        doc: "Seems to be related to the memory depth"
      - id: unknown_41_data_len_p
        type: u4
        doc: "Seems to be related to the memory depth"
      - id: bytes_per_channel_1
        type: u4
      - id: bytes_per_channel_2
        type: u4
        doc: "Copy of the first bytes_per_channel_1?"
      - id: unknown_42
        type: u4
        repeat: expr
        repeat-expr: 21
      - id: unknown_49
        size: 4
        doc: "[0x00, 0x00, 0x00, 0x00]"
      - id: unknown_50
        type: u4
      - id: unknown_51
        size: 8
        doc: "[0x00, 0x00, 0x00, 0x06, 0x00, 0x00, 0x00, 0x00]"
      - id: unknown_52
        type: u4
        repeat: expr
        repeat-expr: 4
      - id: unknown_53
        size: 16
        doc: "[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]"
      - id: unknown_54
        size: 16
        doc: "[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]"
      - id: unknown_55
        type: u4
        repeat: expr
        repeat-expr: 4
      - id: total_samples
        type: u4
      - id: unknown_56
        size: 4
        doc: "[0, 80, 0, 0]"
      - id: unknown_57
        type: u4
        repeat: expr
        repeat-expr: 2
      - id: unknown_59
        size: 4
        doc: "[0, 0, 0, 0]"
      - id: mem_depth_type
        type: u1
        enum: mem_depth_enum
      - id: unknown_60
        size: 11
        doc: "[0, 0, 0, 0, 32, 0, 0, 4, 0, 0, 0]"
      - id: unknown_61
        size: 16
        doc: "[0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0]"
      - id: time
        type: time_header
      - id: channel
        type: channel_header
        repeat: expr
        repeat-expr: 4
    instances:
      vertical_scale_factor:
        value: 'serial_number.substring(2, 3) == "2" ? 25 : 32'
      seconds_per_point:
        value: 1/sample_rate_hz
      time_scale:
        value: 1.0e-12 * time.time_per_div_ps
      time_delay:
        value: 1.0e-12 * time.delay_per_div_ps
      points:
        value: mem_depth

      raw1:
        pos: position.channel_1
        size: mem_depth
        if: enabled.channel_1
      raw2:
        pos: position.channel_2
        size: mem_depth
        if: enabled.channel_2
      raw3:
        pos: position.channel_3
        size: mem_depth
        if: enabled.channel_3
      raw4:
        pos: position.channel_4
        size: mem_depth
        if: enabled.channel_4

  position_type:
    seq:
      - id: channel_1
        type: u4
      - id: channel_2
        type: u4
      - id: channel_3
        type: u4
      - id: channel_4
        type: u4

  time_header:
    seq:
      - id: unknown_1
        type: u2
      - id: unknown_2
        size: 10
        doc: "[0, 0, 6, 0, 0, 0, 26, 0, 0, 0]"
      - id: index
        type: u4
      - id: time_per_div_ps
        type: u4
      - id: unknown_3a
        size: 4
      - id: delay_per_div_ps
        type: u8
      - id: unknown_4
        size: 16
      - id: delay_ps
        type: u8
      - id: unknown_5
        size: 16
      - id: unknown_6
        type: u2
      - id: unknown_7
        type: u1

  channel_header:
    seq:
      - id: unknown_1
        size: 1
        doc: "[0]"
      - id: coupling
        type: u1
        enum: channel_coupling
      - id: bandwidth_limit
        type: u1
        enum: bandwidth_limit
      - id: unknown_2
        size: 2
        doc: "[0x00, 0x00]"
      - id: probe_scale
        type: u1
        enum: probe_scale
      - id: unknown_3
        size: 2
        doc: "[0x01, 0x00]"
      - id: probe_impedance
        type: u1
        enum: probe_impedance_enum
      - id: scale_index
        type: u1
        enum: channel_scale
      - id: unknown_4
        size: 1
        doc: "[0x02]"
      - id: label
        size: 10
        type: str
        terminator: 0
        encoding: ascii
      - id: unknown_6
        type: u4
        doc: "[0xc0, 0xe1, 0xe4, 0x00] or 15M"
      - id: unknown_7
        type: u4
        doc: "[0x00, 0x2d, 0x31, 0x01] or 20M"
      - id: unknown_8
        type: u4
        doc: "[0x00, 0x00, 0x00, 0x00]"
      - id: scale_microvolt
        type: u4
      - id: offset_microvolt
        type: s4
      - id: unknown_9
        type: s2
      - id: unknown_10
        size: 1
    instances:
      volts_per_division:
        value: 1e-6 * scale_microvolt
        doc: Voltage scale in volts per division.
      volts_offset:
        value: 1e-6 * offset_microvolt
        doc: Voltage offset in volts.

  channel_subheader:
    seq:
      - id: volt_scale
        type: f4
      - id: volt_offset
        type: f4
      - id: unknown_3
        type: u4
      - id: unknown_4
        type: u4
        doc: "[0xc0, 0xe1, 0xe4, 0x00] or 15M"
      - id: unknown_5
        type: u4
        doc: "[0x00, 0x2d, 0x31, 0x01] or 20M"
      - id: unknown_6
        type: u4
      - id: unknown_0
        type: u4

  channel_mask:
    seq:
      - id: unused
        type: b4
      - id: channel_4
        type: b1
      - id: channel_3
        type: b1
      - id: channel_2
        type: b1
      - id: channel_1
        type: b1


enums:
  channel_scale:
    0: mv_1
    1: mv_2
    2: mv_5
    3: mv_10
    4: mv_20
    5: mv_50
    6: mv_100
    7: mv_200
    8: mv_500
    9: mv_1000
    10: mv_2000
    11: mv_5000
  channel_coupling:
    0: dc
    1: ac
    2: gnd
  probe_scale:
    0: xp01
    1: xp02
    2: xp05
    3: xp1
    4: xp2
    5: xp5
    6: x1
    7: x2
    8: x5
    9: x10
    10: x20
    11: x50
    12: x100
  probe_impedance_enum:
    0: ohm_50
    1: ohm_1meg
  bandwidth_limit:
    0: none
    1: mhz_50
    2: mhz_100
    3: mhz_200
  mem_depth_enum:
    0: auto
    1: p_7k
    2: p_70k
    3: p_700k
    4: p_7m
    5: p_70m
    6: p_14k
    7: p_140k
    8: p_1m4
    9: p_14m
    10: p_140m
