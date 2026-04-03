meta:
  id: siglent_v5_bin
  title: Siglent V5.0 BIN File Format
  file-extension: bin
  endian: le
doc: |
  Siglent waveform binary layout documented as "Binary Format V5.0".

  This revision is documented for later SDS1002X-E firmware and keeps the
  analog waveform data at offset 0x800 while moving the channel and timing
  metadata into a different fixed layout.

  Sources used for this KSY binary format: The binary waveform layout documented by
  Siglent as "How to Extract Data from the Binary File of SIGLENT Oscilloscope".

  Tested file formats: the synthetic `Binary Format V5.0` fixture in
  `tests/test_siglent.py`, exercised through revision detection, low-level
  Kaitai parsing, and normalized waveform loading.

  Oscilloscope models this format may apply to: later `SDS1002X-E` firmware and
  other Siglent instruments that write `Binary Format V5.0`.

instances:
  version:
    pos: 0x00
    type: u4
  ch1_on:
    pos: 0x76
    type: s4
  ch2_on:
    pos: 0xf0
    type: s4
  ch3_on:
    pos: 0x194
    type: s4
  ch4_on:
    pos: 0x238
    type: s4
  ch1_volt_div:
    pos: 0xab
    type: scaled_value_16
  ch2_volt_div:
    pos: 0x160
    type: scaled_value_16
  ch3_volt_div:
    pos: 0x204
    type: scaled_value_16
  ch4_volt_div:
    pos: 0x2a8
    type: scaled_value_16
  ch1_vert_offset:
    pos: 0xbc
    type: scaled_value_16
  ch2_vert_offset:
    pos: 0x170
    type: scaled_value_16
  ch3_vert_offset:
    pos: 0x214
    type: scaled_value_16
  ch4_vert_offset:
    pos: 0x2b8
    type: scaled_value_16
  time_div:
    pos: 0x1b68
    type: scaled_value_16
  time_delay:
    pos: 0x1b78
    type: scaled_value_16
  wave_length:
    pos: 0x1b88
    type: u4
  sample_rate:
    pos: 0x1b92
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
