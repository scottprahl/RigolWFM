meta:
  id: siglent_v6
  title: Siglent waveform binary V6.0
  file-extension: bin
  endian: le
doc: |
  Siglent waveform binary layout documented as "Binary Format V6.0".

  V6.0 stores a top-level file header followed by one or more waveform records.
  Each waveform contains a fixed shared header, optional extension bytes, an
  optional additional-information block, and then the sample payload.

seq:
  - id: file_header
    type: file_header
  - id: waveforms
    type: waveform
    repeat: expr
    repeat-expr: file_header.wave_number

types:
  file_header:
    seq:
      - id: version
        type: u4
      - id: header_bytes
        type: u2
      - id: endian_marker
        type: u2
      - id: module
        size: 32
        type: str
        encoding: ASCII
        terminator: 0
      - id: serial
        size: 32
        type: str
        encoding: ASCII
        terminator: 0
      - id: software_version
        size: 32
        type: str
        encoding: ASCII
        terminator: 0
      - id: wave_number
        type: u4
      - id: header_extra
        size: header_bytes - 108
        if: header_bytes > 108

  waveform:
    seq:
      - id: header
        type: waveform_header
      - id: add_info
        size: header.add_info_bytes
      - id: data_raw
        size: header.data_bytes

  waveform_header:
    seq:
      - id: base_header_type
        type: u4
      - id: base_header_bytes
        type: u4
      - id: wave_type
        type: u4
      - id: channel_type
        type: u2
      - id: channel_index
        type: u2
      - id: label
        size: 16
        type: str
        encoding: ASCII
        terminator: 0
      - id: date
        size: 16
        type: str
        encoding: ASCII
        terminator: 0
      - id: time_str
        size: 32
        type: str
        encoding: ASCII
        terminator: 0
      - id: hori_scale
        type: f8
      - id: hori_pos
        type: f8
      - id: hori_origin_pos
        type: f8
      - id: hori_interval
        type: f8
      - id: hori_unit
        type: u4
        repeat: expr
        repeat-expr: 8
      - id: hori_unit_str
        size: 16
        type: str
        encoding: ASCII
        terminator: 0
      - id: vert_scale
        type: f8
      - id: vert_pos
        type: f8
      - id: vert_origin_pos
        type: f8
      - id: vert_interval
        type: f8
      - id: vert_unit
        type: u4
        repeat: expr
        repeat-expr: 8
      - id: vert_unit_str
        size: 16
        type: str
        encoding: ASCII
        terminator: 0
      - id: add_info_bytes
        type: u4
      - id: data_type
        type: u4
      - id: data_number
        type: u8
      - id: data_bytes
        type: u8
      - id: base_header_extra
        size: base_header_bytes - 264
        if: base_header_bytes > 264
