# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild

from pkg_resources import parse_version
from kaitaistruct import __version__ as ks_version, KaitaiStruct, KaitaiStream, BytesIO
from enum import Enum


if parse_version(ks_version) < parse_version('0.7'):
    raise Exception("Incompatible Kaitai Struct Python API: 0.7 or later is required, but you have %s" % (ks_version))

class Wfm2000(KaitaiStruct):
    """Rigol DS2000 .wmf format abstracted from a python script.  This is very far
    from complete.
    
    .. seealso::
       Source - https://www.tablix.org/~avian/blog/archives/2019/08/quick_and_ugly_wfm_data_export_for_rigol_ds2072a/#comment_0000
    """

    class TriggerSourceEnum(Enum):
        ch1 = 0
        ch2 = 1
        ext = 2
        ext5 = 3
        ac_line = 5
        dig_ch = 7

    class TriggerModeEnum(Enum):
        edge = 0
        pulse = 1
        slope = 2
        video = 3
        alt = 4
        pattern = 5
        duration = 6
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
            self.magic = self._io.ensure_fixed_contents(b"\xA5\xA5\x00\x00")
            self.skip1 = self._io.read_bytes(64)
            self.ch1_location = self._io.read_u4le()
            self.ch2_location = self._io.read_u4le()
            self.skip_2 = self._io.read_bytes(16)
            self.points = self._io.read_u4le()
            self.skip_3 = self._io.read_bytes(284)
            self.sample_rate_hz = self._io.read_u4le()

        @property
        def time_offset(self):
            if hasattr(self, '_m_time_offset'):
                return self._m_time_offset if hasattr(self, '_m_time_offset') else None

            self._m_time_offset = 0.0
            return self._m_time_offset if hasattr(self, '_m_time_offset') else None

        @property
        def raw_2(self):
            if hasattr(self, '_m_raw_2'):
                return self._m_raw_2 if hasattr(self, '_m_raw_2') else None

            _pos = self._io.pos()
            self._io.seek(self.ch2_location)
            self._m_raw_2 = [None] * (self.points)
            for i in range(self.points):
                self._m_raw_2[i] = self._io.read_u1()

            self._io.seek(_pos)
            return self._m_raw_2 if hasattr(self, '_m_raw_2') else None

        @property
        def time_scale(self):
            if hasattr(self, '_m_time_scale'):
                return self._m_time_scale if hasattr(self, '_m_time_scale') else None

            self._m_time_scale = ((self.sample_rate_hz * self.points) / 10.0)
            return self._m_time_scale if hasattr(self, '_m_time_scale') else None

        @property
        def seconds_per_point(self):
            if hasattr(self, '_m_seconds_per_point'):
                return self._m_seconds_per_point if hasattr(self, '_m_seconds_per_point') else None

            self._m_seconds_per_point = (1.0 / self.sample_rate_hz)
            return self._m_seconds_per_point if hasattr(self, '_m_seconds_per_point') else None

        @property
        def raw_1(self):
            if hasattr(self, '_m_raw_1'):
                return self._m_raw_1 if hasattr(self, '_m_raw_1') else None

            _pos = self._io.pos()
            self._io.seek(self.ch1_location)
            self._m_raw_1 = [None] * (self.points)
            for i in range(self.points):
                self._m_raw_1[i] = self._io.read_u1()

            self._io.seek(_pos)
            return self._m_raw_1 if hasattr(self, '_m_raw_1') else None


    @property
    def header(self):
        if hasattr(self, '_m_header'):
            return self._m_header if hasattr(self, '_m_header') else None

        _pos = self._io.pos()
        self._io.seek(0)
        self._m_header = self._root.Header(self._io, self, self._root)
        self._io.seek(_pos)
        return self._m_header if hasattr(self, '_m_header') else None


