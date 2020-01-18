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
        contents: [ 165, 165, 56, 0 ]
      - id: scope_info
        type: scope_info
      - id: unk1
        type: u4
        repeat: expr
        repeat-expr: 6
      - id: channel_mask
        type: channel_mask
      - id: unk2
        size: 3
      - id: unk3
        type: u4
        repeat: expr
        repeat-expr: 6
      - id: unk2_p7_exp
        size: 4
        contents: [ 0, 0, 0, 0 ]
      - id: mem_depth
        type: u4
      - id: samp_rate
        type: f4
      - id: unk8_exp
        size: 4
        contents: [0,0,0,0]
      - id: time_per_div_ps
        type: u4
      - id: unk9
        type: u4
        repeat: expr
        repeat-expr: 5
      - id: unk11
        type: f4
      - id: unk12
        type: u4
        repeat: expr
        repeat-expr: 2
      - id: unk13_exp
        contents: [0xc0, 0xe1, 0xe4,0]
      - id: unk14_exp
        contents: [0, 0x2d, 0x31,1]
      - id: unk15
        type: u4
        repeat: expr
        repeat-expr: 2
      - id: unk17
        type: f4
      - id: unk18
        type: u4
        repeat: expr
        repeat-expr: 2
      - id: unk19_exp
        contents: [0xc0, 0xe1, 0xe4, 0] # u4: 15M
      - id: unk20_exp
        contents: [0, 0x2d, 0x31, 1] # u4: 20M
      - id: unk21_exp
        type: u4
        repeat: expr
        repeat-expr: 2
      - id: unk22
        type: f4
      - id: unk23
        type: u4
        repeat: expr
        repeat-expr: 2
      - id: unk24_exp
        contents: [0xc0, 0xe1, 0xe4, 0] # u4: 15M
      - id: unk25_exp
        contents: [0, 0x2d, 0x31, 1] # u4: 20M
      - id: unk26
        type: u4
        repeat: expr
        repeat-expr: 2
      - id: unk27
        type: f4
      - id: unk28
        type: f4
      - id: unk29_exp
        type: u4
      - id: unk30_exp
        contents: [0xc0, 0xe1, 0xe4, 0] # u4: 15M
      - id: unk31_exp
        contents: [0, 0x2d, 0x31, 1] # u4: 20M
      - id: unk32_exp
        size: 4
        contents: [0,0,0,0]
      - id: unk33_exp
        contents: [0x78, 5, 0, 0]
      - id: unk34_exp
        contents: [0x78, 5, 0, 0]
      - id: unk35_exp
        contents: [0, 80, 0, 0, 0xe4, 1, 0, 0]
      - id: unk36_exp
        contents: [0xec, 0x51, 0, 0]
      - id: mem_depth_2 # Seems to always be a copy of mem_depth
        type: u4
      - id: unk37_exp
        size: 4
        contents: [0,0,0,0]
      - id: mem_depth_3 # Seems to always be a copy of mem_depth
        type: u4
      - id: unk38
        type: u4
        repeat: expr
        repeat-expr: 7
      - id: unk40_data_len_p # Seems to be related to the memory depth
        type: u4
      - id: unk41_data_len_p # Seems to be related to the memory depth
        type: u4
      - id: bytes_per_channel_1
        type: u4
      - id: bytes_per_channel_2 # Copy of the first one?
        type: u4
      - id: unk42
        type: u4
        repeat: expr
        repeat-expr: 21
      - id: unk49_exp
        size: 4
        contents: [0,0,0,0]
      - id: unk50
        type: u4
      - id: unk51_exp
        contents: [0,0,0,6,0,0,0,0]
      - id: unk52
        type: u4
        repeat: expr
        repeat-expr: 4
      - id: unk53_exp
        contents: [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
      - id: unk54_exp
        contents: [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
      - id: unk55
        type: u4
        repeat: expr
        repeat-expr: 4
      - id: total_samples
        type: u4
      - id: unk56_exp
        contents: [0,80,0,0]
      - id: unk57
        type: u4
        repeat: expr
        repeat-expr: 2
      - id: unk59_exp
        size: 4
        contents: [0,0,0,0]
      - id: mem_depth_enum
        type: u1
        enum: mem_depth
      - id: unk60_exp
        size: 11
#  contents: [0,0,0,0,32,0,0,4,0,0,0]
      - id: unk61_exp
        size: 16
#        contents: [0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0]
      - id: time_header
        type: time_header
      - id: channel_header
        type: channel_header
        repeat: expr
        repeat-expr: 4
  time_header:
    seq:
      - id: unk1
        type: u1
      - id: unk2_exp
        contents: [0,0,0,6,0,0,0,26,0,0,0]
      - id: index
        type: u4
      - id: time_per_div_ps
        type: u4
      - id: pad1
        size: 4
      - id: unk3
        type: u4
      - id: unk4
        type: u4
        repeat: expr
        repeat-expr: 3
      - id: delay_ps
        type: u8
      - id: unk5
        type: u4
      - id: unk6_exp
        size: 14
        contents: [0,0,0,0,0,0,0,0,0,0,0,0,1,0]
      - id: unk7_exp
        type: u2
  channel_header:
    seq:
      - id: unk12_exp
        contents: [0]
      - id: coupling
        type: u1
        enum: channel_coupling
      - id: bandwidth_limit
        type: u1
        enum: bandwidth_limit
      - id: unk13_exp
        size: 2
        contents: [0]
      - id: probe_scale
        type: u1
        enum: probe_scale
      - id: unk1_exp
        size: 2
        contents: [1, 0]
      - id: probe_impedance
        type: u1
        enum: probe_impedance
      - id: scale_index
        type: u1
        enum: channel_scale
      - id: unk2_exp
        size: 1
        contents: [2]
      - id: label
        type: str
        encoding: ascii
        size: 10
      - id: unk3_exp
        contents: [0,0,0,0,0,0,0,0,0,0,0,0]
      - id: unk6_exp
        #type: u4
        contents: [0xc0, 0xe1, 0xe4, 0x00] # u4: 15M
      - id: unk7_exp
        #type: u4
        contents: [0x00, 0x2d, 0x31, 0x01] # u4: 20M
      - id: unk8_exp
        #type: u4
        contents: [0,0,0,0]
      - id: scale_microvolt
        type: u4
      - id: offset_uv
        type: s4
      - id: unk11
        type: s2
      - id: unk12
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
        type: str
        encoding: ascii
        size: 16
      - id: unk1
        size: 4
      - id: firmware_version
        type: str
        encoding: ascii
        size: 16
  channel_data:
    seq:
      - id: channel_1
        type: u1
        repeat: expr
        repeat-expr: '_root.header.mem_depth * (_root.header.channel_mask.channel_1 ? 1 : 0)'
      - id: padding_1
        size: '(_root.header.bytes_per_channel_1 - _root.header.mem_depth) * (_root.header.channel_mask.channel_1 ? 1 : 0)'
      - id: channel_2
        type: u1
        repeat: expr
        repeat-expr: '_root.header.mem_depth * (_root.header.channel_mask.channel_2 ? 1 : 0)'
      - id: padding_2
        size: '(_root.header.bytes_per_channel_1 - _root.header.mem_depth) * (_root.header.channel_mask.channel_2 ? 1 : 0)'
      - id: channel_3
        type: u1
        repeat: expr
        repeat-expr: '_root.header.mem_depth * (_root.header.channel_mask.channel_3 ? 1 : 0)'
      - id: padding_3
        size: '(_root.header.bytes_per_channel_1 - _root.header.mem_depth) * (_root.header.channel_mask.channel_3 ? 1 : 0)'
      - id: channel_4
        type: u1
        repeat: expr
        repeat-expr: '_root.header.mem_depth * (_root.header.channel_mask.channel_4 ? 1 : 0)'
      - id: padding_4
        size: '(_root.header.bytes_per_channel_1 - _root.header.mem_depth) * (_root.header.channel_mask.channel_4 ? 1 : 0)'

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
