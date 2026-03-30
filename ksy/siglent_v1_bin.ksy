meta:
  id: siglent_v1_bin
  title: Siglent V1.0 Binary Format
  file-extension: bin
  endian: le
doc: |
  Siglent waveform binary layout documented as "Binary Format V1.0".

  V1.0 introduces a compact 2 KiB waveform header at the start of the file and
  stores enabled analog channels first in the sample payload at offset 0x800.

instances:
  ch_on:
    pos: 0x00
    type: s4_array_4
  ch_volt_div:
    pos: 0x10
    type: scaled_value_16_array_4
  ch_vert_offset:
    pos: 0x50
    type: scaled_value_16_array_4
  digital_on:
    pos: 0x90
    type: u4
  digital_ch_on:
    pos: 0x94
    type: u4_array_16
  time_div:
    pos: 0xd4
    type: scaled_value_16
  time_delay:
    pos: 0xe4
    type: scaled_value_16
  wave_length:
    pos: 0xf4
    type: u4
  sample_rate:
    pos: 0xf8
    type: scaled_value_16
  digital_wave_length:
    pos: 0x108
    type: u4
  digital_sample_rate:
    pos: 0x10c
    type: scaled_value_16
  wave_data:
    pos: 0x800
    size: _io.size - 0x800

types:
  scaled_value_16:
    seq:
      - id: value
        type: f8
      - id: magnitude
        type: u4
      - id: unit
        type: u4

  scaled_value_16_array_4:
    seq:
      - id: entries
        type: scaled_value_16
        repeat: expr
        repeat-expr: 4

  s4_array_4:
    seq:
      - id: entries
        type: s4
        repeat: expr
        repeat-expr: 4

  u4_array_16:
    seq:
      - id: entries
        type: u4
        repeat: expr
        repeat-expr: 16
