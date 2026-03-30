meta:
  id: rigol_7000_8000_bin
  title: Rigol 7000/8000 Binary Format
  file-extension: bin
  endian: le
doc: |
  Binary waveform export used by Rigol MSO7000/DS7000 and MSO8000 scopes.

  This schema follows the "Binary Data Format (.bin)" tables in:
    - `docs/manuals/Rigol MSO7000 Series User Manual.pdf`
    - `docs/manuals/MSO8000 Series Digital.pdf`

  Documented layout:
    [File Header:      12 bytes]
    for each exported waveform:
      [Waveform Header: 128 bytes]
      [Data Header:      12 bytes]
      [Sample Data:      buffer_size bytes]

  The manuals document analog, logic, and math records in the same container.
  The handwritten adapter currently normalizes analog float32 buffers only.

  Sources used for this KSY binary format: the Rigol "Binary Data Format
  (.bin)" tables in `docs/vendors/lecroy/manuals/Rigol MSO7000 Series User Manual.pdf`
  and `docs/vendors/lecroy/manuals/MSO8000 Series Digital.pdf`, plus the
  checked-in synthetic regression builder in `tests/test_7_8.py`.

  Tested file formats: synthetic `MSO7034` and `MSO8204` analog float32 `.bin`
  captures generated in `tests/test_7_8.py`, plus a negative regression that
  confirms logic-record rejection.

  Oscilloscope models this format may apply to: Rigol `DS7000` / `MSO7000`
  and `MSO8000` family scopes that emit the documented float32 `.bin` export,
  including the synthetic reference models `MSO7034` and `MSO8204`.

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
    4: unused4
    5: unused5
    6: logic

  buffer_type_enum:
    0: unknown
    1: normal_float32
    2: maximum_float32
    3: minimum_float32
    4: unused4
    5: unused5
    6: digital_u8

  unit_enum:
    0: unknown
    1: v
    2: s
    3: constant
    4: a
    5: db
    6: hz
