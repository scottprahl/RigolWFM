meta:
  id: siglent_v2_bin
  title: Siglent V2.0 Binary Format
  file-extension: bin
  endian: le
doc: |
  Siglent waveform binary layout documented as "Binary Format V2.0".

  V2.0 adds a top-level version field and expands the value/unit structure from
  16 bytes to 40 bytes. Analog samples still begin at offset 0x800 and are
  packed channel-by-channel for the enabled channels.

  Sources used for this KSY binary format:
  `docs/vendors/siglent/siglent-binaries.pdf` plus the synthetic regression
  builder in `tests/test_siglent.py`.

  Tested file formats: the synthetic `Binary Format V2.0` fixture in
  `tests/test_siglent.py`, exercised through revision detection, low-level
  Kaitai parsing, and normalized waveform loading.

  Oscilloscope models this format may apply to: Siglent instruments that write
  `Binary Format V2.0`; the checked-in tests do not yet narrow this revision to
  a smaller verified model list.

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
