# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild

import kaitaistruct
from kaitaistruct import KaitaiStruct, KaitaiStream, BytesIO
from enum import Enum


if getattr(kaitaistruct, 'API_VERSION', (0, 9)) < (0, 9):
    raise Exception("Incompatible Kaitai Struct Python API: 0.9 or later is required, but you have %s" % (kaitaistruct.__version__))

class Bindho1000(KaitaiStruct):
    """Official binary waveform export format documented in DHO1000 User Guide
    §19.2.4 (Tables 19.1–19.4). Stores calibrated float32 voltage samples
    for each enabled channel.
    
    File layout:
      [File Header:      16 bytes]
      for each waveform (channel):
        [Waveform Header: 140 bytes]
        [Data Header:      16 bytes]
        [Sample Data:      buffer_size bytes - float32 LE, volts]
    
    Time axis reconstruction:
      t[i] = -x_origin + i * x_increment
      (x_origin is stored as a positive distance from the trigger point)
    """

    class WaveformTypeEnum(Enum):
        normal = 1
        peak = 2
        average = 3
        logic = 6

    class BufferTypeEnum(Enum):
        float32_normal = 1
        float32_maximum = 2
        float32_minimum = 3

    class UnitEnum(Enum):
        unknown = 0
        v = 1
        s = 2
        constant = 3
        a = 4
        db = 5
        hz = 6
    def __init__(self, _io, _parent=None, _root=None):
        self._io = _io
        self._parent = _parent
        self._root = _root if _root else self
        self._read()

    def _read(self):
        self.file_header = Bindho1000.FileHeader(self._io, self, self._root)
        self.waveforms = []
        for i in range(self.file_header.n_waveforms):
            self.waveforms.append(Bindho1000.Waveform(self._io, self, self._root))


    class DataHeader(KaitaiStruct):
        """16-byte data buffer header (Table 19.4)."""
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.header_size = self._io.read_u4le()
            self.buffer_type = KaitaiStream.resolve_enum(Bindho1000.BufferTypeEnum, self._io.read_u2le())
            self.bytes_per_point = self._io.read_u2le()
            self.buffer_size = self._io.read_u8le()


    class WaveformHeader(KaitaiStruct):
        """140-byte per-waveform header (Table 19.2).
        Describes acquisition settings and time-axis parameters for one channel.
        """
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.header_size = self._io.read_u4le()
            self.waveform_type = KaitaiStream.resolve_enum(Bindho1000.WaveformTypeEnum, self._io.read_u4le())
            self.n_buffers = self._io.read_u4le()
            self.n_pts = self._io.read_u4le()
            self.count = self._io.read_u4le()
            self.x_display_range = self._io.read_f4le()
            self.x_display_origin = self._io.read_f8le()
            self.x_increment = self._io.read_f8le()
            self.x_origin = self._io.read_f8le()
            self.x_units = KaitaiStream.resolve_enum(Bindho1000.UnitEnum, self._io.read_u4le())
            self.y_units = KaitaiStream.resolve_enum(Bindho1000.UnitEnum, self._io.read_u4le())
            self.date = (KaitaiStream.bytes_terminate(self._io.read_bytes(16), 0, False)).decode(u"ASCII")
            self.time_str = (KaitaiStream.bytes_terminate(self._io.read_bytes(16), 0, False)).decode(u"ASCII")
            self.model = (KaitaiStream.bytes_terminate(self._io.read_bytes(24), 0, False)).decode(u"ASCII")
            self.channel_name = (KaitaiStream.bytes_terminate(self._io.read_bytes(16), 0, False)).decode(u"ASCII")
            self.padding = self._io.read_bytes(12)

        @property
        def t0(self):
            """Time of the first sample in seconds (x_origin negated)."""
            if hasattr(self, '_m_t0'):
                return self._m_t0

            self._m_t0 = -(self.x_origin)
            return getattr(self, '_m_t0', None)

        @property
        def seconds_per_point(self):
            """Sampling interval in seconds."""
            if hasattr(self, '_m_seconds_per_point'):
                return self._m_seconds_per_point

            self._m_seconds_per_point = self.x_increment
            return getattr(self, '_m_seconds_per_point', None)


    class SampleData(KaitaiStruct):
        """Stream of calibrated float32 voltage samples."""
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.values = []
            i = 0
            while not self._io.is_eof():
                self.values.append(self._io.read_f4le())
                i += 1



    class Waveform(KaitaiStruct):
        """One waveform record - header, data header, and float32 samples."""
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.wfm_header = Bindho1000.WaveformHeader(self._io, self, self._root)
            self.data_header = Bindho1000.DataHeader(self._io, self, self._root)
            self._raw_samples = self._io.read_bytes(self.data_header.buffer_size)
            _io__raw_samples = KaitaiStream(BytesIO(self._raw_samples))
            self.samples = Bindho1000.SampleData(_io__raw_samples, self, self._root)


    class FileHeader(KaitaiStruct):
        """16-byte file header (Table 19.1)."""
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.cookie = self._io.read_bytes(2)
            if not self.cookie == b"\x52\x47":
                raise kaitaistruct.ValidationNotEqualError(b"\x52\x47", self.cookie, self._io, u"/types/file_header/seq/0")
            self.version = (self._io.read_bytes(2)).decode(u"ASCII")
            self.file_size = self._io.read_u8le()
            self.n_waveforms = self._io.read_u4le()



