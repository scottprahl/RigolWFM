# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild
# type: ignore

import kaitaistruct
from kaitaistruct import KaitaiStruct, KaitaiStream, BytesIO


if getattr(kaitaistruct, 'API_VERSION', (0, 9)) < (0, 11):
    raise Exception("Incompatible Kaitai Struct Python API: 0.11 or later is required, but you have %s" % (kaitaistruct.__version__))

class SiglentV4Bin(KaitaiStruct):
    """Siglent waveform binary layout documented as "Binary Format V4.0".
    
    V4.0 increases the header size to 4 KiB, adds a data-offset field, and
    expands the analog channel metadata to support up to eight channels plus
    additional memory/zoom parameters.
    
    Sources used for this KSY binary format:
    `docs/vendors/siglent/siglent-binaries.pdf` plus the synthetic regression
    builder in `tests/test_siglent.py`.
    
    Tested file formats: the synthetic `Binary Format V4.0` fixture in
    `tests/test_siglent.py`, exercised through revision detection, low-level
    Kaitai parsing, and normalized waveform loading.
    
    Oscilloscope models this format may apply to: Siglent instruments that write
    `Binary Format V4.0`; the checked-in tests do not yet narrow this revision to
    a smaller verified model list.
    """
    def __init__(self, _io, _parent=None, _root=None):
        super(SiglentV4Bin, self).__init__(_io)
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

        _ = self.ch_on_1_4
        if hasattr(self, '_m_ch_on_1_4'):
            pass
            self._m_ch_on_1_4._fetch_instances()

        _ = self.ch_on_5_8
        if hasattr(self, '_m_ch_on_5_8'):
            pass
            self._m_ch_on_5_8._fetch_instances()

        _ = self.ch_probe_1_4
        if hasattr(self, '_m_ch_probe_1_4'):
            pass
            self._m_ch_probe_1_4._fetch_instances()

        _ = self.ch_probe_5_8
        if hasattr(self, '_m_ch_probe_5_8'):
            pass
            self._m_ch_probe_5_8._fetch_instances()

        _ = self.ch_vert_code_per_div_1_4
        if hasattr(self, '_m_ch_vert_code_per_div_1_4'):
            pass
            self._m_ch_vert_code_per_div_1_4._fetch_instances()

        _ = self.ch_vert_code_per_div_5_8
        if hasattr(self, '_m_ch_vert_code_per_div_5_8'):
            pass
            self._m_ch_vert_code_per_div_5_8._fetch_instances()

        _ = self.ch_vert_offset_1_4
        if hasattr(self, '_m_ch_vert_offset_1_4'):
            pass
            self._m_ch_vert_offset_1_4._fetch_instances()

        _ = self.ch_vert_offset_5_8
        if hasattr(self, '_m_ch_vert_offset_5_8'):
            pass
            self._m_ch_vert_offset_5_8._fetch_instances()

        _ = self.ch_volt_div_1_4
        if hasattr(self, '_m_ch_volt_div_1_4'):
            pass
            self._m_ch_volt_div_1_4._fetch_instances()

        _ = self.ch_volt_div_5_8
        if hasattr(self, '_m_ch_volt_div_5_8'):
            pass
            self._m_ch_volt_div_5_8._fetch_instances()

        _ = self.data_offset_byte
        if hasattr(self, '_m_data_offset_byte'):
            pass

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
            super(SiglentV4Bin.DataWithUnit, self).__init__(_io)
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
            super(SiglentV4Bin.DataWithUnitArray4, self).__init__(_io)
            self._parent = _parent
            self._root = _root
            self._read()

        def _read(self):
            self.entries = []
            for i in range(4):
                self.entries.append(SiglentV4Bin.DataWithUnit(self._io, self, self._root))



        def _fetch_instances(self):
            pass
            for i in range(len(self.entries)):
                pass
                self.entries[i]._fetch_instances()



    class F8Array4(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            super(SiglentV4Bin.F8Array4, self).__init__(_io)
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
            super(SiglentV4Bin.S4Array4, self).__init__(_io)
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
            super(SiglentV4Bin.U4Array16, self).__init__(_io)
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
            super(SiglentV4Bin.U4Array4, self).__init__(_io)
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
        self._io.seek(613)
        self._m_byte_order = self._io.read_u1()
        self._io.seek(_pos)
        return getattr(self, '_m_byte_order', None)

    @property
    def ch_on_1_4(self):
        if hasattr(self, '_m_ch_on_1_4'):
            return self._m_ch_on_1_4

        _pos = self._io.pos()
        self._io.seek(8)
        self._m_ch_on_1_4 = SiglentV4Bin.S4Array4(self._io, self, self._root)
        self._io.seek(_pos)
        return getattr(self, '_m_ch_on_1_4', None)

    @property
    def ch_on_5_8(self):
        if hasattr(self, '_m_ch_on_5_8'):
            return self._m_ch_on_5_8

        _pos = self._io.pos()
        self._io.seek(1028)
        self._m_ch_on_5_8 = SiglentV4Bin.S4Array4(self._io, self, self._root)
        self._io.seek(_pos)
        return getattr(self, '_m_ch_on_5_8', None)

    @property
    def ch_probe_1_4(self):
        if hasattr(self, '_m_ch_probe_1_4'):
            return self._m_ch_probe_1_4

        _pos = self._io.pos()
        self._io.seek(580)
        self._m_ch_probe_1_4 = SiglentV4Bin.F8Array4(self._io, self, self._root)
        self._io.seek(_pos)
        return getattr(self, '_m_ch_probe_1_4', None)

    @property
    def ch_probe_5_8(self):
        if hasattr(self, '_m_ch_probe_5_8'):
            return self._m_ch_probe_5_8

        _pos = self._io.pos()
        self._io.seek(1364)
        self._m_ch_probe_5_8 = SiglentV4Bin.F8Array4(self._io, self, self._root)
        self._io.seek(_pos)
        return getattr(self, '_m_ch_probe_5_8', None)

    @property
    def ch_vert_code_per_div_1_4(self):
        if hasattr(self, '_m_ch_vert_code_per_div_1_4'):
            return self._m_ch_vert_code_per_div_1_4

        _pos = self._io.pos()
        self._io.seek(624)
        self._m_ch_vert_code_per_div_1_4 = SiglentV4Bin.S4Array4(self._io, self, self._root)
        self._io.seek(_pos)
        return getattr(self, '_m_ch_vert_code_per_div_1_4', None)

    @property
    def ch_vert_code_per_div_5_8(self):
        if hasattr(self, '_m_ch_vert_code_per_div_5_8'):
            return self._m_ch_vert_code_per_div_5_8

        _pos = self._io.pos()
        self._io.seek(1396)
        self._m_ch_vert_code_per_div_5_8 = SiglentV4Bin.S4Array4(self._io, self, self._root)
        self._io.seek(_pos)
        return getattr(self, '_m_ch_vert_code_per_div_5_8', None)

    @property
    def ch_vert_offset_1_4(self):
        if hasattr(self, '_m_ch_vert_offset_1_4'):
            return self._m_ch_vert_offset_1_4

        _pos = self._io.pos()
        self._io.seek(184)
        self._m_ch_vert_offset_1_4 = SiglentV4Bin.DataWithUnitArray4(self._io, self, self._root)
        self._io.seek(_pos)
        return getattr(self, '_m_ch_vert_offset_1_4', None)

    @property
    def ch_vert_offset_5_8(self):
        if hasattr(self, '_m_ch_vert_offset_5_8'):
            return self._m_ch_vert_offset_5_8

        _pos = self._io.pos()
        self._io.seek(1204)
        self._m_ch_vert_offset_5_8 = SiglentV4Bin.DataWithUnitArray4(self._io, self, self._root)
        self._io.seek(_pos)
        return getattr(self, '_m_ch_vert_offset_5_8', None)

    @property
    def ch_volt_div_1_4(self):
        if hasattr(self, '_m_ch_volt_div_1_4'):
            return self._m_ch_volt_div_1_4

        _pos = self._io.pos()
        self._io.seek(24)
        self._m_ch_volt_div_1_4 = SiglentV4Bin.DataWithUnitArray4(self._io, self, self._root)
        self._io.seek(_pos)
        return getattr(self, '_m_ch_volt_div_1_4', None)

    @property
    def ch_volt_div_5_8(self):
        if hasattr(self, '_m_ch_volt_div_5_8'):
            return self._m_ch_volt_div_5_8

        _pos = self._io.pos()
        self._io.seek(1044)
        self._m_ch_volt_div_5_8 = SiglentV4Bin.DataWithUnitArray4(self._io, self, self._root)
        self._io.seek(_pos)
        return getattr(self, '_m_ch_volt_div_5_8', None)

    @property
    def data_offset_byte(self):
        if hasattr(self, '_m_data_offset_byte'):
            return self._m_data_offset_byte

        _pos = self._io.pos()
        self._io.seek(4)
        self._m_data_offset_byte = self._io.read_u4le()
        self._io.seek(_pos)
        return getattr(self, '_m_data_offset_byte', None)

    @property
    def data_width(self):
        if hasattr(self, '_m_data_width'):
            return self._m_data_width

        _pos = self._io.pos()
        self._io.seek(612)
        self._m_data_width = self._io.read_u1()
        self._io.seek(_pos)
        return getattr(self, '_m_data_width', None)

    @property
    def digital_ch_on(self):
        if hasattr(self, '_m_digital_ch_on'):
            return self._m_digital_ch_on

        _pos = self._io.pos()
        self._io.seek(348)
        self._m_digital_ch_on = SiglentV4Bin.U4Array16(self._io, self, self._root)
        self._io.seek(_pos)
        return getattr(self, '_m_digital_ch_on', None)

    @property
    def digital_on(self):
        if hasattr(self, '_m_digital_on'):
            return self._m_digital_on

        _pos = self._io.pos()
        self._io.seek(344)
        self._m_digital_on = self._io.read_u4le()
        self._io.seek(_pos)
        return getattr(self, '_m_digital_on', None)

    @property
    def digital_sample_rate(self):
        if hasattr(self, '_m_digital_sample_rate'):
            return self._m_digital_sample_rate

        _pos = self._io.pos()
        self._io.seek(540)
        self._m_digital_sample_rate = SiglentV4Bin.DataWithUnit(self._io, self, self._root)
        self._io.seek(_pos)
        return getattr(self, '_m_digital_sample_rate', None)

    @property
    def digital_wave_length(self):
        if hasattr(self, '_m_digital_wave_length'):
            return self._m_digital_wave_length

        _pos = self._io.pos()
        self._io.seek(536)
        self._m_digital_wave_length = self._io.read_u4le()
        self._io.seek(_pos)
        return getattr(self, '_m_digital_wave_length', None)

    @property
    def hori_div_num(self):
        if hasattr(self, '_m_hori_div_num'):
            return self._m_hori_div_num

        _pos = self._io.pos()
        self._io.seek(620)
        self._m_hori_div_num = self._io.read_s4le()
        self._io.seek(_pos)
        return getattr(self, '_m_hori_div_num', None)

    @property
    def math_f_time(self):
        if hasattr(self, '_m_math_f_time'):
            return self._m_math_f_time

        _pos = self._io.pos()
        self._io.seek(992)
        self._m_math_f_time = SiglentV4Bin.F8Array4(self._io, self, self._root)
        self._io.seek(_pos)
        return getattr(self, '_m_math_f_time', None)

    @property
    def math_store_len(self):
        if hasattr(self, '_m_math_store_len'):
            return self._m_math_store_len

        _pos = self._io.pos()
        self._io.seek(976)
        self._m_math_store_len = SiglentV4Bin.U4Array4(self._io, self, self._root)
        self._io.seek(_pos)
        return getattr(self, '_m_math_store_len', None)

    @property
    def math_switch(self):
        if hasattr(self, '_m_math_switch'):
            return self._m_math_switch

        _pos = self._io.pos()
        self._io.seek(640)
        self._m_math_switch = SiglentV4Bin.S4Array4(self._io, self, self._root)
        self._io.seek(_pos)
        return getattr(self, '_m_math_switch', None)

    @property
    def math_vert_code_per_div(self):
        if hasattr(self, '_m_math_vert_code_per_div'):
            return self._m_math_vert_code_per_div

        _pos = self._io.pos()
        self._io.seek(1024)
        self._m_math_vert_code_per_div = self._io.read_s4le()
        self._io.seek(_pos)
        return getattr(self, '_m_math_vert_code_per_div', None)

    @property
    def sample_rate(self):
        if hasattr(self, '_m_sample_rate'):
            return self._m_sample_rate

        _pos = self._io.pos()
        self._io.seek(496)
        self._m_sample_rate = SiglentV4Bin.DataWithUnit(self._io, self, self._root)
        self._io.seek(_pos)
        return getattr(self, '_m_sample_rate', None)

    @property
    def time_delay(self):
        if hasattr(self, '_m_time_delay'):
            return self._m_time_delay

        _pos = self._io.pos()
        self._io.seek(452)
        self._m_time_delay = SiglentV4Bin.DataWithUnit(self._io, self, self._root)
        self._io.seek(_pos)
        return getattr(self, '_m_time_delay', None)

    @property
    def time_div(self):
        if hasattr(self, '_m_time_div'):
            return self._m_time_div

        _pos = self._io.pos()
        self._io.seek(412)
        self._m_time_div = SiglentV4Bin.DataWithUnit(self._io, self, self._root)
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
        self._io.seek(self.data_offset_byte)
        self._m_wave_data = self._io.read_bytes(self._io.size() - self.data_offset_byte)
        self._io.seek(_pos)
        return getattr(self, '_m_wave_data', None)

    @property
    def wave_length(self):
        if hasattr(self, '_m_wave_length'):
            return self._m_wave_length

        _pos = self._io.pos()
        self._io.seek(492)
        self._m_wave_length = self._io.read_u4le()
        self._io.seek(_pos)
        return getattr(self, '_m_wave_length', None)


