# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild

from pkg_resources import parse_version
from kaitaistruct import __version__ as ks_version, KaitaiStruct, KaitaiStream, BytesIO
from enum import Enum


if parse_version(ks_version) < parse_version('0.7'):
    raise Exception("Incompatible Kaitai Struct Python API: 0.7 or later is required, but you have %s" % (ks_version))

class Wfm1000e(KaitaiStruct):
    """Rigol DS1102E scope .wmf format abstracted from a python script
    """

    class UnitEnum(Enum):
        w = 0
        a = 1
        v = 2
        u = 3

    class TriggerModeEnum(Enum):
        edge = 0
        pulse = 1
        slope = 2
        video = 3
        alt = 4
        pattern = 5
        duration = 6

    class SourceEnum(Enum):
        ch1 = 0
        ch2 = 1
        ext = 2
        ext5 = 3
        ac_line = 5
        dig_ch = 7

    class FilterEnum(Enum):
        low_pass = 0
        high_pass = 1
        band_pass = 2
        band_reject = 3

    class BandwidthEnum(Enum):
        no_limit = 0
        mhz_20 = 1
        mhz_100 = 2
        mhz_200 = 3
        mhz_250 = 4

    class CouplingEnum(Enum):
        dc = 0
        ac = 1
        gnd = 2
    def __init__(self, _io, _parent=None, _root=None):
        self._io = _io
        self._parent = _parent
        self._root = _root if _root else self
        self._read()

    def _read(self):
        pass

    class TimeHeader(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.scale_display = self._io.read_s8le()
            self.offset_display = self._io.read_s8le()
            self.sample_rate_hz = self._io.read_f4le()
            self.scale_measured = self._io.read_s8le()
            self.offset_measured = self._io.read_s8le()


    class RawData(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            if self._root.header.ch[0].enabled:
                self.ch1 = [None] * (self._root.header.ch1_points)
                for i in range(self._root.header.ch1_points):
                    self.ch1[i] = self._io.read_u1()


            if self._root.header.ch[0].enabled:
                self.roll_stop_padding1 = self._io.read_bytes(self._root.header.ch1_skip)

            if self._root.header.ch[0].enabled:
                self.sentinel_between_datasets = self._io.read_u4le()

            if self._root.header.ch[1].enabled:
                self.ch2 = [None] * (self._root.header.ch2_points)
                for i in range(self._root.header.ch2_points):
                    self.ch2[i] = self._io.read_u1()


            if self._root.header.ch[1].enabled:
                self.roll_stop_padding2 = self._io.read_bytes(self._root.header.ch1_skip)

            self.logic = [None] * ((self._root.header.ch1_points if self._root.header.logic.enabled else 0))
            for i in range((self._root.header.ch1_points if self._root.header.logic.enabled else 0)):
                self.logic[i] = self._io.read_u2le()



    class LogicAnalyzerHeader(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.unused = self._io.read_bits_int(7)
            self.enabled = self._io.read_bits_int(1) != 0
            self._io.align_to_byte()
            self.active_channel = self._io.read_u1()
            self.enabled_channels = self._io.read_u2le()
            self.position = self._io.read_bytes(16)
            self.group8to15size = self._io.read_u1()
            self.group0to7size = self._io.read_u1()


    class ChannelHeader(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
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

        @property
        def unit(self):
            if hasattr(self, '_m_unit'):
                return self._m_unit if hasattr(self, '_m_unit') else None

            self._m_unit = self._root.UnitEnum.v
            return self._m_unit if hasattr(self, '_m_unit') else None

        @property
        def inverted(self):
            if hasattr(self, '_m_inverted'):
                return self._m_inverted if hasattr(self, '_m_inverted') else None

            self._m_inverted = (True if self.inverted_m_val != 0 else False)
            return self._m_inverted if hasattr(self, '_m_inverted') else None

        @property
        def volt_offset(self):
            if hasattr(self, '_m_volt_offset'):
                return self._m_volt_offset if hasattr(self, '_m_volt_offset') else None

            self._m_volt_offset = (self.shift_measured * self.volt_scale)
            return self._m_volt_offset if hasattr(self, '_m_volt_offset') else None

        @property
        def volt_per_division(self):
            if hasattr(self, '_m_volt_per_division'):
                return self._m_volt_per_division if hasattr(self, '_m_volt_per_division') else None

            self._m_volt_per_division = (((-0.0000010 * self.scale_measured) * self.probe_value) if self.inverted else ((0.0000010 * self.scale_measured) * self.probe_value))
            return self._m_volt_per_division if hasattr(self, '_m_volt_per_division') else None

        @property
        def volt_scale(self):
            if hasattr(self, '_m_volt_scale'):
                return self._m_volt_scale if hasattr(self, '_m_volt_scale') else None

            self._m_volt_scale = (((0.0000010 * self.scale_measured) * self.probe_value) / 25.0)
            return self._m_volt_scale if hasattr(self, '_m_volt_scale') else None

        @property
        def enabled(self):
            if hasattr(self, '_m_enabled'):
                return self._m_enabled if hasattr(self, '_m_enabled') else None

            self._m_enabled = (True if self.enabled_val != 0 else False)
            return self._m_enabled if hasattr(self, '_m_enabled') else None


    class Header(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.magic = self._io.ensure_fixed_contents(b"\xA5\xA5\x00\x00")
            self.blank_12 = self._io.ensure_fixed_contents(b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00")
            self.adc_mode = self._io.read_u1()
            self.padding_2 = self._io.ensure_fixed_contents(b"\x00\x00\x00")
            self.roll_stop = self._io.read_u4le()
            self.unused_4 = self._io.ensure_fixed_contents(b"\x00\x00\x00\x00")
            self.ch1_points_tmp = self._io.read_u4le()
            self.active_channel = self._io.read_u1()
            self.padding_3 = self._io.ensure_fixed_contents(b"\x00")
            self.ch = [None] * (2)
            for i in range(2):
                self.ch[i] = self._root.ChannelHeader(self._io, self, self._root)

            self.time_offset = self._io.read_u1()
            self.padding_4 = self._io.ensure_fixed_contents(b"\x00")
            self.time = self._root.TimeHeader(self._io, self, self._root)
            self.logic = self._root.LogicAnalyzerHeader(self._io, self, self._root)
            self.trigger_mode = self._root.TriggerModeEnum(self._io.read_u1())
            self.trigger1 = self._root.TriggerHeader(self._io, self, self._root)
            self.trigger2 = self._root.TriggerHeader(self._io, self, self._root)
            self.padding_6 = self._io.ensure_fixed_contents(b"\x00\x00\x00\x00\x00\x00\x00\x00\x00")
            self.ch2_points_tmp = self._io.read_u4le()
            self.time2 = self._root.TimeHeader(self._io, self, self._root)
            self.la_sample_rate = self._io.read_f4le()

        @property
        def ch2_volt_length(self):
            """In rolling mode, skip invalid samples."""
            if hasattr(self, '_m_ch2_volt_length'):
                return self._m_ch2_volt_length if hasattr(self, '_m_ch2_volt_length') else None

            self._m_ch2_volt_length = (self.ch2_points - self.roll_stop)
            return self._m_ch2_volt_length if hasattr(self, '_m_ch2_volt_length') else None

        @property
        def ch2_time_offset(self):
            if hasattr(self, '_m_ch2_time_offset'):
                return self._m_ch2_time_offset if hasattr(self, '_m_ch2_time_offset') else None

            self._m_ch2_time_offset = ((1.0E-12 * self.time2.offset_measured) if self.trigger_mode == self._root.TriggerModeEnum.alt else self.ch1_time_offset)
            return self._m_ch2_time_offset if hasattr(self, '_m_ch2_time_offset') else None

        @property
        def ch1_time_scale(self):
            if hasattr(self, '_m_ch1_time_scale'):
                return self._m_ch1_time_scale if hasattr(self, '_m_ch1_time_scale') else None

            self._m_ch1_time_scale = (1.0E-12 * self.time.scale_measured)
            return self._m_ch1_time_scale if hasattr(self, '_m_ch1_time_scale') else None

        @property
        def sample_rate_hz(self):
            if hasattr(self, '_m_sample_rate_hz'):
                return self._m_sample_rate_hz if hasattr(self, '_m_sample_rate_hz') else None

            self._m_sample_rate_hz = self.time.sample_rate_hz
            return self._m_sample_rate_hz if hasattr(self, '_m_sample_rate_hz') else None

        @property
        def ch1_volt_length(self):
            """In rolling mode, skip invalid samples."""
            if hasattr(self, '_m_ch1_volt_length'):
                return self._m_ch1_volt_length if hasattr(self, '_m_ch1_volt_length') else None

            self._m_ch1_volt_length = (self.ch1_points - self.roll_stop)
            return self._m_ch1_volt_length if hasattr(self, '_m_ch1_volt_length') else None

        @property
        def ch1_skip(self):
            """In rolling mode, skip invalid points."""
            if hasattr(self, '_m_ch1_skip'):
                return self._m_ch1_skip if hasattr(self, '_m_ch1_skip') else None

            self._m_ch1_skip = (0 if self.roll_stop == 0 else (self.roll_stop + 2))
            return self._m_ch1_skip if hasattr(self, '_m_ch1_skip') else None

        @property
        def ch1_time_offset(self):
            if hasattr(self, '_m_ch1_time_offset'):
                return self._m_ch1_time_offset if hasattr(self, '_m_ch1_time_offset') else None

            self._m_ch1_time_offset = (1.0E-12 * self.time.offset_measured)
            return self._m_ch1_time_offset if hasattr(self, '_m_ch1_time_offset') else None

        @property
        def seconds_per_point(self):
            if hasattr(self, '_m_seconds_per_point'):
                return self._m_seconds_per_point if hasattr(self, '_m_seconds_per_point') else None

            self._m_seconds_per_point = (1 / self.sample_rate_hz)
            return self._m_seconds_per_point if hasattr(self, '_m_seconds_per_point') else None

        @property
        def ch1_points(self):
            """In rolling mode, change the number of valid samples."""
            if hasattr(self, '_m_ch1_points'):
                return self._m_ch1_points if hasattr(self, '_m_ch1_points') else None

            self._m_ch1_points = ((self.ch1_points_tmp - 4) if self.roll_stop == 0 else ((self.ch1_points_tmp - self.roll_stop) - 6))
            return self._m_ch1_points if hasattr(self, '_m_ch1_points') else None

        @property
        def ch2_points(self):
            """Use ch1_points when ch2_points is not written."""
            if hasattr(self, '_m_ch2_points'):
                return self._m_ch2_points if hasattr(self, '_m_ch2_points') else None

            self._m_ch2_points = (self.ch1_points if  ((self.ch[1].enabled) and (self.ch2_points_tmp == 0))  else self.ch2_points_tmp)
            return self._m_ch2_points if hasattr(self, '_m_ch2_points') else None

        @property
        def ch2_time_scale(self):
            if hasattr(self, '_m_ch2_time_scale'):
                return self._m_ch2_time_scale if hasattr(self, '_m_ch2_time_scale') else None

            self._m_ch2_time_scale = ((1.0E-12 * self.time2.scale_measured) if self.trigger_mode == self._root.TriggerModeEnum.alt else self.ch1_time_scale)
            return self._m_ch2_time_scale if hasattr(self, '_m_ch2_time_scale') else None


    class TriggerHeader(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.mode = self._root.TriggerModeEnum(self._io.read_u1())
            self.source = self._root.SourceEnum(self._io.read_u1())
            self.coupling = self._io.read_u1()
            self.sweep = self._io.read_u1()
            self.padding_1 = self._io.ensure_fixed_contents(b"\x00")
            self.sens = self._io.read_f4le()
            self.holdoff = self._io.read_f4le()
            self.level = self._io.read_f4le()
            self.direct = self._io.read_u1()
            self.pulse_type = self._io.read_u1()
            self.padding_2 = self._io.ensure_fixed_contents(b"\x00\x00")
            self.pulse_width = self._io.read_f4le()
            self.slope_type = self._io.read_u1()
            self.padding_3 = self._io.ensure_fixed_contents(b"\x00\x00\x00")
            self.lower = self._io.read_f4le()
            self.slope_width = self._io.read_f4le()
            self.video_pol = self._io.read_u1()
            self.video_sync = self._io.read_u1()
            self.video_std = self._io.read_u1()


    @property
    def header(self):
        if hasattr(self, '_m_header'):
            return self._m_header if hasattr(self, '_m_header') else None

        _pos = self._io.pos()
        self._io.seek(0)
        self._m_header = self._root.Header(self._io, self, self._root)
        self._io.seek(_pos)
        return self._m_header if hasattr(self, '_m_header') else None

    @property
    def data(self):
        if hasattr(self, '_m_data'):
            return self._m_data if hasattr(self, '_m_data') else None

        _pos = self._io.pos()
        self._io.seek(276)
        self._m_data = self._root.RawData(self._io, self, self._root)
        self._io.seek(_pos)
        return self._m_data if hasattr(self, '_m_data') else None


