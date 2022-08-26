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

      - id: model_number
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
        repeat-expr: 2

      - id: ch
        type: channel_header
        repeat: expr
        repeat-expr: 4

      - id: unknown_33
        type: u4
        repeat: expr
        repeat-expr: 6

      - id: mem_depth_2
        type: u4
      - id: unknown_37
        size: 4
      - id: mem_depth
        type: u4

      - id: unknown_38
        type: u4
        repeat: expr
        repeat-expr: 9
      - id: bytes_per_channel_1
        type: u4
      - id: bytes_per_channel_2
        type: u4
      - id: unknown_42
        type: u4
        repeat: expr
        repeat-expr: 41
      - id: total_samples
        type: u4
      - id: unknown_57
        type: u4
        repeat: expr
        repeat-expr: 4
      - id: mem_depth_type
        type: u1
        enum: mem_depth_enum
      - id: unknown_60
        size: 27
      - id: time
        type: time_header

    instances:
      len_raw_1:
        value: "enabled.channel_1 ? mem_depth : 0"
      len_raw_2:
        value: "enabled.channel_2 ? mem_depth : 0"
      len_raw_3:
        value: "enabled.channel_3 ? mem_depth : 0"
      len_raw_4:
        value: "enabled.channel_4 ? mem_depth : 0"
      vertical_scale_factor:
        value: "model_number.substring(2, 3) == '2' ? 25 : 32"
      seconds_per_point:
        value: 1/sample_rate_hz
      time_scale:
        value: 1.0e-12 * time.time_per_div_ps
      time_offset:
        value: 1.0e-12 * time.offset_per_div_ps
      points:
        value: mem_depth

      raw_1:
        io: _root._io
        pos: position.channel_1
        size: len_raw_1
        if: enabled.channel_1
      raw_2:
        io: _root._io
        pos: position.channel_2
        size: len_raw_2
        if: enabled.channel_2
      raw_3:
        io: _root._io
        pos: position.channel_3
        size: len_raw_3
        if: enabled.channel_3
      raw_4:
        io: _root._io
        pos: position.channel_4
        size: len_raw_4
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
      - id: index
        type: u4
      - id: time_per_div_ps
        type: u4
      - id: unknown_3a
        size: 4
      - id: offset_per_div_ps
        type: u8
      - id: unknown_4
        size: 16
      - id: offset_ps
        type: u8
      - id: unknown_5
        size: 16
      - id: unknown_6
        type: u2
      - id: unknown_7
        type: u1

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

  channel_header:
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
        enum: probe_type_enum

      - id: probe_ratio
        type: u1
        enum: probe_ratio_enum

      - id: probe_diff
        type: u1
        enum: probe_enum

      - id: probe_signal
        type: u1
        enum: probe_enum

      - id: probe_impedance
        type: u1
        enum: impedance_enum

      - id: volt_per_division
        type: f4
      - id: volt_offset
        type: f4
      - id: inverted_val
        type: u1
      - id: unit
        type: u1
        enum: unit_enum
      - id: filter_enabled
        type: u1
      - id: filter_type
        type: u1
        enum: filter_enum
      - id: filter_high
        type: u4
      - id: filter_low
        type: u4
    instances:
      inverted:
        value: "inverted_val != 0 ? true : false"
      enabled:
        value: "enabled_val != 0 ? true : false"
      probe_value:
        value: "(probe_ratio == probe_ratio_enum::x0_01 ? 0.01 :
                 probe_ratio == probe_ratio_enum::x0_02 ? 0.02 :
                 probe_ratio == probe_ratio_enum::x0_05 ? 0.05 :
                 probe_ratio == probe_ratio_enum::x0_1 ? 0.1 :
                 probe_ratio == probe_ratio_enum::x0_2 ? 0.2 :
                 probe_ratio == probe_ratio_enum::x0_5 ? 0.5 :
                 probe_ratio == probe_ratio_enum::x1 ? 1.0 :
                 probe_ratio == probe_ratio_enum::x2 ? 2.0 :
                 probe_ratio == probe_ratio_enum::x5 ? 5.0 :
                 probe_ratio == probe_ratio_enum::x10 ? 10.0 :
                 probe_ratio == probe_ratio_enum::x20 ? 20.0 :
                 probe_ratio == probe_ratio_enum::x50 ? 50.0 :
                 probe_ratio == probe_ratio_enum::x100 ? 100.0 :
                 probe_ratio == probe_ratio_enum::x200 ? 200.0 :
                 probe_ratio == probe_ratio_enum::x500 ? 500.0 : 1000.0)"
      volt_signed:
        value: "inverted ?
                -1.0 * volt_per_division:
                +1.0 * volt_per_division"
      volt_scale:
        value: "_root.header.model_number.substring(2, 3) == '2' ?
                                      volt_signed/25.0 :
                                      volt_signed/32.0"

enums:

  acquisition_enum:
    0: normal
    1: average
    2: peak
    3: high_resolution

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

  impedance_enum:
    0: ohm_50
    1: ohm_1meg

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

  probe_enum:
    0: single
    1: diff

  probe_ratio_enum:
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

  probe_type_enum:
    0: normal_type
    1: differential

  time_enum:
    0: yt
    1: xy
    2: roll

  unit_enum:
    0: w
    1: a
    2: v
    3: u
