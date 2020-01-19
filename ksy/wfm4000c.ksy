meta:
  id: wfm4000c
  file-extension: wfm
  endian: le

instances:
  header:
    pos: 0
    type: header
  data:
    pos: 20972
    type: channel_data

types:
  header:
    seq:
      - id: magic
        contents: [0xa5,0xa5,0x38,0x00]
      - id: scope_info
        type: scope_info
      - id: unknown_1
        type: u4
        repeat: expr
        repeat-expr: 6
      - id: enabled
        type: channel_mask
      - id: unknown_2
        size: 3
      - id: unknown_3
        type: u4
        repeat: expr
        repeat-expr: 6
      - id: unknown_2_p7
        size: 4
        doc: "[0x00,0x00,0x00,0x00]"
      - id: mem_depth
        type: u4
      - id: samp_rate
        type: f4
      - id: unknown_8
        size: 4
        doc: "[0x00,0x00,0x00,0x00]"
      - id: time_per_div_ps
        type: u4
      - id: unknown_9
        type: u4
        repeat: expr
        repeat-expr: 5
      - id: unknown_11
        type: f4
      - id: unknown_12
        type: u4
        repeat: expr
        repeat-expr: 2
      - id: unknown_13
        size: 4
        doc: "[0xc0,0xe1,0xe4,0x00]"
      - id: unknown_14
        size: 4
        doc: "[0x00,0x2d,0x31,0x01]"
      - id: unknown_15
        type: u4
        repeat: expr
        repeat-expr: 2
      - id: unknown_17
        type: f4
      - id: unknown_18
        type: u4
        repeat: expr
        repeat-expr: 2
      - id: unknown_19
        type: u4
        doc: "[0xc0,0xe1,0xe4,0], 15M"
      - id: unknown_20
        type: u4
        doc: "[0x00,0x2d,0x31,0x01], 20M"
      - id: unknown_21
        type: u4
        repeat: expr
        repeat-expr: 2
      - id: unknown_22
        type: f4
      - id: unknown_23
        type: u4
        repeat: expr
        repeat-expr: 2
      - id: unknown_24
        type: u4
        doc: "[0xc0,0xe1,0xe4,0x00] or 15M"
      - id: unknown_25
        type: u4
        doc: "[0x00,0x2d,0x31,0x01] or 20M"
      - id: unknown_26
        type: u4
        repeat: expr
        repeat-expr: 2
      - id: unknown_27
        type: f4
      - id: unknown_28
        type: f4
      - id: unknown_29
        size: 4
      - id: unknown_30
        type: u4
        doc: "[0xc0,0xe1,0xe4,0x00] or 15M"
      - id: unknown_31
        type: u4
        doc: "[0x00,0x2d,0x31,0x01] or 20M"
      - id: unknown_32
        size: 4
        doc: "[0x00,0x00,0x00,0x00]"
      - id: unknown_33
        size: 4
        doc: "[0x78,0x05,0x00,0x00]"
      - id: unknown_34
        size: 4
        doc: "[0x78,0x05,0x00,0x00]"
      - id: unknown_35
        size: 8
        doc: "[0x00,0x50,0x00,0x00,0xe4,0x01,0x00,0x00]"
      - id: unknown_36
        size: 4
        doc: "[0xec,0x51,0x00,0x00]"
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
      - id: time_header
        type: time_header
      - id: channel_header
        type: channel_header
        repeat: expr
        repeat-expr: 4
        
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
      - id: unknown_6
        size: 14
        doc: "[0,0,0,0,0,0,0,0,0,0,0,0,1,0]"
      - id: unknown_7
        type: u2
        
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
        doc: "[0x00,0x00]"
      - id: probe_scale
        type: u1
        enum: probe_scale
      - id: unknown_3
        size: 2
        doc: "[0x01,0x00]"
      - id: probe_impedance
        type: u1
        enum: probe_impedance
      - id: scale_index
        type: u1
        enum: channel_scale
      - id: unknown_4
        size: 1
        doc: "[0x02]"
      - id: label
        type: str
        encoding: ascii
        size: 10
      - id: unknown_5
        size: 12
        doc: "[0,0,0,0,0,0,0,0,0,0,0,0]"
      - id: unknown_6
        type: u4
        doc: "[0xc0,0xe1,0xe4,0x00] or 15M"
      - id: unknown_7
        type: u4
        doc: "[0x00,0x2d,0x31,0x01] or 20M"
      - id: unknown_8
        type: u4
        doc: "[0x00,0x00,0x00,0x00]"
      - id: scale_microvolt
        type: u4
      - id: offset_uv
        type: s4
      - id: unknown_9
        type: s2
      - id: unknown_10
        size: 2
        
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
        
  scope_info:
    seq:
      - id: serial
        size: 16
        type: str
        terminator: 0
        encoding: ascii
      - id: unknown_1
        size: 4
      - id: firmware_version
        size: 16
        type: str
        terminator: 0
        encoding: ascii
        
  channel_data:
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
  probe_impedance:
    1: ohm_1meg
    0: ohm_50
  bandwidth_limit:
    0: none
    1: mhz_50
    2: mhz_100
    3: mhz_200
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
