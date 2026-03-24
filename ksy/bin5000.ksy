meta:
  id: bin5000
  title: Rigol MSO5000 binary waveform export
  file-extension: bin
  endian: le
doc: |
  Binary waveform export used by Rigol MSO5000 scopes.

  This schema is based on:
    - example files in `docs/sources/rigol_mso5000-main/waveform_bin/examples`
    - `docs/sources/matlab/importRigolBinMSO5000.m`
    - `docs/sources/rigol_mso5000-main/waveform_bin/Rigol_MSO5000_Waveform_bin.bt`

  File layout:
    [File Header:      12 bytes]
    for each exported waveform:
      [Waveform Header: 140 bytes]
      [Data Header:      12 bytes]
      [Sample Data:      buffer_size bytes]

  The shipped examples only exercise analog float32 buffers. Logic-analyzer
  records are identified by the enums below and handled in handwritten code.

seq:
  - id: file_header
    type: file_header
  - id: waveforms
    type: waveform
    repeat: expr
    repeat-expr: file_header.n_waveforms

types:
  file_header:
    seq:
      - id: cookie
        contents: "RG"
      - id: version
        size: 2
        type: str
        encoding: ASCII
      - id: file_size
        type: u4
      - id: n_waveforms
        type: u4

  waveform:
    seq:
      - id: wfm_header
        type: waveform_header
      - id: data_header
        type: data_header
      - id: data_raw
        size: data_header.buffer_size

  waveform_header:
    seq:
      - id: header_size
        type: u4
      - id: waveform_type
        type: u4
        enum: waveform_type_enum
      - id: n_buffers
        type: u4
      - id: n_pts
        type: u4
      - id: count
        type: u4
      - id: x_display_range
        type: f4
      - id: x_display_origin
        type: f8
      - id: x_increment
        type: f8
      - id: x_origin
        type: f8
      - id: x_units
        type: u4
        enum: unit_enum
      - id: y_units
        type: u4
        enum: unit_enum
      - id: date
        size: 16
        type: str
        encoding: ASCII
        terminator: 0
      - id: time_str
        size: 16
        type: str
        encoding: ASCII
        terminator: 0
      - id: frame_string
        size: 24
        type: str
        encoding: ASCII
        terminator: 0
      - id: waveform_label
        size: 16
        type: str
        encoding: ASCII
        terminator: 0
      - id: time_tag
        type: f8
      - id: segment_index
        type: u4
      - id: extra_padding
        size: header_size - 140
        if: header_size > 140
        doc: Reserved extension bytes present in some firmware versions (e.g. MSO5074).

  data_header:
    seq:
      - id: header_size
        type: u4
      - id: buffer_type
        type: u2
        enum: buffer_type_enum
      - id: bytes_per_point
        type: u2
      - id: buffer_size
        type: u4

enums:
  waveform_type_enum:
    0: unknown
    1: normal
    2: peak_detect
    3: average
    4: horizontal_histogram
    5: vertical_histogram
    6: logic

  buffer_type_enum:
    0: unknown
    1: normal_float32
    2: maximum_float32
    3: minimum_float32
    4: time_float32
    5: counts_float32
    6: digital_u8

  unit_enum:
    0: unknown
    1: v
    2: s
    3: constant
    4: a
    5: db
    6: hz
