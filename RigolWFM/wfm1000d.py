# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild

import kaitaistruct
from kaitaistruct import KaitaiStruct, KaitaiStream, BytesIO
from enum import Enum


if getattr(kaitaistruct, 'API_VERSION', (0, 9)) < (0, 9):
    raise Exception("Incompatible Kaitai Struct Python API: 0.9 or later is required, but you have %s" % (kaitaistruct.__version__))

class Wfm1000d(KaitaiStruct):
    """Rigol DS1102D .wmf format abstracted from a Matlab script with the addition
    of a few fields found in a Pascal program.  Neither program really examines
    the header closely (meaning that they skip 26 bytes).
    
    .. seealso::
       The Matlab script is from https://www.mathworks.com/matlabcentral/fileexchange/18999-read-binary-rigol-waveforms The Pascal program is from https://sourceforge.net/projects/wfmreader/
    """

    class TriggerSourceEnum(Enum):
        ch1 = 0
        ch2 = 1
        ext = 2
        ext5 = 3
        ac_line = 5
        dig_ch = 7

    class TriggerModeEnum(Enum):
        edge = 0
        pulse = 1
        slope = 2
        video = 3
        alt = 4
        pattern = 5
        duration = 6

    class MachineModeEnum(Enum):
        ds1000b = 0
        ds1000c = 1
        ds1000e = 2
        ds1000z = 3
        ds2000 = 4
        ds4000 = 5
        ds6000 = 6

    class UnitEnum(Enum):
        w = 0
        a = 1
        v = 2
        u = 3
    def __init__(self, _io, _parent=None, _root=None):
        self._io = _io
        self._parent = _parent
        self._root = _root if _root else self
        self._read()

    def _read(self):
        pass

    class Header(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.magic = self._io.read_bytes(4)
            if not self.magic == b"\xA5\xA5\x00\x00":
                raise kaitaistruct.ValidationNotEqualError(b"\xA5\xA5\x00\x00", self.magic, self._io, u"/types/header/seq/0")
            self.unknown_1 = []
            for i in range(6):
                self.unknown_1.append(self._io.read_u4le())

            self.points = self._io.read_u4le()
            self.active_channel = self._io.read_u1()
            self.unknown_2a = self._io.read_bytes(3)
            self.ch = []
            for i in range(2):
                self.ch.append(Wfm1000d.ChannelHeader(self._io, self, self._root))

            self.time_scale = self._io.read_u8le()
            self.time_offset = self._io.read_s8le()
            self.sample_rate_hz = self._io.read_f4le()
            self.unknown_3 = []
            for i in range(9):
                self.unknown_3.append(self._io.read_u4le())

            self.unknown_4 = self._io.read_u2le()
            self.trigger_mode = KaitaiStream.resolve_enum(Wfm1000d.TriggerModeEnum, self._io.read_u1())
            self.unknown_6 = self._io.read_u1()
            self.trigger_source = KaitaiStream.resolve_enum(Wfm1000d.TriggerSourceEnum, self._io.read_u1())

        @property
        def seconds_per_point(self):
            if hasattr(self, '_m_seconds_per_point'):
                return self._m_seconds_per_point

            self._m_seconds_per_point = (1.0 / self.sample_rate_hz)
            return getattr(self, '_m_seconds_per_point', None)


    class ChannelHeader(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.scale_display = self._io.read_s4le()
            self.shift_display = self._io.read_s2le()
            self.unknown_1 = self._io.read_u1()
            self.unknown_2 = self._io.read_u1()
            self.probe_value = self._io.read_f4le()
            self.invert_disp_val = self._io.read_u1()
            self.enabled_val = self._io.read_u1()
            self.invert_m_val = self._io.read_u1()
            self.unknown_3 = self._io.read_u1()
            self.scale_measured = self._io.read_s4le()
            self.shift_measured = self._io.read_s2le()
            self.unknown_3a = self._io.read_u2le()

        @property
        def unit(self):
            if hasattr(self, '_m_unit'):
                return self._m_unit

            self._m_unit = Wfm1000d.UnitEnum.v
            return getattr(self, '_m_unit', None)

        @property
        def time_offset(self):
            if hasattr(self, '_m_time_offset'):
                return self._m_time_offset

            self._m_time_offset = self._root.header.time_offset
            return getattr(self, '_m_time_offset', None)

        @property
        def inverted(self):
            if hasattr(self, '_m_inverted'):
                return self._m_inverted

            self._m_inverted = (True if self.invert_m_val != 0 else False)
            return getattr(self, '_m_inverted', None)

        @property
        def time_scale(self):
            if hasattr(self, '_m_time_scale'):
                return self._m_time_scale

            self._m_time_scale = self._root.header.time_scale
            return getattr(self, '_m_time_scale', None)

        @property
        def volt_offset(self):
            if hasattr(self, '_m_volt_offset'):
                return self._m_volt_offset

            self._m_volt_offset = (self.shift_measured * self.volt_scale)
            return getattr(self, '_m_volt_offset', None)

        @property
        def volt_per_division(self):
            if hasattr(self, '_m_volt_per_division'):
                return self._m_volt_per_division

            self._m_volt_per_division = ((-0.0000010 * self.scale_measured) if self.inverted else (0.0000010 * self.scale_measured))
            return getattr(self, '_m_volt_per_division', None)

        @property
        def volt_scale(self):
            if hasattr(self, '_m_volt_scale'):
                return self._m_volt_scale

            self._m_volt_scale = (self.volt_per_division / 25.0)
            return getattr(self, '_m_volt_scale', None)

        @property
        def enabled(self):
            if hasattr(self, '_m_enabled'):
                return self._m_enabled

            self._m_enabled = (True if self.enabled_val != 0 else False)
            return getattr(self, '_m_enabled', None)


    class RawData(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            if self._root.header.ch[0].enabled:
                self.ch1 = self._io.read_bytes(self._root.header.points)

            if self._root.header.ch[1].enabled:
                self.ch2 = self._io.read_bytes(self._root.header.points)



    @property
    def header(self):
        if hasattr(self, '_m_header'):
            return self._m_header

        _pos = self._io.pos()
        self._io.seek(0)
        self._m_header = Wfm1000d.Header(self._io, self, self._root)
        self._io.seek(_pos)
        return getattr(self, '_m_header', None)

    @property
    def data(self):
        if hasattr(self, '_m_data'):
            return self._m_data

        _pos = self._io.pos()
        self._io.seek(272)
        self._m_data = Wfm1000d.RawData(self._io, self, self._root)
        self._io.seek(_pos)
        return getattr(self, '_m_data', None)


