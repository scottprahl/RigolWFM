meta:
  id: rigol_dho800_1000_wfm
  title: Rigol DHO800/DHO1000 WFM File Format
  file-extension: wfm
  endian: le
doc: |
  Proprietary waveform format used by Rigol DHO800/DHO1000 series
  oscilloscopes (reverse-engineered from DHO1074 and DHO824 captures).

  File layout::

    [File Header:      24 bytes  - partially unknown]
    [Metadata blocks:  variable  - 12-byte header + zlib-compressed content each]
    [Zero padding:     variable  - null bytes between block region and data]
    [Data section:     variable  - 40-byte header + uint16 ADC samples]

  Metadata blocks
  ---------------
  Each block has a 12-byte header (six u16 LE fields) followed by len_content_raw
  bytes of content.  When comp_size < decomp_size the content bytes
  [0 .. comp_size-1] are zlib-compressed; the remainder is zero padding.
  Blocks are read until a terminator block where len_content_raw == 0.

  Key blocks (identified by block_id and block_type)::

    block_id=1..4, block_type=9  (~88-96 bytes decompressed)
      Offset  1..8  - int64 LE - voltage scale numerator
      scale = i64 / 750_000_000_000
      Offset 38..45 - int64 LE - channel voltage centre x 1e8
      v_center = i64 / 1e8

    block_type=6  (~1628 bytes decompressed)
      Offset 36..39 - int32 LE - CH1 voltage centre x 1e8
      Legacy fallback for older single-channel captures.

  Voltage calibration
  -------------------
  Per-channel voltage conversion is::

    scale    = i64_channel / 750_000_000_000
    v_center = i64_channel / 1e8
    offset   = -v_center - scale * 32768
    volts[i] = scale * raw_uint16[i] + offset

  Data section
  ------------
  The data section starts after the zero-padding region that follows the
  last metadata block.  Its offset cannot be determined statically; a
  sequential scan for the first non-zero byte is required.

  Data section header (40 bytes)::

    offset+ 0:  u64 LE  - raw total sample count across all enabled channels.
                 DHO1000 firmware stores a value slightly larger than the true
                 total (~+64 samples); n_ch is recovered via
                 round(n_pts_u64 / n_pts_per_channel) rather than exact
                 division.
    offset+ 8:  8 bytes - capture marker (opaque)
    offset+16:  u32 LE  - x_increment in ADC ticks (see below)
    offset+20:  u32 LE  - unknown (observed: 77)
    offset+24:  u32 LE  - n_pts per enabled channel
    offset+28:  u32 LE  - n_pts per enabled channel (repeated)
    offset+32:  u32 LE  - timestamp / unknown
    offset+36:  u32 LE  - unknown (observed: 120 for single-channel, 0 for multi)
    offset+40:  uint16 LE samples begin (n_pts_per_channel × n_channels × 2 bytes)

  Time axis
  ---------
  The x_increment field stores the sampling interval as an integer count of
  ADC clock ticks.  The tick duration is a fixed hardware property::

    DHO800  (e.g. DHO824):  0.8 ns / tick  — one cycle of the 1.25 GSa/s ADC
    DHO1000 (e.g. DHO1074): 10 ns / tick   — one cycle of a 100 MHz reference clock

  x_origin is not stored explicitly.  For the common case of a centered
  trigger (trigger at 50% of the capture window, which is the scope default)::

    x_origin = -(n_pts_per_channel / 2) * x_increment
    t[i]     =  x_origin + i * x_increment

  Trigger position as a percentage of the capture window is likely encoded
  in the metadata block with id=282, u32 at byte offset 12 (observed: 50 for
  center trigger in all available DHO800 and DHO1000 test captures).

  LIMITATION: This KSY describes the block region only.  The zero-padding
  region and the data section require sequential runtime scanning and cannot
  be expressed as fixed-offset KSY instances.

  Sources used for this KSY binary format: reverse-engineering from the
  checked-in `DHO1074.wfm`, `DHO824-ch1.wfm`, `DHO824-ch12.wfm`, and
  `DHO824-ch1234.wfm` captures, cross-checked against matching `.bin` exports
  from the same scopes.

  Tested file formats: real repo fixtures `DHO1074.wfm`, `DHO824-ch1.wfm`,
  `DHO824-ch12.wfm`, and `DHO824-ch1234.wfm`, with matching `.bin`
  comparisons used for time-axis and voltage-correlation regressions.

  Oscilloscope models this format may apply to: `DHO804`, `DHO812`, `DHO814`,
  `DHO824`, `DHO1072`, `DHO1074`, `DHO1102`, `DHO1202`, and related
  `DHO800` / `DHO1000` family scopes that write this proprietary `.wfm`
  container.

