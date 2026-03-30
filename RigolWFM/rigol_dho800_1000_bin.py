# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild
# type: ignore

import kaitaistruct
from kaitaistruct import KaitaiStruct, KaitaiStream, BytesIO
from enum import IntEnum


if getattr(kaitaistruct, 'API_VERSION', (0, 9)) < (0, 11):
    raise Exception("Incompatible Kaitai Struct Python API: 0.11 or later is required, but you have %s" % (kaitaistruct.__version__))

class RigolDho8001000Bin(KaitaiStruct):
    """Official binary waveform export format documented in DHO1000 User Guide
    §19.2.4 (Tables 19.1–19.4).
    
    This schema currently models the float32 analog waveform buffers used by
    this project. The user guide also documents digital unsigned 8-bit buffers
    and math waveforms; those buffer types are identified in the enums below,
    and the downstream wrapper rejects them explicitly instead of treating them
    as calibrated volt samples.
    
    File layout:
      [File Header:      16 bytes]
      for each waveform (channel):
        [Waveform Header: 140 bytes]
        [Data Header:      16 bytes]
        [Sample Data:      buffer_size bytes - float32 LE, volts]
    
    Time axis reconstruction used by the current parser:
      t[i] = -x_origin + i * x_increment
    
    The manual describes X Origin as the x-value of the first data point.
    Empirically, the analog captures used by this repo behave as if x_origin
    stores a positive pre-trigger distance, so downstream code negates it.
    
    Sources used for this KSY binary format: the official DHO1000 User Guide
    section 19.2.4 (Tables 19.1-19.4) plus comparison against checked-in
    `DHO1074.bin`, `DHO824-ch1.bin`, `DHO824-ch12.bin`, and `DHO824-ch1234.bin`
    captures.
    
    Tested file formats: real repo fixtures `DHO1074.bin`, `DHO824-ch1.bin`,
    `DHO824-ch12.bin`, and `DHO824-ch1234.bin`, covering one-, two-, and
    four-channel analog float32 exports.
    
    Oscilloscope models this format may apply to: `DHO804`, `DHO812`, `DHO814`,
    `DHO824`, `DHO1072`, `DHO1074`, `DHO1102`, `DHO1202`, and related
    `DHO800` / `DHO1000` family scopes that write the documented `.bin` export.
    """

    class BufferTypeEnum(IntEnum):
        unknown = 0
        float32_normal = 1
        float32_maximum = 2
        float32_minimum = 3
        not_used = 4
        digital_u8 = 5

    class UnitEnum(IntEnum):
        unknown = 0
        v = 1
        s = 2
        constant = 3
        a = 4
        db = 5
        hz = 6

    class WaveformTypeEnum(IntEnum):
        unknown = 0
        normal = 1
        peak = 2
        average = 3
        not_used_4 = 4
        not_used_5 = 5
        logic = 6
    def __init__(self, _io, _parent=None, _root=None):
        super(RigolDho8001000Bin, self).__init__(_io)
        self._parent = _parent
        self._root = _root or self
        self._read()

    def _read(self):
        self.file_header = RigolDho8001000Bin.FileHeader(self._io, self, self._root)
        self.waveforms = []
        for i in range(self.file_header.n_waveforms):
            self.waveforms.append(RigolDho8001000Bin.Waveform(self._io, self, self._root))



    def _fetch_instances(self):
        pass
        self.file_header._fetch_instances()
        for i in range(len(self.waveforms)):
            pass
            self.waveforms[i]._fetch_instances()


    class DataHeader(KaitaiStruct):
        """16-byte data buffer header (Table 19.4)."""
        def __init__(self, _io, _parent=None, _root=None):
            super(RigolDho8001000Bin.DataHeader, self).__init__(_io)
            self._parent = _parent
            self._root = _root
            self._read()

        def _read(self):
            self.header_size = self._io.read_u4le()
            self.buffer_type = KaitaiStream.resolve_enum(RigolDho8001000Bin.BufferTypeEnum, self._io.read_u2le())
            self.bytes_per_point = self._io.read_u2le()
            self.buffer_size = self._io.read_u8le()


        def _fetch_instances(self):
            pass


    class FileHeader(KaitaiStruct):
        """16-byte file header (Table 19.2)."""
        def __init__(self, _io, _parent=None, _root=None):
            super(RigolDho8001000Bin.FileHeader, self).__init__(_io)
            self._parent = _parent
            self._root = _root
            self._read()

        def _read(self):
            self.cookie = self._io.read_bytes(2)
            if not self.cookie == b"\x52\x47":
                raise kaitaistruct.ValidationNotEqualError(b"\x52\x47", self.cookie, self._io, u"/types/file_header/seq/0")
            self.version = (self._io.read_bytes(2)).decode(u"ASCII")
            self.file_size = self._io.read_u8le()
            self.n_waveforms = self._io.read_u4le()


        def _fetch_instances(self):
            pass


    class SampleData(KaitaiStruct):
        """Stream of calibrated float32 voltage samples for analog buffers."""
        def __init__(self, _io, _parent=None, _root=None):
            super(RigolDho8001000Bin.SampleData, self).__init__(_io)
            self._parent = _parent
            self._root = _root
            self._read()

        def _read(self):
            self.values = []
            i = 0
            while not self._io.is_eof():
                self.values.append(self._io.read_f4le())
                i += 1



        def _fetch_instances(self):
            pass
            for i in range(len(self.values)):
                pass



    class Waveform(KaitaiStruct):
        """One waveform record: header, data header, and sample payload.
        """
        def __init__(self, _io, _parent=None, _root=None):
            super(RigolDho8001000Bin.Waveform, self).__init__(_io)
            self._parent = _parent
            self._root = _root
            self._read()

        def _read(self):
            self.wfm_header = RigolDho8001000Bin.WaveformHeader(self._io, self, self._root)
            self.data_header = RigolDho8001000Bin.DataHeader(self._io, self, self._root)
            self._raw_samples = self._io.read_bytes(self.data_header.buffer_size)
            _io__raw_samples = KaitaiStream(BytesIO(self._raw_samples))
            self.samples = RigolDho8001000Bin.SampleData(_io__raw_samples, self, self._root)


        def _fetch_instances(self):
            pass
            self.wfm_header._fetch_instances()
            self.data_header._fetch_instances()
            self.samples._fetch_instances()


    class WaveformHeader(KaitaiStruct):
        """140-byte per-waveform header (Table 19.3).
        Describes acquisition settings and time-axis parameters for one channel.
        """
        def __init__(self, _io, _parent=None, _root=None):
            super(RigolDho8001000Bin.WaveformHeader, self).__init__(_io)
            self._parent = _parent
            self._root = _root
            self._read()

        def _read(self):
            self.header_size = self._io.read_u4le()
            self.waveform_type = KaitaiStream.resolve_enum(RigolDho8001000Bin.WaveformTypeEnum, self._io.read_u4le())
            self.n_buffers = self._io.read_u4le()
            self.n_pts = self._io.read_u4le()
            self.count = self._io.read_u4le()
            self.x_display_range = self._io.read_f4le()
            self.x_display_origin = self._io.read_f8le()
            self.x_increment = self._io.read_f8le()
            self.x_origin = self._io.read_f8le()
            self.x_units = KaitaiStream.resolve_enum(RigolDho8001000Bin.UnitEnum, self._io.read_u4le())
            self.y_units = KaitaiStream.resolve_enum(RigolDho8001000Bin.UnitEnum, self._io.read_u4le())
            self.date = (KaitaiStream.bytes_terminate(self._io.read_bytes(16), 0, False)).decode(u"ASCII")
            self.time_str = (KaitaiStream.bytes_terminate(self._io.read_bytes(16), 0, False)).decode(u"ASCII")
            self.model = (KaitaiStream.bytes_terminate(self._io.read_bytes(24), 0, False)).decode(u"ASCII")
            self.channel_name = (KaitaiStream.bytes_terminate(self._io.read_bytes(16), 0, False)).decode(u"ASCII")
            self.padding = self._io.read_bytes(12)


        def _fetch_instances(self):
            pass

        @property
        def seconds_per_point(self):
            """Sampling interval in seconds."""
            if hasattr(self, '_m_seconds_per_point'):
                return self._m_seconds_per_point

            self._m_seconds_per_point = self.x_increment
            return getattr(self, '_m_seconds_per_point', None)

        @property
        def t0(self):
            """Empirical first-sample time used by the current analog parser."""
            if hasattr(self, '_m_t0'):
                return self._m_t0

            self._m_t0 = -(self.x_origin)
            return getattr(self, '_m_t0', None)



