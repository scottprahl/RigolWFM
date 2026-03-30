meta:
  id: siglent_v4
  title: Siglent V4.0 Binary Format
  file-extension: bin
  endian: le
doc: |
  Siglent waveform binary layout documented as "Binary Format V4.0".

  V4.0 increases the header size to 4 KiB, adds a data-offset field, and
  expands the analog channel metadata to support up to eight channels plus
  additional memory/zoom parameters.

instances:
  version:
    pos: 0x00
    type: u4
  data_offset_byte:
    pos: 0x04
    type: u4
  ch_on_1_4:
    pos: 0x08
    type: s4_array_4
  ch_volt_div_1_4:
    pos: 0x18
    type: data_with_unit_array_4
  ch_vert_offset_1_4:
    pos: 0xb8
    type: data_with_unit_array_4
  digital_on:
    pos: 0x158
    type: u4
  digital_ch_on:
    pos: 0x15c
    type: u4_array_16
  time_div:
    pos: 0x19c
    type: data_with_unit
  time_delay:
    pos: 0x1c4
    type: data_with_unit
  wave_length:
    pos: 0x1ec
    type: u4
  sample_rate:
    pos: 0x1f0
    type: data_with_unit
  digital_wave_length:
    pos: 0x218
    type: u4
  digital_sample_rate:
    pos: 0x21c
    type: data_with_unit
  ch_probe_1_4:
    pos: 0x244
    type: f8_array_4
  data_width:
    pos: 0x264
    type: u1
  byte_order:
    pos: 0x265
    type: u1
  hori_div_num:
    pos: 0x26c
    type: s4
  ch_vert_code_per_div_1_4:
    pos: 0x270
    type: s4_array_4
  math_switch:
    pos: 0x280
    type: s4_array_4
  math_store_len:
    pos: 0x3d0
    type: u4_array_4
  math_f_time:
    pos: 0x3e0
    type: f8_array_4
  math_vert_code_per_div:
    pos: 0x400
    type: s4
  ch_on_5_8:
    pos: 0x404
    type: s4_array_4
  ch_volt_div_5_8:
    pos: 0x414
    type: data_with_unit_array_4
  ch_vert_offset_5_8:
    pos: 0x4b4
    type: data_with_unit_array_4
  ch_probe_5_8:
    pos: 0x554
    type: f8_array_4
  ch_vert_code_per_div_5_8:
    pos: 0x574
    type: s4_array_4
  wave_data:
    pos: data_offset_byte
    size: _io.size - data_offset_byte

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
