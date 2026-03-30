meta:
  id: siglent_v3
  title: Siglent V3.0 Binary Format
  file-extension: bin
  endian: le
doc: |
  Siglent waveform binary layout documented as "Binary Format V3.0".

  V3.0 retains the V2.0 2 KiB header but adds byte order, horizontal grid
  count, per-channel code-per-division values, and math-wave metadata.

instances:
  version:
    pos: 0x00
    type: u4
  ch_on:
    pos: 0x04
    type: s4_array_4
  ch_volt_div:
    pos: 0x14
    type: data_with_unit_array_4
  ch_vert_offset:
    pos: 0xb4
    type: data_with_unit_array_4
  digital_on:
    pos: 0x154
    type: u4
  digital_ch_on:
    pos: 0x158
    type: u4_array_16
  time_div:
    pos: 0x198
    type: data_with_unit
  time_delay:
    pos: 0x1c0
    type: data_with_unit
  wave_length:
    pos: 0x1e8
    type: u4
  sample_rate:
    pos: 0x1ec
    type: data_with_unit
  digital_wave_length:
    pos: 0x214
    type: u4
  digital_sample_rate:
    pos: 0x218
    type: data_with_unit
  ch_probe:
    pos: 0x240
    type: f8_array_4
  data_width:
    pos: 0x260
    type: u1
  byte_order:
    pos: 0x261
    type: u1
  hori_div_num:
    pos: 0x268
    type: s4
  ch_vert_code_per_div:
    pos: 0x26c
    type: s4_array_4
  math_switch:
    pos: 0x27c
    type: s4_array_4
  math_store_len:
    pos: 0x3cc
    type: u4_array_4
  math_f_time:
    pos: 0x3dc
    type: f8_array_4
  math_vert_code_per_div:
    pos: 0x3fc
    type: s4
  wave_data:
    pos: 0x800
    size: _io.size - 0x800

types:
  data_with_unit:
    seq:
      - id: value
        type: f8
      - id: magnitude
        type: u4
      - id: unit_words
        type: u4
        repeat: expr
        repeat-expr: 7

  data_with_unit_array_4:
    seq:
      - id: entries
        type: data_with_unit
        repeat: expr
        repeat-expr: 4

  s4_array_4:
    seq:
      - id: entries
        type: s4
        repeat: expr
        repeat-expr: 4

  u4_array_4:
    seq:
      - id: entries
        type: u4
        repeat: expr
        repeat-expr: 4

  u4_array_16:
    seq:
      - id: entries
        type: u4
        repeat: expr
        repeat-expr: 16

  f8_array_4:
    seq:
      - id: entries
        type: f8
        repeat: expr
        repeat-expr: 4
