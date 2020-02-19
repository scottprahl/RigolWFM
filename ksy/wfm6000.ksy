meta:
  id: wfm6000
  file-extension: wfm
  endian: le

instances:
  header:
    pos: 0
    type: header
    WfmInfoStru 56 funcStoreBlockStru 416 CTag 428 Setup 436
  data:
    pos: 20972
    type: raw_data

types:
  header:
    seq:
      - id: magic
        contents: [0xa5,0xa5]
        
      - id: structure_size
        type: u2
        doc: size of this structure, should be 0x38
        
      - id: model
        size: 20
        type: str
        terminator: 0
        encoding: ascii
        
      - id: version
        size: 20
        type: str
        terminator: 0
        encoding: ascii
        
      - id: enabled
        type: channel_mask
        
      - id: unknown_2
        size: 3
        
      - id: unknown_3
        type: u4
        repeat: expr
        repeat-expr: 7
        
      - id: mem_depth
        type: u4
        
      - id: sample_rate_hz
        type: f4
        
      - id: unknown_8
        size: 4
        
      - id: time_per_div_ps
        type: u4
        
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
        repeat-expr: 5
        
      - id: mem_depth_2 
        type: u4
        doc: "Seems to always be a copy of mem_depth"
      - id: unknown_37
        size: 4
        doc: "[0x00,0x00,0x00,0x00]"
      - id: mem_depth_3
        type: u4
        doc: "Seems to always be a copy of mem_depth"
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
        doc: "[0x00,0x00,0x00,0x00]"
      - id: unknown_50
        type: u4
      - id: unknown_51
        size: 8
        doc: "[0x00,0x00,0x00,0x06,0x00,0x00,0x00,0x00]"
      - id: unknown_52
        type: u4
        repeat: expr
        repeat-expr: 4
      - id: unknown_53
        size: 16
        doc: "[1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]"
      - id: unknown_54
        size: 16
        doc: "[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]"
      - id: unknown_55
        type: u4
        repeat: expr
        repeat-expr: 4
      - id: total_samples
        type: u4
      - id: unknown_56
        size: 4
        doc: "[0,80,0,0]"
      - id: unknown_57
        type: u4
        repeat: expr
        repeat-expr: 2
      - id: unknown_59
        size: 4
        doc: "[0,0,0,0]"
      - id: mem_depth_enum
        type: u1
        enum: mem_depth
      - id: unknown_60
        size: 11
        doc: "[0,0,0,0,32,0,0,4,0,0,0]"
      - id: unknown_61
        size: 16
        doc: "[0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0]"
      - id: time
        type: time_header
      - id: channel
        type: channel_header
        repeat: expr
        repeat-expr: 4
    instances:
      seconds_per_point:
        value: 1/sample_rate_hz
      time_scale:
        value: 1.0e-12 * _root.header.time.time_per_div_ps
      time_delay:
        value: 1.0e-12 * _root.header.time.delay_ps
      points:
        value: _root.header.mem_depth
        
  time_header:
    seq:
      - id: unknown_1
        type: u2
      - id: unknown_2
        size: 10
        doc: "[0,0,6,0,0,0,26,0,0,0]"
      - id: index
        type: u4
      - id: time_per_div_ps
        type: u4
      - id: unknown_3a
        size: 4
      - id: unknown_3b
        type: u4
      - id: unknown_4
        type: u4
        repeat: expr
        repeat-expr: 3
      - id: delay_ps
        type: u8
      - id: unknown_5
        type: u4
        repeat: expr
        repeat-expr: 4
      - id: unknown_6
        type: u2
      - id: unknown_7
        type: u1
        
  channel_header:
    seq:
      - id: enabled
        type: u1
      - id: coupling
        type: u1
        enum: coupling_enum
      - id: bandwidth_limit
        type: u1
        enum: bandwidth_enum
      - id: probe_type
        size: u1
        enum: probe_type_enum
      - id: probe_ratio
        size: u1
        enum: probe_ratio_enun
      - id: probe_diff
        type: u1
        enum: probe_enum
      - id: probe_signal
        type: u1
        enum: probe_enum
      - id: probe_impedance
        type: u1
        enum: impedance_enum

      - id: scale
        type: f4
      - id: offset
        type: f4
      - id: invert
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
      volts_per_division:
        value: 1e-6 * scale
        doc: Voltage scale in volts per division.
      volts_offset:
        value: 1e-6 * offset
        doc: Voltage offset in volts.  
        
  channel_subheader:
    seq:
      - id: unknown_0
        type: u4
      - id: unknown_1
        type: f4
      - id: unknown_2
        type: u4
      - id: unknown_3
        type: u4
      - id: unknown_4
        type: u4
        doc: "[0xc0,0xe1,0xe4,0x00] or 15M"
      - id: unknown_5
        type: u4
        doc: "[0x00,0x2d,0x31,0x01] or 20M"
      - id: unknown_6
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
        
  raw_data:
    seq:
      - id: channel_1
        type: u1
        repeat: expr
        repeat-expr: _root.header.mem_depth
        if: _root.header.enabled.channel_1
      - id: padding_1
        size: _root.header.bytes_per_channel_1 - _root.header.mem_depth
        if: _root.header.enabled.channel_1
        
      - id: channel_2
        type: u1
        repeat: expr
        repeat-expr: _root.header.mem_depth
        if: _root.header.enabled.channel_2
      - id: padding_2
        size: _root.header.bytes_per_channel_1 - _root.header.mem_depth
        if: _root.header.enabled.channel_2
        
      - id: channel_3
        type: u1
        repeat: expr
        repeat-expr: _root.header.mem_depth
        if: _root.header.enabled.channel_3
      - id: padding_3
        size: _root.header.bytes_per_channel_1 - _root.header.mem_depth
        if: _root.header.enabled.channel_3
        
      - id: channel_4
        type: u1
        repeat: expr
        repeat-expr: _root.header.mem_depth
        if: _root.header.enabled.channel_4
      - id: padding_4
        size: _root.header.bytes_per_channel_1 - _root.header.mem_depth
        if: _root.header.enabled.channel_4

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

  coupling_enum:
    0: dc
    1: ac
    2: gnd

  impedance_enum:
    0: ohm_50
    1: ohm_1meg

  bandwidth_enum:
    0: none
    1: mhz_20
    2: mhz_100
    3: mhz_200
    4: mhz_250

  probe_type_enum:
    0: normal
    1: diff

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

  unit_enum:
    0: watts
    1: amps
    2: volts
    3: unknown
    
  mem_depth:
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
