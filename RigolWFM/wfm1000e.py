# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild
# type: ignore

import kaitaistruct
from kaitaistruct import KaitaiStruct, KaitaiStream, BytesIO
from enum import IntEnum


if getattr(kaitaistruct, 'API_VERSION', (0, 9)) < (0, 11):
    raise Exception("Incompatible Kaitai Struct Python API: 0.11 or later is required, but you have %s" % (kaitaistruct.__version__))

class Wfm1000e(KaitaiStruct):
    """Rigol DS1102E scope .wmf format abstracted from a python script
    """

    class BandwidthEnum(IntEnum):
        no_limit = 0
        mhz_20 = 1
        mhz_100 = 2
        mhz_200 = 3
        mhz_250 = 4

    class CouplingEnum(IntEnum):
        dc = 0
        ac = 1
        gnd = 2

    class FilterEnum(IntEnum):
        low_pass = 0
        high_pass = 1
        band_pass = 2
        band_reject = 3

    class SourceEnum(IntEnum):
        ch1 = 0
        ch2 = 1
        ext = 2
        ext5 = 3
        ac_line = 5
        dig_ch = 7

    class TriggerModeEnum(IntEnum):
        edge = 0
        pulse = 1
        slope = 2
        video = 3
        alt = 4
        pattern = 5
        duration = 6

    class UnitEnum(IntEnum):
        w = 0
        a = 1
        v = 2
        u = 3
    def __init__(self, _io, _parent=None, _root=None):
        super(Wfm1000e, self).__init__(_io)
        self._parent = _parent
        self._root = _root or self
        self._read()

    def _read(self):
        pass


    def _fetch_instances(self):
        pass
        _ = self.data
        if hasattr(self, '_m_data'):
            pass
            self._m_data._fetch_instances()

        _ = self.header
        if hasattr(self, '_m_header'):
            pass
            self._m_header._fetch_instances()


    class ChannelHeader(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            super(Wfm1000e.ChannelHeader, self).__init__(_io)
            self._parent = _parent
            self._root = _root
            self._read()

        def _read(self):
            self.unknown_0 = self._io.read_u2le()
            self.scale_display = self._io.read_s4le()
            self.shift_display = self._io.read_s2le()
            self.unknown_1 = self._io.read_u1()
            self.unknown_2 = self._io.read_u1()
            self.probe_value = self._io.read_f4le()
            self.invert_disp_val = self._io.read_u1()
            self.enabled_val = self._io.read_u1()
            self.inverted_m_val = self._io.read_u1()
            self.unknown_3 = self._io.read_u1()
            self.scale_measured = self._io.read_s4le()
            self.shift_measured = self._io.read_s2le()


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

            self._m_inverted = (True if self.inverted_m_val != 0 else False)
            return getattr(self, '_m_inverted', None)

        @property
        def unit(self):
            if hasattr(self, '_m_unit'):
                return self._m_unit

            self._m_unit = Wfm1000e.UnitEnum.v
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

            self._m_volt_scale = ((0.0000010 * self.scale_measured) * self.probe_value) / 25.0
            return getattr(self, '_m_volt_scale', None)


    class Header(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            super(Wfm1000e.Header, self).__init__(_io)
            self._parent = _parent
            self._root = _root
            self._read()

        def _read(self):
            self.magic = self._io.read_bytes(4)
            if not self.magic == b"\xA5\xA5\x00\x00":
                raise kaitaistruct.ValidationNotEqualError(b"\xA5\xA5\x00\x00", self.magic, self._io, u"/types/header/seq/0")
            self.unused_1 = self._io.read_u2le()
            self.blank_10 = self._io.read_bytes(10)
            if not self.blank_10 == b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00":
                raise kaitaistruct.ValidationNotEqualError(b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00", self.blank_10, self._io, u"/types/header/seq/2")
            self.adc_mode = self._io.read_u1()
            self.padding_2 = self._io.read_bytes(3)
            if not self.padding_2 == b"\x00\x00\x00":
                raise kaitaistruct.ValidationNotEqualError(b"\x00\x00\x00", self.padding_2, self._io, u"/types/header/seq/4")
            self.roll_stop = self._io.read_u4le()
            self.unused_4 = self._io.read_bytes(4)
            if not self.unused_4 == b"\x00\x00\x00\x00":
                raise kaitaistruct.ValidationNotEqualError(b"\x00\x00\x00\x00", self.unused_4, self._io, u"/types/header/seq/6")
            self.ch1_points_tmp = self._io.read_u4le()
            self.active_channel = self._io.read_u1()
            self.padding_3 = self._io.read_bytes(1)
            if not self.padding_3 == b"\x00":
                raise kaitaistruct.ValidationNotEqualError(b"\x00", self.padding_3, self._io, u"/types/header/seq/9")
            self.ch = []
            for i in range(2):
                self.ch.append(Wfm1000e.ChannelHeader(self._io, self, self._root))

            self.time_offset = self._io.read_u1()
            self.padding_4 = self._io.read_bytes(1)
            if not self.padding_4 == b"\x00":
                raise kaitaistruct.ValidationNotEqualError(b"\x00", self.padding_4, self._io, u"/types/header/seq/12")
            self.time = Wfm1000e.TimeHeader(self._io, self, self._root)
            self.logic = Wfm1000e.LogicAnalyzerHeader(self._io, self, self._root)
            self.trigger_mode = KaitaiStream.resolve_enum(Wfm1000e.TriggerModeEnum, self._io.read_u1())
            self.trigger1 = Wfm1000e.TriggerHeader(self._io, self, self._root)
            self.trigger2 = Wfm1000e.TriggerHeader(self._io, self, self._root)
            self.padding_6 = self._io.read_bytes(9)
            if not self.padding_6 == b"\x00\x00\x00\x00\x00\x00\x00\x00\x00":
                raise kaitaistruct.ValidationNotEqualError(b"\x00\x00\x00\x00\x00\x00\x00\x00\x00", self.padding_6, self._io, u"/types/header/seq/18")
            self.ch2_points_tmp = self._io.read_u4le()
            self.time2 = Wfm1000e.TimeHeader(self._io, self, self._root)
            self.la_sample_rate = self._io.read_f4le()


        def _fetch_instances(self):
            pass
            for i in range(len(self.ch)):
                pass
                self.ch[i]._fetch_instances()

            self.time._fetch_instances()
            self.logic._fetch_instances()
            self.trigger1._fetch_instances()
            self.trigger2._fetch_instances()
            self.time2._fetch_instances()

        @property
        def ch1_points(self):
            """In rolling mode, change the number of valid samples."""
            if hasattr(self, '_m_ch1_points'):
                return self._m_ch1_points

            self._m_ch1_points = (self.ch1_points_tmp - 4 if self.roll_stop == 0 else (self.ch1_points_tmp - self.roll_stop) - 6)
            return getattr(self, '_m_ch1_points', None)

        @property
        def ch1_skip(self):
            """In rolling mode, skip invalid points."""
            if hasattr(self, '_m_ch1_skip'):
                return self._m_ch1_skip

            self._m_ch1_skip = (0 if self.roll_stop == 0 else self.roll_stop + 2)
            return getattr(self, '_m_ch1_skip', None)

        @property
        def ch1_time_offset(self):
            if hasattr(self, '_m_ch1_time_offset'):
                return self._m_ch1_time_offset

            self._m_ch1_time_offset = 1.0E-12 * self.time.offset_measured
            return getattr(self, '_m_ch1_time_offset', None)

        @property
        def ch1_time_scale(self):
            if hasattr(self, '_m_ch1_time_scale'):
                return self._m_ch1_time_scale

            self._m_ch1_time_scale = 1.0E-12 * self.time.scale_measured
            return getattr(self, '_m_ch1_time_scale', None)

        @property
        def ch1_volt_length(self):
            """In rolling mode, skip invalid samples."""
            if hasattr(self, '_m_ch1_volt_length'):
                return self._m_ch1_volt_length

            self._m_ch1_volt_length = self.ch1_points - self.roll_stop
            return getattr(self, '_m_ch1_volt_length', None)

        @property
        def ch2_points(self):
            """Use ch1_points when ch2_points is not written."""
            if hasattr(self, '_m_ch2_points'):
                return self._m_ch2_points

            self._m_ch2_points = (self.ch1_points if  ((self.ch[1].enabled) and (self.ch2_points_tmp == 0))  else self.ch2_points_tmp)
            return getattr(self, '_m_ch2_points', None)

        @property
        def ch2_time_offset(self):
            if hasattr(self, '_m_ch2_time_offset'):
                return self._m_ch2_time_offset

            self._m_ch2_time_offset = (1.0E-12 * self.time2.offset_measured if self.trigger_mode == Wfm1000e.TriggerModeEnum.alt else self.ch1_time_offset)
            return getattr(self, '_m_ch2_time_offset', None)

        @property
        def ch2_time_scale(self):
            if hasattr(self, '_m_ch2_time_scale'):
                return self._m_ch2_time_scale

            self._m_ch2_time_scale = (1.0E-12 * self.time2.scale_measured if self.trigger_mode == Wfm1000e.TriggerModeEnum.alt else self.ch1_time_scale)
            return getattr(self, '_m_ch2_time_scale', None)

        @property
        def ch2_volt_length(self):
            """In rolling mode, skip invalid samples."""
            if hasattr(self, '_m_ch2_volt_length'):
                return self._m_ch2_volt_length

            self._m_ch2_volt_length = self.ch2_points - self.roll_stop
            return getattr(self, '_m_ch2_volt_length', None)

        @property
        def sample_rate_hz(self):
            if hasattr(self, '_m_sample_rate_hz'):
                return self._m_sample_rate_hz

            self._m_sample_rate_hz = self.time.sample_rate_hz
            return getattr(self, '_m_sample_rate_hz', None)

        @property
        def seconds_per_point(self):
            if hasattr(self, '_m_seconds_per_point'):
                return self._m_seconds_per_point

            self._m_seconds_per_point = 1 / self.sample_rate_hz
            return getattr(self, '_m_seconds_per_point', None)


    class LogicAnalyzerHeader(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            super(Wfm1000e.LogicAnalyzerHeader, self).__init__(_io)
            self._parent = _parent
            self._root = _root
            self._read()

        def _read(self):
            self.unused = self._io.read_bits_int_be(7)
            self.enabled = self._io.read_bits_int_be(1) != 0
            self.active_channel = self._io.read_u1()
            self.enabled_channels = self._io.read_u2le()
            self.position = self._io.read_bytes(16)
            self.group8to15size = self._io.read_u1()
            self.group0to7size = self._io.read_u1()


        def _fetch_instances(self):
            pass


    class RawData(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            super(Wfm1000e.RawData, self).__init__(_io)
            self._parent = _parent
            self._root = _root
            self._read()

        def _read(self):
            if self._root.header.ch[0].enabled:
                pass
                self.ch1 = self._io.read_bytes(self._root.header.ch1_points)

            if self._root.header.ch[0].enabled:
                pass
                self.roll_stop_padding1 = self._io.read_bytes(self._root.header.ch1_skip)

            if self._root.header.ch[0].enabled:
                pass
                self.sentinel_between_datasets = self._io.read_u4le()

            if self._root.header.ch[1].enabled:
                pass
                self.ch2 = self._io.read_bytes(self._root.header.ch2_points)

            if self._root.header.ch[1].enabled:
                pass
                self.roll_stop_padding2 = self._io.read_bytes(self._root.header.ch1_skip)

            if self._root.header.ch[1].enabled:
                pass
                self.sentinel_between_datasets2 = self._io.read_u4le()

            self.logic = []
            for i in range((self._root.header.ch1_points if self._root.header.logic.enabled else 0)):
                self.logic.append(self._io.read_u2le())



        def _fetch_instances(self):
            pass
            if self._root.header.ch[0].enabled:
                pass

            if self._root.header.ch[0].enabled:
                pass

            if self._root.header.ch[0].enabled:
                pass

            if self._root.header.ch[1].enabled:
                pass

            if self._root.header.ch[1].enabled:
                pass

            if self._root.header.ch[1].enabled:
                pass

            for i in range(len(self.logic)):
                pass



    class TimeHeader(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            super(Wfm1000e.TimeHeader, self).__init__(_io)
            self._parent = _parent
            self._root = _root
            self._read()

        def _read(self):
            self.scale_display = self._io.read_s8le()
            self.offset_display = self._io.read_s8le()
            self.sample_rate_hz = self._io.read_f4le()
            self.scale_measured = self._io.read_s8le()
            self.offset_measured = self._io.read_s8le()


        def _fetch_instances(self):
            pass


    class TriggerHeader(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            super(Wfm1000e.TriggerHeader, self).__init__(_io)
            self._parent = _parent
            self._root = _root
            self._read()

        def _read(self):
            self.mode = KaitaiStream.resolve_enum(Wfm1000e.TriggerModeEnum, self._io.read_u1())
            self.source = KaitaiStream.resolve_enum(Wfm1000e.SourceEnum, self._io.read_u1())
            self.coupling = self._io.read_u1()
            self.sweep = self._io.read_u1()
            self.padding_1 = self._io.read_bytes(1)
            if not self.padding_1 == b"\x00":
                raise kaitaistruct.ValidationNotEqualError(b"\x00", self.padding_1, self._io, u"/types/trigger_header/seq/4")
            self.sens = self._io.read_f4le()
            self.holdoff = self._io.read_f4le()
            self.level = self._io.read_f4le()
            self.direct = self._io.read_u1()
            self.pulse_type = self._io.read_u1()
            self.padding_2 = self._io.read_bytes(2)
            if not self.padding_2 == b"\x00\x00":
                raise kaitaistruct.ValidationNotEqualError(b"\x00\x00", self.padding_2, self._io, u"/types/trigger_header/seq/10")
            self.pulse_width = self._io.read_f4le()
            self.slope_type = self._io.read_u1()
            self.padding_3 = self._io.read_bytes(3)
            if not self.padding_3 == b"\x00\x00\x00":
                raise kaitaistruct.ValidationNotEqualError(b"\x00\x00\x00", self.padding_3, self._io, u"/types/trigger_header/seq/13")
            self.lower = self._io.read_f4le()
            self.slope_width = self._io.read_f4le()
            self.video_pol = self._io.read_u1()
            self.video_sync = self._io.read_u1()
            self.video_std = self._io.read_u1()


        def _fetch_instances(self):
            pass


    @property
    def data(self):
        if hasattr(self, '_m_data'):
            return self._m_data

        _pos = self._io.pos()
        self._io.seek(276)
        self._m_data = Wfm1000e.RawData(self._io, self, self._root)
        self._io.seek(_pos)
        return getattr(self, '_m_data', None)

    @property
    def header(self):
        if hasattr(self, '_m_header'):
            return self._m_header

        _pos = self._io.pos()
        self._io.seek(0)
        self._m_header = Wfm1000e.Header(self._io, self, self._root)
        self._io.seek(_pos)
        return getattr(self, '_m_header', None)


