meta:
  id: wfm1000z
  title: Rigol DS1000Z oscilloscope waveform file format
  file-extension: wfm
  endian: le

doc: |
  Rigol DS1000Z scope .wmf file format.

instances:
  preheader:
    pos: 0
    type: file_header
  header:
    pos: 64
    type: wfm_header
  data:
    pos: 304 + _root.header.setup_size + _root.header.horizontal_size
    type: raw_data

types:
  file_header:
    seq:
      - id: magic
        contents: [0x01, 0xff, 0xff, 0xff]
      - id: magic2
        type: u2
        doc: should be [0xa5, 0xa5] or [0xa5, 0xa6]
      - id: structure_size
        type: u2
        doc: should be 0x38
      - id: model_number
        type: str
        size: 20
        terminator: 0
        encoding: ascii
      - id: firmware_version
        type: str
        size: 20
        terminator: 0
        encoding: ascii
      - id: block
        contents: [0x01, 0x00]
      - id: file_version
        type: u2

  wfm_header:
    seq:
      - id: picoseconds_per_division
        type: u8
      - id: picoseconds_offset
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
      - id: ch1_file_offset
        type: u4
      - id: ch2_file_offset
        type: u4
      - id: ch3_file_offset
        type: u4
      - id: ch4_file_offset
        type: u4
      - id: la_offset
        type: u4
      - id: acq_mode
        type: u1
        enum: acquistion_enum
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

      - id: ch
        type: channel_head
        repeat: expr
        repeat-expr: 4

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
      sample_rate_hz:
        value: sample_rate_ghz * 1e9
      seconds_per_division:
        value: picoseconds_per_division * 1e-12
      time_offset:
        value: picoseconds_offset * 1e-12
      seconds_per_point:
        value: 1/sample_rate_hz

  channel_head:
    seq:
      - id: enabled_val
        type: u1
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
      - id: inverted_val
        type: u1
      - id: unit
        type: u1
        enum: unit_enum
      - id: unknown_2
        size: 10
    instances:
      inverted:
        value: "inverted_val != 0 ? true : false"
      enabled:
        value: "enabled_val != 0 ? true : false"
      probe_value:
        value: "(probe_ratio == probe_enum::x0_01 ? 0.01 :
                probe_ratio == probe_enum::x0_02 ? 0.02 :
                probe_ratio == probe_enum::x0_05 ? 0.05 :
                probe_ratio == probe_enum::x0_1 ? 0.1 :
                probe_ratio == probe_enum::x0_2 ? 0.2 :
                probe_ratio == probe_enum::x0_5 ? 0.5 :
                probe_ratio == probe_enum::x1 ? 1.0 :
                probe_ratio == probe_enum::x2 ? 2.0 :
                probe_ratio == probe_enum::x5 ? 5.0 :
                probe_ratio == probe_enum::x10 ? 10.0 :
                probe_ratio == probe_enum::x20 ? 20.0 :
                probe_ratio == probe_enum::x50 ? 50.0 :
                probe_ratio == probe_enum::x100 ? 100.0 :
                probe_ratio == probe_enum::x200 ? 200.0 :
                probe_ratio == probe_enum::x500 ? 500.0 :
                1000.0)"
      volt_per_division:
        value: "inverted ?
                -1.0 * scale * probe_value:
                +1.0 * scale * probe_value"
      volt_scale:
        value: volt_per_division/25.0
      volt_offset:
        value: shift * volt_scale

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
        repeat-expr: _root.header.points
        if: _root.header.stride == 1

      - id: raw2
        type: u2
        repeat: expr
        repeat-expr: _root.header.points
        if: _root.header.stride == 2

      - id: raw4
        type: u4
        repeat: expr
        repeat-expr: _root.header.points
        if: _root.header.stride == 4

enums:
  acquistion_enum:
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
    0: mhz_20
    1: no_limit

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

  unit_enum:
    0: watts
    1: amps
    2: volts
    3: unknown
