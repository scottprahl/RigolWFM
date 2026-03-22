meta:
  id: wfmdho1000
  title: Rigol DHO800/DHO900/DHO1000 proprietary waveform file
  file-extension: wfm
  endian: le
  doc: |
    Proprietary waveform format used by Rigol DHO800/DHO900/DHO1000 series
    oscilloscopes (reverse-engineered from DHO1074 captures).

    File layout:
      [File Header:      24 bytes  — partially unknown]
      [Metadata blocks:  variable  — 12-byte header + zlib-compressed content each]
      [Zero padding:     variable  — null bytes between block region and data]
      [Data section:     variable  — 40-byte header + uint16 ADC samples]

    ---- Metadata blocks ----
    Each block has a 12-byte header (six u16 LE fields) followed by padded_size
    bytes of content.  When comp_size < decomp_size the content bytes
    [0 .. comp_size-1] are zlib-compressed; the remainder is zero padding.
    Blocks are read until a terminator block where padded_size == 0.

    Key blocks (identified by block_id and block_type):
      block_id=1, block_type=9  (~96 bytes decompressed)
        Offset  1..8  — int64 LE — voltage scale numerator
        scale = i64 / 750_000_000_000

      block_type=6  (~1628 bytes decompressed)
        Offset 36..39 — int32 LE — CH1 voltage centre × 1e8
        v_center = i32 / 1e8

    ---- Voltage calibration ----
      scale    = i64_ch1 / 750_000_000_000
      v_center = i32_settings / 1e8
      offset   = v_center - scale * 32768
      volts[i] = scale * raw_uint16[i] + offset

    ---- Data section ----
    The data section starts after the zero-padding region that follows the
    last metadata block.  Its offset cannot be determined statically; a
    sequential scan for the first non-zero byte is required.

    Data section header (40 bytes):
      offset+ 0:  u64 LE  — n_pts + 64  (identifies the section)
      offset+ 8:  8 bytes — capture marker (opaque)
      offset+16:  u32 LE  — x_increment in nanoseconds
      offset+20:  u32 LE  — unknown (79 in observed files)
      offset+24:  u32 LE  — n_pts (repeated)
      offset+28:  u32 LE  — n_pts (repeated)
      offset+32:  u32 LE  — timestamp / unknown
      offset+36:  u32 LE  — unknown (120 in observed files)
      offset+40:  uint16 LE samples begin (n_pts × 2 bytes)

    x_origin is not stored; it is derived as:
      x_origin = -(n_pts / 2) * x_increment
      t[i]     =  x_origin + i * x_increment

    LIMITATION: This KSY describes the block region only.  The zero-padding
    region and the data section require sequential runtime scanning and cannot
    be expressed as fixed-offset KSY instances.

seq:
  - id: file_header
    type: file_header
  - id: blocks
    type: block
    repeat: until
    repeat-until: _.padded_size == 0 and _.comp_size == 0
    doc: Metadata blocks terminated by an all-zero block header.

types:
  file_header:
    doc: |
      24-byte file header.  Internal structure not fully reverse-engineered;
      treated as opaque.
    seq:
      - id: reserved
        size: 24
        doc: File header bytes — internal layout not yet fully known.

  block:
    doc: |
      One metadata block.  A block with padded_size == 0 and comp_size == 0
      signals the end of the metadata region.
    seq:
      - id: block_id
        type: u2
        doc: |
          Channel / block identifier.
          1 = CH1 channel parameters (contains voltage scale factor at offset 1).
      - id: block_type
        type: u2
        enum: block_type_enum
        doc: |
          Content type.
          9 = channel parameters (block_id=1 carries scale numerator at offset 1).
          6 = trigger/display settings (carries v_center at offset 36).
      - id: decomp_size
        type: u2
        doc: Decompressed content size in bytes.
      - id: comp_size
        type: u2
        doc: |
          Compressed content size in bytes.
          Equal to decomp_size when content is stored verbatim (not compressed).
      - id: padded_size
        type: u2
        doc: |
          Total bytes consumed in the file for this block's content
          (comp_size rounded up to the next alignment boundary).
          Zero in the terminator block.
      - id: reserved
        type: u2
        doc: Always 0.
      - id: content_raw
        size: padded_size
        doc: |
          Block content bytes.  The first comp_size bytes hold the payload
          (zlib-compressed when comp_size != decomp_size; verbatim otherwise).
          Remaining bytes (padded_size - comp_size) are zero padding.
    instances:
      is_ch1_params:
        value: block_id == 1 and block_type == 9
        doc: |
          True for the CH1 channel-parameters block.
          Decompressed content bytes [1..8] hold an int64 LE voltage scale
          numerator: scale = i64 / 750_000_000_000.
      is_settings:
        value: block_type == 6
        doc: |
          True for the trigger/display settings block.
          Decompressed content bytes [36..39] hold an int32 LE voltage centre
          value: v_center = i32 / 1e8.
      is_terminator:
        value: padded_size == 0 and comp_size == 0
        doc: True for the sentinel block that ends the metadata region.

enums:
  block_type_enum:
    6: settings
    9: channel_params
