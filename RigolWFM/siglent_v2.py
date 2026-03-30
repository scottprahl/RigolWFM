# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild
# type: ignore

import kaitaistruct
from kaitaistruct import KaitaiStruct, KaitaiStream, BytesIO


if getattr(kaitaistruct, 'API_VERSION', (0, 9)) < (0, 11):
    raise Exception("Incompatible Kaitai Struct Python API: 0.11 or later is required, but you have %s" % (kaitaistruct.__version__))

class SiglentV2(KaitaiStruct):
    """Siglent waveform binary layout documented as "Binary Format V2.0".
    
    V2.0 adds a top-level version field and expands the value/unit structure from
    16 bytes to 40 bytes. Analog samples still begin at offset 0x800 and are
    packed channel-by-channel for the enabled channels.
    """
    def __init__(self, _io, _parent=None, _root=None):
        super(SiglentV2, self).__init__(_io)
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

        _ = self.ch_probe
        if hasattr(self, '_m_ch_probe'):
            pass
            self._m_ch_probe._fetch_instances()

        _ = self.ch_vert_offset
        if hasattr(self, '_m_ch_vert_offset'):
            pass
            self._m_ch_vert_offset._fetch_instances()

        _ = self.ch_volt_div
        if hasattr(self, '_m_ch_volt_div'):
            pass
            self._m_ch_volt_div._fetch_instances()

        _ = self.data_width
        if hasattr(self, '_m_data_width'):
            pass

        _ = self.digital_ch_on
        if hasattr(self, '_m_digital_ch_on'):
            pass
            self._m_digital_ch_on._fetch_instances()

        _ = self.digital_on
        if hasattr(self, '_m_digital_on'):
            pass

        _ = self.digital_sample_rate
        if hasattr(self, '_m_digital_sample_rate'):
            pass
            self._m_digital_sample_rate._fetch_instances()

        _ = self.digital_wave_length
        if hasattr(self, '_m_digital_wave_length'):
            pass

        _ = self.sample_rate
        if hasattr(self, '_m_sample_rate'):
            pass
            self._m_sample_rate._fetch_instances()

        _ = self.time_delay
        if hasattr(self, '_m_time_delay'):
            pass
            self._m_time_delay._fetch_instances()

        _ = self.time_div
        if hasattr(self, '_m_time_div'):
            pass
            self._m_time_div._fetch_instances()

        _ = self.version
        if hasattr(self, '_m_version'):
            pass

        _ = self.wave_data
        if hasattr(self, '_m_wave_data'):
            pass

        _ = self.wave_length
        if hasattr(self, '_m_wave_length'):
            pass


    class DataWithUnit(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            super(SiglentV2.DataWithUnit, self).__init__(_io)
            self._parent = _parent
            self._root = _root
            self._read()

        def _read(self):
            self.value = self._io.read_f8le()
            self.magnitude = self._io.read_u4le()
            self.unit_words = []
            for i in range(7):
                self.unit_words.append(self._io.read_u4le())



        def _fetch_instances(self):
            pass
            for i in range(len(self.unit_words)):
                pass



    class DataWithUnitArray4(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            super(SiglentV2.DataWithUnitArray4, self).__init__(_io)
            self._parent = _parent
            self._root = _root
            self._read()

        def _read(self):
            self.entries = []
            for i in range(4):
                self.entries.append(SiglentV2.DataWithUnit(self._io, self, self._root))



        def _fetch_instances(self):
            pass
            for i in range(len(self.entries)):
                pass
                self.entries[i]._fetch_instances()



    class F8Array4(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            super(SiglentV2.F8Array4, self).__init__(_io)
            self._parent = _parent
            self._root = _root
            self._read()

        def _read(self):
            self.entries = []
            for i in range(4):
                self.entries.append(self._io.read_f8le())



        def _fetch_instances(self):
            pass
            for i in range(len(self.entries)):
                pass



    class S4Array4(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            super(SiglentV2.S4Array4, self).__init__(_io)
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



    class U4Array16(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            super(SiglentV2.U4Array16, self).__init__(_io)
            self._parent = _parent
            self._root = _root
            self._read()

        def _read(self):
            self.entries = []
            for i in range(16):
                self.entries.append(self._io.read_u4le())



        def _fetch_instances(self):
            pass
            for i in range(len(self.entries)):
                pass



    @property
    def ch_on(self):
        if hasattr(self, '_m_ch_on'):
            return self._m_ch_on

        _pos = self._io.pos()
        self._io.seek(4)
        self._m_ch_on = SiglentV2.S4Array4(self._io, self, self._root)
        self._io.seek(_pos)
        return getattr(self, '_m_ch_on', None)

    @property
    def ch_probe(self):
        if hasattr(self, '_m_ch_probe'):
            return self._m_ch_probe

        _pos = self._io.pos()
        self._io.seek(576)
        self._m_ch_probe = SiglentV2.F8Array4(self._io, self, self._root)
        self._io.seek(_pos)
        return getattr(self, '_m_ch_probe', None)

    @property
    def ch_vert_offset(self):
        if hasattr(self, '_m_ch_vert_offset'):
            return self._m_ch_vert_offset

        _pos = self._io.pos()
        self._io.seek(180)
        self._m_ch_vert_offset = SiglentV2.DataWithUnitArray4(self._io, self, self._root)
        self._io.seek(_pos)
        return getattr(self, '_m_ch_vert_offset', None)

    @property
    def ch_volt_div(self):
        if hasattr(self, '_m_ch_volt_div'):
            return self._m_ch_volt_div

        _pos = self._io.pos()
        self._io.seek(20)
        self._m_ch_volt_div = SiglentV2.DataWithUnitArray4(self._io, self, self._root)
        self._io.seek(_pos)
        return getattr(self, '_m_ch_volt_div', None)

    @property
    def data_width(self):
        if hasattr(self, '_m_data_width'):
            return self._m_data_width

        _pos = self._io.pos()
        self._io.seek(608)
        self._m_data_width = self._io.read_u1()
        self._io.seek(_pos)
        return getattr(self, '_m_data_width', None)

    @property
    def digital_ch_on(self):
        if hasattr(self, '_m_digital_ch_on'):
            return self._m_digital_ch_on

        _pos = self._io.pos()
        self._io.seek(344)
        self._m_digital_ch_on = SiglentV2.U4Array16(self._io, self, self._root)
        self._io.seek(_pos)
        return getattr(self, '_m_digital_ch_on', None)

    @property
    def digital_on(self):
        if hasattr(self, '_m_digital_on'):
            return self._m_digital_on

        _pos = self._io.pos()
        self._io.seek(340)
        self._m_digital_on = self._io.read_u4le()
        self._io.seek(_pos)
        return getattr(self, '_m_digital_on', None)

    @property
    def digital_sample_rate(self):
        if hasattr(self, '_m_digital_sample_rate'):
            return self._m_digital_sample_rate

        _pos = self._io.pos()
        self._io.seek(536)
        self._m_digital_sample_rate = SiglentV2.DataWithUnit(self._io, self, self._root)
        self._io.seek(_pos)
        return getattr(self, '_m_digital_sample_rate', None)

    @property
    def digital_wave_length(self):
        if hasattr(self, '_m_digital_wave_length'):
            return self._m_digital_wave_length

        _pos = self._io.pos()
        self._io.seek(532)
        self._m_digital_wave_length = self._io.read_u4le()
        self._io.seek(_pos)
        return getattr(self, '_m_digital_wave_length', None)

    @property
    def sample_rate(self):
        if hasattr(self, '_m_sample_rate'):
            return self._m_sample_rate

        _pos = self._io.pos()
        self._io.seek(492)
        self._m_sample_rate = SiglentV2.DataWithUnit(self._io, self, self._root)
        self._io.seek(_pos)
        return getattr(self, '_m_sample_rate', None)

    @property
    def time_delay(self):
        if hasattr(self, '_m_time_delay'):
            return self._m_time_delay

        _pos = self._io.pos()
        self._io.seek(448)
        self._m_time_delay = SiglentV2.DataWithUnit(self._io, self, self._root)
        self._io.seek(_pos)
        return getattr(self, '_m_time_delay', None)

    @property
    def time_div(self):
        if hasattr(self, '_m_time_div'):
            return self._m_time_div

        _pos = self._io.pos()
        self._io.seek(408)
        self._m_time_div = SiglentV2.DataWithUnit(self._io, self, self._root)
        self._io.seek(_pos)
        return getattr(self, '_m_time_div', None)

    @property
    def version(self):
        if hasattr(self, '_m_version'):
            return self._m_version

        _pos = self._io.pos()
        self._io.seek(0)
        self._m_version = self._io.read_u4le()
        self._io.seek(_pos)
        return getattr(self, '_m_version', None)

    @property
    def wave_data(self):
        if hasattr(self, '_m_wave_data'):
            return self._m_wave_data

        _pos = self._io.pos()
        self._io.seek(2048)
        self._m_wave_data = self._io.read_bytes(self._io.size() - 2048)
        self._io.seek(_pos)
        return getattr(self, '_m_wave_data', None)

    @property
    def wave_length(self):
        if hasattr(self, '_m_wave_length'):
            return self._m_wave_length

        _pos = self._io.pos()
        self._io.seek(488)
        self._m_wave_length = self._io.read_u4le()
        self._io.seek(_pos)
        return getattr(self, '_m_wave_length', None)


