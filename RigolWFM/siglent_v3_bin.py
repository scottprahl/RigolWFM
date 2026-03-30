# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild
# type: ignore

import kaitaistruct
from kaitaistruct import KaitaiStruct, KaitaiStream, BytesIO


if getattr(kaitaistruct, 'API_VERSION', (0, 9)) < (0, 11):
    raise Exception("Incompatible Kaitai Struct Python API: 0.11 or later is required, but you have %s" % (kaitaistruct.__version__))

class SiglentV3Bin(KaitaiStruct):
    """Siglent waveform binary layout documented as "Binary Format V3.0".
    
    V3.0 retains the V2.0 2 KiB header but adds byte order, horizontal grid
    count, per-channel code-per-division values, and math-wave metadata.
    """
    def __init__(self, _io, _parent=None, _root=None):
        super(SiglentV3Bin, self).__init__(_io)
        self._parent = _parent
        self._root = _root or self
        self._read()

    def _read(self):
        pass


    def _fetch_instances(self):
        pass
        _ = self.byte_order
        if hasattr(self, '_m_byte_order'):
            pass

        _ = self.ch_on
        if hasattr(self, '_m_ch_on'):
            pass
            self._m_ch_on._fetch_instances()

        _ = self.ch_probe
        if hasattr(self, '_m_ch_probe'):
            pass
            self._m_ch_probe._fetch_instances()

        _ = self.ch_vert_code_per_div
        if hasattr(self, '_m_ch_vert_code_per_div'):
            pass
            self._m_ch_vert_code_per_div._fetch_instances()

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

        _ = self.hori_div_num
        if hasattr(self, '_m_hori_div_num'):
            pass

        _ = self.math_f_time
        if hasattr(self, '_m_math_f_time'):
            pass
            self._m_math_f_time._fetch_instances()

        _ = self.math_store_len
        if hasattr(self, '_m_math_store_len'):
            pass
            self._m_math_store_len._fetch_instances()

        _ = self.math_switch
        if hasattr(self, '_m_math_switch'):
            pass
            self._m_math_switch._fetch_instances()

        _ = self.math_vert_code_per_div
        if hasattr(self, '_m_math_vert_code_per_div'):
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
            super(SiglentV3Bin.DataWithUnit, self).__init__(_io)
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
            super(SiglentV3Bin.DataWithUnitArray4, self).__init__(_io)
            self._parent = _parent
            self._root = _root
            self._read()

        def _read(self):
            self.entries = []
            for i in range(4):
                self.entries.append(SiglentV3Bin.DataWithUnit(self._io, self, self._root))



        def _fetch_instances(self):
            pass
            for i in range(len(self.entries)):
                pass
                self.entries[i]._fetch_instances()



    class F8Array4(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            super(SiglentV3Bin.F8Array4, self).__init__(_io)
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
            super(SiglentV3Bin.S4Array4, self).__init__(_io)
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
            super(SiglentV3Bin.U4Array16, self).__init__(_io)
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



    class U4Array4(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            super(SiglentV3Bin.U4Array4, self).__init__(_io)
            self._parent = _parent
            self._root = _root
            self._read()

        def _read(self):
            self.entries = []
            for i in range(4):
                self.entries.append(self._io.read_u4le())



        def _fetch_instances(self):
            pass
            for i in range(len(self.entries)):
                pass



    @property
    def byte_order(self):
        if hasattr(self, '_m_byte_order'):
            return self._m_byte_order

        _pos = self._io.pos()
        self._io.seek(609)
        self._m_byte_order = self._io.read_u1()
        self._io.seek(_pos)
        return getattr(self, '_m_byte_order', None)

    @property
    def ch_on(self):
        if hasattr(self, '_m_ch_on'):
            return self._m_ch_on

        _pos = self._io.pos()
        self._io.seek(4)
        self._m_ch_on = SiglentV3Bin.S4Array4(self._io, self, self._root)
        self._io.seek(_pos)
        return getattr(self, '_m_ch_on', None)

    @property
    def ch_probe(self):
        if hasattr(self, '_m_ch_probe'):
            return self._m_ch_probe

        _pos = self._io.pos()
        self._io.seek(576)
        self._m_ch_probe = SiglentV3Bin.F8Array4(self._io, self, self._root)
        self._io.seek(_pos)
        return getattr(self, '_m_ch_probe', None)

    @property
    def ch_vert_code_per_div(self):
        if hasattr(self, '_m_ch_vert_code_per_div'):
            return self._m_ch_vert_code_per_div

        _pos = self._io.pos()
        self._io.seek(620)
        self._m_ch_vert_code_per_div = SiglentV3Bin.S4Array4(self._io, self, self._root)
        self._io.seek(_pos)
        return getattr(self, '_m_ch_vert_code_per_div', None)

    @property
    def ch_vert_offset(self):
        if hasattr(self, '_m_ch_vert_offset'):
            return self._m_ch_vert_offset

        _pos = self._io.pos()
        self._io.seek(180)
        self._m_ch_vert_offset = SiglentV3Bin.DataWithUnitArray4(self._io, self, self._root)
        self._io.seek(_pos)
        return getattr(self, '_m_ch_vert_offset', None)

    @property
    def ch_volt_div(self):
        if hasattr(self, '_m_ch_volt_div'):
            return self._m_ch_volt_div

        _pos = self._io.pos()
        self._io.seek(20)
        self._m_ch_volt_div = SiglentV3Bin.DataWithUnitArray4(self._io, self, self._root)
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
        self._m_digital_ch_on = SiglentV3Bin.U4Array16(self._io, self, self._root)
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
        self._m_digital_sample_rate = SiglentV3Bin.DataWithUnit(self._io, self, self._root)
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
    def hori_div_num(self):
        if hasattr(self, '_m_hori_div_num'):
            return self._m_hori_div_num

        _pos = self._io.pos()
        self._io.seek(616)
        self._m_hori_div_num = self._io.read_s4le()
        self._io.seek(_pos)
        return getattr(self, '_m_hori_div_num', None)

    @property
    def math_f_time(self):
        if hasattr(self, '_m_math_f_time'):
            return self._m_math_f_time

        _pos = self._io.pos()
        self._io.seek(988)
        self._m_math_f_time = SiglentV3Bin.F8Array4(self._io, self, self._root)
        self._io.seek(_pos)
        return getattr(self, '_m_math_f_time', None)

    @property
    def math_store_len(self):
        if hasattr(self, '_m_math_store_len'):
            return self._m_math_store_len

        _pos = self._io.pos()
        self._io.seek(972)
        self._m_math_store_len = SiglentV3Bin.U4Array4(self._io, self, self._root)
        self._io.seek(_pos)
        return getattr(self, '_m_math_store_len', None)

    @property
    def math_switch(self):
        if hasattr(self, '_m_math_switch'):
            return self._m_math_switch

        _pos = self._io.pos()
        self._io.seek(636)
        self._m_math_switch = SiglentV3Bin.S4Array4(self._io, self, self._root)
        self._io.seek(_pos)
        return getattr(self, '_m_math_switch', None)

    @property
    def math_vert_code_per_div(self):
        if hasattr(self, '_m_math_vert_code_per_div'):
            return self._m_math_vert_code_per_div

        _pos = self._io.pos()
        self._io.seek(1020)
        self._m_math_vert_code_per_div = self._io.read_s4le()
        self._io.seek(_pos)
        return getattr(self, '_m_math_vert_code_per_div', None)

    @property
    def sample_rate(self):
        if hasattr(self, '_m_sample_rate'):
            return self._m_sample_rate

        _pos = self._io.pos()
        self._io.seek(492)
        self._m_sample_rate = SiglentV3Bin.DataWithUnit(self._io, self, self._root)
        self._io.seek(_pos)
        return getattr(self, '_m_sample_rate', None)

    @property
    def time_delay(self):
        if hasattr(self, '_m_time_delay'):
            return self._m_time_delay

        _pos = self._io.pos()
        self._io.seek(448)
        self._m_time_delay = SiglentV3Bin.DataWithUnit(self._io, self, self._root)
        self._io.seek(_pos)
        return getattr(self, '_m_time_delay', None)

    @property
    def time_div(self):
        if hasattr(self, '_m_time_div'):
            return self._m_time_div

        _pos = self._io.pos()
        self._io.seek(408)
        self._m_time_div = SiglentV3Bin.DataWithUnit(self._io, self, self._root)
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


