# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild
# type: ignore

import kaitaistruct
from kaitaistruct import KaitaiStruct, KaitaiStream, BytesIO


if getattr(kaitaistruct, 'API_VERSION', (0, 9)) < (0, 11):
    raise Exception("Incompatible Kaitai Struct Python API: 0.11 or later is required, but you have %s" % (kaitaistruct.__version__))

class YokogawaDlWeWvf(KaitaiStruct):
    """Binary waveform data (.wvf) produced by Yokogawa DL/WE-series oscilloscopes.
    
    Applicable models (per IM 707713-61E, WVF File Access Toolkit for MATLAB)
    --------------------------------------------------------------------------
    WE7000
    DL708, DL708E, DL716, DL750
    DL1720, DL1740
    DL1600 Series
    DL1500 Series
    DL7100, DL7200
    DL7400 Series
    
    Two-file format
    ---------------
    Every capture produces a PAIR of files that share the same base name:
    
      <name>.hdr   — ASCII text, key/value metadata (parsed separately)
      <name>.wvf   — this file: flat binary sample data
    
    ALL structural metadata (data type, sample count, voltage scaling, time
    axis, data layout) lives in the .hdr file.  The .wvf file is a plain byte
    array with no self-describing framing.  The companion .hdr MUST be parsed
    first; its fields supply the params used to interpret the binary data here.
    
    Sequential file mode
    --------------------
    Long captures are split across numbered files sharing the same header:
      <name>.wvf        — first segment (seriesNo = 0)
      <name>_2.wvf      — second segment (seriesNo = 1)
      <name>_3.wvf      — third segment, etc.
    All segments use the same companion <name>.hdr.
    
    Companion .hdr file — common information (ComInfo)
    ---------------------------------------------------
    The .hdr file is an ASCII key/value text file.  The WVF File Access API
    exposes these fields via ComInfo.  Both the .hdr key name and the API
    structure field name are shown where they differ.
    
      .hdr key          API field           Description
      -----------       -----------------   ------------------------------------------
      (none)            Comment             Free-text comment string
      TraceTotalNumber  ChanelNum           Total number of channels (note: API spells
                                            this "Chanel", one 'n')
      BlockSize         SamplingNum         Number of samples per channel per block
      HResolution       SamplingInterval    Time between samples (seconds/sample)
      (computed)        PreTrigger          Number of pre-trigger samples
      HUnit             XUnit               Horizontal axis unit (typically "s")
      Date              Date                Recording date (YYYY/MM/DD)
      Time              Time                Recording time (HH:MM:SS)
    
    Global .hdr section ($PublicInfo):
      FormatVersion   Version string (e.g. "1.11")
      Model           Oscilloscope model string (e.g. "WE7000", "DL1600")
      Endian          "Big" = big-endian (Motorola 68000 CPU)
                      "Ltl" = little-endian (Intel x86 CPU)
      DataFormat      "TRACE" or "BLOCK" — layout of the binary data (see below)
      GroupNumber     Number of data groups in the file
      TraceTotalNumber  Total number of traces (channels) across all groups
      DataOffset      Leading unused bytes at the start of the .wvf file;
                      the first sample byte is at this file offset.
    
    Per-group section ($Group<N>, one section per group, N = 1, 2, ...):
      TraceNumber     Number of traces in this group
      BlockNumber     Number of time blocks captured in this group
    
    Per-trace entries in .hdr (all on one line, space-separated, one value per
    trace; API per-channel structure is ChInfo[]):
    
      .hdr key        API field     Description
      ----------      ----------    -----------------------------------------------
      TraceName       ChanelName    Channel label (e.g. "CH1"); note API spelling
      BlockSize       (SamplingNum) Samples per block for this trace
      VResolution     ScaleA        Vertical scale factor (physical units / ADC count)
      VOffset         ScaleB        Vertical DC offset in physical units
      VDataType       dataType      ADC format code string (see VDataType codes below)
      VUnit           Unit          Physical unit string, e.g. "V" or "A"
      VPlusOverData   plusOverData  Raw ADC value meaning upper overrange (optional)
      VMinusOverData  minusOverData Raw ADC value meaning lower overrange (optional)
      VIllegalData    nonData       Raw ADC value meaning illegal/invalid sample
      VMaxData        dispMaxData   Maximum valid raw ADC value
      VMinData        dispMinData   Minimum valid raw ADC value
      HResolution     interval      Time between samples (seconds/sample)
      HOffset         time          Time of first sample relative to trigger (seconds)
      HUnit           XUnit         Horizontal axis unit (typically "s")
      Date/Date<N>    (Date)        Recording date per block (YYYY/MM/DD)
      Time/Time<N>    (Time)        Recording time per block (HH:MM:SS)
    
    Additional per-channel AcqInfo fields exposed by the API (not all appear in
    every .hdr file):
      startBit        First valid bit position in each sample word
      effectiveBit    Number of effective ADC bits
      trigActive      Trigger active flag
      record          Record type
      recordLen       Record length
      trigPosition    Trigger position (sample index, 0-origin)
      trigLevel       Trigger level in physical units
      trigWidth       Trigger pulse width
    
    VDataType codes  (.hdr string)
    ------------------------------
    Each trace entry in the .hdr carries a code describing its binary sample
    format.  This is the string that appears in the VDataType field:
    
      IS<n>   Signed integer,   n bytes per sample  (IS1=int8, IS2=int16, IS4=int32)
      IU<n>   Unsigned integer, n bytes per sample  (IU1=uint8, IU2=uint16, IU4=uint32)
      FS<n>   Signed IEEE 754 float, n bytes/sample (FS4=float32, FS8=float64)
      FU<n>   Unsigned float (parsed identically to FS<n>)
      B<m>    Raw binary (logic signals), m bytes/sample (B16 = 16-byte / 128-bit
              words; individual bits = digital channels; DL750 only)
    
    WVF File Access API dataForm codes  (numeric, used by mexWeDPDataRead etc.)
    ---------------------------------------------------------------------------
    When reading data via the API, the caller requests a conversion format:
      1  = WE_UBYTE   unsigned 8-bit integer
      17 = WE_SWORD   signed 16-bit integer
      33 = WE_SLONG   signed 32-bit integer
      34 = WE_FLOAT   IEEE 754 32-bit float
      50 = WE_DOUBLE  IEEE 754 64-bit float  (recommended for general use)
    
    These codes are distinct from the VDataType strings; they describe the
    output type requested by the caller, not the on-disk storage format.
    
    Data layout in .wvf
    -------------------
    After the DataOffset-byte preamble the samples are laid out in one of two
    orders depending on the .hdr DataFormat field.
    
    Block numbering convention:
      The WVF File Access API uses 0-origin block numbers (blockNo = 0 is the
      first block).  The offset formulas below use 1-based indices (b = 1..B[g])
      to match the MATLAB reference implementation; subtract 1 when translating
      API blockNo values.
    
    Let:
      G     = total number of groups
      T[g]  = number of traces in group g   (g = 1..G)
      B[g]  = number of blocks in group g
      S[g,t] = BlockSize (samples/block) for trace t in group g
      W[g,t] = VDataType byte-width for trace t in group g
    
    TRACE format  (DataFormat = "TRACE"):
      All blocks of a given trace are stored contiguously; traces ordered by group:
    
      for g = 1..G:
        for t = 1..T[g]:
          for b = 1..B[g]:
            S[g,t] × W[g,t]  raw bytes
    
      Byte offset of (group g, trace t, block b):
        DataOffset
        + sum_{g'<g} sum_{t'=1}^{T[g']}  S[g',t'] × B[g'] × W[g',t']
        + sum_{t'<t}  S[g,t'] × B[g] × W[g,t']
        + (b-1) × S[g,t] × W[g,t]
    
    BLOCK format  (DataFormat = "BLOCK"):
      All traces within a block are stored contiguously; blocks ordered by group:
    
      for g = 1..G:
        for b = 1..B[g]:
          for t = 1..T[g]:
            S[g,t] × W[g,t]  raw bytes
    
      Byte offset of (group g, trace t, block b):
        DataOffset
        + sum_{g'<g} sum_{b'=1}^{B[g']} sum_{t'=1}^{T[g']}  S[g',t'] × W[g',t']
        + sum_{b'<b} sum_{t'=1}^{T[g]}  S[g,t'] × W[g,t']
        + sum_{t'<t}  S[g,t'] × W[g,t']
    
    Voltage calibration
    --------------------
      volts[i] = VOffset + VResolution * raw[i]
               = ScaleB  + ScaleA      * raw[i]      (API field names)
    
    Time axis
    ---------
      t[i] = HOffset + HResolution * i   (i = 0 .. BlockSize-1, 0-based Python)
      t[i] = HOffset + HResolution * (i-1)  (i = 1 .. BlockSize, 1-based MATLAB)
    
    Endianness
    ----------
    The Endian field in the .hdr controls byte order for all multi-byte samples:
      "Big"  — big-endian (Motorola 68000 byte order; older DL series)
      "Ltl"  — little-endian (Intel x86 byte order; newer DL/WE series)
    
    Logic (B-type) traces
    ----------------------
    Logic channels (DL750 and similar) store 16-byte (128-bit) words per sample.
    Each bit represents one digital channel.  Extract individual bits with
    bitwise operations (e.g. Python: (raw >> bit) & 1).  These traces are not
    calibrated to physical units; the raw integer value is used directly.
    
    References
    ----------
    Yokogawa Electric Corporation, "Model 707713 WVF File Access Toolkit for
      MATLAB User's Manual", IM 707713-61E, 1st Edition, July 2003.
    Erik Benkler, "wvfread v1.7", Physikalisch-Technische Bundesanstalt, 2011.
    Yokogawa Technical Information TI 7000-21 E, 1998 (3rd edition).
    Yokogawa DL 1640 User Manual, Appendix 3.
    """
    def __init__(self, len_leading_unused, _io, _parent=None, _root=None):
        super(YokogawaDlWeWvf, self).__init__(_io)
        self._parent = _parent
        self._root = _root or self
        self.len_leading_unused = len_leading_unused
        self._read()

    def _read(self):
        self.leading_unused = self._io.read_bytes(self.len_leading_unused)
        self.samples_raw = self._io.read_bytes_full()


    def _fetch_instances(self):
        pass


