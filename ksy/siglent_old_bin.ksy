meta:
  id: siglent_old_bin
  title: Siglent Old-Platform Binary Format
  file-extension: bin
  endian: le
doc: |
  Binary waveform layout documented by Siglent as "Binary Format in Old
  Platform". This revision is used by older SDS1000X / SDS2000X families.

  The file does not include an explicit format-version field or instrument
  model identifier, so the surrounding Python adapter is responsible for any
  remaining family-specific interpretation.

instances:
  mso_wave_length:
    pos: 0x04
    type: u4
  mso_ch_open_num:
    pos: 0x10
    type: u4
  mso_ch_open_stats:
    pos: 0x14
    type: u1_array_16
  ch_volt_div_mv:
    pos: 0xbc
    type: f4_array_4
  ch_vert_offset_pixels:
    pos: 0xdc
    type: s4_array_4
  ch_on:
    pos: 0x100
    type: s4_array_4
  time_div_index:
    pos: 0x248
    type: s4
  time_delay_pixels:
    pos: 0x250
    type: s4
  wave_data:
    pos: 0x1470
    size: _io.size - 0x1470

types:
  u1_array_16:
    seq:
      - id: entries
        type: u1
        repeat: expr
        repeat-expr: 16

  f4_array_4:
    seq:
      - id: entries
        type: f4
        repeat: expr
        repeat-expr: 4

  s4_array_4:
    seq:
      - id: entries
        type: s4
        repeat: expr
        repeat-expr: 4
