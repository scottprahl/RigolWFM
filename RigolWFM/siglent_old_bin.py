# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild
# type: ignore

import kaitaistruct
from kaitaistruct import KaitaiStruct, KaitaiStream, BytesIO


if getattr(kaitaistruct, 'API_VERSION', (0, 9)) < (0, 11):
    raise Exception("Incompatible Kaitai Struct Python API: 0.11 or later is required, but you have %s" % (kaitaistruct.__version__))

class SiglentOldBin(KaitaiStruct):
    """This revision is used by older SDS1000X / SDS2000X families.
    
    Sources used for this KSY binary format: The binary waveform layout documented by
    Siglent as "How to Extract Data from the Binary File of SIGLENT Oscilloscope".
    
    Tested file formats: the synthetic old-platform fixture built in
    `tests/test_siglent.py`, exercised through revision detection and low-level
    parsing only.
    
    Oscilloscope models this format may apply to: older Siglent `SDS1000X` and
    `SDS2000X` families that the vendor PDF documents as using the "Binary Format
    in Old Platform" layout.
    """
    def __init__(self, _io, _parent=None, _root=None):
        super(SiglentOldBin, self).__init__(_io)
        self._parent = _parent
        self._root = _root or self
        self._read()

    def _read(self):
        pass


    def _fetch_instances(self):
        pass
        _ = self.ch_on
        if hasattr(self, '_m_ch_on'):
            pass
            self._m_ch_on._fetch_instances()

        _ = self.ch_vert_offset_pixels
        if hasattr(self, '_m_ch_vert_offset_pixels'):
            pass
            self._m_ch_vert_offset_pixels._fetch_instances()

        _ = self.ch_volt_div_mv
        if hasattr(self, '_m_ch_volt_div_mv'):
            pass
            self._m_ch_volt_div_mv._fetch_instances()

        _ = self.mso_ch_open_num
        if hasattr(self, '_m_mso_ch_open_num'):
            pass

        _ = self.mso_ch_open_stats
        if hasattr(self, '_m_mso_ch_open_stats'):
            pass
            self._m_mso_ch_open_stats._fetch_instances()

        _ = self.mso_wave_length
        if hasattr(self, '_m_mso_wave_length'):
            pass

        _ = self.time_delay_pixels
        if hasattr(self, '_m_time_delay_pixels'):
            pass

        _ = self.time_div_index
        if hasattr(self, '_m_time_div_index'):
            pass

        _ = self.wave_data
        if hasattr(self, '_m_wave_data'):
            pass


    class F4Array4(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            super(SiglentOldBin.F4Array4, self).__init__(_io)
            self._parent = _parent
            self._root = _root
            self._read()

        def _read(self):
            self.entries = []
            for i in range(4):
                self.entries.append(self._io.read_f4le())



        def _fetch_instances(self):
            pass
            for i in range(len(self.entries)):
                pass



    class S4Array4(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            super(SiglentOldBin.S4Array4, self).__init__(_io)
            self._parent = _parent
            self._root = _root
            self._read()

        def _read(self):
            self.entries = []
            for i in range(4):
                self.entries.append(self._io.read_s4le())



        def _fetch_instances(self):
            pass
            for i in range(len(self.entries)):
                pass



    class U1Array16(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            super(SiglentOldBin.U1Array16, self).__init__(_io)
            self._parent = _parent
            self._root = _root
            self._read()

        def _read(self):
            self.entries = []
            for i in range(16):
                self.entries.append(self._io.read_u1())



        def _fetch_instances(self):
            pass
            for i in range(len(self.entries)):
                pass



    @property
    def ch_on(self):
        if hasattr(self, '_m_ch_on'):
            return self._m_ch_on

        _pos = self._io.pos()
        self._io.seek(256)
        self._m_ch_on = SiglentOldBin.S4Array4(self._io, self, self._root)
        self._io.seek(_pos)
        return getattr(self, '_m_ch_on', None)

    @property
    def ch_vert_offset_pixels(self):
        if hasattr(self, '_m_ch_vert_offset_pixels'):
            return self._m_ch_vert_offset_pixels

        _pos = self._io.pos()
        self._io.seek(220)
        self._m_ch_vert_offset_pixels = SiglentOldBin.S4Array4(self._io, self, self._root)
        self._io.seek(_pos)
        return getattr(self, '_m_ch_vert_offset_pixels', None)

    @property
    def ch_volt_div_mv(self):
        if hasattr(self, '_m_ch_volt_div_mv'):
            return self._m_ch_volt_div_mv

        _pos = self._io.pos()
        self._io.seek(188)
        self._m_ch_volt_div_mv = SiglentOldBin.F4Array4(self._io, self, self._root)
        self._io.seek(_pos)
        return getattr(self, '_m_ch_volt_div_mv', None)

    @property
    def mso_ch_open_num(self):
        if hasattr(self, '_m_mso_ch_open_num'):
            return self._m_mso_ch_open_num

        _pos = self._io.pos()
        self._io.seek(16)
        self._m_mso_ch_open_num = self._io.read_u4le()
        self._io.seek(_pos)
        return getattr(self, '_m_mso_ch_open_num', None)

    @property
    def mso_ch_open_stats(self):
        if hasattr(self, '_m_mso_ch_open_stats'):
            return self._m_mso_ch_open_stats

        _pos = self._io.pos()
        self._io.seek(20)
        self._m_mso_ch_open_stats = SiglentOldBin.U1Array16(self._io, self, self._root)
        self._io.seek(_pos)
        return getattr(self, '_m_mso_ch_open_stats', None)

    @property
    def mso_wave_length(self):
        if hasattr(self, '_m_mso_wave_length'):
            return self._m_mso_wave_length

        _pos = self._io.pos()
        self._io.seek(4)
        self._m_mso_wave_length = self._io.read_u4le()
        self._io.seek(_pos)
        return getattr(self, '_m_mso_wave_length', None)

    @property
    def time_delay_pixels(self):
        if hasattr(self, '_m_time_delay_pixels'):
            return self._m_time_delay_pixels

        _pos = self._io.pos()
        self._io.seek(592)
        self._m_time_delay_pixels = self._io.read_s4le()
        self._io.seek(_pos)
        return getattr(self, '_m_time_delay_pixels', None)

    @property
    def time_div_index(self):
        if hasattr(self, '_m_time_div_index'):
            return self._m_time_div_index

        _pos = self._io.pos()
        self._io.seek(584)
        self._m_time_div_index = self._io.read_s4le()
        self._io.seek(_pos)
        return getattr(self, '_m_time_div_index', None)

    @property
    def wave_data(self):
        if hasattr(self, '_m_wave_data'):
            return self._m_wave_data

        _pos = self._io.pos()
        self._io.seek(5232)
        self._m_wave_data = self._io.read_bytes(self._io.size() - 5232)
        self._io.seek(_pos)
        return getattr(self, '_m_wave_data', None)


