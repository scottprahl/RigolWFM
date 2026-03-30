# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild
# type: ignore

import kaitaistruct
from kaitaistruct import KaitaiStruct, KaitaiStream, BytesIO
from enum import IntEnum


if getattr(kaitaistruct, 'API_VERSION', (0, 9)) < (0, 11):
    raise Exception("Incompatible Kaitai Struct Python API: 0.11 or later is required, but you have %s" % (kaitaistruct.__version__))

class Lecroy23LeTrc(KaitaiStruct):
    """Teledyne LeCroy LECROY_2_3 binary waveform format (.trc files) — little-endian variant.
    
    This parser handles files where byte 34 (the low byte of COMM_ORDER) equals 1,
    indicating LOFIRST (little-endian) byte order.  Use lecroy_2_3_be for big-endian
    files (byte 34 == 0).
    
    File layout:
      [WAVEDESC block:   346 bytes  — main waveform descriptor (WAVE_DESCRIPTOR field)]
      [USERTEXT block:   variable  — optional free-form text (USER_TEXT bytes; 0 if absent)]
      [TRIGTIME array:   variable  — segment trigger times for sequence acquisitions]
      [RIS_TIME array:   variable  — random-interleaved-sampling time array (0 if absent)]
      [WAVE_ARRAY_1:     variable  — primary sample data (WAVE_ARRAY_1 bytes)]
      [WAVE_ARRAY_2:     variable  — secondary sample data (0 if absent)]
    
    WAVEDESC always starts with the 8-byte ASCII marker "WAVEDESC", null-padded to
    16 bytes.  Normal .trc files written by the oscilloscope begin at byte 0.  Files
    transferred via SCPI may carry a short numeric prefix before WAVEDESC; those
    files are not supported directly by this parser.
    
    Endianness detection (performed by the caller before selecting this parser):
      COMM_ORDER is a u2 at offset 34.  Because COMM_ORDER can only be 0 or 1,
      the low byte at offset 34 is unambiguous in both byte orders:
        byte 34 == 0  →  HIFIRST (big-endian,    use lecroy_2_3_be)
        byte 34 == 1  →  LOFIRST (little-endian, use lecroy_2_3_le)
    
    Voltage reconstruction (single sweep):
      volts[i] = VERTICAL_GAIN * adc[i] - VERTICAL_OFFSET
    where adc[i] is signed 8-bit (COMM_TYPE == byte) or signed 16-bit (COMM_TYPE == word).
    
    Time axis:
      t[i] = HORIZ_OFFSET + i * HORIZ_INTERVAL   (i = 0 … WAVE_ARRAY_COUNT − 1)
    
    For sequence acquisitions (SUBARRAY_COUNT > 1), the time axis for segment k is:
      t[k,i] = (trigtime_array[k].trigger_time + trigtime_array[k].trigger_offset)
               + i * HORIZ_INTERVAL
    """

    class BandwidthLimitEnum(IntEnum):
        bw_full = 0
        bw_limited = 1

    class CommOrderEnum(IntEnum):
        big_endian = 0
        little_endian = 1

    class CommTypeEnum(IntEnum):
        byte = 0
        word = 1

    class ProcessingDoneEnum(IntEnum):
        no_processing = 0
        fir_filter = 1
        interpolated = 2
        sparsed = 3
        autoscaled = 4
        no_result = 5
        rolling = 6
        cumulative = 7

    class RecordTypeEnum(IntEnum):
        single_sweep = 0
        interleaved = 1
        histogram = 2
        graph = 3
        filter_coefficient = 4
        complex = 5
        extrema = 6
        sequence_obsolete = 7
        centered_ris = 8
        peak_detect = 9

    class VertCouplingEnum(IntEnum):
        dc_50_ohm = 0
        ground = 1
        dc_1m_ohm = 2
        ground_b = 3
        ac_1m_ohm = 4

    class WaveSourceEnum(IntEnum):
        channel_1 = 0
        channel_2 = 1
        channel_3 = 2
        channel_4 = 3
        unknown = 4
    def __init__(self, _io, _parent=None, _root=None):
        super(Lecroy23LeTrc, self).__init__(_io)
        self._parent = _parent
        self._root = _root or self
        self._read()

    def _read(self):
        self.wavedesc = Lecroy23LeTrc.Wavedesc(self._io, self, self._root)


    def _fetch_instances(self):
        pass
        self.wavedesc._fetch_instances()
        _ = self.trigtime_array
        if hasattr(self, '_m_trigtime_array'):
            pass
            for i in range(len(self._m_trigtime_array)):
                pass
                self._m_trigtime_array[i]._fetch_instances()


        _ = self.user_text
        if hasattr(self, '_m_user_text'):
            pass

        _ = self.wave_array_1
        if hasattr(self, '_m_wave_array_1'):
            pass

        _ = self.wave_array_2
        if hasattr(self, '_m_wave_array_2'):
            pass


    class TriggerTimestamp(KaitaiStruct):
        """16-byte absolute trigger timestamp embedded in WAVEDESC at offset 296.
        Endianness is inherited from the root type.
        """
        def __init__(self, _io, _parent=None, _root=None):
            super(Lecroy23LeTrc.TriggerTimestamp, self).__init__(_io)
            self._parent = _parent
            self._root = _root
            self._read()

        def _read(self):
            self.seconds = self._io.read_f8le()
            self.minutes = self._io.read_u1()
            self.hours = self._io.read_u1()
            self.days = self._io.read_u1()
            self.months = self._io.read_u1()
            self.year = self._io.read_s2le()
            self.unused = self._io.read_s2le()


        def _fetch_instances(self):
            pass


    class TrigtimeEntry(KaitaiStruct):
        """One 16-byte record in the TRIGTIME array.  Present only for sequence-mode
        acquisitions (SUBARRAY_COUNT > 1).  Endianness is inherited from the root type.
        
        Time axis for segment k (0-based):
          t[k,i] = (trigger_time + trigger_offset) + i * HORIZ_INTERVAL
        """
        def __init__(self, _io, _parent=None, _root=None):
            super(Lecroy23LeTrc.TrigtimeEntry, self).__init__(_io)
            self._parent = _parent
            self._root = _root
            self._read()

        def _read(self):
            self.trigger_time = self._io.read_f8le()
            self.trigger_offset = self._io.read_f8le()


        def _fetch_instances(self):
            pass


    class Wavedesc(KaitaiStruct):
        """346-byte WAVEDESC header block (LECROY_2_3 template).  All byte offsets in the
        original LeCroy template documentation are relative to the start of this struct.
        Endianness is inherited from the root type (little-endian).
        """
        def __init__(self, _io, _parent=None, _root=None):
            super(Lecroy23LeTrc.Wavedesc, self).__init__(_io)
            self._parent = _parent
            self._root = _root
            self._read()

        def _read(self):
            self.descriptor_name = self._io.read_bytes(16)
            self.template_name = self._io.read_bytes(16)
            self.comm_type = KaitaiStream.resolve_enum(Lecroy23LeTrc.CommTypeEnum, self._io.read_u2le())
            self.comm_order = KaitaiStream.resolve_enum(Lecroy23LeTrc.CommOrderEnum, self._io.read_u2le())
            self.wave_descriptor = self._io.read_s4le()
            self.user_text_len = self._io.read_s4le()
            self.res_desc1 = self._io.read_s4le()
            self.trigtime_array_len = self._io.read_s4le()
            self.ris_time_array_len = self._io.read_s4le()
            self.res_array1 = self._io.read_s4le()
            self.wave_array_1_len = self._io.read_s4le()
            self.wave_array_2_len = self._io.read_s4le()
            self.res_array2 = self._io.read_s4le()
            self.res_array3 = self._io.read_s4le()
            self.instrument_name = self._io.read_bytes(16)
            self.instrument_number = self._io.read_s4le()
            self.trace_label = self._io.read_bytes(16)
            self.reserved1 = self._io.read_s2le()
            self.reserved2 = self._io.read_s2le()
            self.wave_array_count = self._io.read_s4le()
            self.pnts_per_screen = self._io.read_s4le()
            self.first_valid_pnt = self._io.read_s4le()
            self.last_valid_pnt = self._io.read_s4le()
            self.first_point = self._io.read_s4le()
            self.sparsing_factor = self._io.read_s4le()
            self.segment_index = self._io.read_s4le()
            self.subarray_count = self._io.read_s4le()
            self.sweeps_per_acq = self._io.read_s4le()
            self.points_per_pair = self._io.read_s2le()
            self.pair_offset = self._io.read_s2le()
            self.vertical_gain = self._io.read_f4le()
            self.vertical_offset = self._io.read_f4le()
            self.max_value = self._io.read_f4le()
            self.min_value = self._io.read_f4le()
            self.nominal_bits = self._io.read_s2le()
            self.nom_subarray_count = self._io.read_s2le()
            self.horiz_interval = self._io.read_f4le()
            self.horiz_offset = self._io.read_f8le()
            self.pixel_offset = self._io.read_f8le()
            self.vert_unit = self._io.read_bytes(48)
            self.hor_unit = self._io.read_bytes(48)
            self.horiz_uncertainty = self._io.read_f4le()
            self.trigger_time = Lecroy23LeTrc.TriggerTimestamp(self._io, self, self._root)
            self.acq_duration = self._io.read_f4le()
            self.record_type = KaitaiStream.resolve_enum(Lecroy23LeTrc.RecordTypeEnum, self._io.read_u2le())
            self.processing_done = KaitaiStream.resolve_enum(Lecroy23LeTrc.ProcessingDoneEnum, self._io.read_u2le())
            self.reserved5 = self._io.read_s2le()
            self.ris_sweeps = self._io.read_s2le()
            self.timebase = self._io.read_u2le()
            self.vert_coupling = KaitaiStream.resolve_enum(Lecroy23LeTrc.VertCouplingEnum, self._io.read_u2le())
            self.probe_att = self._io.read_f4le()
            self.fixed_vert_gain = self._io.read_u2le()
            self.bandwidth_limit = KaitaiStream.resolve_enum(Lecroy23LeTrc.BandwidthLimitEnum, self._io.read_u2le())
            self.vertical_vernier = self._io.read_f4le()
            self.acq_vert_offset = self._io.read_f4le()
            self.wave_source = KaitaiStream.resolve_enum(Lecroy23LeTrc.WaveSourceEnum, self._io.read_u2le())


        def _fetch_instances(self):
            pass
            self.trigger_time._fetch_instances()

        @property
        def is_16bit(self):
            """True when samples are 16-bit words; false for 8-bit bytes."""
            if hasattr(self, '_m_is_16bit'):
                return self._m_is_16bit

            self._m_is_16bit = self.comm_type == Lecroy23LeTrc.CommTypeEnum.word
            return getattr(self, '_m_is_16bit', None)

        @property
        def is_sequence(self):
            """True when this is a sequence-mode (multi-segment) acquisition."""
            if hasattr(self, '_m_is_sequence'):
                return self._m_is_sequence

            self._m_is_sequence = self.subarray_count > 1
            return getattr(self, '_m_is_sequence', None)

        @property
        def seconds_per_point(self):
            """Alias for horiz_interval; seconds between consecutive ADC samples."""
            if hasattr(self, '_m_seconds_per_point'):
                return self._m_seconds_per_point

            self._m_seconds_per_point = self.horiz_interval
            return getattr(self, '_m_seconds_per_point', None)

        @property
        def volt_per_division(self):
            """Vertical scale in volts per division.  MAX_VALUE and MIN_VALUE are ADC
            counts; multiply by vertical_gain to convert to volts, then divide by
            the standard 8-division display height.
            """
            if hasattr(self, '_m_volt_per_division'):
                return self._m_volt_per_division

            self._m_volt_per_division = ((self.max_value - self.min_value) * self.vertical_gain) / 8.0
            return getattr(self, '_m_volt_per_division', None)


    @property
    def trigtime_array(self):
        """Per-segment trigger-time entries for sequence acquisitions.
        Present only when SUBARRAY_COUNT > 1.  Each entry is 16 bytes
        (two f8 values: trigger_time, trigger_offset).
        """
        if hasattr(self, '_m_trigtime_array'):
            return self._m_trigtime_array

        if self.wavedesc.trigtime_array_len > 0:
            pass
            _pos = self._io.pos()
            self._io.seek(self.wavedesc.wave_descriptor + self.wavedesc.user_text_len)
            self._m_trigtime_array = []
            for i in range(self.wavedesc.trigtime_array_len // 16):
                self._m_trigtime_array.append(Lecroy23LeTrc.TrigtimeEntry(self._io, self, self._root))

            self._io.seek(_pos)

        return getattr(self, '_m_trigtime_array', None)

    @property
    def user_text(self):
        """Optional ASCII user text (up to 160 bytes)."""
        if hasattr(self, '_m_user_text'):
            return self._m_user_text

        if self.wavedesc.user_text_len > 0:
            pass
            _pos = self._io.pos()
            self._io.seek(self.wavedesc.wave_descriptor)
            self._m_user_text = self._io.read_bytes(self.wavedesc.user_text_len)
            self._io.seek(_pos)

        return getattr(self, '_m_user_text', None)

    @property
    def wave_array_1(self):
        """Primary sample data as raw bytes.
        Interpret as s1 array (COMM_TYPE == byte) or s2 array (COMM_TYPE == word),
        little-endian byte order.
        Apply: volts[i] = VERTICAL_GAIN * adc[i] - VERTICAL_OFFSET.
        """
        if hasattr(self, '_m_wave_array_1'):
            return self._m_wave_array_1

        _pos = self._io.pos()
        self._io.seek(((self.wavedesc.wave_descriptor + self.wavedesc.user_text_len) + self.wavedesc.trigtime_array_len) + self.wavedesc.ris_time_array_len)
        self._m_wave_array_1 = self._io.read_bytes(self.wavedesc.wave_array_1_len)
        self._io.seek(_pos)
        return getattr(self, '_m_wave_array_1', None)

    @property
    def wave_array_2(self):
        """Secondary sample data as raw bytes (same format as wave_array_1).
        Interpretation depends on RECORD_TYPE:
          extrema (6)     — floor (minimum) trace
          complex (5)     — imaginary part of FFT
          peak_detect (9) — floor trace
        """
        if hasattr(self, '_m_wave_array_2'):
            return self._m_wave_array_2

        if self.wavedesc.wave_array_2_len > 0:
            pass
            _pos = self._io.pos()
            self._io.seek((((self.wavedesc.wave_descriptor + self.wavedesc.user_text_len) + self.wavedesc.trigtime_array_len) + self.wavedesc.ris_time_array_len) + self.wavedesc.wave_array_1_len)
            self._m_wave_array_2 = self._io.read_bytes(self.wavedesc.wave_array_2_len)
            self._io.seek(_pos)

        return getattr(self, '_m_wave_array_2', None)


