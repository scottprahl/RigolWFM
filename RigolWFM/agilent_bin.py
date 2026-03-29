# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild
# type: ignore

import kaitaistruct
from kaitaistruct import KaitaiStruct, KaitaiStream, BytesIO
from enum import IntEnum


if getattr(kaitaistruct, 'API_VERSION', (0, 9)) < (0, 11):
    raise Exception("Incompatible Kaitai Struct Python API: 0.11 or later is required, but you have %s" % (kaitaistruct.__version__))

class AgilentBin(KaitaiStruct):
    """Binary waveform export used by Agilent and Keysight oscilloscopes.
    
    This schema is based on the reverse-engineered parser and checked-in sample
    captures from `docs/vendors/wavebin-master`, which exercise the `AG10`
    container written by DSO-X / MSO-X scopes. The same container family also
    appears to exist in `AG01` and `AG03` variants; the vendor parser handles
    those by widening the file-size and buffer-size fields for version 3.
    
    File layout:
      [File Header: 12 bytes for AG01 / AG10, 16 bytes for AG03]
      for each exported waveform:
        [Waveform Header: usually 140 bytes]
        [Data Header: 12 bytes for AG01 / AG10, 16 bytes for AG03]
        [Sample Data:   buffer_size bytes]
    
    Analog waveforms are stored as float32 buffers. Digital / logic-like
    captures use the same container but store `u1` samples and are handled by
    handwritten code rather than normalized directly by the Kaitai schema.
    """

    class BufferTypeEnum(IntEnum):
        unknown = 0
        normal_float32 = 1
        maximum_float32 = 2
        minimum_float32 = 3
        time_float32 = 4
        counts_float32 = 5
        digital_u8 = 6

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
        peak_detect = 2
        average = 3
        horizontal_histogram = 4
        vertical_histogram = 5
        logic = 6
    def __init__(self, _io, _parent=None, _root=None):
        super(AgilentBin, self).__init__(_io)
        self._parent = _parent
        self._root = _root or self
        self._read()

    def _read(self):
        self.file_header = AgilentBin.FileHeader(self._io, self, self._root)
        self.waveforms = []
        for i in range(self.file_header.n_waveforms):
            self.waveforms.append(AgilentBin.Waveform(self._io, self, self._root))



    def _fetch_instances(self):
        pass
        self.file_header._fetch_instances()
        for i in range(len(self.waveforms)):
            pass
            self.waveforms[i]._fetch_instances()


    class DataHeader(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            super(AgilentBin.DataHeader, self).__init__(_io)
            self._parent = _parent
            self._root = _root
            self._read()

        def _read(self):
            self.header_size = self._io.read_u4le()
            self.buffer_type = KaitaiStream.resolve_enum(AgilentBin.BufferTypeEnum, self._io.read_u2le())
            self.bytes_per_point = self._io.read_u2le()
            if  ((self._root.file_header.version_num == 1) or (self._root.file_header.version_num == 10)) :
                pass
                self.buffer_size_32 = self._io.read_u4le()

            if self._root.file_header.version_num == 3:
                pass
                self.buffer_size_64 = self._io.read_u8le()



        def _fetch_instances(self):
            pass
            if  ((self._root.file_header.version_num == 1) or (self._root.file_header.version_num == 10)) :
                pass

            if self._root.file_header.version_num == 3:
                pass


        @property
        def buffer_size(self):
            if hasattr(self, '_m_buffer_size'):
                return self._m_buffer_size

            self._m_buffer_size = (self.buffer_size_64 if self._root.file_header.version_num == 3 else self.buffer_size_32)
            return getattr(self, '_m_buffer_size', None)


    class FileHeader(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            super(AgilentBin.FileHeader, self).__init__(_io)
            self._parent = _parent
            self._root = _root
            self._read()

        def _read(self):
            self.cookie = self._io.read_bytes(2)
            if not self.cookie == b"\x41\x47":
                raise kaitaistruct.ValidationNotEqualError(b"\x41\x47", self.cookie, self._io, u"/types/file_header/seq/0")
            self.version = (self._io.read_bytes(2)).decode(u"ASCII")
            if  ((self.version_num == 1) or (self.version_num == 10)) :
                pass
                self.file_size_32 = self._io.read_u4le()

            if self.version_num == 3:
                pass
                self.file_size_64 = self._io.read_u8le()

            self.n_waveforms = self._io.read_u4le()


        def _fetch_instances(self):
            pass
            if  ((self.version_num == 1) or (self.version_num == 10)) :
                pass

            if self.version_num == 3:
                pass


        @property
        def file_size(self):
            if hasattr(self, '_m_file_size'):
                return self._m_file_size

            self._m_file_size = (self.file_size_64 if self.version_num == 3 else self.file_size_32)
            return getattr(self, '_m_file_size', None)

        @property
        def version_num(self):
            if hasattr(self, '_m_version_num'):
                return self._m_version_num

            self._m_version_num = int(self.version)
            return getattr(self, '_m_version_num', None)


    class Waveform(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            super(AgilentBin.Waveform, self).__init__(_io)
            self._parent = _parent
            self._root = _root
            self._read()

        def _read(self):
            self.wfm_header = AgilentBin.WaveformHeader(self._io, self, self._root)
            self.data_header = AgilentBin.DataHeader(self._io, self, self._root)
            self.data_raw = self._io.read_bytes(self.data_header.buffer_size)


        def _fetch_instances(self):
            pass
            self.wfm_header._fetch_instances()
            self.data_header._fetch_instances()


    class WaveformHeader(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            super(AgilentBin.WaveformHeader, self).__init__(_io)
            self._parent = _parent
            self._root = _root
            self._read()

        def _read(self):
            self.header_size = self._io.read_u4le()
            self.waveform_type = KaitaiStream.resolve_enum(AgilentBin.WaveformTypeEnum, self._io.read_u4le())
            self.n_buffers = self._io.read_u4le()
            self.n_pts = self._io.read_u4le()
            self.count = self._io.read_u4le()
            self.x_display_range = self._io.read_f4le()
            self.x_display_origin = self._io.read_f8le()
            self.x_increment = self._io.read_f8le()
            self.x_origin = self._io.read_f8le()
            self.x_units = KaitaiStream.resolve_enum(AgilentBin.UnitEnum, self._io.read_u4le())
            self.y_units = KaitaiStream.resolve_enum(AgilentBin.UnitEnum, self._io.read_u4le())
            self.date = (KaitaiStream.bytes_terminate(self._io.read_bytes(16), 0, False)).decode(u"ASCII")
            self.time_str = (KaitaiStream.bytes_terminate(self._io.read_bytes(16), 0, False)).decode(u"ASCII")
            self.frame_string = (KaitaiStream.bytes_terminate(self._io.read_bytes(24), 0, False)).decode(u"ASCII")
            self.waveform_label = (KaitaiStream.bytes_terminate(self._io.read_bytes(16), 0, False)).decode(u"ASCII")
            self.time_tag = self._io.read_f8le()
            self.segment_index = self._io.read_u4le()
            if self.header_size > 140:
                pass
                self.extra_padding = self._io.read_bytes(self.header_size - 140)



        def _fetch_instances(self):
            pass
            if self.header_size > 140:
                pass




