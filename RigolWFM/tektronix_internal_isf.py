# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild
# type: ignore

import kaitaistruct
from kaitaistruct import KaitaiStruct, KaitaiStream, BytesIO


if getattr(kaitaistruct, 'API_VERSION', (0, 9)) < (0, 11):
    raise Exception("Incompatible Kaitai Struct Python API: 0.11 or later is required, but you have %s" % (kaitaistruct.__version__))

class TektronixInternalIsf(KaitaiStruct):
    """Tektronix ISF (Internal Save Format) waveform file.
    
    Applies to: TDS300/340A/360/380, TDS1000/2000/3000, TDS5000B/6000/7000
    series, and most other Tektronix oscilloscopes that export waveforms in
    binary format.  The extension is ".ISF" or ".isf".
    
    File structure
    --------------
    The file consists of a variable-length ASCII text header immediately
    followed by a SCPI definite-length binary block containing the raw ADC
    samples::
    
      <text_header> '#' <n_digits> <byte_count_str> <curve_data>
    
    The text header is a sequence of semicolon-delimited key/value pairs.  No
    fixed layout exists — fields may appear in any order and optional fields may
    be absent.  Field names exist in two variants::
    
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
    not otherwise appear in the header, it uniquely marks the boundary::
    
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
    The raw sample encodings are::
    
      BYT_NR / BYT_N = 1: signed 8-bit integers  (int8)
      BYT_NR / BYT_N = 2: signed 16-bit integers (int16)
    
    BN_FMT / BN_F values::
    
      RI — signed (two's complement) integer (most common)
      RP — unsigned (positive) integer
    
    Voltage reconstruction
    ----------------------
    Analog samples are converted with::
    
      volts[i] = YZERO + YMULT * (adc[i] - YOFF)
    
    Time axis
    ---------
    For PT_FMT / PT_F = "Y" (normal single-value)::
    
      t[i] = XZERO + XINCR * (i - PT_OFF)    (i = 0 … NR_PT-1)
    
    For PT_FMT / PT_F = "ENV" (envelope min/max pairs, NR_PT is even)::
    
      sample_count = NR_PT / 2
      t[i] = XZERO + XINCR * (2*i - PT_OFF)  (i = 0 … sample_count-1)
      adc_min[i] = adc[2*i]
      adc_max[i] = adc[2*i + 1]
    
    References
    ----------
    Tektronix Programmer Manuals::
    
      TDS 340A / 360 / 380 (070-9442-02)
      TDS3000/B/C Series (071-0381-03)
      TDS5000B/6000/7000 Series
    
    Sources used for this KSY binary format: the Tektronix programmer manuals
    listed above together with the shared ISF adapter in this repository.
    
    Tested file formats: synthetic `.isf` fixtures in `tests/test_isf.py`
    covering metadata cleanup, voltage scaling, time-axis reconstruction, and
    autodetection; no checked-in real ISF file is present yet.
    
    Oscilloscope models this format may apply to: `TDS300` / `340A` / `360` /
    `380`, `TDS1000` / `2000` / `3000`, `TDS5000B` / `6000` / `7000`, and other
    Tektronix scopes that export ISF waveforms.
    """
    def __init__(self, _io, _parent=None, _root=None):
        super(TektronixInternalIsf, self).__init__(_io)
        self._parent = _parent
        self._root = _root or self
        self._read()

    def _read(self):
        self.header_text = (self._io.read_bytes_term(35, False, True, True)).decode(u"ASCII")
        self.n_digits = self._io.read_u1()
        self.byte_count_str = (self._io.read_bytes(self.n_digits - 48)).decode(u"ASCII")
        self.curve_data = self._io.read_bytes_full()


    def _fetch_instances(self):
        pass


