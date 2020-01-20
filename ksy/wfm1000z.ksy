meta:
  id: wfm1000z
  title: Rigol DS1000Z oscilloscope waveform file format
  file-extension: wfm
  endian: le

doc: |
  Rigol DS1000Z scope .wmf file format.

instances:
  header:
    pos: 0
    type: file_header
  info:
    pos: 64
    type: wfm_header
  data:
    pos: 304 + _root.info.setup_size + _root.info.horizontal_size
    type: raw_data

types:
  file_header:
    seq:
      - id: magic
        contents: [0x01,0xff,0xff,0xff]
      - id: structure_id
        type: u2
      - id: structure_size
        contents: [0x38]
      - id: model_number
        type: str
        size: 20
        terminator: 0
        encoding: UTF-8
      - id: firmware_version
        type: str
        size: 20
        terminator: 0
        encoding: UTF-8
      - id: block
        contents: [0x00,0x01]
      - id: file_version
        type: u2

  wfm_header:
    seq:
      - id: time_scale_ps
        type: u8
      - id: time_offset_ps
        type: s8
      - id: crc
        type: u4
      - id: structure_size
        contents: [0xd8, 0x00]
      - id: structure_version
        type: u2
      - id: unused_bits_1
        type: b4
      - id: ch4_enabled
        type: b1
      - id: ch3_enabled
        type: b1
      - id: ch2_enabled
        type: b1
      - id: ch1_enabled
        type: b1
      - id: unused_mask_bytes
        size: 3
      - id: ch1_offset
        type: u4
      - id: ch2_offset
        type: u4
      - id: ch3_offset
        type: u4
      - id: ch4_offset
        type: u4
      - id: la_offset
        type: u4
      - id: acq_mode
        type: u1
        enum: acq_mode_enum
      - id: average_time
        type: u1
      - id: sample_mode
        contents: [0x00]
      - id: time_mode
        type: u1
        enum: time_mode_enum
      - id: memory_depth
        type: u4
      - id: sample_rate_ghz
        type: f4

      - id: ch1
        type: channel_head

      - id: ch2
        type: channel_head

      - id: ch3
        type: channel_head

      - id: ch4
        type: channel_head

      - id: la_parameters
        size: 12

      - id: setup_size
        type: u4
      - id: setup_offset
        type: u4
      - id: horizontal_size
        type: u4
      - id: horizontal_offset
        type: u4

    instances:
      ch1_int:
        value: "ch1_enabled ? 1 : 0"
      ch2_int:
        value: "ch2_enabled ? 1 : 0"
      ch3_int:
        value: "ch3_enabled ? 1 : 0"
      ch4_int:
        value: "ch4_enabled ? 1 : 0"
      total_channels:
        value: ch1_int + ch2_int + ch3_int + ch4_int
      stride:
        value: "total_channels == 3 ? 4 : total_channels"
      points:
        value: memory_depth/stride
      sample_rate: 
        value: sample_rate_ghz * 1e9
      time_scale: 
        value: time_scale_ps * 1e-12
      time_offset: 
        value: time_offset_ps * 1e-12
      delta_t: 
        value: 1/sample_rate

  channel_head:
    seq:
      - id: unused_bits_1
        type: b7
      - id: enabled
        type: b1

      - id: coupling
        type: u1
        enum: coupling_enum
      - id: bandwidth_limit
        type: u1
        enum: bandwidth_enum
      - id: probe_type
        type: u1
      - id: probe_ratio
        type: u1
        enum: probe_enum
      - id: unused
        size: 3
      - id: scale
        type: f4
      - id: shift
        type: f4
      - id: unused_bits_2
        type: b7
      - id: inverted
        type: b1
      - id: unknown_2
        size: 11

  channel_subhead:
    seq:
      - id: unknown_1
        size: 3
      - id: unused_bits_1
        type: b7
      - id: enabled
        type: b1
      - id: unknown_2
        size: 7
      - id: unused_bits_2
        type: b7
      - id: inverted
        type: b1
      - id: unknown_3
        size: 10
      - id: probe_attenuation
        type: s8
      - id: unknown_4
        size: 16
      - id: label
        type: str
        size: 4
        terminator: 0
        encoding: UTF-8
      - id: unknown_5
        size: 10

  raw_data:
    seq:
      - id: raw1
        type: u1
        repeat: expr
        repeat-expr: _root.info.points
        if: _root.info.stride == 1

      - id: raw2
        type: u2
        repeat: expr
        repeat-expr: _root.info.points
        if: _root.info.stride == 2

      - id: raw4
        type: u4
        repeat: expr
        repeat-expr: _root.info.points
        if: _root.info.stride == 4

enums:
  acq_mode_enum:
    0: normal
    1: peak
    2: average
    3: high_resolution

  time_mode_enum:
    0: yt
    1: xy
    2: roll

  coupling_enum:
    0: dc
    1: ac
    2: gnd

  bandwidth_enum:
    0: twenty_mhz
    1: off

  probe_enum:
    0: x0_01
    1: x0_02
    2: x0_05
    3: x0_1
    4: x0_2
    5: x0_5
    6: x1
    7: x2
    8: x5
    9: x10
    10: x20
    11: x50
    12: x100
    13: x200
    14: x500
    15: x1000


