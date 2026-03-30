meta:
  id: tek_isf
  title: Tektronix ISF Binary Format
  file-extension: isf
  encoding: ASCII
  endian: le

doc: |
  Tektronix ISF (Internal Save Format) waveform file.

  Applies to: TDS300/340A/360/380, TDS1000/2000/3000, TDS5000B/6000/7000
  series, and most other Tektronix oscilloscopes that export waveforms in
  binary format.  The extension is ".ISF" or ".isf".

  File structure
  --------------
  The file consists of a variable-length ASCII text header immediately
  followed by a SCPI definite-length binary block containing the raw ADC
  samples.

    <text_header> '#' <n_digits> <byte_count_str> <curve_data>

  The text header is a sequence of semicolon-delimited key/value pairs.  No
  fixed layout exists — fields may appear in any order and optional fields may
  be absent.  Field names exist in two variants:

    Long form (older firmware):   BYT_NR, BIT_NR, ENCDG, BN_FMT, BYT_OR,
                                  WFID, NR_PT, PT_FMT, XUNIT, XINCR, PT_OFF,
                                  YUNIT, YMULT, YOFF, YZERO
    Short form (newer firmware):  BYT_N,  BIT_N,  ENC,   BN_F,   BYT_O,
                                  WFI,    NR_P,   PT_F,   XUN,    XIN,   PT_O,
                                  YUN,    YMU,    YOF,    YZE

  Both variants may appear in the same file (the short-form prefix appears
  first as a ":WFMP:" SCPI response header, then the long-form values follow
  without the prefix).  All numeric values use IEEE floating-point notation
  (e.g. "6.2500E-6").

  The SCPI definite-length binary block starts with the hash character '#'
  that immediately follows the last semicolon/header pair.  Because '#' does
  not otherwise appear in the header, it uniquely marks the boundary.

    '#' consumed as terminator of header_text
    n_digits      — 1 ASCII digit: the count of decimal digits that follow
    byte_count_str — that many ASCII digits: total byte count of curve_data
    curve_data    — NR_PT × BYT_NR raw sample bytes

  Note: some files have a trailing newline (0x0A) after the last curve byte.
  Parsers should use size-eos to capture all remaining bytes and let the
  caller trim trailing whitespace.

  Endianness
  ----------
  BYT_OR / BYT_O in the header: "MSB" = big-endian, "LSB" = little-endian.
  Because the endianness is encoded in the text header this parser treats
  curve_data as opaque bytes; the calling code must apply the correct byte
  order when unpacking the samples.

  Sample data types
  -----------------
  BYT_NR / BYT_N = 1: signed 8-bit integers  (int8)
  BYT_NR / BYT_N = 2: signed 16-bit integers (int16)

  BN_FMT / BN_F values:
    RI — signed (two's complement) integer (most common)
    RP — unsigned (positive) integer

  Voltage reconstruction
  ----------------------
    volts[i] = YZERO + YMULT * (adc[i] - YOFF)

  Time axis
  ---------
  For PT_FMT / PT_F = "Y" (normal single-value):
    t[i] = XZERO + XINCR * (i - PT_OFF)    (i = 0 … NR_PT-1)

  For PT_FMT / PT_F = "ENV" (envelope min/max pairs, NR_PT is even):
    sample_count = NR_PT / 2
    t[i] = XZERO + XINCR * (2*i - PT_OFF)  (i = 0 … sample_count-1)
    adc_min[i] = adc[2*i]
    adc_max[i] = adc[2*i + 1]

  References
  ----------
  Tektronix Programmer Manuals:
    TDS 340A / 360 / 380 (070-9442-02)
    TDS3000/B/C Series (071-0381-03)
    TDS5000B/6000/7000 Series

seq:
  - id: header_text
    type: str
    encoding: ASCII
    terminator: 0x23
    doc: |
      ASCII text header containing the semicolon-delimited key=value metadata.
      The '#' terminator (0x23) is consumed and marks the start of the SCPI
      binary block; it is not included in this field.  The string therefore
      ends with ":CURV " or ":CURVE " (the trailing space before the hash).

  - id: n_digits
    type: u1
    doc: |
      First byte of the SCPI definite-length binary block, stored as an ASCII
      decimal digit character ('1'–'9').  Its numeric value is
      (n_digits - 0x30).  It specifies how many ASCII digits follow in
      byte_count_str.

  - id: byte_count_str
    type: str
    size: n_digits - 0x30
    encoding: ASCII
    doc: |
      ASCII decimal string giving the total number of bytes in curve_data.
      Has exactly (n_digits - 0x30) characters.  Its value must equal
      NR_PT * BYT_NR as declared in the text header.

  - id: curve_data
    size-eos: true
    doc: |
      Raw ADC sample bytes.  The length is NR_PT * BYT_NR as declared in the
      text header and confirmed by byte_count_str.

      Samples are packed tightly with no padding:
        BYT_NR = 1: each sample is one int8  / uint8 byte
        BYT_NR = 2: each sample is two bytes in the order given by BYT_OR
                    (MSB = big-endian, LSB = little-endian)

      For PT_FMT "ENV", alternating pairs (min, max) are interleaved:
        adc[0]=min[0], adc[1]=max[0], adc[2]=min[1], adc[3]=max[1], …

      A trailing 0x0A newline byte may be present; callers should strip it.
