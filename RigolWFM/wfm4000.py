# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild

import kaitaistruct
from kaitaistruct import KaitaiStruct, KaitaiStream, BytesIO
from enum import Enum


if getattr(kaitaistruct, 'API_VERSION', (0, 9)) < (0, 9):
    raise Exception("Incompatible Kaitai Struct Python API: 0.9 or later is required, but you have %s" % (kaitaistruct.__version__))

class Wfm4000(KaitaiStruct):

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

    class MemDepthEnum(Enum):
        auto = 0
        p_7k = 1
        p_70k = 2
        p_700k = 3
        p_7m = 4
        p_70m = 5
        p_14k = 6
        p_140k = 7
        p_1m4 = 8
        p_14m = 9
        p_140m = 10

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

    class TimeHeader(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.unknown_1 = self._io.read_u2le()
            self.unknown_2 = self._io.read_bytes(10)
            self.index = self._io.read_u4le()
            self.time_per_div_ps = self._io.read_u4le()
            self.unknown_3a = self._io.read_bytes(4)
            self.offset_per_div_ps = self._io.read_u8le()
            self.unknown_4 = self._io.read_bytes(16)
            self.offset_ps = self._io.read_u8le()
            self.unknown_5 = self._io.read_bytes(16)
            self.unknown_6 = self._io.read_u2le()
            self.unknown_7 = self._io.read_u1()


    class ChannelMask(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.unused = self._io.read_bits_int_be(4)
            self.channel_4 = self._io.read_bits_int_be(1) != 0
            self.channel_3 = self._io.read_bits_int_be(1) != 0
            self.channel_2 = self._io.read_bits_int_be(1) != 0
            self.channel_1 = self._io.read_bits_int_be(1) != 0


    class ChannelHeader(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.enabled_val = self._io.read_u1()
            self.coupling = KaitaiStream.resolve_enum(Wfm4000.CouplingEnum, self._io.read_u1())
            self.bandwidth_limit = KaitaiStream.resolve_enum(Wfm4000.BandwidthEnum, self._io.read_u1())
            self.probe_type = KaitaiStream.resolve_enum(Wfm4000.ProbeTypeEnum, self._io.read_u1())
            self.probe_ratio = KaitaiStream.resolve_enum(Wfm4000.ProbeRatioEnum, self._io.read_u1())
            self.probe_diff = KaitaiStream.resolve_enum(Wfm4000.ProbeEnum, self._io.read_u1())
            self.probe_signal = KaitaiStream.resolve_enum(Wfm4000.ProbeEnum, self._io.read_u1())
            self.probe_impedance = KaitaiStream.resolve_enum(Wfm4000.ImpedanceEnum, self._io.read_u1())
            self.volt_per_division = self._io.read_f4le()
            self.volt_offset = self._io.read_f4le()
            self.inverted_val = self._io.read_u1()
            self.unit = KaitaiStream.resolve_enum(Wfm4000.UnitEnum, self._io.read_u1())
            self.filter_enabled = self._io.read_u1()
            self.filter_type = KaitaiStream.resolve_enum(Wfm4000.FilterEnum, self._io.read_u1())
            self.filter_high = self._io.read_u4le()
            self.filter_low = self._io.read_u4le()

        @property
        def inverted(self):
            if hasattr(self, '_m_inverted'):
                return self._m_inverted

            self._m_inverted = (True if self.inverted_val != 0 else False)
            return getattr(self, '_m_inverted', None)

        @property
        def volt_scale(self):
            if hasattr(self, '_m_volt_scale'):
                return self._m_volt_scale

            self._m_volt_scale = ((self.volt_signed / 25.0) if (self._root.header.model_number)[2:3] == u"2" else (self.volt_signed / 32.0))
            return getattr(self, '_m_volt_scale', None)

        @property
        def probe_value(self):
            if hasattr(self, '_m_probe_value'):
                return self._m_probe_value

            self._m_probe_value = (0.01 if self.probe_ratio == Wfm4000.ProbeRatioEnum.x0_01 else (0.02 if self.probe_ratio == Wfm4000.ProbeRatioEnum.x0_02 else (0.05 if self.probe_ratio == Wfm4000.ProbeRatioEnum.x0_05 else (0.1 if self.probe_ratio == Wfm4000.ProbeRatioEnum.x0_1 else (0.2 if self.probe_ratio == Wfm4000.ProbeRatioEnum.x0_2 else (0.5 if self.probe_ratio == Wfm4000.ProbeRatioEnum.x0_5 else (1.0 if self.probe_ratio == Wfm4000.ProbeRatioEnum.x1 else (2.0 if self.probe_ratio == Wfm4000.ProbeRatioEnum.x2 else (5.0 if self.probe_ratio == Wfm4000.ProbeRatioEnum.x5 else (10.0 if self.probe_ratio == Wfm4000.ProbeRatioEnum.x10 else (20.0 if self.probe_ratio == Wfm4000.ProbeRatioEnum.x20 else (50.0 if self.probe_ratio == Wfm4000.ProbeRatioEnum.x50 else (100.0 if self.probe_ratio == Wfm4000.ProbeRatioEnum.x100 else (200.0 if self.probe_ratio == Wfm4000.ProbeRatioEnum.x200 else (500.0 if self.probe_ratio == Wfm4000.ProbeRatioEnum.x500 else 1000.0)))))))))))))))
            return getattr(self, '_m_probe_value', None)

        @property
        def enabled(self):
            if hasattr(self, '_m_enabled'):
                return self._m_enabled

            self._m_enabled = (True if self.enabled_val != 0 else False)
            return getattr(self, '_m_enabled', None)

        @property
        def volt_signed(self):
            if hasattr(self, '_m_volt_signed'):
                return self._m_volt_signed

            self._m_volt_signed = ((-1.0 * self.volt_per_division) if self.inverted else (1.0 * self.volt_per_division))
            return getattr(self, '_m_volt_signed', None)


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
            self.unknown_1 = []
            for i in range(5):
                self.unknown_1.append(self._io.read_u4le())

            self.enabled = Wfm4000.ChannelMask(self._io, self, self._root)
            self.unknown_2 = self._io.read_bytes(3)
            self.position = Wfm4000.PositionType(self._io, self, self._root)
            self.unknown_3 = self._io.read_u4le()
            self.unknown_4 = self._io.read_u4le()
            self.unknown_5 = self._io.read_u4le()
            self.mem_depth_1 = self._io.read_u4le()
            self.sample_rate_hz = self._io.read_f4le()
            self.unknown_8 = self._io.read_u4le()
            self.time_per_div_ps = self._io.read_u8le()
            self.unknown_9 = []
            for i in range(2):
                self.unknown_9.append(self._io.read_u4le())

            self.ch = []
            for i in range(4):
                self.ch.append(Wfm4000.ChannelHeader(self._io, self, self._root))

            self.unknown_33 = []
            for i in range(6):
                self.unknown_33.append(self._io.read_u4le())

            self.mem_depth_2 = self._io.read_u4le()
            self.unknown_37 = self._io.read_bytes(4)
            self.mem_depth = self._io.read_u4le()
            self.unknown_38 = []
            for i in range(9):
                self.unknown_38.append(self._io.read_u4le())

            self.bytes_per_channel_1 = self._io.read_u4le()
            self.bytes_per_channel_2 = self._io.read_u4le()
            self.unknown_42 = []
            for i in range(41):
                self.unknown_42.append(self._io.read_u4le())

            self.total_samples = self._io.read_u4le()
            self.unknown_57 = []
            for i in range(4):
                self.unknown_57.append(self._io.read_u4le())

            self.mem_depth_type = KaitaiStream.resolve_enum(Wfm4000.MemDepthEnum, self._io.read_u1())
            self.unknown_60 = self._io.read_bytes(27)
            self.time = Wfm4000.TimeHeader(self._io, self, self._root)

        @property
        def len_raw_3(self):
            if hasattr(self, '_m_len_raw_3'):
                return self._m_len_raw_3

            self._m_len_raw_3 = (self.mem_depth if self.enabled.channel_3 else 0)
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

            self._m_len_raw_4 = (self.mem_depth if self.enabled.channel_4 else 0)
            return getattr(self, '_m_len_raw_4', None)

        @property
        def len_raw_2(self):
            if hasattr(self, '_m_len_raw_2'):
                return self._m_len_raw_2

            self._m_len_raw_2 = (self.mem_depth if self.enabled.channel_2 else 0)
            return getattr(self, '_m_len_raw_2', None)

        @property
        def time_offset(self):
            if hasattr(self, '_m_time_offset'):
                return self._m_time_offset

            self._m_time_offset = (1.0E-12 * self.time.offset_per_div_ps)
            return getattr(self, '_m_time_offset', None)

        @property
        def vertical_scale_factor(self):
            if hasattr(self, '_m_vertical_scale_factor'):
                return self._m_vertical_scale_factor

            self._m_vertical_scale_factor = (25 if (self.model_number)[2:3] == u"2" else 32)
            return getattr(self, '_m_vertical_scale_factor', None)

        @property
        def raw_2(self):
            if hasattr(self, '_m_raw_2'):
                return self._m_raw_2

            if self.enabled.channel_2:
                io = self._root._io
                _pos = io.pos()
                io.seek(self.position.channel_2)
                self._m_raw_2 = io.read_bytes(self.len_raw_2)
                io.seek(_pos)

            return getattr(self, '_m_raw_2', None)

        @property
        def time_scale(self):
            if hasattr(self, '_m_time_scale'):
                return self._m_time_scale

            self._m_time_scale = (1.0E-12 * self.time.time_per_div_ps)
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

            if self.enabled.channel_4:
                io = self._root._io
                _pos = io.pos()
                io.seek(self.position.channel_4)
                self._m_raw_4 = io.read_bytes(self.len_raw_4)
                io.seek(_pos)

            return getattr(self, '_m_raw_4', None)

        @property
        def raw_3(self):
            if hasattr(self, '_m_raw_3'):
                return self._m_raw_3

            if self.enabled.channel_3:
                io = self._root._io
                _pos = io.pos()
                io.seek(self.position.channel_3)
                self._m_raw_3 = io.read_bytes(self.len_raw_3)
                io.seek(_pos)

            return getattr(self, '_m_raw_3', None)

        @property
        def len_raw_1(self):
            if hasattr(self, '_m_len_raw_1'):
                return self._m_len_raw_1

            self._m_len_raw_1 = (self.mem_depth if self.enabled.channel_1 else 0)
            return getattr(self, '_m_len_raw_1', None)

        @property
        def raw_1(self):
            if hasattr(self, '_m_raw_1'):
                return self._m_raw_1

            if self.enabled.channel_1:
                io = self._root._io
                _pos = io.pos()
                io.seek(self.position.channel_1)
                self._m_raw_1 = io.read_bytes(self.len_raw_1)
                io.seek(_pos)

            return getattr(self, '_m_raw_1', None)


    class PositionType(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.channel_1 = self._io.read_u4le()
            self.channel_2 = self._io.read_u4le()
            self.channel_3 = self._io.read_u4le()
            self.channel_4 = self._io.read_u4le()


    @property
    def header(self):
        if hasattr(self, '_m_header'):
            return self._m_header

        _pos = self._io.pos()
        self._io.seek(0)
        self._m_header = Wfm4000.Header(self._io, self, self._root)
        self._io.seek(_pos)
        return getattr(self, '_m_header', None)


