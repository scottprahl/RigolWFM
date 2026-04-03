# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild
# type: ignore

import kaitaistruct
from kaitaistruct import KaitaiStruct, KaitaiStream, BytesIO


if getattr(kaitaistruct, 'API_VERSION', (0, 9)) < (0, 11):
    raise Exception("Incompatible Kaitai Struct Python API: 0.11 or later is required, but you have %s" % (kaitaistruct.__version__))

class SiglentV6Bin(KaitaiStruct):
    """Siglent waveform binary layout documented as "Binary Format V6.0".
    
    V6.0 stores a top-level file header followed by one or more waveform records.
    Each waveform contains a fixed shared header, optional extension bytes, an
    optional additional-information block, and then the sample payload.
    
    Sources used for this KSY binary format: The binary waveform layout documented by 
    Siglent as "How to Extract Data from the Binary File of SIGLENT Oscilloscope". 
    
    Tested file formats: the synthetic `Binary Format V6.0` fixture in
    `tests/test_siglent.py`, exercised through revision detection, low-level
    Kaitai parsing, and normalized waveform loading with an `SDS1002X-E` module
    string.
    
    Oscilloscope models this format may apply to: `SDS1002X-E` is the checked-in
    reference model, and other Siglent instruments that write `Binary Format
    V6.0` may share this layout.
    """
    def __init__(self, _io, _parent=None, _root=None):
        super(SiglentV6Bin, self).__init__(_io)
        self._parent = _parent
        self._root = _root or self
        self._read()

    def _read(self):
        self.file_header = SiglentV6Bin.FileHeader(self._io, self, self._root)
        self.waveforms = []
        for i in range(self.file_header.wave_number):
            self.waveforms.append(SiglentV6Bin.Waveform(self._io, self, self._root))



    def _fetch_instances(self):
        pass
        self.file_header._fetch_instances()
        for i in range(len(self.waveforms)):
            pass
            self.waveforms[i]._fetch_instances()


    class FileHeader(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            super(SiglentV6Bin.FileHeader, self).__init__(_io)
            self._parent = _parent
            self._root = _root
            self._read()

        def _read(self):
            self.version = self._io.read_u4le()
            self.header_bytes = self._io.read_u2le()
            self.endian_marker = self._io.read_u2le()
            self.module = (KaitaiStream.bytes_terminate(self._io.read_bytes(32), 0, False)).decode(u"ASCII")
            self.serial = (KaitaiStream.bytes_terminate(self._io.read_bytes(32), 0, False)).decode(u"ASCII")
            self.software_version = (KaitaiStream.bytes_terminate(self._io.read_bytes(32), 0, False)).decode(u"ASCII")
            self.wave_number = self._io.read_u4le()
            if self.header_bytes > 108:
                pass
                self.header_extra = self._io.read_bytes(self.header_bytes - 108)



        def _fetch_instances(self):
            pass
            if self.header_bytes > 108:
                pass



    class Waveform(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            super(SiglentV6Bin.Waveform, self).__init__(_io)
            self._parent = _parent
            self._root = _root
            self._read()

        def _read(self):
            self.header = SiglentV6Bin.WaveformHeader(self._io, self, self._root)
            self.add_info = self._io.read_bytes(self.header.add_info_bytes)
            self.data_raw = self._io.read_bytes(self.header.data_bytes)


        def _fetch_instances(self):
            pass
            self.header._fetch_instances()


    class WaveformHeader(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            super(SiglentV6Bin.WaveformHeader, self).__init__(_io)
            self._parent = _parent
            self._root = _root
            self._read()

        def _read(self):
            self.base_header_type = self._io.read_u4le()
            self.base_header_bytes = self._io.read_u4le()
            self.wave_type = self._io.read_u4le()
            self.channel_type = self._io.read_u2le()
            self.channel_index = self._io.read_u2le()
            self.label = (KaitaiStream.bytes_terminate(self._io.read_bytes(16), 0, False)).decode(u"ASCII")
            self.date = (KaitaiStream.bytes_terminate(self._io.read_bytes(16), 0, False)).decode(u"ASCII")
            self.time_str = (KaitaiStream.bytes_terminate(self._io.read_bytes(32), 0, False)).decode(u"ASCII")
            self.hori_scale = self._io.read_f8le()
            self.hori_pos = self._io.read_f8le()
            self.hori_origin_pos = self._io.read_f8le()
            self.hori_interval = self._io.read_f8le()
            self.hori_unit = []
            for i in range(8):
                self.hori_unit.append(self._io.read_u4le())

            self.hori_unit_str = (KaitaiStream.bytes_terminate(self._io.read_bytes(16), 0, False)).decode(u"ASCII")
            self.vert_scale = self._io.read_f8le()
            self.vert_pos = self._io.read_f8le()
            self.vert_origin_pos = self._io.read_f8le()
            self.vert_interval = self._io.read_f8le()
            self.vert_unit = []
            for i in range(8):
                self.vert_unit.append(self._io.read_u4le())

            self.vert_unit_str = (KaitaiStream.bytes_terminate(self._io.read_bytes(16), 0, False)).decode(u"ASCII")
            self.add_info_bytes = self._io.read_u4le()
            self.data_type = self._io.read_u4le()
            self.data_number = self._io.read_u8le()
            self.data_bytes = self._io.read_u8le()
            if self.base_header_bytes > 264:
                pass
                self.base_header_extra = self._io.read_bytes(self.base_header_bytes - 264)



        def _fetch_instances(self):
            pass
            for i in range(len(self.hori_unit)):
                pass

            for i in range(len(self.vert_unit)):
                pass

            if self.base_header_bytes > 264:
                pass




