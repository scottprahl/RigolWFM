# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild

from pkg_resources import parse_version
from kaitaistruct import __version__ as ks_version, KaitaiStruct, KaitaiStream, BytesIO
from enum import Enum


if parse_version(ks_version) < parse_version('0.7'):
    raise Exception("Incompatible Kaitai Struct Python API: 0.7 or later is required, but you have %s" % (ks_version))

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
            self.unused_bits_1 = self._io.read_bits_int(7)
            self.enabled = self._io.read_bits_int(1) != 0
            self._io.align_to_byte()
            self.unknown_2 = self._io.read_bytes(7)
            self.unused_bits_2 = self._io.read_bits_int(7)
            self.inverted = self._io.read_bits_int(1) != 0
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
            if self._root.header.stride == 1:
                self.raw1 = [None] * (self._root.header.points)
                for i in range(self._root.header.points):
                    self.raw1[i] = self._io.read_u1()


            if self._root.header.stride == 2:
                self.raw2 = [None] * (self._root.header.points)
                for i in range(self._root.header.points):
                    self.raw2[i] = self._io.read_u2le()


            if self._root.header.stride == 4:
                self.raw4 = [None] * (self._root.header.points)
                for i in range(self._root.header.points):
                    self.raw4[i] = self._io.read_u4le()




    class ChannelHead(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.enabled_val = self._io.read_u1()
            self.coupling = self._root.CouplingEnum(self._io.read_u1())
            self.bandwidth_limit = self._root.BandwidthEnum(self._io.read_u1())
            self.probe_type = self._io.read_u1()
            self.probe_ratio = self._root.ProbeEnum(self._io.read_u1())
            self.unused = self._io.read_bytes(3)
            self.scale = self._io.read_f4le()
            self.shift = self._io.read_f4le()
            self.inverted_val = self._io.read_u1()
            self.unit = self._root.UnitEnum(self._io.read_u1())
            self.unknown_2 = self._io.read_bytes(10)

        @property
        def y_scale(self):
            if hasattr(self, '_m_y_scale'):
                return self._m_y_scale if hasattr(self, '_m_y_scale') else None

            self._m_y_scale = (-(self.volt_per_division) / 20.0)
            return self._m_y_scale if hasattr(self, '_m_y_scale') else None

        @property
        def y_offset(self):
            if hasattr(self, '_m_y_offset'):
                return self._m_y_offset if hasattr(self, '_m_y_offset') else None

            self._m_y_offset = (self.shift - self.volt_per_division)
            return self._m_y_offset if hasattr(self, '_m_y_offset') else None

        @property
        def time_offset(self):
            if hasattr(self, '_m_time_offset'):
                return self._m_time_offset if hasattr(self, '_m_time_offset') else None

            self._m_time_offset = self._root.header.time_offset
            return self._m_time_offset if hasattr(self, '_m_time_offset') else None

        @property
        def inverted(self):
            if hasattr(self, '_m_inverted'):
                return self._m_inverted if hasattr(self, '_m_inverted') else None

            self._m_inverted = (True if self.inverted_val != 0 else False)
            return self._m_inverted if hasattr(self, '_m_inverted') else None

        @property
        def time_scale(self):
            if hasattr(self, '_m_time_scale'):
                return self._m_time_scale if hasattr(self, '_m_time_scale') else None

            self._m_time_scale = self._root.header.time_scale
            return self._m_time_scale if hasattr(self, '_m_time_scale') else None

        @property
        def volt_offset(self):
            if hasattr(self, '_m_volt_offset'):
                return self._m_volt_offset if hasattr(self, '_m_volt_offset') else None

            self._m_volt_offset = self.shift
            return self._m_volt_offset if hasattr(self, '_m_volt_offset') else None

        @property
        def volt_per_division(self):
            if hasattr(self, '_m_volt_per_division'):
                return self._m_volt_per_division if hasattr(self, '_m_volt_per_division') else None

            self._m_volt_per_division = ((-1.0 * self.scale) if self.inverted else (1.0 * self.scale))
            return self._m_volt_per_division if hasattr(self, '_m_volt_per_division') else None

        @property
        def volt_scale(self):
            if hasattr(self, '_m_volt_scale'):
                return self._m_volt_scale if hasattr(self, '_m_volt_scale') else None

            self._m_volt_scale = (self.volt_per_division / 25.0)
            return self._m_volt_scale if hasattr(self, '_m_volt_scale') else None

        @property
        def probe_value(self):
            if hasattr(self, '_m_probe_value'):
                return self._m_probe_value if hasattr(self, '_m_probe_value') else None

            self._m_probe_value = (0.01 if self.probe_ratio == self._root.ProbeEnum.x0_01 else (0.02 if self.probe_ratio == self._root.ProbeEnum.x0_02 else (0.05 if self.probe_ratio == self._root.ProbeEnum.x0_05 else (0.1 if self.probe_ratio == self._root.ProbeEnum.x0_1 else (0.2 if self.probe_ratio == self._root.ProbeEnum.x0_2 else (0.5 if self.probe_ratio == self._root.ProbeEnum.x0_5 else (1.0 if self.probe_ratio == self._root.ProbeEnum.x1 else (2.0 if self.probe_ratio == self._root.ProbeEnum.x2 else (5.0 if self.probe_ratio == self._root.ProbeEnum.x5 else (10.0 if self.probe_ratio == self._root.ProbeEnum.x10 else (20.0 if self.probe_ratio == self._root.ProbeEnum.x20 else (50.0 if self.probe_ratio == self._root.ProbeEnum.x50 else (100.0 if self.probe_ratio == self._root.ProbeEnum.x100 else (200.0 if self.probe_ratio == self._root.ProbeEnum.x200 else (500.0 if self.probe_ratio == self._root.ProbeEnum.x500 else 1000.0)))))))))))))))
            return self._m_probe_value if hasattr(self, '_m_probe_value') else None

        @property
        def enabled(self):
            if hasattr(self, '_m_enabled'):
                return self._m_enabled if hasattr(self, '_m_enabled') else None

            self._m_enabled = (True if self.enabled_val != 0 else False)
            return self._m_enabled if hasattr(self, '_m_enabled') else None


    class FileHeader(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.magic = self._io.ensure_fixed_contents(b"\x01\xFF\xFF\xFF")
            self.magic2 = self._io.read_u2le()
            self.structure_size = self._io.read_u2le()
            self.model_number = (KaitaiStream.bytes_terminate(self._io.read_bytes(20), 0, False)).decode(u"ascii")
            self.firmware_version = (KaitaiStream.bytes_terminate(self._io.read_bytes(20), 0, False)).decode(u"ascii")
            self.block = self._io.ensure_fixed_contents(b"\x01\x00")
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
            self.structure_size = self._io.ensure_fixed_contents(b"\xD8\x00")
            self.structure_version = self._io.read_u2le()
            self.unused_bits_1 = self._io.read_bits_int(4)
            self.ch4_enabled = self._io.read_bits_int(1) != 0
            self.ch3_enabled = self._io.read_bits_int(1) != 0
            self.ch2_enabled = self._io.read_bits_int(1) != 0
            self.ch1_enabled = self._io.read_bits_int(1) != 0
            self._io.align_to_byte()
            self.unused_mask_bytes = self._io.read_bytes(3)
            self.ch1_file_offset = self._io.read_u4le()
            self.ch2_file_offset = self._io.read_u4le()
            self.ch3_file_offset = self._io.read_u4le()
            self.ch4_file_offset = self._io.read_u4le()
            self.la_offset = self._io.read_u4le()
            self.acq_mode = self._root.AcquistionEnum(self._io.read_u1())
            self.average_time = self._io.read_u1()
            self.sample_mode = self._io.ensure_fixed_contents(b"\x00")
            self.time_mode = self._root.TimeModeEnum(self._io.read_u1())
            self.memory_depth = self._io.read_u4le()
            self.sample_rate_ghz = self._io.read_f4le()
            self.ch = [None] * (4)
            for i in range(4):
                self.ch[i] = self._root.ChannelHead(self._io, self, self._root)

            self.la_parameters = self._io.read_bytes(12)
            self.setup_size = self._io.read_u4le()
            self.setup_offset = self._io.read_u4le()
            self.horizontal_size = self._io.read_u4le()
            self.horizontal_offset = self._io.read_u4le()

        @property
        def points(self):
            if hasattr(self, '_m_points'):
                return self._m_points if hasattr(self, '_m_points') else None

            self._m_points = self.memory_depth // self.stride
            return self._m_points if hasattr(self, '_m_points') else None

        @property
        def ch2_int(self):
            if hasattr(self, '_m_ch2_int'):
                return self._m_ch2_int if hasattr(self, '_m_ch2_int') else None

            self._m_ch2_int = (1 if self.ch2_enabled else 0)
            return self._m_ch2_int if hasattr(self, '_m_ch2_int') else None

        @property
        def sample_rate_hz(self):
            if hasattr(self, '_m_sample_rate_hz'):
                return self._m_sample_rate_hz if hasattr(self, '_m_sample_rate_hz') else None

            self._m_sample_rate_hz = (self.sample_rate_ghz * 1E+9)
            return self._m_sample_rate_hz if hasattr(self, '_m_sample_rate_hz') else None

        @property
        def time_offset(self):
            if hasattr(self, '_m_time_offset'):
                return self._m_time_offset if hasattr(self, '_m_time_offset') else None

            self._m_time_offset = (self.picoseconds_offset * 1E-12)
            return self._m_time_offset if hasattr(self, '_m_time_offset') else None

        @property
        def ch4_int(self):
            if hasattr(self, '_m_ch4_int'):
                return self._m_ch4_int if hasattr(self, '_m_ch4_int') else None

            self._m_ch4_int = (1 if self.ch4_enabled else 0)
            return self._m_ch4_int if hasattr(self, '_m_ch4_int') else None

        @property
        def ch3_int(self):
            if hasattr(self, '_m_ch3_int'):
                return self._m_ch3_int if hasattr(self, '_m_ch3_int') else None

            self._m_ch3_int = (1 if self.ch3_enabled else 0)
            return self._m_ch3_int if hasattr(self, '_m_ch3_int') else None

        @property
        def total_channels(self):
            if hasattr(self, '_m_total_channels'):
                return self._m_total_channels if hasattr(self, '_m_total_channels') else None

            self._m_total_channels = (((self.ch1_int + self.ch2_int) + self.ch3_int) + self.ch4_int)
            return self._m_total_channels if hasattr(self, '_m_total_channels') else None

        @property
        def time_scale(self):
            if hasattr(self, '_m_time_scale'):
                return self._m_time_scale if hasattr(self, '_m_time_scale') else None

            self._m_time_scale = (self.picoseconds_per_division * 1E-12)
            return self._m_time_scale if hasattr(self, '_m_time_scale') else None

        @property
        def seconds_per_point(self):
            if hasattr(self, '_m_seconds_per_point'):
                return self._m_seconds_per_point if hasattr(self, '_m_seconds_per_point') else None

            self._m_seconds_per_point = (1 / self.sample_rate_hz)
            return self._m_seconds_per_point if hasattr(self, '_m_seconds_per_point') else None

        @property
        def ch1_int(self):
            if hasattr(self, '_m_ch1_int'):
                return self._m_ch1_int if hasattr(self, '_m_ch1_int') else None

            self._m_ch1_int = (1 if self.ch1_enabled else 0)
            return self._m_ch1_int if hasattr(self, '_m_ch1_int') else None

        @property
        def stride(self):
            if hasattr(self, '_m_stride'):
                return self._m_stride if hasattr(self, '_m_stride') else None

            self._m_stride = (4 if self.total_channels == 3 else self.total_channels)
            return self._m_stride if hasattr(self, '_m_stride') else None


    @property
    def preheader(self):
        if hasattr(self, '_m_preheader'):
            return self._m_preheader if hasattr(self, '_m_preheader') else None

        _pos = self._io.pos()
        self._io.seek(0)
        self._m_preheader = self._root.FileHeader(self._io, self, self._root)
        self._io.seek(_pos)
        return self._m_preheader if hasattr(self, '_m_preheader') else None

    @property
    def header(self):
        if hasattr(self, '_m_header'):
            return self._m_header if hasattr(self, '_m_header') else None

        _pos = self._io.pos()
        self._io.seek(64)
        self._m_header = self._root.WfmHeader(self._io, self, self._root)
        self._io.seek(_pos)
        return self._m_header if hasattr(self, '_m_header') else None

    @property
    def data(self):
        if hasattr(self, '_m_data'):
            return self._m_data if hasattr(self, '_m_data') else None

        _pos = self._io.pos()
        self._io.seek(((304 + self._root.header.setup_size) + self._root.header.horizontal_size))
        self._m_data = self._root.RawData(self._io, self, self._root)
        self._io.seek(_pos)
        return self._m_data if hasattr(self, '_m_data') else None


