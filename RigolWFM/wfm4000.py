# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild

from pkg_resources import parse_version
from kaitaistruct import __version__ as ks_version, KaitaiStruct, KaitaiStream, BytesIO
from enum import Enum


if parse_version(ks_version) < parse_version('0.7'):
    raise Exception("Incompatible Kaitai Struct Python API: 0.7 or later is required, but you have %s" % (ks_version))

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
            self.unused = self._io.read_bits_int(4)
            self.channel_4 = self._io.read_bits_int(1) != 0
            self.channel_3 = self._io.read_bits_int(1) != 0
            self.channel_2 = self._io.read_bits_int(1) != 0
            self.channel_1 = self._io.read_bits_int(1) != 0


    class ChannelHeader(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.enabled_val = self._io.read_u1()
            self.coupling = self._root.CouplingEnum(self._io.read_u1())
            self.bandwidth_limit = self._root.BandwidthEnum(self._io.read_u1())
            self.probe_type = self._root.ProbeTypeEnum(self._io.read_u1())
            self.probe_ratio = self._root.ProbeRatioEnum(self._io.read_u1())
            self.probe_diff = self._root.ProbeEnum(self._io.read_u1())
            self.probe_signal = self._root.ProbeEnum(self._io.read_u1())
            self.probe_impedance = self._root.ImpedanceEnum(self._io.read_u1())
            self.volt_per_division = self._io.read_f4le()
            self.volt_offset = self._io.read_f4le()
            self.inverted_val = self._io.read_u1()
            self.unit = self._root.UnitEnum(self._io.read_u1())
            self.filter_enabled = self._io.read_u1()
            self.filter_type = self._root.FilterEnum(self._io.read_u1())
            self.filter_high = self._io.read_u4le()
            self.filter_low = self._io.read_u4le()

        @property
        def inverted(self):
            if hasattr(self, '_m_inverted'):
                return self._m_inverted if hasattr(self, '_m_inverted') else None

            self._m_inverted = (True if self.inverted_val != 0 else False)
            return self._m_inverted if hasattr(self, '_m_inverted') else None

        @property
        def volt_scale(self):
            if hasattr(self, '_m_volt_scale'):
                return self._m_volt_scale if hasattr(self, '_m_volt_scale') else None

            self._m_volt_scale = ((self.volt_signed / 25.0) if self._root.header.model_number[2:3] == u"2" else (self.volt_signed / 32.0))
            return self._m_volt_scale if hasattr(self, '_m_volt_scale') else None

        @property
        def probe_value(self):
            if hasattr(self, '_m_probe_value'):
                return self._m_probe_value if hasattr(self, '_m_probe_value') else None

            self._m_probe_value = (0.01 if self.probe_ratio == self._root.ProbeRatioEnum.x0_01 else (0.02 if self.probe_ratio == self._root.ProbeRatioEnum.x0_02 else (0.05 if self.probe_ratio == self._root.ProbeRatioEnum.x0_05 else (0.1 if self.probe_ratio == self._root.ProbeRatioEnum.x0_1 else (0.2 if self.probe_ratio == self._root.ProbeRatioEnum.x0_2 else (0.5 if self.probe_ratio == self._root.ProbeRatioEnum.x0_5 else (1.0 if self.probe_ratio == self._root.ProbeRatioEnum.x1 else (2.0 if self.probe_ratio == self._root.ProbeRatioEnum.x2 else (5.0 if self.probe_ratio == self._root.ProbeRatioEnum.x5 else (10.0 if self.probe_ratio == self._root.ProbeRatioEnum.x10 else (20.0 if self.probe_ratio == self._root.ProbeRatioEnum.x20 else (50.0 if self.probe_ratio == self._root.ProbeRatioEnum.x50 else (100.0 if self.probe_ratio == self._root.ProbeRatioEnum.x100 else (200.0 if self.probe_ratio == self._root.ProbeRatioEnum.x200 else (500.0 if self.probe_ratio == self._root.ProbeRatioEnum.x500 else 1000.0)))))))))))))))
            return self._m_probe_value if hasattr(self, '_m_probe_value') else None

        @property
        def enabled(self):
            if hasattr(self, '_m_enabled'):
                return self._m_enabled if hasattr(self, '_m_enabled') else None

            self._m_enabled = (True if self.enabled_val != 0 else False)
            return self._m_enabled if hasattr(self, '_m_enabled') else None

        @property
        def volt_signed(self):
            if hasattr(self, '_m_volt_signed'):
                return self._m_volt_signed if hasattr(self, '_m_volt_signed') else None

            self._m_volt_signed = ((-1.0 * self.volt_per_division) if self.inverted else (1.0 * self.volt_per_division))
            return self._m_volt_signed if hasattr(self, '_m_volt_signed') else None


    class Header(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.magic = self._io.ensure_fixed_contents(b"\xA5\xA5\x38\x00")
            self.model_number = (KaitaiStream.bytes_terminate(self._io.read_bytes(20), 0, False)).decode(u"ascii")
            self.firmware_version = (KaitaiStream.bytes_terminate(self._io.read_bytes(20), 0, False)).decode(u"ascii")
            self.unknown_1 = [None] * (5)
            for i in range(5):
                self.unknown_1[i] = self._io.read_u4le()

            self.enabled = self._root.ChannelMask(self._io, self, self._root)
            self.unknown_2 = self._io.read_bytes(3)
            self.position = self._root.PositionType(self._io, self, self._root)
            self.unknown_3 = self._io.read_u4le()
            self.unknown_4 = self._io.read_u4le()
            self.unknown_5 = self._io.read_u4le()
            self.mem_depth_1 = self._io.read_u4le()
            self.sample_rate_hz = self._io.read_f4le()
            self.unknown_8 = self._io.read_u4le()
            self.time_per_div_ps = self._io.read_u8le()
            self.unknown_9 = [None] * (2)
            for i in range(2):
                self.unknown_9[i] = self._io.read_u4le()

            self.ch = [None] * (4)
            for i in range(4):
                self.ch[i] = self._root.ChannelHeader(self._io, self, self._root)

            self.unknown_33 = [None] * (6)
            for i in range(6):
                self.unknown_33[i] = self._io.read_u4le()

            self.mem_depth_2 = self._io.read_u4le()
            self.unknown_37 = self._io.read_bytes(4)
            self.mem_depth = self._io.read_u4le()
            self.unknown_38 = [None] * (9)
            for i in range(9):
                self.unknown_38[i] = self._io.read_u4le()

            self.bytes_per_channel_1 = self._io.read_u4le()
            self.bytes_per_channel_2 = self._io.read_u4le()
            self.unknown_42 = [None] * (41)
            for i in range(41):
                self.unknown_42[i] = self._io.read_u4le()

            self.total_samples = self._io.read_u4le()
            self.unknown_57 = [None] * (4)
            for i in range(4):
                self.unknown_57[i] = self._io.read_u4le()

            self.mem_depth_type = self._root.MemDepthEnum(self._io.read_u1())
            self.unknown_60 = self._io.read_bytes(27)
            self.time = self._root.TimeHeader(self._io, self, self._root)

        @property
        def points(self):
            if hasattr(self, '_m_points'):
                return self._m_points if hasattr(self, '_m_points') else None

            self._m_points = self.mem_depth
            return self._m_points if hasattr(self, '_m_points') else None

        @property
        def time_offset(self):
            if hasattr(self, '_m_time_offset'):
                return self._m_time_offset if hasattr(self, '_m_time_offset') else None

            self._m_time_offset = (1.0E-12 * self.time.offset_per_div_ps)
            return self._m_time_offset if hasattr(self, '_m_time_offset') else None

        @property
        def vertical_scale_factor(self):
            if hasattr(self, '_m_vertical_scale_factor'):
                return self._m_vertical_scale_factor if hasattr(self, '_m_vertical_scale_factor') else None

            self._m_vertical_scale_factor = (25 if self.model_number[2:3] == u"2" else 32)
            return self._m_vertical_scale_factor if hasattr(self, '_m_vertical_scale_factor') else None

        @property
        def raw_2(self):
            if hasattr(self, '_m_raw_2'):
                return self._m_raw_2 if hasattr(self, '_m_raw_2') else None

            if self.enabled.channel_2:
                _pos = self._io.pos()
                self._io.seek(self.position.channel_2)
                self._m_raw_2 = [None] * (self.mem_depth)
                for i in range(self.mem_depth):
                    self._m_raw_2[i] = self._io.read_u1()

                self._io.seek(_pos)

            return self._m_raw_2 if hasattr(self, '_m_raw_2') else None

        @property
        def time_scale(self):
            if hasattr(self, '_m_time_scale'):
                return self._m_time_scale if hasattr(self, '_m_time_scale') else None

            self._m_time_scale = (1.0E-12 * self.time.time_per_div_ps)
            return self._m_time_scale if hasattr(self, '_m_time_scale') else None

        @property
        def seconds_per_point(self):
            if hasattr(self, '_m_seconds_per_point'):
                return self._m_seconds_per_point if hasattr(self, '_m_seconds_per_point') else None

            self._m_seconds_per_point = (1 / self.sample_rate_hz)
            return self._m_seconds_per_point if hasattr(self, '_m_seconds_per_point') else None

        @property
        def raw_4(self):
            if hasattr(self, '_m_raw_4'):
                return self._m_raw_4 if hasattr(self, '_m_raw_4') else None

            if self.enabled.channel_4:
                _pos = self._io.pos()
                self._io.seek(self.position.channel_4)
                self._m_raw_4 = [None] * (self.mem_depth)
                for i in range(self.mem_depth):
                    self._m_raw_4[i] = self._io.read_u1()

                self._io.seek(_pos)

            return self._m_raw_4 if hasattr(self, '_m_raw_4') else None

        @property
        def raw_3(self):
            if hasattr(self, '_m_raw_3'):
                return self._m_raw_3 if hasattr(self, '_m_raw_3') else None

            if self.enabled.channel_3:
                _pos = self._io.pos()
                self._io.seek(self.position.channel_3)
                self._m_raw_3 = [None] * (self.mem_depth)
                for i in range(self.mem_depth):
                    self._m_raw_3[i] = self._io.read_u1()

                self._io.seek(_pos)

            return self._m_raw_3 if hasattr(self, '_m_raw_3') else None

        @property
        def raw_1(self):
            if hasattr(self, '_m_raw_1'):
                return self._m_raw_1 if hasattr(self, '_m_raw_1') else None

            if self.enabled.channel_1:
                _pos = self._io.pos()
                self._io.seek(self.position.channel_1)
                self._m_raw_1 = [None] * (self.mem_depth)
                for i in range(self.mem_depth):
                    self._m_raw_1[i] = self._io.read_u1()

                self._io.seek(_pos)

            return self._m_raw_1 if hasattr(self, '_m_raw_1') else None


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
            return self._m_header if hasattr(self, '_m_header') else None

        _pos = self._io.pos()
        self._io.seek(0)
        self._m_header = self._root.Header(self._io, self, self._root)
        self._io.seek(_pos)
        return self._m_header if hasattr(self, '_m_header') else None


