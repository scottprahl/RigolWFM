# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild
# type: ignore

import kaitaistruct
from kaitaistruct import KaitaiStruct, KaitaiStream, BytesIO


if getattr(kaitaistruct, 'API_VERSION', (0, 9)) < (0, 11):
    raise Exception("Incompatible Kaitai Struct Python API: 0.11 or later is required, but you have %s" % (kaitaistruct.__version__))

class SiglentV5Bin(KaitaiStruct):
    """Siglent waveform binary layout documented as "Binary Format V5.0".
    
    This revision is documented for later SDS1002X-E firmware and keeps the
    analog waveform data at offset 0x800 while moving the channel and timing
    metadata into a different fixed layout.
    
    Sources used for this KSY binary format: The binary waveform layout documented by
    Siglent as "How to Extract Data from the Binary File of SIGLENT Oscilloscope".
    
    Tested file formats: the synthetic `Binary Format V5.0` fixture in
    `tests/test_siglent.py`, exercised through revision detection, low-level
    Kaitai parsing, and normalized waveform loading.
    
    Oscilloscope models this format may apply to: later `SDS1002X-E` firmware and
    other Siglent instruments that write `Binary Format V5.0`.
    """
    def __init__(self, _io, _parent=None, _root=None):
        super(SiglentV5Bin, self).__init__(_io)
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

        _ = self.version
        if hasattr(self, '_m_version'):
            pass

        _ = self.wave_data
        if hasattr(self, '_m_wave_data'):
            pass

        _ = self.wave_length
        if hasattr(self, '_m_wave_length'):
            pass


    class ScaledValue16(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            super(SiglentV5Bin.ScaledValue16, self).__init__(_io)
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
        self._io.seek(118)
        self._m_ch1_on = self._io.read_s4le()
        self._io.seek(_pos)
        return getattr(self, '_m_ch1_on', None)

    @property
    def ch1_vert_offset(self):
        if hasattr(self, '_m_ch1_vert_offset'):
            return self._m_ch1_vert_offset

        _pos = self._io.pos()
        self._io.seek(188)
        self._m_ch1_vert_offset = SiglentV5Bin.ScaledValue16(self._io, self, self._root)
        self._io.seek(_pos)
        return getattr(self, '_m_ch1_vert_offset', None)

    @property
    def ch1_volt_div(self):
        if hasattr(self, '_m_ch1_volt_div'):
            return self._m_ch1_volt_div

        _pos = self._io.pos()
        self._io.seek(171)
        self._m_ch1_volt_div = SiglentV5Bin.ScaledValue16(self._io, self, self._root)
        self._io.seek(_pos)
        return getattr(self, '_m_ch1_volt_div', None)

    @property
    def ch2_on(self):
        if hasattr(self, '_m_ch2_on'):
            return self._m_ch2_on

        _pos = self._io.pos()
        self._io.seek(240)
        self._m_ch2_on = self._io.read_s4le()
        self._io.seek(_pos)
        return getattr(self, '_m_ch2_on', None)

    @property
    def ch2_vert_offset(self):
        if hasattr(self, '_m_ch2_vert_offset'):
            return self._m_ch2_vert_offset

        _pos = self._io.pos()
        self._io.seek(368)
        self._m_ch2_vert_offset = SiglentV5Bin.ScaledValue16(self._io, self, self._root)
        self._io.seek(_pos)
        return getattr(self, '_m_ch2_vert_offset', None)

    @property
    def ch2_volt_div(self):
        if hasattr(self, '_m_ch2_volt_div'):
            return self._m_ch2_volt_div

        _pos = self._io.pos()
        self._io.seek(352)
        self._m_ch2_volt_div = SiglentV5Bin.ScaledValue16(self._io, self, self._root)
        self._io.seek(_pos)
        return getattr(self, '_m_ch2_volt_div', None)

    @property
    def ch3_on(self):
        if hasattr(self, '_m_ch3_on'):
            return self._m_ch3_on

        _pos = self._io.pos()
        self._io.seek(404)
        self._m_ch3_on = self._io.read_s4le()
        self._io.seek(_pos)
        return getattr(self, '_m_ch3_on', None)

    @property
    def ch3_vert_offset(self):
        if hasattr(self, '_m_ch3_vert_offset'):
            return self._m_ch3_vert_offset

        _pos = self._io.pos()
        self._io.seek(532)
        self._m_ch3_vert_offset = SiglentV5Bin.ScaledValue16(self._io, self, self._root)
        self._io.seek(_pos)
        return getattr(self, '_m_ch3_vert_offset', None)

    @property
    def ch3_volt_div(self):
        if hasattr(self, '_m_ch3_volt_div'):
            return self._m_ch3_volt_div

        _pos = self._io.pos()
        self._io.seek(516)
        self._m_ch3_volt_div = SiglentV5Bin.ScaledValue16(self._io, self, self._root)
        self._io.seek(_pos)
        return getattr(self, '_m_ch3_volt_div', None)

    @property
    def ch4_on(self):
        if hasattr(self, '_m_ch4_on'):
            return self._m_ch4_on

        _pos = self._io.pos()
        self._io.seek(568)
        self._m_ch4_on = self._io.read_s4le()
        self._io.seek(_pos)
        return getattr(self, '_m_ch4_on', None)

    @property
    def ch4_vert_offset(self):
        if hasattr(self, '_m_ch4_vert_offset'):
            return self._m_ch4_vert_offset

        _pos = self._io.pos()
        self._io.seek(696)
        self._m_ch4_vert_offset = SiglentV5Bin.ScaledValue16(self._io, self, self._root)
        self._io.seek(_pos)
        return getattr(self, '_m_ch4_vert_offset', None)

    @property
    def ch4_volt_div(self):
        if hasattr(self, '_m_ch4_volt_div'):
            return self._m_ch4_volt_div

        _pos = self._io.pos()
        self._io.seek(680)
        self._m_ch4_volt_div = SiglentV5Bin.ScaledValue16(self._io, self, self._root)
        self._io.seek(_pos)
        return getattr(self, '_m_ch4_volt_div', None)

    @property
    def sample_rate(self):
        if hasattr(self, '_m_sample_rate'):
            return self._m_sample_rate

        _pos = self._io.pos()
        self._io.seek(7058)
        self._m_sample_rate = SiglentV5Bin.ScaledValue16(self._io, self, self._root)
        self._io.seek(_pos)
        return getattr(self, '_m_sample_rate', None)

    @property
    def time_delay(self):
        if hasattr(self, '_m_time_delay'):
            return self._m_time_delay

        _pos = self._io.pos()
        self._io.seek(7032)
        self._m_time_delay = SiglentV5Bin.ScaledValue16(self._io, self, self._root)
        self._io.seek(_pos)
        return getattr(self, '_m_time_delay', None)

    @property
    def time_div(self):
        if hasattr(self, '_m_time_div'):
            return self._m_time_div

        _pos = self._io.pos()
        self._io.seek(7016)
        self._m_time_div = SiglentV5Bin.ScaledValue16(self._io, self, self._root)
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
        self._io.seek(7048)
        self._m_wave_length = self._io.read_u4le()
        self._io.seek(_pos)
        return getattr(self, '_m_wave_length', None)


