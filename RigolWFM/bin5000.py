# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild
# type: ignore

import kaitaistruct
from kaitaistruct import KaitaiStruct, KaitaiStream, BytesIO
from enum import IntEnum


if getattr(kaitaistruct, 'API_VERSION', (0, 9)) < (0, 11):
    raise Exception("Incompatible Kaitai Struct Python API: 0.11 or later is required, but you have %s" % (kaitaistruct.__version__))

class Bin5000(KaitaiStruct):
    """Binary waveform export used by Rigol MSO5000 scopes.
    
    This schema is based on:
      - example files in `docs/sources/rigol_mso5000-main/waveform_bin/examples`
      - `docs/sources/matlab/importRigolBinMSO5000.m`
      - `docs/sources/rigol_mso5000-main/waveform_bin/Rigol_MSO5000_Waveform_bin.bt`
    
    File layout:
      [File Header:      12 bytes]
      for each exported waveform:
        [Waveform Header: 140 bytes]
        [Data Header:      12 bytes]
        [Sample Data:      buffer_size bytes]
    
    The shipped examples only exercise analog float32 buffers. Logic-analyzer
    records are identified by the enums below and handled in handwritten code.
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
        super(Bin5000, self).__init__(_io)
        self._parent = _parent
        self._root = _root or self
        self._read()

    def _read(self):
        self.file_header = Bin5000.FileHeader(self._io, self, self._root)
        self.waveforms = []
        for i in range(self.file_header.n_waveforms):
            self.waveforms.append(Bin5000.Waveform(self._io, self, self._root))



    def _fetch_instances(self):
        pass
        self.file_header._fetch_instances()
        for i in range(len(self.waveforms)):
            pass
            self.waveforms[i]._fetch_instances()


    class DataHeader(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            super(Bin5000.DataHeader, self).__init__(_io)
            self._parent = _parent
            self._root = _root
            self._read()

        def _read(self):
            self.header_size = self._io.read_u4le()
            self.buffer_type = KaitaiStream.resolve_enum(Bin5000.BufferTypeEnum, self._io.read_u2le())
            self.bytes_per_point = self._io.read_u2le()
            self.buffer_size = self._io.read_u4le()


        def _fetch_instances(self):
            pass


    class FileHeader(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            super(Bin5000.FileHeader, self).__init__(_io)
            self._parent = _parent
            self._root = _root
            self._read()

        def _read(self):
            self.cookie = self._io.read_bytes(2)
            if not self.cookie == b"\x52\x47":
                raise kaitaistruct.ValidationNotEqualError(b"\x52\x47", self.cookie, self._io, u"/types/file_header/seq/0")
            self.version = (self._io.read_bytes(2)).decode(u"ASCII")
            self.file_size = self._io.read_u4le()
            self.n_waveforms = self._io.read_u4le()


        def _fetch_instances(self):
            pass


    class Waveform(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            super(Bin5000.Waveform, self).__init__(_io)
            self._parent = _parent
            self._root = _root
            self._read()

        def _read(self):
            self.wfm_header = Bin5000.WaveformHeader(self._io, self, self._root)
            self.data_header = Bin5000.DataHeader(self._io, self, self._root)
            self.data_raw = self._io.read_bytes(self.data_header.buffer_size)


        def _fetch_instances(self):
            pass
            self.wfm_header._fetch_instances()
            self.data_header._fetch_instances()


    class WaveformHeader(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            super(Bin5000.WaveformHeader, self).__init__(_io)
            self._parent = _parent
            self._root = _root
            self._read()

        def _read(self):
            self.header_size = self._io.read_u4le()
            self.waveform_type = KaitaiStream.resolve_enum(Bin5000.WaveformTypeEnum, self._io.read_u4le())
            self.n_buffers = self._io.read_u4le()
            self.n_pts = self._io.read_u4le()
            self.count = self._io.read_u4le()
            self.x_display_range = self._io.read_f4le()
            self.x_display_origin = self._io.read_f8le()
            self.x_increment = self._io.read_f8le()
            self.x_origin = self._io.read_f8le()
            self.x_units = KaitaiStream.resolve_enum(Bin5000.UnitEnum, self._io.read_u4le())
            self.y_units = KaitaiStream.resolve_enum(Bin5000.UnitEnum, self._io.read_u4le())
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




