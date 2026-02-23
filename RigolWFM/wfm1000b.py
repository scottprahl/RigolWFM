# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild
# type: ignore

import kaitaistruct
from kaitaistruct import KaitaiStruct, KaitaiStream, BytesIO
from enum import IntEnum


if getattr(kaitaistruct, 'API_VERSION', (0, 9)) < (0, 11):
    raise Exception("Incompatible Kaitai Struct Python API: 0.11 or later is required, but you have %s" % (kaitaistruct.__version__))

class Wfm1000b(KaitaiStruct):
    """This was put together based on an excel header list of unknown provenance.
    It has been tested with a handful of different files.  The offset to the
    data seems correct and the channel coupling is untested.
    """

    class MachineModeEnum(IntEnum):
        ds1000b = 0
        ds1000c = 1
        ds1000e = 2
        ds1000z = 3
        ds2000 = 4
        ds4000 = 5
        ds6000 = 6

    class TriggerModeEnum(IntEnum):
        edge = 0
        pulse = 1
        slope = 2
        video = 3
        alt = 4
        pattern = 5
        duration = 6

    class TriggerSourceEnum(IntEnum):
        ch1 = 0
        ch2 = 1
        ext = 2
        ext5 = 3
        ac_line = 5
        dig_ch = 7

    class UnitEnum(IntEnum):
        w = 0
        a = 1
        v = 2
        u = 3
    def __init__(self, _io, _parent=None, _root=None):
        super(Wfm1000b, self).__init__(_io)
        self._parent = _parent
        self._root = _root or self
        self._read()

    def _read(self):
        pass


    def _fetch_instances(self):
        pass
        _ = self.header
        if hasattr(self, '_m_header'):
            pass
            self._m_header._fetch_instances()


    class ChannelHeader(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            super(Wfm1000b.ChannelHeader, self).__init__(_io)
            self._parent = _parent
            self._root = _root
            self._read()

        def _read(self):
            self.scale_display = self._io.read_s4le()
            self.shift_display = self._io.read_s2le()
            self.unknown1 = self._io.read_bytes(2)
            self.probe_value = self._io.read_f4le()
            self.probe_type = self._io.read_s1()
            self.invert_disp_val = self._io.read_u1()
            self.enabled_val = self._io.read_u1()
            self.invert_m_val = self._io.read_u1()
            self.scale_measured = self._io.read_s4le()
            self.shift_measured = self._io.read_s2le()
            self.time_delayed = self._io.read_u1()
            self.unknown2 = self._io.read_bytes(1)


        def _fetch_instances(self):
            pass

        @property
        def enabled(self):
            if hasattr(self, '_m_enabled'):
                return self._m_enabled

            self._m_enabled = (True if self.enabled_val != 0 else False)
            return getattr(self, '_m_enabled', None)

        @property
        def inverted(self):
            if hasattr(self, '_m_inverted'):
                return self._m_inverted

            self._m_inverted = (True if self.invert_m_val != 0 else False)
            return getattr(self, '_m_inverted', None)

        @property
        def time_offset(self):
            if hasattr(self, '_m_time_offset'):
                return self._m_time_offset

            self._m_time_offset = self._root.header.time_offset
            return getattr(self, '_m_time_offset', None)

        @property
        def time_scale(self):
            if hasattr(self, '_m_time_scale'):
                return self._m_time_scale

            self._m_time_scale = self._root.header.time_scale
            return getattr(self, '_m_time_scale', None)

        @property
        def unit(self):
            if hasattr(self, '_m_unit'):
                return self._m_unit

            self._m_unit = Wfm1000b.UnitEnum.v
            return getattr(self, '_m_unit', None)

        @property
        def volt_offset(self):
            if hasattr(self, '_m_volt_offset'):
                return self._m_volt_offset

            self._m_volt_offset = self.shift_measured * self.volt_scale
            return getattr(self, '_m_volt_offset', None)

        @property
        def volt_per_division(self):
            if hasattr(self, '_m_volt_per_division'):
                return self._m_volt_per_division

            self._m_volt_per_division = ((-0.0000010 * self.scale_measured) * self.probe_value if self.inverted else (0.0000010 * self.scale_measured) * self.probe_value)
            return getattr(self, '_m_volt_per_division', None)

        @property
        def volt_scale(self):
            if hasattr(self, '_m_volt_scale'):
                return self._m_volt_scale

            self._m_volt_scale = self.volt_per_division / 25.0
            return getattr(self, '_m_volt_scale', None)


    class Header(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            super(Wfm1000b.Header, self).__init__(_io)
            self._parent = _parent
            self._root = _root
            self._read()

        def _read(self):
            self.magic = self._io.read_bytes(4)
            if not self.magic == b"\xA5\xA5\xA4\x01":
                raise kaitaistruct.ValidationNotEqualError(b"\xA5\xA5\xA4\x01", self.magic, self._io, u"/types/header/seq/0")
            self.scopetype = (KaitaiStream.bytes_terminate(self._io.read_bytes(8), 0, False)).decode(u"UTF-8")
            self.unknown_1 = self._io.read_bytes(44)
            self.adcmode = self._io.read_u1()
            self.unknown_2 = self._io.read_bytes(3)
            self.points = self._io.read_u4le()
            self.active_channel = self._io.read_u1()
            self.unknown_3 = self._io.read_bytes(3)
            self.ch = []
            for i in range(4):
                self.ch.append(Wfm1000b.ChannelHeader(self._io, self, self._root))

            self.time_scale = self._io.read_u8le()
            self.time_offset = self._io.read_s8le()
            self.sample_rate_hz = self._io.read_f4le()
            self.time_scale_stop = self._io.read_u8le()
            self.time_scale_offset = self._io.read_s8le()
            self.unknown_4 = []
            for i in range(4):
                self.unknown_4.append(self._io.read_u4le())

            self.coupling_ch12 = self._io.read_u1()
            self.coupling_ch34 = self._io.read_u1()
            self.unknown_5 = self._io.read_bytes(4)
            self.trigger_mode = KaitaiStream.resolve_enum(Wfm1000b.TriggerModeEnum, self._io.read_u1())
            self.unknown_6 = self._io.read_u1()
            self.trigger_source = KaitaiStream.resolve_enum(Wfm1000b.TriggerSourceEnum, self._io.read_u1())


        def _fetch_instances(self):
            pass
            for i in range(len(self.ch)):
                pass
                self.ch[i]._fetch_instances()

            for i in range(len(self.unknown_4)):
                pass

            _ = self.ch1
            if hasattr(self, '_m_ch1'):
                pass

            _ = self.ch2
            if hasattr(self, '_m_ch2'):
                pass

            _ = self.ch3
            if hasattr(self, '_m_ch3'):
                pass

            _ = self.ch4
            if hasattr(self, '_m_ch4'):
                pass


        @property
        def ch1(self):
            if hasattr(self, '_m_ch1'):
                return self._m_ch1

            if self.ch[0].enabled:
                pass
                io = self._root._io
                _pos = io.pos()
                io.seek(420)
                self._m_ch1 = io.read_bytes(self.len_ch1)
                io.seek(_pos)

            return getattr(self, '_m_ch1', None)

        @property
        def ch2(self):
            if hasattr(self, '_m_ch2'):
                return self._m_ch2

            if self.ch[1].enabled:
                pass
                io = self._root._io
                _pos = io.pos()
                io.seek(420 + self._root.header.points)
                self._m_ch2 = io.read_bytes(self.len_ch2)
                io.seek(_pos)

            return getattr(self, '_m_ch2', None)

        @property
        def ch3(self):
            if hasattr(self, '_m_ch3'):
                return self._m_ch3

            if self.ch[2].enabled:
                pass
                io = self._root._io
                _pos = io.pos()
                io.seek(420 + self._root.header.points * 2)
                self._m_ch3 = io.read_bytes(self.len_ch3)
                io.seek(_pos)

            return getattr(self, '_m_ch3', None)

        @property
        def ch4(self):
            if hasattr(self, '_m_ch4'):
                return self._m_ch4

            if self.ch[3].enabled:
                pass
                io = self._root._io
                _pos = io.pos()
                io.seek(420 + self._root.header.points * 3)
                self._m_ch4 = io.read_bytes(self.len_ch4)
                io.seek(_pos)

            return getattr(self, '_m_ch4', None)

        @property
        def len_ch1(self):
            if hasattr(self, '_m_len_ch1'):
                return self._m_len_ch1

            self._m_len_ch1 = (self.points if self.ch[0].enabled else 0)
            return getattr(self, '_m_len_ch1', None)

        @property
        def len_ch2(self):
            if hasattr(self, '_m_len_ch2'):
                return self._m_len_ch2

            self._m_len_ch2 = (self.points if self.ch[1].enabled else 0)
            return getattr(self, '_m_len_ch2', None)

        @property
        def len_ch3(self):
            if hasattr(self, '_m_len_ch3'):
                return self._m_len_ch3

            self._m_len_ch3 = (self.points if self.ch[2].enabled else 0)
            return getattr(self, '_m_len_ch3', None)

        @property
        def len_ch4(self):
            if hasattr(self, '_m_len_ch4'):
                return self._m_len_ch4

            self._m_len_ch4 = (self.points if self.ch[3].enabled else 0)
            return getattr(self, '_m_len_ch4', None)

        @property
        def seconds_per_point(self):
            if hasattr(self, '_m_seconds_per_point'):
                return self._m_seconds_per_point

            self._m_seconds_per_point = 1.0 / self.sample_rate_hz
            return getattr(self, '_m_seconds_per_point', None)


    @property
    def header(self):
        if hasattr(self, '_m_header'):
            return self._m_header

        _pos = self._io.pos()
        self._io.seek(0)
        self._m_header = Wfm1000b.Header(self._io, self, self._root)
        self._io.seek(_pos)
        return getattr(self, '_m_header', None)