seq:
  - id: file_header
    type: file_header
  - id: blocks
    type: block
    repeat: until
    repeat-until: _.len_content_raw == 0 and _.comp_size == 0
    doc: Metadata blocks terminated by an all-zero block header.

types:
  file_header:
    doc: |
      24-byte file header.  Internal structure not fully reverse-engineered;
      treated as opaque.
    seq:
      - id: reserved
        size: 24
        doc: File header bytes - internal layout not yet fully known.

  block:
    doc: |
      One metadata block.  A block with len_content_raw == 0 and comp_size == 0
      signals the end of the metadata region.
    seq:
      - id: block_id
        type: u2
        doc: |
          Channel / block identifier.
          1..4 = analog channel parameters for CH1..CH4 when block_type == 9.
      - id: block_type
        type: u2
        enum: block_type_enum
        doc: |
          Content type.
          9 = channel parameters.
          6 = trigger/display settings (legacy CH1 v_center fallback).
      - id: decomp_size
        type: u2
        doc: Decompressed content size in bytes.
      - id: comp_size
        type: u2
        doc: |
          Compressed content size in bytes.
          Equal to decomp_size when content is stored verbatim (not compressed).
      - id: len_content_raw
        type: u2
        doc: |
          Total bytes consumed in the file for this block's content
          (comp_size rounded up to the next alignment boundary).
          Zero in the terminator block.
      - id: reserved
        type: u2
        doc: Always 0.
      - id: content_raw
        size: len_content_raw
        doc: |
          Block content bytes.  The first comp_size bytes hold the payload
          (zlib-compressed when comp_size != decomp_size; verbatim otherwise).
          Remaining bytes (len_content_raw - comp_size) are zero padding.
    instances:
      is_channel_params:
        value: block_type == block_type_enum::channel_params and block_id >= 1 and block_id <= 4
        doc: |
          True for one of the per-channel parameter blocks.
          Decompressed content bytes [1..8] hold an int64 LE voltage scale
          numerator, and bytes [38..45] hold an int64 LE channel center.
      is_settings:
        value: block_type == block_type_enum::settings
        doc: |
          True for the trigger/display settings block.
          Decompressed content bytes [36..39] hold an int32 LE voltage centre
          value: v_center = i32 / 1e8.
      is_terminator:
        value: len_content_raw == 0 and comp_size == 0
        doc: True for the sentinel block that ends the metadata region.

  dho1000_channel_params:
    doc: |
      DHO1000 per-channel parameter payload after optional zlib decompression.
      Observed channel blocks store the displayed vertical center with the
      opposite sign from the sample reconstruction offset.
    seq:
      - id: reserved_0
        size: 1
      - id: scale_numerator
        type: s8
      - id: reserved_1
        size: 29
      - id: v_center_raw
        type: s8
      - id: reserved_2
        size-eos: true
    instances:
      scale:
        value: scale_numerator / 750000000000.0
      v_center:
        value: v_center_raw / 1.0e8
      offset:
        value: -v_center - scale * 32768

  dho800_channel_params:
    doc: |
      DHO800 per-channel parameter payload after optional zlib decompression.
      The stored center value is negated and scaled in 1e-9 volt units.
    seq:
      - id: reserved_0
        size: 1
      - id: scale_numerator
        type: s8
      - id: reserved_1
        size: 29
      - id: v_center_raw
        type: s4
      - id: reserved_2
        size-eos: true
    instances:
      scale:
        value: scale_numerator / 7500000000000.0
      v_center:
        value: -v_center_raw / 1.0e9
      offset:
        value: v_center - scale * 32768

  settings_block:
    doc: |
      Trigger/display settings payload after optional zlib decompression.
      Older single-channel captures expose only the CH1 vertical center here.
    seq:
      - id: reserved_0
        size: 36
      - id: v_center_raw
        type: s4
      - id: reserved_1
        size-eos: true
    instances:
      v_center:
        value: v_center_raw / 1.0e8

enums:
  block_type_enum:
    5: dho800_channel_params
    6: settings
    9: channel_params
