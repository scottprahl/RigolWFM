# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild

from pkg_resources import parse_version
from kaitaistruct import __version__ as ks_version, KaitaiStruct, KaitaiStream, BytesIO
from enum import Enum


if parse_version(ks_version) < parse_version('0.7'):
    raise Exception("Incompatible Kaitai Struct Python API: 0.7 or later is required, but you have %s" % (ks_version))

class Wfm6000(KaitaiStruct):

    class UnitEnum(Enum):
        w = 0
        a = 1
        v = 2
        u = 3

    class ProbeRatioEnum(Enum):
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

    class ImpedanceEnum(Enum):
        ohm_50 = 0
        ohm_1meg = 1

    class ProbeTypeEnum(Enum):
        normal_type = 0
        differential = 1

    class ProbeEnum(Enum):
        single = 0
        diff = 1

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

    class TimeEnum(Enum):
        yt = 0
        xy = 1
        roll = 2

    class AcquisitionEnum(Enum):
        normal = 0
        average = 1
        peak = 2
        high_resolution = 3

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

    class Header(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.magic = self._io.ensure_fixed_contents(b"\xA5\xA5\x38\x00")
            self.model_number = (KaitaiStream.bytes_terminate(self._io.read_bytes(20), 0, False)).decode(u"ascii")
            self.firmware_version = (KaitaiStream.bytes_terminate(self._io.read_bytes(20), 0, False)).decode(u"ascii")
            self.block_num = self._io.read_u2le()
            self.file_version = self._io.read_u2le()
            self.unused_1 = self._io.read_bytes(18)
            self.enabled = self._root.ChannelMask(self._io, self, self._root)
            self.channel_offset = [None] * (4)
            for i in range(4):
                self.channel_offset[i] = self._io.read_u4le()

            self.acquisition_mode = self._root.AcquisitionEnum(self._io.read_u1())
            self.average_time = self._io.read_u2le()
            self.sample_mode = self._io.read_u2le()
            self.mem_depth = self._io.read_u4le()
            self.sample_rate_hz = self._io.read_f4le()
            self.time_mode = self._root.TimeEnum(self._io.read_u2le())
            self.time_scale_ps = self._io.read_u8le()
            self.time_offset_ps = self._io.read_s8le()
            self.ch = [None] * (4)
            for i in range(4):
                self.ch[i] = self._root.ChannelHeader(self._io, self, self._root)

            self.setup_size = self._io.read_u4le()
            self.setup_offset = self._io.read_u4le()
            self.wfm_offset = self._io.read_u4le()
            self.storage_depth = self._io.read_u4le()
            self.z_pt_offset = self._io.read_u4le()
            self.wfm_len = self._io.read_u4le()
            self.mem_offset = [None] * (2)
            for i in range(2):
                self.mem_offset[i] = self._io.read_u2le()

            self.equ_coarse = [None] * (2)
            for i in range(2):
                self.equ_coarse[i] = self._io.read_u2le()

            self.equ_fine = [None] * (2)
            for i in range(2):
                self.equ_fine[i] = self._io.read_u2le()

            self.mem_last_addr = [None] * (2)
            for i in range(2):
                self.mem_last_addr[i] = self._io.read_u4le()

            self.mem_length = [None] * (2)
            for i in range(2):
                self.mem_length[i] = self._io.read_u4le()

            self.mem_start_addr = [None] * (2)
            for i in range(2):
                self.mem_start_addr[i] = self._io.read_u4le()

            self.bank_size = [None] * (2)
            for i in range(2):
                self.bank_size[i] = self._io.read_u4le()

            self.roll_scrn_wave_length = self._io.read_u2le()
            self.analog_interp_en = self._io.read_u1()
            self.main_force_analog_trig = self._io.read_u1()
            self.zoom_force_analog_trig = self._io.read_u1()
            self.horiz_slow_force_stop_frame = self._io.read_u1()
            self.get_spu_dig_data_status = self._io.read_u1()
            self.main_mem_offset = self._io.read_s8le()
            self.mem_view_offset = self._io.read_s8le()
            self.slow_deta_wave_length = self._io.read_s8le()
            self.slow_deta_wave_length_no_delay = self._io.read_s8le()
            self.real_sa_dot_period = self._io.read_u8le()
            self.trig_type_deta_delay = self._io.read_s4le()
            self.chnl1_2_max_delay = self._io.read_s4le()
            self.chnl3_4_max_delay = self._io.read_s4le()
            self.chnl_dly_to_mem_len = self._io.read_u4le()
            self.spu_mem_depth_deta = self._io.read_u4le()
            self.spu_mem_depth_rema = self._io.read_u4le()
            self.mem_offset_base = self._io.read_u4le()
            self.spu_mem_bank_size = self._io.read_u4le()
            self.s16_adc1_clock_delay = self._io.read_u2le()
            self.s16_adc2_clock_delay = self._io.read_u2le()
            self.max_main_scrn_chnl_delay = self._io.read_u2le()
            self.max_zoom_scrn_chnl_delay = self._io.read_u2le()
            self.main_dgtl_trig_data_offset = self._io.read_u2le()
            self.zoom_dgtl_trig_data_offset = self._io.read_u2le()
            self.record_frame_index = self._io.read_u4le()

        @property
        def seconds_per_point(self):
            if hasattr(self, '_m_seconds_per_point'):
                return self._m_seconds_per_point if hasattr(self, '_m_seconds_per_point') else None

            self._m_seconds_per_point = (1 / self.sample_rate_hz)
            return self._m_seconds_per_point if hasattr(self, '_m_seconds_per_point') else None

        @property
        def time_scale(self):
            if hasattr(self, '_m_time_scale'):
                return self._m_time_scale if hasattr(self, '_m_time_scale') else None

            self._m_time_scale = (1.0E-12 * self.time_scale_ps)
            return self._m_time_scale if hasattr(self, '_m_time_scale') else None

        @property
        def time_offset(self):
            if hasattr(self, '_m_time_offset'):
                return self._m_time_offset if hasattr(self, '_m_time_offset') else None

            self._m_time_offset = (1.0E-12 * self.time_offset_ps)
            return self._m_time_offset if hasattr(self, '_m_time_offset') else None

        @property
        def points(self):
            if hasattr(self, '_m_points'):
                return self._m_points if hasattr(self, '_m_points') else None

            self._m_points = self._root.header.mem_depth
            return self._m_points if hasattr(self, '_m_points') else None


    class ChannelHeader(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.enabled = self._io.read_u1()
            self.coupling = self._root.CouplingEnum(self._io.read_u1())
            self.bandwidth_limit = self._root.BandwidthEnum(self._io.read_u1())
            self.probe_type = self._root.ProbeTypeEnum(self._io.read_u1())
            self.probe_ratio = self._root.ProbeRatioEnum(self._io.read_u1())
            self.probe_diff = self._root.ProbeEnum(self._io.read_u1())
            self.probe_signal = self._root.ProbeEnum(self._io.read_u1())
            self.probe_impedance = self._root.ImpedanceEnum(self._io.read_u1())
            self.volt_per_division = self._io.read_f4le()
            self.volt_offset = self._io.read_f4le()
            self.invert = self._io.read_u1()
            self.unit = self._root.UnitEnum(self._io.read_u1())
            self.filter_enabled = self._io.read_u1()
            self.filter_type = self._root.FilterEnum(self._io.read_u1())
            self.filter_high = self._io.read_u4le()
            self.filter_low = self._io.read_u4le()

        @property
        def probe_value(self):
            if hasattr(self, '_m_probe_value'):
                return self._m_probe_value if hasattr(self, '_m_probe_value') else None

            self._m_probe_value = (0.01 if self.probe_ratio == self._root.ProbeRatioEnum.x0_01 else (0.02 if self.probe_ratio == self._root.ProbeRatioEnum.x0_02 else (0.05 if self.probe_ratio == self._root.ProbeRatioEnum.x0_05 else (0.1 if self.probe_ratio == self._root.ProbeRatioEnum.x0_1 else (0.2 if self.probe_ratio == self._root.ProbeRatioEnum.x0_2 else (0.5 if self.probe_ratio == self._root.ProbeRatioEnum.x0_5 else (1.0 if self.probe_ratio == self._root.ProbeRatioEnum.x1 else (2.0 if self.probe_ratio == self._root.ProbeRatioEnum.x2 else (5.0 if self.probe_ratio == self._root.ProbeRatioEnum.x5 else (10.0 if self.probe_ratio == self._root.ProbeRatioEnum.x10 else (20.0 if self.probe_ratio == self._root.ProbeRatioEnum.x20 else (50.0 if self.probe_ratio == self._root.ProbeRatioEnum.x50 else (100.0 if self.probe_ratio == self._root.ProbeRatioEnum.x100 else (200.0 if self.probe_ratio == self._root.ProbeRatioEnum.x200 else (500.0 if self.probe_ratio == self._root.ProbeRatioEnum.x500 else 1000.0)))))))))))))))
            return self._m_probe_value if hasattr(self, '_m_probe_value') else None


    class ChannelMask(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.unused = self._io.read_bits_int(4)
            self.channel_4 = self._io.read_bits_int(1) != 0
            self.channel_3 = self._io.read_bits_int(1) != 0
            self.channel_2 = self._io.read_bits_int(1) != 0
            self.channel_1 = self._io.read_bits_int(1) != 0


    class RawData(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            if self._root.header.enabled.channel_1:
                self.channel_1 = [None] * (self._root.header.mem_depth)
                for i in range(self._root.header.mem_depth):
                    self.channel_1[i] = self._io.read_u1()


            if self._root.header.enabled.channel_2:
                self.channel_2 = [None] * (self._root.header.mem_depth)
                for i in range(self._root.header.mem_depth):
                    self.channel_2[i] = self._io.read_u1()


            if self._root.header.enabled.channel_3:
                self.channel_3 = [None] * (self._root.header.mem_depth)
                for i in range(self._root.header.mem_depth):
                    self.channel_3[i] = self._io.read_u1()


            if self._root.header.enabled.channel_4:
                self.channel_4 = [None] * (self._root.header.mem_depth)
                for i in range(self._root.header.mem_depth):
                    self.channel_4[i] = self._io.read_u1()




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
        self._io.seek(20916)
        self._m_data = self._root.RawData(self._io, self, self._root)
        self._io.seek(_pos)
        return self._m_data if hasattr(self, '_m_data') else None


