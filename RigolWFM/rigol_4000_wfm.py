# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild
# type: ignore

import kaitaistruct
from kaitaistruct import KaitaiStruct, KaitaiStream, BytesIO
from enum import IntEnum


if getattr(kaitaistruct, 'API_VERSION', (0, 9)) < (0, 11):
    raise Exception("Incompatible Kaitai Struct Python API: 0.11 or later is required, but you have %s" % (kaitaistruct.__version__))

class Rigol4000Wfm(KaitaiStruct):

    class AcquisitionEnum(IntEnum):
        normal = 0
        average = 1
        peak = 2
        high_resolution = 3

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

    class ImpedanceEnum(IntEnum):
        ohm_50 = 0
        ohm_1meg = 1

    class MemDepthEnum(IntEnum):
        auto = 0
        p_7k = 1
        p_70k = 2
        p_700k = 3
        p_7m = 4
        p_70m = 5
        p_14k = 6
        p_140k = 7
        p_1m4 = 8
        p_14m = 9
        p_140m = 10

    class ProbeEnum(IntEnum):
        single = 0
        diff = 1

    class ProbeRatioEnum(IntEnum):
        x0_01 = 0
        x0_02 = 1
        x0_05 = 2
        x0_1 = 3
        x0_2 = 4
        x0_5 = 5
        x1 = 6
        x2 = 7
        x5 = 8
        x10 = 9
        x20 = 10
        x50 = 11
        x100 = 12
        x200 = 13
        x500 = 14
        x1000 = 15

    class ProbeTypeEnum(IntEnum):
        normal_type = 0
        differential = 1

    class TimeEnum(IntEnum):
        yt = 0
        xy = 1
        roll = 2

    class TriggerModeEnum(IntEnum):
        edge = 3
        video = 4

    class TriggerSourceEnum(IntEnum):
        ch1 = 1
        ch2 = 2
        ch3 = 3
        ch4 = 4
        ext = 5

    class UnitEnum(IntEnum):
        w = 0
        a = 1
        v = 2
        u = 3
    def __init__(self, _io, _parent=None, _root=None):
        super(Rigol4000Wfm, self).__init__(_io)
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
            super(Rigol4000Wfm.ChannelHeader, self).__init__(_io)
            self._parent = _parent
            self._root = _root
            self._read()

        def _read(self):
            self.enabled_val = self._io.read_u1()
            self.coupling = KaitaiStream.resolve_enum(Rigol4000Wfm.CouplingEnum, self._io.read_u1())
            self.bandwidth_limit = KaitaiStream.resolve_enum(Rigol4000Wfm.BandwidthEnum, self._io.read_u1())
            self.probe_type = KaitaiStream.resolve_enum(Rigol4000Wfm.ProbeTypeEnum, self._io.read_u1())
            self.probe_ratio = KaitaiStream.resolve_enum(Rigol4000Wfm.ProbeRatioEnum, self._io.read_u1())
            self.probe_diff = KaitaiStream.resolve_enum(Rigol4000Wfm.ProbeEnum, self._io.read_u1())
            self.probe_signal = KaitaiStream.resolve_enum(Rigol4000Wfm.ProbeEnum, self._io.read_u1())
            self.probe_impedance = KaitaiStream.resolve_enum(Rigol4000Wfm.ImpedanceEnum, self._io.read_u1())
            self.volt_per_division = self._io.read_f4le()
            self.volt_offset = self._io.read_f4le()
            self.inverted_val = self._io.read_u1()
            self.unit = KaitaiStream.resolve_enum(Rigol4000Wfm.UnitEnum, self._io.read_u1())
            self.filter_enabled = self._io.read_u1()
            self.filter_type = KaitaiStream.resolve_enum(Rigol4000Wfm.FilterEnum, self._io.read_u1())
            self.filter_high = self._io.read_u4le()
            self.filter_low = self._io.read_u4le()


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

            self._m_inverted = (True if self.inverted_val != 0 else False)
            return getattr(self, '_m_inverted', None)

        @property
        def probe_value(self):
            if hasattr(self, '_m_probe_value'):
                return self._m_probe_value

            self._m_probe_value = (0.01 if self.probe_ratio == Rigol4000Wfm.ProbeRatioEnum.x0_01 else (0.02 if self.probe_ratio == Rigol4000Wfm.ProbeRatioEnum.x0_02 else (0.05 if self.probe_ratio == Rigol4000Wfm.ProbeRatioEnum.x0_05 else (0.1 if self.probe_ratio == Rigol4000Wfm.ProbeRatioEnum.x0_1 else (0.2 if self.probe_ratio == Rigol4000Wfm.ProbeRatioEnum.x0_2 else (0.5 if self.probe_ratio == Rigol4000Wfm.ProbeRatioEnum.x0_5 else (1.0 if self.probe_ratio == Rigol4000Wfm.ProbeRatioEnum.x1 else (2.0 if self.probe_ratio == Rigol4000Wfm.ProbeRatioEnum.x2 else (5.0 if self.probe_ratio == Rigol4000Wfm.ProbeRatioEnum.x5 else (10.0 if self.probe_ratio == Rigol4000Wfm.ProbeRatioEnum.x10 else (20.0 if self.probe_ratio == Rigol4000Wfm.ProbeRatioEnum.x20 else (50.0 if self.probe_ratio == Rigol4000Wfm.ProbeRatioEnum.x50 else (100.0 if self.probe_ratio == Rigol4000Wfm.ProbeRatioEnum.x100 else (200.0 if self.probe_ratio == Rigol4000Wfm.ProbeRatioEnum.x200 else (500.0 if self.probe_ratio == Rigol4000Wfm.ProbeRatioEnum.x500 else 1000.0)))))))))))))))
            return getattr(self, '_m_probe_value', None)

        @property
        def volt_scale(self):
            if hasattr(self, '_m_volt_scale'):
                return self._m_volt_scale

            self._m_volt_scale = (self.volt_signed / 25.0 if self._root.header.model_number[2:3] == u"2" else self.volt_signed / 32.0)
            return getattr(self, '_m_volt_scale', None)

        @property
        def volt_signed(self):
            if hasattr(self, '_m_volt_signed'):
                return self._m_volt_signed

            self._m_volt_signed = (-1.0 * self.volt_per_division if self.inverted else 1.0 * self.volt_per_division)
            return getattr(self, '_m_volt_signed', None)


    class ChannelMask(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            super(Rigol4000Wfm.ChannelMask, self).__init__(_io)
            self._parent = _parent
            self._root = _root
            self._read()

        def _read(self):
            self.unused = self._io.read_bits_int_be(4)
            self.channel_4 = self._io.read_bits_int_be(1) != 0
            self.channel_3 = self._io.read_bits_int_be(1) != 0
            self.channel_2 = self._io.read_bits_int_be(1) != 0
            self.channel_1 = self._io.read_bits_int_be(1) != 0


        def _fetch_instances(self):
            pass


    class Header(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            super(Rigol4000Wfm.Header, self).__init__(_io)
            self._parent = _parent
            self._root = _root
            self._read()

        def _read(self):
            self.magic = self._io.read_bytes(4)
            if not self.magic == b"\xA5\xA5\x38\x00":
                raise kaitaistruct.ValidationNotEqualError(b"\xA5\xA5\x38\x00", self.magic, self._io, u"/types/header/seq/0")
            self.model_number = (KaitaiStream.bytes_terminate(self._io.read_bytes(20), 0, False)).decode(u"ASCII")
            self.firmware_version = (KaitaiStream.bytes_terminate(self._io.read_bytes(20), 0, False)).decode(u"ASCII")
            self.unknown_1 = []
            for i in range(5):
                self.unknown_1.append(self._io.read_u4le())

            self.enabled = Rigol4000Wfm.ChannelMask(self._io, self, self._root)
            self.unknown_2 = self._io.read_bytes(3)
            self.position = Rigol4000Wfm.PositionType(self._io, self, self._root)
            self.unknown_3 = self._io.read_u4le()
            self.unknown_4 = self._io.read_u4le()
            self.unknown_5 = self._io.read_u4le()
            self.mem_depth_1 = self._io.read_u4le()
            self.sample_rate_hz = self._io.read_f4le()
            self.unknown_8 = self._io.read_u4le()
            self.time_per_div_ps = self._io.read_u8le()
            self.unknown_9 = []
            for i in range(2):
                self.unknown_9.append(self._io.read_u4le())

            self.ch = []
            for i in range(4):
                self.ch.append(Rigol4000Wfm.ChannelHeader(self._io, self, self._root))

            self.unknown_33 = []
            for i in range(6):
                self.unknown_33.append(self._io.read_u4le())

            self.mem_depth_2 = self._io.read_u4le()
            self.unknown_37 = self._io.read_bytes(4)
            self.mem_depth = self._io.read_u4le()
            self.unknown_38 = []
            for i in range(9):
                self.unknown_38.append(self._io.read_u4le())

            self.bytes_per_channel_1 = self._io.read_u4le()
            self.bytes_per_channel_2 = self._io.read_u4le()
            self.unknown_42 = []
            for i in range(41):
                self.unknown_42.append(self._io.read_u4le())

            self.total_samples = self._io.read_u4le()
            self.unknown_57 = []
            for i in range(4):
                self.unknown_57.append(self._io.read_u4le())

            self.mem_depth_type = KaitaiStream.resolve_enum(Rigol4000Wfm.MemDepthEnum, self._io.read_u1())
            self.unknown_60 = self._io.read_bytes(27)
            self.time = Rigol4000Wfm.TimeHeader(self._io, self, self._root)


        def _fetch_instances(self):
            pass
            for i in range(len(self.unknown_1)):
                pass

            self.enabled._fetch_instances()
            self.position._fetch_instances()
            for i in range(len(self.unknown_9)):
                pass

            for i in range(len(self.ch)):
                pass
                self.ch[i]._fetch_instances()

            for i in range(len(self.unknown_33)):
                pass

            for i in range(len(self.unknown_38)):
                pass

            for i in range(len(self.unknown_42)):
                pass

            for i in range(len(self.unknown_57)):
                pass

            self.time._fetch_instances()
            _ = self.raw_1
            if hasattr(self, '_m_raw_1'):
                pass

            _ = self.raw_2
            if hasattr(self, '_m_raw_2'):
                pass

            _ = self.raw_3
            if hasattr(self, '_m_raw_3'):
                pass

            _ = self.raw_4
            if hasattr(self, '_m_raw_4'):
                pass

            _ = self.setup
            if hasattr(self, '_m_setup'):
                pass
                self._m_setup._fetch_instances()


        @property
        def data_start(self):
            if hasattr(self, '_m_data_start'):
                return self._m_data_start

            self._m_data_start = (self.position.channel_1 if self.position.channel_1 != 0 else (self.position.channel_2 if self.position.channel_2 != 0 else (self.position.channel_3 if self.position.channel_3 != 0 else self.position.channel_4)))
            return getattr(self, '_m_data_start', None)

        @property
        def len_raw_1(self):
            if hasattr(self, '_m_len_raw_1'):
                return self._m_len_raw_1

            self._m_len_raw_1 = (self.mem_depth if self.enabled.channel_1 else 0)
            return getattr(self, '_m_len_raw_1', None)

        @property
        def len_raw_2(self):
            if hasattr(self, '_m_len_raw_2'):
                return self._m_len_raw_2

            self._m_len_raw_2 = (self.mem_depth if self.enabled.channel_2 else 0)
            return getattr(self, '_m_len_raw_2', None)

        @property
        def len_raw_3(self):
            if hasattr(self, '_m_len_raw_3'):
                return self._m_len_raw_3

            self._m_len_raw_3 = (self.mem_depth if self.enabled.channel_3 else 0)
            return getattr(self, '_m_len_raw_3', None)

        @property
        def len_raw_4(self):
            if hasattr(self, '_m_len_raw_4'):
                return self._m_len_raw_4

            self._m_len_raw_4 = (self.mem_depth if self.enabled.channel_4 else 0)
            return getattr(self, '_m_len_raw_4', None)

        @property
        def points(self):
            if hasattr(self, '_m_points'):
                return self._m_points

            self._m_points = self.mem_depth
            return getattr(self, '_m_points', None)

        @property
        def raw_1(self):
            if hasattr(self, '_m_raw_1'):
                return self._m_raw_1

            if self.enabled.channel_1:
                pass
                io = self._root._io
                _pos = io.pos()
                io.seek(self.position.channel_1)
                self._m_raw_1 = io.read_bytes(self.len_raw_1)
                io.seek(_pos)

            return getattr(self, '_m_raw_1', None)

        @property
        def raw_2(self):
            if hasattr(self, '_m_raw_2'):
                return self._m_raw_2

            if self.enabled.channel_2:
                pass
                io = self._root._io
                _pos = io.pos()
                io.seek(self.position.channel_2)
                self._m_raw_2 = io.read_bytes(self.len_raw_2)
                io.seek(_pos)

            return getattr(self, '_m_raw_2', None)

        @property
        def raw_3(self):
            if hasattr(self, '_m_raw_3'):
                return self._m_raw_3

            if self.enabled.channel_3:
                pass
                io = self._root._io
                _pos = io.pos()
                io.seek(self.position.channel_3)
                self._m_raw_3 = io.read_bytes(self.len_raw_3)
                io.seek(_pos)

            return getattr(self, '_m_raw_3', None)

        @property
        def raw_4(self):
            if hasattr(self, '_m_raw_4'):
                return self._m_raw_4

            if self.enabled.channel_4:
                pass
                io = self._root._io
                _pos = io.pos()
                io.seek(self.position.channel_4)
                self._m_raw_4 = io.read_bytes(self.len_raw_4)
                io.seek(_pos)

            return getattr(self, '_m_raw_4', None)

        @property
        def seconds_per_point(self):
            if hasattr(self, '_m_seconds_per_point'):
                return self._m_seconds_per_point

            self._m_seconds_per_point = 1 / self.sample_rate_hz
            return getattr(self, '_m_seconds_per_point', None)

        @property
        def serial_number(self):
            if hasattr(self, '_m_serial_number'):
                return self._m_serial_number

            self._m_serial_number = self.model_number
            return getattr(self, '_m_serial_number', None)

        @property
        def setup(self):
            if hasattr(self, '_m_setup'):
                return self._m_setup

            _pos = self._io.pos()
            self._io.seek(597)
            self._raw__m_setup = self._io.read_bytes(self.data_start - 597)
            _io__raw__m_setup = KaitaiStream(BytesIO(self._raw__m_setup))
            self._m_setup = Rigol4000Wfm.SetupBlock(_io__raw__m_setup, self, self._root)
            self._io.seek(_pos)
            return getattr(self, '_m_setup', None)

        @property
        def time_offset(self):
            if hasattr(self, '_m_time_offset'):
                return self._m_time_offset

            self._m_time_offset = 1.0E-12 * self.time.actual_offset_ps
            return getattr(self, '_m_time_offset', None)

        @property
        def time_scale(self):
            if hasattr(self, '_m_time_scale'):
                return self._m_time_scale

            self._m_time_scale = 1.0E-12 * self.time.time_per_div_ps
            return getattr(self, '_m_time_scale', None)

        @property
        def vertical_scale_factor(self):
            if hasattr(self, '_m_vertical_scale_factor'):
                return self._m_vertical_scale_factor

            self._m_vertical_scale_factor = (25 if self.model_number[2:3] == u"2" else 32)
            return getattr(self, '_m_vertical_scale_factor', None)


    class PositionType(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            super(Rigol4000Wfm.PositionType, self).__init__(_io)
            self._parent = _parent
            self._root = _root
            self._read()

        def _read(self):
            self.channel_1 = self._io.read_u4le()
            self.channel_2 = self._io.read_u4le()
            self.channel_3 = self._io.read_u4le()
            self.channel_4 = self._io.read_u4le()


        def _fetch_instances(self):
            pass


    class SetupBlock(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            super(Rigol4000Wfm.SetupBlock, self).__init__(_io)
            self._parent = _parent
            self._root = _root
            self._read()

        def _read(self):
            pass


        def _fetch_instances(self):
            pass
            _ = self.legacy_trigger_levels
            if hasattr(self, '_m_legacy_trigger_levels'):
                pass
                self._m_legacy_trigger_levels._fetch_instances()

            _ = self.modern_trigger_levels
            if hasattr(self, '_m_modern_trigger_levels'):
                pass
                self._m_modern_trigger_levels._fetch_instances()

            _ = self.modern_trigger_mode
            if hasattr(self, '_m_modern_trigger_mode'):
                pass

            _ = self.modern_trigger_source
            if hasattr(self, '_m_modern_trigger_source'):
                pass


        @property
        def legacy_trigger_levels(self):
            if hasattr(self, '_m_legacy_trigger_levels'):
                return self._m_legacy_trigger_levels

            if self._io.size() >= 558:
                pass
                _pos = self._io.pos()
                self._io.seek(538)
                self._m_legacy_trigger_levels = Rigol4000Wfm.TriggerLevelBlock(self._io, self, self._root)
                self._io.seek(_pos)

            return getattr(self, '_m_legacy_trigger_levels', None)

        @property
        def modern_trigger_levels(self):
            if hasattr(self, '_m_modern_trigger_levels'):
                return self._m_modern_trigger_levels

            if self._io.size() >= 606:
                pass
                _pos = self._io.pos()
                self._io.seek(586)
                self._m_modern_trigger_levels = Rigol4000Wfm.TriggerLevelBlock(self._io, self, self._root)
                self._io.seek(_pos)

            return getattr(self, '_m_modern_trigger_levels', None)

        @property
        def modern_trigger_mode(self):
            if hasattr(self, '_m_modern_trigger_mode'):
                return self._m_modern_trigger_mode

            if self._io.size() >= 611:
                pass
                _pos = self._io.pos()
                self._io.seek(610)
                self._m_modern_trigger_mode = KaitaiStream.resolve_enum(Rigol4000Wfm.TriggerModeEnum, self._io.read_u1())
                self._io.seek(_pos)

            return getattr(self, '_m_modern_trigger_mode', None)

        @property
        def modern_trigger_source(self):
            if hasattr(self, '_m_modern_trigger_source'):
                return self._m_modern_trigger_source

            if self._io.size() >= 624:
                pass
                _pos = self._io.pos()
                self._io.seek(623)
                self._m_modern_trigger_source = KaitaiStream.resolve_enum(Rigol4000Wfm.TriggerSourceEnum, self._io.read_u1())
                self._io.seek(_pos)

            return getattr(self, '_m_modern_trigger_source', None)


    class TimeHeader(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            super(Rigol4000Wfm.TimeHeader, self).__init__(_io)
            self._parent = _parent
            self._root = _root
            self._read()

        def _read(self):
            self.unknown_1 = self._io.read_u2le()
            self.unknown_2 = self._io.read_bytes(10)
            self.index = self._io.read_u4le()
            self.time_per_div_ps = self._io.read_u4le()
            self.unknown_3a = self._io.read_bytes(4)
            self.offset_per_div_ps = self._io.read_u8le()
            self.unknown_4_head = self._io.read_bytes(8)
            self.actual_offset_ps = self._io.read_s8le()
            self.offset_ps = self._io.read_u8le()
            self.unknown_5 = self._io.read_bytes(16)
            self.unknown_6 = self._io.read_u2le()
            self.unknown_7 = self._io.read_u1()


        def _fetch_instances(self):
            pass


    class TriggerLevelBlock(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            super(Rigol4000Wfm.TriggerLevelBlock, self).__init__(_io)
            self._parent = _parent
            self._root = _root
            self._read()

        def _read(self):
            self.ch1_level_uv = self._io.read_s4le()
            self.ch2_level_uv = self._io.read_s4le()
            self.ch3_level_uv = self._io.read_s4le()
            self.ch4_level_uv = self._io.read_s4le()
            self.ext_level_uv = self._io.read_s4le()


        def _fetch_instances(self):
            pass


    @property
    def header(self):
        if hasattr(self, '_m_header'):
            return self._m_header

        _pos = self._io.pos()
        self._io.seek(0)
        self._m_header = Rigol4000Wfm.Header(self._io, self, self._root)
        self._io.seek(_pos)
        return getattr(self, '_m_header', None)


