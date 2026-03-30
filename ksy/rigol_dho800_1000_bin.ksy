meta:
  id: rigol_dho800_1000_bin
  title: Rigol DHO800/DHO1000 BIN Format
  file-extension: bin
  endian: le
doc: |
  Official binary waveform export format documented in DHO1000 User Guide
  §19.2.4 (Tables 19.1–19.4).

  This schema currently models the float32 analog waveform buffers used by
  this project. The user guide also documents digital unsigned 8-bit buffers
  and math waveforms; those buffer types are identified in the enums below,
  and the downstream wrapper rejects them explicitly instead of treating them
  as calibrated volt samples.

  File layout:
    [File Header:      16 bytes]
    for each waveform (channel):
      [Waveform Header: 140 bytes]
      [Data Header:      16 bytes]
      [Sample Data:      buffer_size bytes - float32 LE, volts]

  Time axis reconstruction used by the current parser:
    t[i] = -x_origin + i * x_increment

  The manual describes X Origin as the x-value of the first data point.
  Empirically, the analog captures used by this repo behave as if x_origin
  stores a positive pre-trigger distance, so downstream code negates it.

  Sources used for this KSY binary format: the official DHO1000 User Guide
  section 19.2.4 (Tables 19.1-19.4) plus comparison against checked-in
  `DHO1074.bin`, `DHO824-ch1.bin`, `DHO824-ch12.bin`, and `DHO824-ch1234.bin`
  captures.

  Tested file formats: real repo fixtures `DHO1074.bin`, `DHO824-ch1.bin`,
  `DHO824-ch12.bin`, and `DHO824-ch1234.bin`, covering one-, two-, and
  four-channel analog float32 exports.

  Oscilloscope models this format may apply to: `DHO804`, `DHO812`, `DHO814`,
  `DHO824`, `DHO1072`, `DHO1074`, `DHO1102`, `DHO1202`, and related
  `DHO800` / `DHO1000` family scopes that write the documented `.bin` export.

seq:
  - id: file_header
    type: file_header
  - id: waveforms
    type: waveform
    repeat: expr
    repeat-expr: file_header.n_waveforms

types:
  file_header:
    doc: 16-byte file header (Table 19.2).
    seq:
      - id: cookie
        contents: "RG"
        doc: Magic bytes identifying a Rigol DHO .bin file.
      - id: version
        size: 2
        type: str
        encoding: ASCII
        doc: File format version string.
      - id: file_size
        type: u8
        doc: Total file size in bytes.
      - id: n_waveforms
        type: u4
        doc: Number of waveform records (one per enabled channel).

  waveform:
    doc: |
      One waveform record: header, data header, and sample payload.
    seq:
      - id: wfm_header
        type: waveform_header
      - id: data_header
        type: data_header
      - id: samples
        size: data_header.buffer_size
        type: sample_data
        doc: Calibrated voltage values in volts (float32 LE).

  waveform_header:
    doc: |
      140-byte per-waveform header (Table 19.3).
      Describes acquisition settings and time-axis parameters for one channel.
    seq:
      - id: header_size
        type: u4
        doc: Size of this header in bytes (= 140).
      - id: waveform_type
        type: u4
        enum: waveform_type_enum
        doc: Acquisition mode.
      - id: n_buffers
        type: u4
        doc: Number of data buffers (= 1).
      - id: n_pts
        type: u4
        doc: Number of sample points.
      - id: count
        type: u4
        doc: Unused, always 0.
      - id: x_display_range
        type: f4
        doc: Horizontal display range in seconds.
      - id: x_display_origin
        type: f8
        doc: Horizontal display origin.
      - id: x_increment
        type: f8
        doc: Time between consecutive samples in seconds.
      - id: x_origin
        type: f8
        doc: |
          Manual: x-value of the first data point in seconds.
          Empirical analog captures used by this repo behave as if this is a
          positive trigger distance; downstream code therefore negates it:
            t[0] = -x_origin
            t[i] = -x_origin + i * x_increment
      - id: x_units
        type: u4
        enum: unit_enum
        doc: X-axis unit.
      - id: y_units
        type: u4
        enum: unit_enum
        doc: Y-axis unit.
      - id: date
        size: 16
        type: str
        encoding: ASCII
        terminator: 0
        doc: Capture date (null-terminated ASCII).
      - id: time_str
        size: 16
        type: str
        encoding: ASCII
        terminator: 0
        doc: Capture time (null-terminated ASCII).
      - id: model
        size: 24
        type: str
        encoding: ASCII
        terminator: 0
        doc: Model and serial number string "MODEL#:SERIAL#".
      - id: channel_name
        size: 16
        type: str
        encoding: ASCII
        terminator: 0
        doc: Channel label, e.g. "CH1".
      - id: padding
        size: 12
        doc: Reserved, always zero.
    instances:
      t0:
        value: -x_origin
        doc: Empirical first-sample time used by the current analog parser.
      seconds_per_point:
        value: x_increment
        doc: Sampling interval in seconds.

  data_header:
    doc: 16-byte data buffer header (Table 19.4).
    seq:
      - id: header_size
        type: u4
        doc: Size of this header in bytes (= 16).
      - id: buffer_type
        type: u2
        enum: buffer_type_enum
        doc: |
          Sample encoding per Table 19.4.
          The current wrapper supports float32 analog buffers only.
      - id: bytes_per_point
        type: u2
        doc: Bytes per sample (= 4 for float32).
      - id: buffer_size
        type: u8
        doc: Total byte count of sample data (= n_pts * 4).

  sample_data:
    doc: Stream of calibrated float32 voltage samples for analog buffers.
    seq:
      - id: values
        type: f4
        repeat: eos
        doc: Voltage at each sample point in volts.

enums:
  waveform_type_enum:
    0: unknown
    1: normal
    2: peak
    3: average
    4: not_used_4
    5: not_used_5
    6: logic

  buffer_type_enum:
    0: unknown
    1: float32_normal
    2: float32_maximum
    3: float32_minimum
    4: not_used
    5: digital_u8

  unit_enum:
    0: unknown
    1: v
    2: s
    3: constant
    4: a
    5: db
    6: hz
