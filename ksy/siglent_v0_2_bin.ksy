meta:
  id: siglent_v0_2_bin
  title: Siglent V0.2 Binary Format
  file-extension: bin
  endian: le
doc: |
  Siglent waveform binary layout documented as "Binary Format V0.2".

  V0.2 keeps the V0.1 analog-only sample packing but moves the horizontal
  timing metadata to later offsets in the file.

instances:
  ch1_on:
    pos: 0x44
    type: s4
  ch2_on:
    pos: 0xe8
    type: s4
  ch3_on:
    pos: 0x18c
    type: s4
  ch4_on:
    pos: 0x230
    type: s4
  ch1_volt_div:
    pos: 0xb4
    type: scaled_value_16
  ch2_volt_div:
    pos: 0x158
    type: scaled_value_16
  ch3_volt_div:
    pos: 0x1fc
    type: scaled_value_16
  ch4_volt_div:
    pos: 0x2a0
    type: scaled_value_16
  ch1_vert_offset:
    pos: 0xc4
    type: scaled_value_16
  ch2_vert_offset:
    pos: 0x168
    type: scaled_value_16
  ch3_vert_offset:
    pos: 0x20c
    type: scaled_value_16
  ch4_vert_offset:
    pos: 0x2b0
    type: scaled_value_16
  time_div:
    pos: 0xdb8
    type: scaled_value_16
  time_delay:
    pos: 0xdc8
    type: scaled_value_16
  wave_length:
    pos: 0xdd8
    type: u4
  sample_rate:
    pos: 0xddc
    type: scaled_value_16
  wave_data:
    pos: 0x932c
    size: _io.size - 0x932c

types:
  scaled_value_16:
    seq:
      - id: value
        type: f8
      - id: magnitude
        type: u4
      - id: unit
        type: u4
