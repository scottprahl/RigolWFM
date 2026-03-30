# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild
# type: ignore

import kaitaistruct
from kaitaistruct import KaitaiStruct, KaitaiStream, BytesIO
from enum import IntEnum


if getattr(kaitaistruct, 'API_VERSION', (0, 9)) < (0, 11):
    raise Exception("Incompatible Kaitai Struct Python API: 0.11 or later is required, but you have %s" % (kaitaistruct.__version__))

class Lecroy10BeTrc(KaitaiStruct):
    """Teledyne LeCroy LECROY_1_0 binary waveform format (.trc / .000 files) — big-endian variant.
    
    This older format has a 320-byte WAVEDESC (vs 346 bytes in LECROY_2_3) with a different
    field layout.  Key differences from LECROY_2_3:
      - wave_array_1_len is at offset 48 (not 60)
      - instrument_name is at offset 56 (not 76)
      - wave_array_count is at offset 92 (not 116)
      - vertical calibration: volts[i] = vertical_gain * adc[i] - acq_vert_offset
      - wave_source at offset 296 is 1-indexed (1=CH1, 2=CH2, …)
      - No ris_time_array field
    
    Endianness detection (performed by the caller before selecting this parser):
      COMM_ORDER is a u2 at offset 34.  byte 34 == 0 → HIFIRST (little-endian, use lecroy_1_0_le).
    
    Voltage reconstruction:
      volts[i] = vertical_gain * adc[i] - acq_vert_offset
    where adc[i] is signed 8-bit (COMM_TYPE == byte) or signed 16-bit (COMM_TYPE == word).
    
    Time axis:
      t[i] = horiz_offset + i * horiz_interval   (i = 0 … wave_array_count − 1)
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

    class VertCouplingEnum(IntEnum):
        dc_50_ohm = 0
        ground = 1
        dc_1m_ohm = 2
        ground_b = 3
        ac_1m_ohm = 4
    def __init__(self, _io, _parent=None, _root=None):
        super(Lecroy10BeTrc, self).__init__(_io)
        self._parent = _parent
        self._root = _root or self
        self._read()

    def _read(self):
        self.wavedesc = Lecroy10BeTrc.Wavedesc(self._io, self, self._root)


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
        """16-byte absolute trigger timestamp."""
        def __init__(self, _io, _parent=None, _root=None):
            super(Lecroy10BeTrc.TriggerTimestamp, self).__init__(_io)
            self._parent = _parent
            self._root = _root
            self._read()

        def _read(self):
            self.seconds = self._io.read_f8be()
            self.minutes = self._io.read_u1()
            self.hours = self._io.read_u1()
            self.days = self._io.read_u1()
            self.months = self._io.read_u1()
            self.year = self._io.read_s2be()
            self.unused = self._io.read_s2be()


        def _fetch_instances(self):
            pass


    class TrigtimeEntry(KaitaiStruct):
        """One 16-byte record in the TRIGTIME array."""
        def __init__(self, _io, _parent=None, _root=None):
            super(Lecroy10BeTrc.TrigtimeEntry, self).__init__(_io)
            self._parent = _parent
            self._root = _root
            self._read()

        def _read(self):
            self.trigger_time = self._io.read_f8be()
            self.trigger_offset = self._io.read_f8be()


        def _fetch_instances(self):
            pass


    class Wavedesc(KaitaiStruct):
        """320-byte WAVEDESC header block (LECROY_1_0 template).  All byte offsets are
        relative to the start of this struct.  Endianness is inherited from root (big-endian).
        """
        def __init__(self, _io, _parent=None, _root=None):
            super(Lecroy10BeTrc.Wavedesc, self).__init__(_io)
            self._parent = _parent
            self._root = _root
            self._read()

        def _read(self):
            self.descriptor_name = self._io.read_bytes(16)
            self.template_name = self._io.read_bytes(16)
            self.comm_type = KaitaiStream.resolve_enum(Lecroy10BeTrc.CommTypeEnum, self._io.read_u2be())
            self.comm_order = KaitaiStream.resolve_enum(Lecroy10BeTrc.CommOrderEnum, self._io.read_u2be())
            self.wave_descriptor = self._io.read_s4be()
            self.user_text_len = self._io.read_s4be()
            self.trigtime_array_len = self._io.read_s4be()
            self.wave_array_1_len = self._io.read_s4be()
            self.wave_array_2_len = self._io.read_s4be()
            self.instrument_name = self._io.read_bytes(16)
            self.instrument_number = self._io.read_s4be()
            self.trace_label = self._io.read_bytes(16)
            self.wave_array_count = self._io.read_s4be()
            self.points_per_screen = self._io.read_s4be()
            self.first_valid_pnt = self._io.read_s4be()
            self.last_valid_pnt = self._io.read_s4be()
            self.subarray_count = self._io.read_s4be()
            self.nom_subarray_count = self._io.read_s4be()
            self.sweeps_per_acq = self._io.read_s4be()
            self.vertical_gain = self._io.read_f4be()
            self.vertical_offset = self._io.read_f4be()
            self.max_value = self._io.read_s2be()
            self.min_value = self._io.read_s2be()
            self.nominal_bits = self._io.read_s2be()
            self.horiz_interval = self._io.read_f4be()
            self.horiz_offset = self._io.read_f8be()
            self.pixel_offset = self._io.read_f8be()
            self.vert_unit = self._io.read_bytes(48)
            self.hor_unit = self._io.read_bytes(48)
            self.trigger_time = Lecroy10BeTrc.TriggerTimestamp(self._io, self, self._root)
            self.acq_duration = self._io.read_f4be()
            self.record_type = self._io.read_s2be()
            self.processing_done = self._io.read_s2be()
            self.timebase = self._io.read_u2be()
            self.vert_coupling = KaitaiStream.resolve_enum(Lecroy10BeTrc.VertCouplingEnum, self._io.read_u2be())
            self.probe_att = self._io.read_f4be()
            self.fixed_vert_gain = self._io.read_u2be()
            self.bandwidth_limit = KaitaiStream.resolve_enum(Lecroy10BeTrc.BandwidthLimitEnum, self._io.read_u2be())
            self.vert_vernier = self._io.read_f4be()
            self.acq_vert_offset = self._io.read_f4be()
            self.wave_source_plugin = self._io.read_s2be()
            self.wave_source = self._io.read_s2be()
            self.trigger_source = self._io.read_s2be()
            self.trigger_coupling = self._io.read_s2be()
            self.trigger_slope = self._io.read_s2be()
            self.smart_trigger = self._io.read_s2be()
            self.trigger_level = self._io.read_f4be()
            self.sweeps_array_1 = self._io.read_s4be()
            self.sweeps_array_2 = self._io.read_s4be()
            self.reserved_end = self._io.read_bytes(2)


        def _fetch_instances(self):
            pass
            self.trigger_time._fetch_instances()

        @property
        def is_16bit(self):
            """True when samples are 16-bit words; false for 8-bit bytes."""
            if hasattr(self, '_m_is_16bit'):
                return self._m_is_16bit

            self._m_is_16bit = self.comm_type == Lecroy10BeTrc.CommTypeEnum.word
            return getattr(self, '_m_is_16bit', None)

        @property
        def is_sequence(self):
            """True when this is a sequence-mode acquisition."""
            if hasattr(self, '_m_is_sequence'):
                return self._m_is_sequence

            self._m_is_sequence = self.subarray_count > 1
            return getattr(self, '_m_is_sequence', None)

        @property
        def seconds_per_point(self):
            """Alias for horiz_interval."""
            if hasattr(self, '_m_seconds_per_point'):
                return self._m_seconds_per_point

            self._m_seconds_per_point = self.horiz_interval
            return getattr(self, '_m_seconds_per_point', None)

        @property
        def volt_per_division(self):
            """Vertical scale in volts per division, computed from the full ADC count
            range scaled by vertical_gain and divided by 8 display divisions.
            """
            if hasattr(self, '_m_volt_per_division'):
                return self._m_volt_per_division

            self._m_volt_per_division = ((self.max_value - self.min_value) * self.vertical_gain) / 8.0
            return getattr(self, '_m_volt_per_division', None)


    @property
    def trigtime_array(self):
        """Per-segment trigger-time entries for sequence acquisitions."""
        if hasattr(self, '_m_trigtime_array'):
            return self._m_trigtime_array

        if self.wavedesc.trigtime_array_len > 0:
            pass
            _pos = self._io.pos()
            self._io.seek(self.wavedesc.wave_descriptor + self.wavedesc.user_text_len)
            self._m_trigtime_array = []
            for i in range(self.wavedesc.trigtime_array_len // 16):
                self._m_trigtime_array.append(Lecroy10BeTrc.TrigtimeEntry(self._io, self, self._root))

            self._io.seek(_pos)

        return getattr(self, '_m_trigtime_array', None)

    @property
    def user_text(self):
        """Optional ASCII user text."""
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
        big-endian byte order.
        Apply: volts[i] = vertical_gain * adc[i] - acq_vert_offset.
        """
        if hasattr(self, '_m_wave_array_1'):
            return self._m_wave_array_1

        _pos = self._io.pos()
        self._io.seek((self.wavedesc.wave_descriptor + self.wavedesc.user_text_len) + self.wavedesc.trigtime_array_len)
        self._m_wave_array_1 = self._io.read_bytes(self.wavedesc.wave_array_1_len)
        self._io.seek(_pos)
        return getattr(self, '_m_wave_array_1', None)

    @property
    def wave_array_2(self):
        """Secondary sample data as raw bytes."""
        if hasattr(self, '_m_wave_array_2'):
            return self._m_wave_array_2

        if self.wavedesc.wave_array_2_len > 0:
            pass
            _pos = self._io.pos()
            self._io.seek(((self.wavedesc.wave_descriptor + self.wavedesc.user_text_len) + self.wavedesc.trigtime_array_len) + self.wavedesc.wave_array_1_len)
            self._m_wave_array_2 = self._io.read_bytes(self.wavedesc.wave_array_2_len)
            self._io.seek(_pos)

        return getattr(self, '_m_wave_array_2', None)


