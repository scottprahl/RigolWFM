# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild
# type: ignore

import kaitaistruct
from kaitaistruct import KaitaiStruct, KaitaiStream, BytesIO


if getattr(kaitaistruct, 'API_VERSION', (0, 9)) < (0, 11):
    raise Exception("Incompatible Kaitai Struct Python API: 0.11 or later is required, but you have %s" % (kaitaistruct.__version__))

class SiglentV02(KaitaiStruct):
    """Siglent waveform binary layout documented as "Binary Format V0.2".
    
    V0.2 keeps the V0.1 analog-only sample packing but moves the horizontal
    timing metadata to later offsets in the file.
    """
    def __init__(self, _io, _parent=None, _root=None):
        super(SiglentV02, self).__init__(_io)
        self._parent = _parent
        self._root = _root or self
        self._read()

    def _read(self):
        pass


    def _fetch_instances(self):
        pass
        _ = self.ch1_on
        if hasattr(self, '_m_ch1_on'):
            pass

        _ = self.ch1_vert_offset
        if hasattr(self, '_m_ch1_vert_offset'):
            pass
            self._m_ch1_vert_offset._fetch_instances()

        _ = self.ch1_volt_div
        if hasattr(self, '_m_ch1_volt_div'):
            pass
            self._m_ch1_volt_div._fetch_instances()

        _ = self.ch2_on
        if hasattr(self, '_m_ch2_on'):
            pass

        _ = self.ch2_vert_offset
        if hasattr(self, '_m_ch2_vert_offset'):
            pass
            self._m_ch2_vert_offset._fetch_instances()

        _ = self.ch2_volt_div
        if hasattr(self, '_m_ch2_volt_div'):
            pass
            self._m_ch2_volt_div._fetch_instances()

        _ = self.ch3_on
        if hasattr(self, '_m_ch3_on'):
            pass

        _ = self.ch3_vert_offset
        if hasattr(self, '_m_ch3_vert_offset'):
            pass
            self._m_ch3_vert_offset._fetch_instances()

        _ = self.ch3_volt_div
        if hasattr(self, '_m_ch3_volt_div'):
            pass
            self._m_ch3_volt_div._fetch_instances()

        _ = self.ch4_on
        if hasattr(self, '_m_ch4_on'):
            pass

        _ = self.ch4_vert_offset
        if hasattr(self, '_m_ch4_vert_offset'):
            pass
            self._m_ch4_vert_offset._fetch_instances()

        _ = self.ch4_volt_div
        if hasattr(self, '_m_ch4_volt_div'):
            pass
            self._m_ch4_volt_div._fetch_instances()

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

        _ = self.wave_data
        if hasattr(self, '_m_wave_data'):
            pass

        _ = self.wave_length
        if hasattr(self, '_m_wave_length'):
            pass


    class ScaledValue16(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            super(SiglentV02.ScaledValue16, self).__init__(_io)
            self._parent = _parent
            self._root = _root
            self._read()

        def _read(self):
            self.value = self._io.read_f8le()
            self.magnitude = self._io.read_u4le()
            self.unit = self._io.read_u4le()


        def _fetch_instances(self):
            pass


    @property
    def ch1_on(self):
        if hasattr(self, '_m_ch1_on'):
            return self._m_ch1_on

        _pos = self._io.pos()
        self._io.seek(68)
        self._m_ch1_on = self._io.read_s4le()
        self._io.seek(_pos)
        return getattr(self, '_m_ch1_on', None)

    @property
    def ch1_vert_offset(self):
        if hasattr(self, '_m_ch1_vert_offset'):
            return self._m_ch1_vert_offset

        _pos = self._io.pos()
        self._io.seek(196)
        self._m_ch1_vert_offset = SiglentV02.ScaledValue16(self._io, self, self._root)
        self._io.seek(_pos)
        return getattr(self, '_m_ch1_vert_offset', None)

    @property
    def ch1_volt_div(self):
        if hasattr(self, '_m_ch1_volt_div'):
            return self._m_ch1_volt_div

        _pos = self._io.pos()
        self._io.seek(180)
        self._m_ch1_volt_div = SiglentV02.ScaledValue16(self._io, self, self._root)
        self._io.seek(_pos)
        return getattr(self, '_m_ch1_volt_div', None)

    @property
    def ch2_on(self):
        if hasattr(self, '_m_ch2_on'):
            return self._m_ch2_on

        _pos = self._io.pos()
        self._io.seek(232)
        self._m_ch2_on = self._io.read_s4le()
        self._io.seek(_pos)
        return getattr(self, '_m_ch2_on', None)

    @property
    def ch2_vert_offset(self):
        if hasattr(self, '_m_ch2_vert_offset'):
            return self._m_ch2_vert_offset

        _pos = self._io.pos()
        self._io.seek(360)
        self._m_ch2_vert_offset = SiglentV02.ScaledValue16(self._io, self, self._root)
        self._io.seek(_pos)
        return getattr(self, '_m_ch2_vert_offset', None)

    @property
    def ch2_volt_div(self):
        if hasattr(self, '_m_ch2_volt_div'):
            return self._m_ch2_volt_div

        _pos = self._io.pos()
        self._io.seek(344)
        self._m_ch2_volt_div = SiglentV02.ScaledValue16(self._io, self, self._root)
        self._io.seek(_pos)
        return getattr(self, '_m_ch2_volt_div', None)

    @property
    def ch3_on(self):
        if hasattr(self, '_m_ch3_on'):
            return self._m_ch3_on

        _pos = self._io.pos()
        self._io.seek(396)
        self._m_ch3_on = self._io.read_s4le()
        self._io.seek(_pos)
        return getattr(self, '_m_ch3_on', None)

    @property
    def ch3_vert_offset(self):
        if hasattr(self, '_m_ch3_vert_offset'):
            return self._m_ch3_vert_offset

        _pos = self._io.pos()
        self._io.seek(524)
        self._m_ch3_vert_offset = SiglentV02.ScaledValue16(self._io, self, self._root)
        self._io.seek(_pos)
        return getattr(self, '_m_ch3_vert_offset', None)

    @property
    def ch3_volt_div(self):
        if hasattr(self, '_m_ch3_volt_div'):
            return self._m_ch3_volt_div

        _pos = self._io.pos()
        self._io.seek(508)
        self._m_ch3_volt_div = SiglentV02.ScaledValue16(self._io, self, self._root)
        self._io.seek(_pos)
        return getattr(self, '_m_ch3_volt_div', None)

    @property
    def ch4_on(self):
        if hasattr(self, '_m_ch4_on'):
            return self._m_ch4_on

        _pos = self._io.pos()
        self._io.seek(560)
        self._m_ch4_on = self._io.read_s4le()
        self._io.seek(_pos)
        return getattr(self, '_m_ch4_on', None)

    @property
    def ch4_vert_offset(self):
        if hasattr(self, '_m_ch4_vert_offset'):
            return self._m_ch4_vert_offset

        _pos = self._io.pos()
        self._io.seek(688)
        self._m_ch4_vert_offset = SiglentV02.ScaledValue16(self._io, self, self._root)
        self._io.seek(_pos)
        return getattr(self, '_m_ch4_vert_offset', None)

    @property
    def ch4_volt_div(self):
        if hasattr(self, '_m_ch4_volt_div'):
            return self._m_ch4_volt_div

        _pos = self._io.pos()
        self._io.seek(672)
        self._m_ch4_volt_div = SiglentV02.ScaledValue16(self._io, self, self._root)
        self._io.seek(_pos)
        return getattr(self, '_m_ch4_volt_div', None)

    @property
    def sample_rate(self):
        if hasattr(self, '_m_sample_rate'):
            return self._m_sample_rate

        _pos = self._io.pos()
        self._io.seek(3548)
        self._m_sample_rate = SiglentV02.ScaledValue16(self._io, self, self._root)
        self._io.seek(_pos)
        return getattr(self, '_m_sample_rate', None)

    @property
    def time_delay(self):
        if hasattr(self, '_m_time_delay'):
            return self._m_time_delay

        _pos = self._io.pos()
        self._io.seek(3528)
        self._m_time_delay = SiglentV02.ScaledValue16(self._io, self, self._root)
        self._io.seek(_pos)
        return getattr(self, '_m_time_delay', None)

    @property
    def time_div(self):
        if hasattr(self, '_m_time_div'):
            return self._m_time_div

        _pos = self._io.pos()
        self._io.seek(3512)
        self._m_time_div = SiglentV02.ScaledValue16(self._io, self, self._root)
        self._io.seek(_pos)
        return getattr(self, '_m_time_div', None)

    @property
    def wave_data(self):
        if hasattr(self, '_m_wave_data'):
            return self._m_wave_data

        _pos = self._io.pos()
        self._io.seek(37676)
        self._m_wave_data = self._io.read_bytes(self._io.size() - 37676)
        self._io.seek(_pos)
        return getattr(self, '_m_wave_data', None)

    @property
    def wave_length(self):
        if hasattr(self, '_m_wave_length'):
            return self._m_wave_length

        _pos = self._io.pos()
        self._io.seek(3544)
        self._m_wave_length = self._io.read_u4le()
        self._io.seek(_pos)
        return getattr(self, '_m_wave_length', None)


