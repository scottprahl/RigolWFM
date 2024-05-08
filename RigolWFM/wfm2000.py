# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild

import kaitaistruct
from kaitaistruct import KaitaiStruct, KaitaiStream, BytesIO
from enum import Enum


if getattr(kaitaistruct, 'API_VERSION', (0, 9)) < (0, 9):
    raise Exception("Incompatible Kaitai Struct Python API: 0.9 or later is required, but you have %s" % (kaitaistruct.__version__))

class Wfm2000(KaitaiStruct):

    class UnitEnum(Enum):
        w = 0
        a = 1
        v = 2
        u = 3

    class ProbeRatioEnum(Enum):
        x0_01 = 0
        x0_02 = 1
        x0_05 = 2
        x0_1 = 3
        x0_2 = 4
        x0_5 = 5
        x1 = 6
        x2 = 7
        x5 = 8
        x10 = 9
        x20 = 10
        x50 = 11
        x100 = 12
        x200 = 13
        x500 = 14
        x1000 = 15

    class ImpedanceEnum(Enum):
        ohm_50 = 0
        ohm_1meg = 1

    class ProbeTypeEnum(Enum):
        normal_type = 0
        differential = 1

    class ProbeEnum(Enum):
        single = 0
        diff = 1

    class FilterEnum(Enum):
        low_pass = 0
        high_pass = 1
        band_pass = 2
        band_reject = 3

    class BandwidthEnum(Enum):
        no_limit = 0
        mhz_20 = 1
        mhz_100 = 2
        mhz_200 = 3
        mhz_250 = 4

    class TimeEnum(Enum):
        yt = 0
        xy = 1
        roll = 2

    class AcquisitionEnum(Enum):
        normal = 0
        average = 1
        peak = 2
        high_resolution = 3

    class CouplingEnum(Enum):
        dc = 0
        ac = 1
        gnd = 2
    def __init__(self, _io, _parent=None, _root=None):
        self._io = _io
        self._parent = _parent
        self._root = _root if _root else self
        self._read()

    def _read(self):
        pass

    class Header(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.magic = self._io.read_bytes(4)
            if not self.magic == b"\xA5\xA5\x38\x00":
                raise kaitaistruct.ValidationNotEqualError(b"\xA5\xA5\x38\x00", self.magic, self._io, u"/types/header/seq/0")
            self.model_number = (KaitaiStream.bytes_terminate(self._io.read_bytes(20), 0, False)).decode(u"ascii")
            self.firmware_version = (KaitaiStream.bytes_terminate(self._io.read_bytes(20), 0, False)).decode(u"ascii")
            self.block_num = self._io.read_bytes(2)
            if not self.block_num == b"\x01\x00":
                raise kaitaistruct.ValidationNotEqualError(b"\x01\x00", self.block_num, self._io, u"/types/header/seq/3")
            self.file_version = self._io.read_u2le()
            self.unused_1 = self._io.read_bytes(8)
            self.crc = self._io.read_u4le()
            self.structure_size = self._io.read_u2le()
            self.structure_version = self._io.read_u2le()
            self.enabled = Wfm2000.ChannelMask(self._io, self, self._root)
            self.extra_1a = self._io.read_bytes(2)
            self.channel_offset = []
            for i in range(4):
                self.channel_offset.append(self._io.read_u4le())

            self.acquisition_mode = KaitaiStream.resolve_enum(Wfm2000.AcquisitionEnum, self._io.read_u2le())
            self.average_time = self._io.read_u2le()
            self.sample_mode = self._io.read_u2le()
            self.extra_1b = self._io.read_bytes(2)
            self.mem_depth = self._io.read_u4le()
            self.sample_rate_hz = self._io.read_f4le()
            self.extra_1c = self._io.read_bytes(2)
            self.time_mode = KaitaiStream.resolve_enum(Wfm2000.TimeEnum, self._io.read_u2le())
            self.time_scale_ps = self._io.read_u8le()
            self.time_offset_ps = self._io.read_s8le()
            self.ch = []
            for i in range(4):
                self.ch.append(Wfm2000.ChannelHeader(self._io, self, self._root))

            self.setup_size = self._io.read_u4le()
            self.setup_offset = self._io.read_u4le()
            self.wfm_offset = self._io.read_u4le()
            self.storage_depth = self._io.read_u4le()
            self.z_pt_offset = self._io.read_u4le()
            self.wfm_len = self._io.read_u4le()
            self.equ_coarse = []
            for i in range(2):
                self.equ_coarse.append(self._io.read_u2le())

            self.equ_fine = []
            for i in range(2):
                self.equ_fine.append(self._io.read_u2le())

            self.mem_start_addr = []
            for i in range(2):
                self.mem_start_addr.append(self._io.read_u4le())

            self.mem_last_addr = self._io.read_u4le()
            self.mem_length = self._io.read_u4le()
            self.channel_depth = self._io.read_u4le()
            self.bank_size = self._io.read_u4le()
            self.bank_offset = self._io.read_u4le()
            self.real_offset = self._io.read_u4le()
            self.real_ch_offset = self._io.read_u4le()
            self.horiz_slow_force_stop_frame_boolean = self._io.read_u1()
            self.get_spu_dig_data_status_boolean = self._io.read_u1()
            self.spu_load_data_status_boolean = self._io.read_u1()
            self.trig_delay_mem_offset = self._io.read_s8le()
            self.trig_delay_view_offset = self._io.read_s8le()
            self.mem_offset_compensate = self._io.read_s8le()
            self.slow_delta_wave_length = self._io.read_s8le()
            self.channel_pos_max_delay = self._io.read_s8le()
            self.channel_neg_min_delay = self._io.read_s8le()
            self.real_sa_dot_period = self._io.read_u8le()
            self.mem_offset_base = self._io.read_u8le()
            self.trig_type_delta_delay = self._io.read_s4le()
            self.ch1_delay = self._io.read_s4le()
            self.ch2_delay = self._io.read_s4le()
            self.channel_delay_to_mem_len = self._io.read_u4le()
            self.spu_mem_bank_size = self._io.read_u4le()
            self.roll_scrn_wave_length = self._io.read_u2le()
            self.trigger_source = self._io.read_u1()
            self.cal_index = self._io.read_u1()
            self.record_frame_index = self._io.read_u4le()
            self.frame_cur = self._io.read_u4le()

        @property
        def len_raw_3(self):
            if hasattr(self, '_m_len_raw_3'):
                return self._m_len_raw_3

            self._m_len_raw_3 = (self.raw_depth if self.channel_offset[2] > 0 else 0)
            return getattr(self, '_m_len_raw_3', None)

        @property
        def points(self):
            if hasattr(self, '_m_points'):
                return self._m_points

            self._m_points = self.mem_depth
            return getattr(self, '_m_points', None)

        @property
        def len_raw_4(self):
            if hasattr(self, '_m_len_raw_4'):
                return self._m_len_raw_4

            self._m_len_raw_4 = (self.raw_depth if self.channel_offset[3] > 0 else 0)
            return getattr(self, '_m_len_raw_4', None)

        @property
        def len_raw_2(self):
            if hasattr(self, '_m_len_raw_2'):
                return self._m_len_raw_2

            self._m_len_raw_2 = (self.raw_depth if self.channel_offset[1] > 0 else 0)
            return getattr(self, '_m_len_raw_2', None)

        @property
        def time_offset(self):
            if hasattr(self, '_m_time_offset'):
                return self._m_time_offset

            self._m_time_offset = (1.0E-12 * self.time_offset_ps)
            return getattr(self, '_m_time_offset', None)

        @property
        def raw_depth(self):
            if hasattr(self, '_m_raw_depth'):
                return self._m_raw_depth

            self._m_raw_depth = (self.storage_depth // 2 if self.enabled.interwoven else self.storage_depth)
            return getattr(self, '_m_raw_depth', None)

        @property
        def raw_2(self):
            if hasattr(self, '_m_raw_2'):
                return self._m_raw_2

            if self.channel_offset[1] > 0:
                _pos = self._io.pos()
                self._io.seek(self.channel_offset[1])
                self._m_raw_2 = self._io.read_bytes(self.len_raw_2)
                self._io.seek(_pos)

            return getattr(self, '_m_raw_2', None)

        @property
        def time_scale(self):
            if hasattr(self, '_m_time_scale'):
                return self._m_time_scale

            self._m_time_scale = (1.0E-12 * self.time_scale_ps)
            return getattr(self, '_m_time_scale', None)

        @property
        def seconds_per_point(self):
            if hasattr(self, '_m_seconds_per_point'):
                return self._m_seconds_per_point

            self._m_seconds_per_point = (1 / self.sample_rate_hz)
            return getattr(self, '_m_seconds_per_point', None)

        @property
        def raw_4(self):
            if hasattr(self, '_m_raw_4'):
                return self._m_raw_4

            if self.channel_offset[3] > 0:
                _pos = self._io.pos()
                self._io.seek(self.channel_offset[3])
                self._m_raw_4 = self._io.read_bytes(self.len_raw_4)
                self._io.seek(_pos)

            return getattr(self, '_m_raw_4', None)

        @property
        def raw_3(self):
            if hasattr(self, '_m_raw_3'):
                return self._m_raw_3

            if self.channel_offset[2] > 0:
                _pos = self._io.pos()
                self._io.seek(self.channel_offset[2])
                self._m_raw_3 = self._io.read_bytes(self.len_raw_3)
                self._io.seek(_pos)

            return getattr(self, '_m_raw_3', None)

        @property
        def len_raw_1(self):
            if hasattr(self, '_m_len_raw_1'):
                return self._m_len_raw_1

            self._m_len_raw_1 = (self.raw_depth if self.channel_offset[0] > 0 else 0)
            return getattr(self, '_m_len_raw_1', None)

        @property
        def raw_1(self):
            if hasattr(self, '_m_raw_1'):
                return self._m_raw_1

            if self.channel_offset[0] > 0:
                _pos = self._io.pos()
                self._io.seek(self.channel_offset[0])
                self._m_raw_1 = self._io.read_bytes(self.len_raw_1)
                self._io.seek(_pos)

            return getattr(self, '_m_raw_1', None)


    class ChannelHeader(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.enabled_temp = self._io.read_u1()
            self.coupling = KaitaiStream.resolve_enum(Wfm2000.CouplingEnum, self._io.read_bits_int_be(2))
            self.skip_coupling = self._io.read_bits_int_be(6)
            self._io.align_to_byte()
            self.bandwidth_limit = KaitaiStream.resolve_enum(Wfm2000.BandwidthEnum, self._io.read_u1())
            self.probe_type = KaitaiStream.resolve_enum(Wfm2000.ProbeTypeEnum, self._io.read_u1())
            self.probe_ratio = KaitaiStream.resolve_enum(Wfm2000.ProbeRatioEnum, self._io.read_u1())
            self.probe_diff = KaitaiStream.resolve_enum(Wfm2000.ProbeEnum, self._io.read_u1())
            self.probe_signal = KaitaiStream.resolve_enum(Wfm2000.ProbeEnum, self._io.read_u1())
            self.probe_impedance = KaitaiStream.resolve_enum(Wfm2000.ImpedanceEnum, self._io.read_u1())
            self.volt_per_division = self._io.read_f4le()
            self.volt_offset = self._io.read_f4le()
            self.inverted_temp = self._io.read_u1()
            self.unit_temp = self._io.read_u1()
            self.filter_enabled = self._io.read_u1()
            self.filter_type = self._io.read_u1()
            self.filter_high = self._io.read_u4le()
            self.filter_low = self._io.read_u4le()

        @property
        def unit(self):
            if hasattr(self, '_m_unit'):
                return self._m_unit

            self._m_unit = self.unit_actual
            return getattr(self, '_m_unit', None)

        @property
        def unit_actual(self):
            if hasattr(self, '_m_unit_actual'):
                return self._m_unit_actual

            self._m_unit_actual = (self.unit_temp if self.enabled_temp == 1 else self.inverted_temp)
            return getattr(self, '_m_unit_actual', None)

        @property
        def inverted(self):
            if hasattr(self, '_m_inverted'):
                return self._m_inverted

            self._m_inverted = (True if self.inverted_actual == 1 else False)
            return getattr(self, '_m_inverted', None)

        @property
        def volt_scale(self):
            if hasattr(self, '_m_volt_scale'):
                return self._m_volt_scale

            self._m_volt_scale = (self.volt_signed / 25.0)
            return getattr(self, '_m_volt_scale', None)

        @property
        def inverted_actual(self):
            if hasattr(self, '_m_inverted_actual'):
                return self._m_inverted_actual

            self._m_inverted_actual = (self.inverted_temp if self.enabled_temp == 1 else self.unit_temp)
            return getattr(self, '_m_inverted_actual', None)

        @property
        def probe_value(self):
            if hasattr(self, '_m_probe_value'):
                return self._m_probe_value

            self._m_probe_value = (0.01 if self.probe_ratio == Wfm2000.ProbeRatioEnum.x0_01 else (0.02 if self.probe_ratio == Wfm2000.ProbeRatioEnum.x0_02 else (0.05 if self.probe_ratio == Wfm2000.ProbeRatioEnum.x0_05 else (0.1 if self.probe_ratio == Wfm2000.ProbeRatioEnum.x0_1 else (0.2 if self.probe_ratio == Wfm2000.ProbeRatioEnum.x0_2 else (0.5 if self.probe_ratio == Wfm2000.ProbeRatioEnum.x0_5 else (1.0 if self.probe_ratio == Wfm2000.ProbeRatioEnum.x1 else (2.0 if self.probe_ratio == Wfm2000.ProbeRatioEnum.x2 else (5.0 if self.probe_ratio == Wfm2000.ProbeRatioEnum.x5 else (10.0 if self.probe_ratio == Wfm2000.ProbeRatioEnum.x10 else (20.0 if self.probe_ratio == Wfm2000.ProbeRatioEnum.x20 else (50.0 if self.probe_ratio == Wfm2000.ProbeRatioEnum.x50 else (100.0 if self.probe_ratio == Wfm2000.ProbeRatioEnum.x100 else (200.0 if self.probe_ratio == Wfm2000.ProbeRatioEnum.x200 else (500.0 if self.probe_ratio == Wfm2000.ProbeRatioEnum.x500 else 1000.0)))))))))))))))
            return getattr(self, '_m_probe_value', None)

        @property
        def enabled(self):
            if hasattr(self, '_m_enabled'):
                return self._m_enabled

            self._m_enabled = (True if self.enabled_temp != 0 else False)
            return getattr(self, '_m_enabled', None)

        @property
        def volt_signed(self):
            if hasattr(self, '_m_volt_signed'):
                return self._m_volt_signed

            self._m_volt_signed = ((-1.0 * self.volt_per_division) if self.inverted else (1.0 * self.volt_per_division))
            return getattr(self, '_m_volt_signed', None)


    class ChannelMask(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.unused_1 = self._io.read_bits_int_be(4)
            self.channel_4 = self._io.read_bits_int_be(1) != 0
            self.channel_3 = self._io.read_bits_int_be(1) != 0
            self.channel_2 = self._io.read_bits_int_be(1) != 0
            self.channel_1 = self._io.read_bits_int_be(1) != 0
            self.unused_2 = self._io.read_bits_int_be(7)
            self.interwoven = self._io.read_bits_int_be(1) != 0


    @property
    def header(self):
        if hasattr(self, '_m_header'):
            return self._m_header

        _pos = self._io.pos()
        self._io.seek(0)
        self._m_header = Wfm2000.Header(self._io, self, self._root)
        self._io.seek(_pos)
        return getattr(self, '_m_header', None)


