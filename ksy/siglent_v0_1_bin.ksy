meta:
  id: siglent_v0_1_bin
  title: Siglent V0.1 BIN File Format
  file-extension: bin
  endian: le
doc: |
  Siglent waveform binary layout documented as "Binary Format V0.1".

  This revision predates the explicit top-level version field used by later
  layouts. It stores four analog channels with 16-byte value/unit structures
  and places waveform samples after a large fixed metadata block.

  Sources used for this KSY binary format: The binary waveform layout documented by
  Siglent as "How to Extract Data from the Binary File of SIGLENT Oscilloscope".

  Tested file formats: the synthetic `Binary Format V0.1` fixture in
  `tests/test_siglent.py`, exercised through revision detection, low-level
  Kaitai parsing, and normalized waveform loading.

  Oscilloscope models this format may apply to: Siglent instruments that write
  `Binary Format V0.1`; the checked-in tests do not yet narrow this revision to
  a smaller verified model list.

instances:
  ch1_on:
    pos: 0x44
    type: s4
  ch2_on:
    pos: 0xc0
    type: s4
  ch3_on:
    pos: 0x13c
    type: s4
  ch4_on:
    pos: 0x1b8
    type: s4
  ch1_volt_div:
    pos: 0x90
    type: scaled_value_16
  ch2_volt_div:
    pos: 0x10c
    type: scaled_value_16
  ch3_volt_div:
    pos: 0x188
    type: scaled_value_16
  ch4_volt_div:
    pos: 0x204
    type: scaled_value_16
  ch1_vert_offset:
    pos: 0xa0
    type: scaled_value_16
  ch2_vert_offset:
    pos: 0x11c
    type: scaled_value_16
  ch3_vert_offset:
    pos: 0x198
    type: scaled_value_16
  ch4_vert_offset:
    pos: 0x214
    type: scaled_value_16
  time_div:
    pos: 0xa84
    type: scaled_value_16
  time_delay:
    pos: 0xa94
    type: scaled_value_16
  wave_length:
    pos: 0xaa4
    type: u4
  sample_rate:
    pos: 0xaa8
    type: scaled_value_16
  wave_data:
    pos: 0x8a60
    size: _io.size - 0x8a60

types:
  scaled_value_16:
    seq:
      - id: value
        type: f8
      - id: magnitude
        type: u4
      - id: unit
        type: u4
