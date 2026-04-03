meta:
  id: agilent_agxx_bin
  title: Agilent / Keysight AGxx File Format
  file-extension: bin
  endian: le
doc: |
  Binary waveform export used by Agilent and Keysight oscilloscopes.

  This schema is based on the checked-in vendor parsers plus the Agilent
  6000 Series and InfiniiVision 2000 manuals. Those sources describe the
  `AG01` / `AG03` / `AG10` container family written by several
  Agilent / Keysight oscilloscopes.

  File layout::
    [File Header: 12 bytes for AG01 / AG10, 16 bytes for AG03]
    for each exported waveform:
      [Waveform Header: usually 140 bytes]
      repeat n_buffers times:
        [Data Header: 12 bytes for AG01 / AG10, 16 bytes for AG03]
        [Sample Data: buffer_size bytes]

  Normal analog waveforms are float32. Peak Detect acquisitions can store
  separate minimum and maximum float32 buffers for a single waveform header.
  Logic-style records use byte-oriented buffers.

  Sources used for this KSY binary format: `Agilent InfiniiVision
  6000 Series Oscilloscopes` and `Agilent InfiniiVision 2000 X-Series
  Oscilloscopes` as well as GitHub repositories
  <https://github.com/shotaizu/agilent-oscilloscope-bin-parser>,
  <https://github.com/AntonBryansky/ImportAgilentBin>,
  <https://github.com/yodalee/keysightBin>, and
  <https://github.com/FaustinCarter/agilent_read_binary>

  Tested file formats: `agilent_1.bin` through `agilent_5.bin`
  and `agilent_msox4154a_01.bin`; all checked-in real samples are `AG10`
  captures, and the regression builders additionally exercise multi-buffer and
  per-channel-timing edge cases within the same `AG10` container layout.

  Oscilloscope models this format may apply to: confirmed `DSO-X 1102G` and
  `MSO-X 4154A` captures, plus other Agilent / Keysight 6000 Series and
  InfiniiVision 2000/3000/4000/X instruments that export `AG01`, `AG03`, or
  `AG10` `.bin` files.

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
        contents: "AG"
      - id: version
        size: 2
        type: str
        encoding: ASCII
      - id: file_size_32
        type: u4
        if: version_num == 1 or version_num == 10
      - id: file_size_64
        type: u8
        if: version_num == 3
      - id: n_waveforms
        type: u4
    instances:
      version_num:
        value: version.to_i
      file_size:
        value: 'version_num == 3 ? file_size_64 : file_size_32'

  waveform:
    seq:
      - id: wfm_header
        type: waveform_header
      - id: buffers
        type: waveform_buffer
        repeat: expr
        repeat-expr: wfm_header.n_buffers

  waveform_buffer:
    seq:
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
        doc: Reserved extension bytes present in some firmware revisions.

  data_header:
    seq:
      - id: header_size
        type: u4
      - id: buffer_type
        type: u2
        enum: buffer_type_enum
      - id: bytes_per_point
        type: u2
      - id: buffer_size_32
        type: u4
        if: _root.file_header.version_num == 1 or _root.file_header.version_num == 10
      - id: buffer_size_64
        type: u8
        if: _root.file_header.version_num == 3
    instances:
      buffer_size:
        value: '_root.file_header.version_num == 3 ? buffer_size_64 : buffer_size_32'

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
    4: counts_i32
    5: logic_u8
    6: digital_u8

  unit_enum:
    0: unknown
    1: v
    2: s
    3: constant
    4: a
    5: db
    6: hz
