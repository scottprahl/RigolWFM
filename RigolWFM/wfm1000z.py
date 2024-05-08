# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild

import kaitaistruct
from kaitaistruct import KaitaiStruct, KaitaiStream, BytesIO
from enum import Enum


if getattr(kaitaistruct, 'API_VERSION', (0, 9)) < (0, 9):
    raise Exception("Incompatible Kaitai Struct Python API: 0.9 or later is required, but you have %s" % (kaitaistruct.__version__))

class Wfm1000z(KaitaiStruct):
    """Rigol DS1000Z scope .wmf file format.
    """

    class UnitEnum(Enum):
        w = 0
        a = 1
        v = 2
        u = 3

    class AcquistionEnum(Enum):
        normal = 0
        peak = 1
        average = 2
        high_resolution = 3

    class TimeModeEnum(Enum):
        yt = 0
        xy = 1
        roll = 2

    class ProbeEnum(Enum):
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

    class BandwidthEnum(Enum):
        mhz_20 = 0
        no_limit = 1

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

    class ChannelSubhead(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.unknown_1 = self._io.read_bytes(3)
            self.unused_bits_1 = self._io.read_bits_int_be(7)
            self.enabled = self._io.read_bits_int_be(1) != 0
            self._io.align_to_byte()
            self.unknown_2 = self._io.read_bytes(7)
            self.unused_bits_2 = self._io.read_bits_int_be(7)
            self.inverted = self._io.read_bits_int_be(1) != 0
            self._io.align_to_byte()
            self.unknown_3 = self._io.read_bytes(10)
            self.probe_attenuation = self._io.read_s8le()
            self.unknown_4 = self._io.read_bytes(16)
            self.label = (KaitaiStream.bytes_terminate(self._io.read_bytes(4), 0, False)).decode(u"UTF-8")
            self.unknown_5 = self._io.read_bytes(10)


    class RawData(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.raw = self._io.read_bytes((self._root.header.points * self._root.header.stride))


    class ChannelHead(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.enabled_val = self._io.read_u1()
            self.coupling = KaitaiStream.resolve_enum(Wfm1000z.CouplingEnum, self._io.read_u1())
            self.bandwidth_limit = KaitaiStream.resolve_enum(Wfm1000z.BandwidthEnum, self._io.read_u1())
            self.probe_type = self._io.read_u1()
            self.probe_ratio = KaitaiStream.resolve_enum(Wfm1000z.ProbeEnum, self._io.read_u1())
            self.unused = self._io.read_bytes(3)
            self.scale = self._io.read_f4le()
            self.shift = self._io.read_f4le()
            self.inverted_val = self._io.read_u1()
            self.unit = KaitaiStream.resolve_enum(Wfm1000z.UnitEnum, self._io.read_u1())
            self.unknown_2 = self._io.read_bytes(10)

        @property
        def y_scale(self):
            if hasattr(self, '_m_y_scale'):
                return self._m_y_scale

            self._m_y_scale = (-(self.volt_per_division) / 20.0)
            return getattr(self, '_m_y_scale', None)

        @property
        def y_offset(self):
            if hasattr(self, '_m_y_offset'):
                return self._m_y_offset

            self._m_y_offset = (self.shift - self.volt_per_division)
            return getattr(self, '_m_y_offset', None)

        @property
        def time_offset(self):
            if hasattr(self, '_m_time_offset'):
                return self._m_time_offset

            self._m_time_offset = self._root.header.time_offset
            return getattr(self, '_m_time_offset', None)

        @property
        def inverted(self):
            if hasattr(self, '_m_inverted'):
                return self._m_inverted

            self._m_inverted = (True if self.inverted_val != 0 else False)
            return getattr(self, '_m_inverted', None)

        @property
        def time_scale(self):
            if hasattr(self, '_m_time_scale'):
                return self._m_time_scale

            self._m_time_scale = self._root.header.time_scale
            return getattr(self, '_m_time_scale', None)

        @property
        def volt_offset(self):
            if hasattr(self, '_m_volt_offset'):
                return self._m_volt_offset

            self._m_volt_offset = self.shift
            return getattr(self, '_m_volt_offset', None)

        @property
        def volt_per_division(self):
            if hasattr(self, '_m_volt_per_division'):
                return self._m_volt_per_division

            self._m_volt_per_division = ((-1.0 * self.scale) if self.inverted else (1.0 * self.scale))
            return getattr(self, '_m_volt_per_division', None)

        @property
        def volt_scale(self):
            if hasattr(self, '_m_volt_scale'):
                return self._m_volt_scale

            self._m_volt_scale = (self.volt_per_division / 25.0)
            return getattr(self, '_m_volt_scale', None)

        @property
        def probe_value(self):
            if hasattr(self, '_m_probe_value'):
                return self._m_probe_value

            self._m_probe_value = (0.01 if self.probe_ratio == Wfm1000z.ProbeEnum.x0_01 else (0.02 if self.probe_ratio == Wfm1000z.ProbeEnum.x0_02 else (0.05 if self.probe_ratio == Wfm1000z.ProbeEnum.x0_05 else (0.1 if self.probe_ratio == Wfm1000z.ProbeEnum.x0_1 else (0.2 if self.probe_ratio == Wfm1000z.ProbeEnum.x0_2 else (0.5 if self.probe_ratio == Wfm1000z.ProbeEnum.x0_5 else (1.0 if self.probe_ratio == Wfm1000z.ProbeEnum.x1 else (2.0 if self.probe_ratio == Wfm1000z.ProbeEnum.x2 else (5.0 if self.probe_ratio == Wfm1000z.ProbeEnum.x5 else (10.0 if self.probe_ratio == Wfm1000z.ProbeEnum.x10 else (20.0 if self.probe_ratio == Wfm1000z.ProbeEnum.x20 else (50.0 if self.probe_ratio == Wfm1000z.ProbeEnum.x50 else (100.0 if self.probe_ratio == Wfm1000z.ProbeEnum.x100 else (200.0 if self.probe_ratio == Wfm1000z.ProbeEnum.x200 else (500.0 if self.probe_ratio == Wfm1000z.ProbeEnum.x500 else 1000.0)))))))))))))))
            return getattr(self, '_m_probe_value', None)

        @property
        def enabled(self):
            if hasattr(self, '_m_enabled'):
                return self._m_enabled

            self._m_enabled = (True if self.enabled_val != 0 else False)
            return getattr(self, '_m_enabled', None)


    class FileHeader(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.magic = self._io.read_bytes(4)
            if not self.magic == b"\x01\xFF\xFF\xFF":
                raise kaitaistruct.ValidationNotEqualError(b"\x01\xFF\xFF\xFF", self.magic, self._io, u"/types/file_header/seq/0")
            self.magic2 = self._io.read_u2le()
            self.structure_size = self._io.read_u2le()
            self.model_number = (KaitaiStream.bytes_terminate(self._io.read_bytes(20), 0, False)).decode(u"ascii")
            self.firmware_version = (KaitaiStream.bytes_terminate(self._io.read_bytes(20), 0, False)).decode(u"ascii")
            self.block = self._io.read_bytes(2)
            if not self.block == b"\x01\x00":
                raise kaitaistruct.ValidationNotEqualError(b"\x01\x00", self.block, self._io, u"/types/file_header/seq/5")
            self.file_version = self._io.read_u2le()


    class WfmHeader(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.picoseconds_per_division = self._io.read_u8le()
            self.picoseconds_offset = self._io.read_s8le()
            self.crc = self._io.read_u4le()
            self.structure_size = self._io.read_bytes(2)
            if not self.structure_size == b"\xD8\x00":
                raise kaitaistruct.ValidationNotEqualError(b"\xD8\x00", self.structure_size, self._io, u"/types/wfm_header/seq/3")
            self.structure_version = self._io.read_u2le()
            self.unused_bits_1 = self._io.read_bits_int_be(4)
            self.ch4_enabled = self._io.read_bits_int_be(1) != 0
            self.ch3_enabled = self._io.read_bits_int_be(1) != 0
            self.ch2_enabled = self._io.read_bits_int_be(1) != 0
            self.ch1_enabled = self._io.read_bits_int_be(1) != 0
            self._io.align_to_byte()
            self.unused_mask_bytes = self._io.read_bytes(3)
            self.ch1_file_offset = self._io.read_u4le()
            self.ch2_file_offset = self._io.read_u4le()
            self.ch3_file_offset = self._io.read_u4le()
            self.ch4_file_offset = self._io.read_u4le()
            self.la_offset = self._io.read_u4le()
            self.acq_mode = KaitaiStream.resolve_enum(Wfm1000z.AcquistionEnum, self._io.read_u1())
            self.average_time = self._io.read_u1()
            self.sample_mode = self._io.read_bytes(1)
            if not self.sample_mode == b"\x00":
                raise kaitaistruct.ValidationNotEqualError(b"\x00", self.sample_mode, self._io, u"/types/wfm_header/seq/18")
            self.time_mode = KaitaiStream.resolve_enum(Wfm1000z.TimeModeEnum, self._io.read_u1())
            self.memory_depth = self._io.read_u4le()
            self.sample_rate_ghz = self._io.read_f4le()
            self.ch = []
            for i in range(4):
                self.ch.append(Wfm1000z.ChannelHead(self._io, self, self._root))

            self.la_parameters = self._io.read_bytes(12)
            self.setup_size = self._io.read_u4le()
            self.setup_offset = self._io.read_u4le()
            self.horizontal_size = self._io.read_u4le()
            self.horizontal_offset = self._io.read_u4le()

        @property
        def points(self):
            if hasattr(self, '_m_points'):
                return self._m_points

            self._m_points = self.memory_depth // self.stride
            return getattr(self, '_m_points', None)

        @property
        def ch2_int(self):
            if hasattr(self, '_m_ch2_int'):
                return self._m_ch2_int

            self._m_ch2_int = (1 if self.ch2_enabled else 0)
            return getattr(self, '_m_ch2_int', None)

        @property
        def sample_rate_hz(self):
            if hasattr(self, '_m_sample_rate_hz'):
                return self._m_sample_rate_hz

            self._m_sample_rate_hz = (self.sample_rate_ghz * 1E+9)
            return getattr(self, '_m_sample_rate_hz', None)

        @property
        def time_offset(self):
            if hasattr(self, '_m_time_offset'):
                return self._m_time_offset

            self._m_time_offset = (self.picoseconds_offset * 1E-12)
            return getattr(self, '_m_time_offset', None)

        @property
        def ch4_int(self):
            if hasattr(self, '_m_ch4_int'):
                return self._m_ch4_int

            self._m_ch4_int = (1 if self.ch4_enabled else 0)
            return getattr(self, '_m_ch4_int', None)

        @property
        def ch3_int(self):
            if hasattr(self, '_m_ch3_int'):
                return self._m_ch3_int

            self._m_ch3_int = (1 if self.ch3_enabled else 0)
            return getattr(self, '_m_ch3_int', None)

        @property
        def total_channels(self):
            if hasattr(self, '_m_total_channels'):
                return self._m_total_channels

            self._m_total_channels = (1 if self.total_count == 0 else self.total_count)
            return getattr(self, '_m_total_channels', None)

        @property
        def time_scale(self):
            if hasattr(self, '_m_time_scale'):
                return self._m_time_scale

            self._m_time_scale = (self.picoseconds_per_division * 1E-12)
            return getattr(self, '_m_time_scale', None)

        @property
        def seconds_per_point(self):
            if hasattr(self, '_m_seconds_per_point'):
                return self._m_seconds_per_point

            self._m_seconds_per_point = (1 / self.sample_rate_hz)
            return getattr(self, '_m_seconds_per_point', None)

        @property
        def ch1_int(self):
            if hasattr(self, '_m_ch1_int'):
                return self._m_ch1_int

            self._m_ch1_int = (1 if self.ch1_enabled else 0)
            return getattr(self, '_m_ch1_int', None)

        @property
        def stride(self):
            if hasattr(self, '_m_stride'):
                return self._m_stride

            self._m_stride = (4 if self.total_channels == 3 else self.total_channels)
            return getattr(self, '_m_stride', None)

        @property
        def total_count(self):
            if hasattr(self, '_m_total_count'):
                return self._m_total_count

            self._m_total_count = (((self.ch1_int + self.ch2_int) + self.ch3_int) + self.ch4_int)
            return getattr(self, '_m_total_count', None)


    @property
    def preheader(self):
        if hasattr(self, '_m_preheader'):
            return self._m_preheader

        _pos = self._io.pos()
        self._io.seek(0)
        self._m_preheader = Wfm1000z.FileHeader(self._io, self, self._root)
        self._io.seek(_pos)
        return getattr(self, '_m_preheader', None)

    @property
    def header(self):
        if hasattr(self, '_m_header'):
            return self._m_header

        _pos = self._io.pos()
        self._io.seek(64)
        self._m_header = Wfm1000z.WfmHeader(self._io, self, self._root)
        self._io.seek(_pos)
        return getattr(self, '_m_header', None)

    @property
    def data(self):
        if hasattr(self, '_m_data'):
            return self._m_data

        _pos = self._io.pos()
        self._io.seek(((304 + self._root.header.setup_size) + self._root.header.horizontal_size))
        self._m_data = Wfm1000z.RawData(self._io, self, self._root)
        self._io.seek(_pos)
        return getattr(self, '_m_data', None)


