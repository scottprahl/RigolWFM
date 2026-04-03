# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild
# type: ignore

import kaitaistruct
from kaitaistruct import KaitaiStruct, KaitaiStream, BytesIO
from enum import IntEnum


if getattr(kaitaistruct, 'API_VERSION', (0, 9)) < (0, 11):
    raise Exception("Incompatible Kaitai Struct Python API: 0.11 or later is required, but you have %s" % (kaitaistruct.__version__))

class Rigol2000Wfm(KaitaiStruct):
    """Rigol DS2000 / MSO2000 waveform file format.
    
    Sources used for this KSY binary format: a document titled "WFM save format: Secretary Bird"
    
    Tested file formats: real repo fixtures `DS2000-A.wfm`, `DS2000-B.wfm`, and
    `DS2072A-1.wfm` through `DS2072A-9.wfm`, plus small header-window mutation
    regressions built from those files.
    
    Oscilloscope models this format may apply to: DS2000 family models c
    `DS2072A`, `DS2102A`, `MSO2102A`,
    `MSO2102A-S`, `DS2202A`, `MSO2202A`, `MSO2202A-S`, `DS2302A`, `MSO2302A`,
    and `MSO2302A-S`.
    """

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

    class SetupTriggerSourceEnum(IntEnum):
        ch1 = 0
        ch2 = 1
        ext = 2
        ac_line = 3

    class TimeEnum(IntEnum):
        yt = 0
        xy = 1
        roll = 2

    class UnitEnum(IntEnum):
        w = 0
        a = 1
        v = 2
        u = 3
    def __init__(self, _io, _parent=None, _root=None):
        super(Rigol2000Wfm, self).__init__(_io)
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
            super(Rigol2000Wfm.ChannelHeader, self).__init__(_io)
            self._parent = _parent
            self._root = _root
            self._read()

        def _read(self):
            self.enabled_temp = self._io.read_u1()
            self.coupling_raw = self._io.read_u1()
            self.bandwidth_limit = KaitaiStream.resolve_enum(Rigol2000Wfm.BandwidthEnum, self._io.read_u1())
            self.probe_type = KaitaiStream.resolve_enum(Rigol2000Wfm.ProbeTypeEnum, self._io.read_u1())
            self.probe_ratio_raw = KaitaiStream.resolve_enum(Rigol2000Wfm.ProbeRatioEnum, self._io.read_u1())
            self.probe_diff = KaitaiStream.resolve_enum(Rigol2000Wfm.ProbeEnum, self._io.read_u1())
            self.probe_signal = KaitaiStream.resolve_enum(Rigol2000Wfm.ProbeEnum, self._io.read_u1())
            self.probe_impedance_raw = KaitaiStream.resolve_enum(Rigol2000Wfm.ImpedanceEnum, self._io.read_u1())
            self.volt_per_division = self._io.read_f4le()
            self.volt_offset = self._io.read_f4le()
            self.inverted_temp = self._io.read_u1()
            self.unit_temp = self._io.read_u1()
            self.filter_enabled = self._io.read_u1()
            self.filter_type = self._io.read_u1()
            self.filter_high = self._io.read_u4le()
            self.filter_low = self._io.read_u4le()


        def _fetch_instances(self):
            pass

        @property
        def coupling(self):
            if hasattr(self, '_m_coupling'):
                return self._m_coupling

            self._m_coupling = (Rigol2000Wfm.CouplingEnum.dc if self.coupling_raw >> 6 == 0 else (Rigol2000Wfm.CouplingEnum.ac if self.coupling_raw >> 6 == 1 else Rigol2000Wfm.CouplingEnum.gnd))
            return getattr(self, '_m_coupling', None)

        @property
        def enabled(self):
            if hasattr(self, '_m_enabled'):
                return self._m_enabled

            self._m_enabled = (True if self.enabled_temp != 0 else False)
            return getattr(self, '_m_enabled', None)

        @property
        def inverted(self):
            if hasattr(self, '_m_inverted'):
                return self._m_inverted

            self._m_inverted = (True if self.inverted_actual == 1 else False)
            return getattr(self, '_m_inverted', None)

        @property
        def inverted_actual(self):
            if hasattr(self, '_m_inverted_actual'):
                return self._m_inverted_actual

            self._m_inverted_actual = (self.inverted_temp if self.legacy_vertical_layout else self.unit_temp)
            return getattr(self, '_m_inverted_actual', None)

        @property
        def legacy_vertical_layout(self):
            """The older DS2000 captures in this repo store invert/unit in the
            documented order when bChanEn is 1.  The DS2072A captures instead
            store unit first and use zeroed probe fields, so a small compatibility
            shim is needed to recover the visible settings.
            """
            if hasattr(self, '_m_legacy_vertical_layout'):
                return self._m_legacy_vertical_layout

            self._m_legacy_vertical_layout = (True if self.enabled_temp == 1 else False)
            return getattr(self, '_m_legacy_vertical_layout', None)

        @property
        def probe_impedance(self):
            if hasattr(self, '_m_probe_impedance'):
                return self._m_probe_impedance

            self._m_probe_impedance = (Rigol2000Wfm.ImpedanceEnum.ohm_1meg if  (((not (self.legacy_vertical_layout))) and (self.probe_ratio_raw == Rigol2000Wfm.ProbeRatioEnum.x0_01) and (self.probe_impedance_raw == Rigol2000Wfm.ImpedanceEnum.ohm_50))  else self.probe_impedance_raw)
            return getattr(self, '_m_probe_impedance', None)

        @property
        def probe_ratio(self):
            if hasattr(self, '_m_probe_ratio'):
                return self._m_probe_ratio

            self._m_probe_ratio = (Rigol2000Wfm.ProbeRatioEnum.x1 if  (((not (self.legacy_vertical_layout))) and (self.probe_ratio_raw == Rigol2000Wfm.ProbeRatioEnum.x0_01) and (self.probe_impedance_raw == Rigol2000Wfm.ImpedanceEnum.ohm_50))  else self.probe_ratio_raw)
            return getattr(self, '_m_probe_ratio', None)

        @property
        def probe_value(self):
            if hasattr(self, '_m_probe_value'):
                return self._m_probe_value

            self._m_probe_value = (0.01 if self.probe_ratio == Rigol2000Wfm.ProbeRatioEnum.x0_01 else (0.02 if self.probe_ratio == Rigol2000Wfm.ProbeRatioEnum.x0_02 else (0.05 if self.probe_ratio == Rigol2000Wfm.ProbeRatioEnum.x0_05 else (0.1 if self.probe_ratio == Rigol2000Wfm.ProbeRatioEnum.x0_1 else (0.2 if self.probe_ratio == Rigol2000Wfm.ProbeRatioEnum.x0_2 else (0.5 if self.probe_ratio == Rigol2000Wfm.ProbeRatioEnum.x0_5 else (1.0 if self.probe_ratio == Rigol2000Wfm.ProbeRatioEnum.x1 else (2.0 if self.probe_ratio == Rigol2000Wfm.ProbeRatioEnum.x2 else (5.0 if self.probe_ratio == Rigol2000Wfm.ProbeRatioEnum.x5 else (10.0 if self.probe_ratio == Rigol2000Wfm.ProbeRatioEnum.x10 else (20.0 if self.probe_ratio == Rigol2000Wfm.ProbeRatioEnum.x20 else (50.0 if self.probe_ratio == Rigol2000Wfm.ProbeRatioEnum.x50 else (100.0 if self.probe_ratio == Rigol2000Wfm.ProbeRatioEnum.x100 else (200.0 if self.probe_ratio == Rigol2000Wfm.ProbeRatioEnum.x200 else (500.0 if self.probe_ratio == Rigol2000Wfm.ProbeRatioEnum.x500 else 1000.0)))))))))))))))
            return getattr(self, '_m_probe_value', None)

        @property
        def unit(self):
            if hasattr(self, '_m_unit'):
                return self._m_unit

            self._m_unit = self.unit_actual
            return getattr(self, '_m_unit', None)

        @property
        def unit_actual(self):
            if hasattr(self, '_m_unit_actual'):
                return self._m_unit_actual

            self._m_unit_actual = (self.unit_temp if self.legacy_vertical_layout else self.inverted_temp)
            return getattr(self, '_m_unit_actual', None)

        @property
        def volt_scale(self):
            if hasattr(self, '_m_volt_scale'):
                return self._m_volt_scale

            self._m_volt_scale = self.volt_signed / 25.0
            return getattr(self, '_m_volt_scale', None)

        @property
        def volt_signed(self):
            if hasattr(self, '_m_volt_signed'):
                return self._m_volt_signed

            self._m_volt_signed = (-1.0 * self.volt_per_division if self.inverted else 1.0 * self.volt_per_division)
            return getattr(self, '_m_volt_signed', None)


    class ChannelMask(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            super(Rigol2000Wfm.ChannelMask, self).__init__(_io)
            self._parent = _parent
            self._root = _root
            self._read()

        def _read(self):
            self.unused_1 = self._io.read_bits_int_be(4)
            self.channel_4 = self._io.read_bits_int_be(1) != 0
            self.channel_3 = self._io.read_bits_int_be(1) != 0
            self.channel_2 = self._io.read_bits_int_be(1) != 0
            self.channel_1 = self._io.read_bits_int_be(1) != 0
            self.unused_2 = self._io.read_bits_int_be(7)
            self.interwoven = self._io.read_bits_int_be(1) != 0


        def _fetch_instances(self):
            pass


    class Header(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            super(Rigol2000Wfm.Header, self).__init__(_io)
            self._parent = _parent
            self._root = _root
            self._read()

        def _read(self):
            self.magic = self._io.read_bytes(4)
            if not self.magic == b"\xA5\xA5\x38\x00":
                raise kaitaistruct.ValidationNotEqualError(b"\xA5\xA5\x38\x00", self.magic, self._io, u"/types/header/seq/0")
            self.model_number = (KaitaiStream.bytes_terminate(self._io.read_bytes(20), 0, False)).decode(u"ASCII")
            self.firmware_version = (KaitaiStream.bytes_terminate(self._io.read_bytes(20), 0, False)).decode(u"ASCII")
            self.block_num = self._io.read_bytes(2)
            if not self.block_num == b"\x01\x00":
                raise kaitaistruct.ValidationNotEqualError(b"\x01\x00", self.block_num, self._io, u"/types/header/seq/3")
            self.file_version = self._io.read_u2le()
            self.unused_1 = self._io.read_bytes(8)
            self.crc = self._io.read_u4le()
            self.structure_size = self._io.read_u2le()
            self.structure_version = self._io.read_u2le()
            self.enabled = Rigol2000Wfm.ChannelMask(self._io, self, self._root)
            self.extra_1a = self._io.read_bytes(2)
            self.channel_offset = []
            for i in range(4):
                self.channel_offset.append(self._io.read_u4le())

            self.acquisition_mode = KaitaiStream.resolve_enum(Rigol2000Wfm.AcquisitionEnum, self._io.read_u2le())
            self.average_time = self._io.read_u2le()
            self.sample_mode = self._io.read_u2le()
            self.extra_1b = self._io.read_bytes(2)
            self.mem_depth = self._io.read_u4le()
            self.sample_rate_hz = self._io.read_f4le()
            self.extra_1c = self._io.read_bytes(2)
            self.time_mode = KaitaiStream.resolve_enum(Rigol2000Wfm.TimeEnum, self._io.read_u2le())
            self.time_scale_ps = self._io.read_u8le()
            self.time_offset_ps = self._io.read_s8le()
            self.ch = []
            for i in range(4):
                self.ch.append(Rigol2000Wfm.ChannelHeader(self._io, self, self._root))

            self.len_setup = self._io.read_u4le()
            self.setup_offset = self._io.read_u4le()
            self.wfm_offset = self._io.read_u4le()
            self.storage_depth = self._io.read_u4le()
            self.z_pt_offset = self._io.read_u4le()
            self.wfm_len = self._io.read_u4le()
            self.equ_coarse = self._io.read_u2le()
            self.equ_fine = self._io.read_u2le()
            self.mem_start_addr = []
            for i in range(2):
                self.mem_start_addr.append(self._io.read_u4le())

            self.mem_last_addr = self._io.read_u4le()
            self.mem_length = self._io.read_u4le()
            self.channel_depth = self._io.read_u4le()
            self.bank_size = self._io.read_u4le()
            self.bank_offset = self._io.read_u4le()
            self.real_offset = self._io.read_u4le()
            self.real_ch_offset = self._io.read_u4le()
            self.horiz_slow_force_stop_frame_boolean = self._io.read_u1()
            self.get_spu_dig_data_status_boolean = self._io.read_u1()
            self.spu_load_data_status_boolean = self._io.read_u1()
            self.reserved_243 = self._io.read_bytes(1)
            self.trig_delay_mem_offset = self._io.read_s8le()
            self.trig_delay_view_offset = self._io.read_s8le()
            self.mem_offset_compensate = self._io.read_s8le()
            self.slow_delta_wave_length = self._io.read_s8le()
            self.channel_pos_max_delay = self._io.read_s8le()
            self.channel_neg_min_delay = self._io.read_s8le()
            self.real_sa_dot_period = self._io.read_u8le()
            self.mem_offset_base = self._io.read_u8le()
            self.trig_type_delta_delay = self._io.read_s4le()
            self.ch1_delay = self._io.read_s4le()
            self.ch2_delay = self._io.read_s4le()
            self.channel_delay_to_mem_len = self._io.read_u4le()
            self.spu_mem_bank_size = self._io.read_u4le()
            self.roll_scrn_wave_length = self._io.read_u2le()
            self.trigger_source = self._io.read_u1()
            self.cal_index = self._io.read_u1()
            self.record_frame_index = self._io.read_u4le()
            self.frame_cur = self._io.read_u4le()
            self.private = []
            for i in range(4):
                self.private.append(self._io.read_u4le())



        def _fetch_instances(self):
            pass
            self.enabled._fetch_instances()
            for i in range(len(self.channel_offset)):
                pass

            for i in range(len(self.ch)):
                pass
                self.ch[i]._fetch_instances()

            for i in range(len(self.mem_start_addr)):
                pass

            for i in range(len(self.private)):
                pass

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
        def len_raw_1(self):
            if hasattr(self, '_m_len_raw_1'):
                return self._m_len_raw_1

            self._m_len_raw_1 = (self.raw_depth if self.channel_offset[0] > 0 else 0)
            return getattr(self, '_m_len_raw_1', None)

        @property
        def len_raw_2(self):
            if hasattr(self, '_m_len_raw_2'):
                return self._m_len_raw_2

            self._m_len_raw_2 = (self.raw_depth if self.channel_offset[1] > 0 else 0)
            return getattr(self, '_m_len_raw_2', None)

        @property
        def len_raw_3(self):
            if hasattr(self, '_m_len_raw_3'):
                return self._m_len_raw_3

            self._m_len_raw_3 = (self.raw_depth if self.channel_offset[2] > 0 else 0)
            return getattr(self, '_m_len_raw_3', None)

        @property
        def len_raw_4(self):
            if hasattr(self, '_m_len_raw_4'):
                return self._m_len_raw_4

            self._m_len_raw_4 = (self.raw_depth if self.channel_offset[3] > 0 else 0)
            return getattr(self, '_m_len_raw_4', None)

        @property
        def points(self):
            if hasattr(self, '_m_points'):
                return self._m_points

            self._m_points = self.wfm_len
            return getattr(self, '_m_points', None)

        @property
        def raw_1(self):
            if hasattr(self, '_m_raw_1'):
                return self._m_raw_1

            if self.channel_offset[0] > 0:
                pass
                _pos = self._io.pos()
                self._io.seek(self.channel_offset[0] + self.z_pt_offset)
                self._m_raw_1 = self._io.read_bytes(self.len_raw_1)
                self._io.seek(_pos)

            return getattr(self, '_m_raw_1', None)

        @property
        def raw_2(self):
            if hasattr(self, '_m_raw_2'):
                return self._m_raw_2

            if self.channel_offset[1] > 0:
                pass
                _pos = self._io.pos()
                self._io.seek(self.channel_offset[1] + self.z_pt_offset)
                self._m_raw_2 = self._io.read_bytes(self.len_raw_2)
                self._io.seek(_pos)

            return getattr(self, '_m_raw_2', None)

        @property
        def raw_3(self):
            if hasattr(self, '_m_raw_3'):
                return self._m_raw_3

            if self.channel_offset[2] > 0:
                pass
                _pos = self._io.pos()
                self._io.seek(self.channel_offset[2] + self.z_pt_offset)
                self._m_raw_3 = self._io.read_bytes(self.len_raw_3)
                self._io.seek(_pos)

            return getattr(self, '_m_raw_3', None)

        @property
        def raw_4(self):
            if hasattr(self, '_m_raw_4'):
                return self._m_raw_4

            if self.channel_offset[3] > 0:
                pass
                _pos = self._io.pos()
                self._io.seek(self.channel_offset[3] + self.z_pt_offset)
                self._m_raw_4 = self._io.read_bytes(self.len_raw_4)
                self._io.seek(_pos)

            return getattr(self, '_m_raw_4', None)

        @property
        def raw_depth(self):
            if hasattr(self, '_m_raw_depth'):
                return self._m_raw_depth

            self._m_raw_depth = (self.wfm_len // 2 if self.enabled.interwoven else self.wfm_len)
            return getattr(self, '_m_raw_depth', None)

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
            self._io.seek(self.setup_offset - 56)
            self._raw__m_setup = self._io.read_bytes(self.len_setup)
            _io__raw__m_setup = KaitaiStream(BytesIO(self._raw__m_setup))
            self._m_setup = Rigol2000Wfm.SetupBlock(_io__raw__m_setup, self, self._root)
            self._io.seek(_pos)
            return getattr(self, '_m_setup', None)

        @property
        def time_offset(self):
            if hasattr(self, '_m_time_offset'):
                return self._m_time_offset

            self._m_time_offset = 1.0E-12 * self.time_offset_ps
            return getattr(self, '_m_time_offset', None)

        @property
        def time_scale(self):
            if hasattr(self, '_m_time_scale'):
                return self._m_time_scale

            self._m_time_scale = 1.0E-12 * self.time_scale_ps
            return getattr(self, '_m_time_scale', None)


    class SetupBlock(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            super(Rigol2000Wfm.SetupBlock, self).__init__(_io)
            self._parent = _parent
            self._root = _root
            self._read()

        def _read(self):
            pass


        def _fetch_instances(self):
            pass
            _ = self.trigger_holdoff_ns
            if hasattr(self, '_m_trigger_holdoff_ns'):
                pass

            _ = self.trigger_levels
            if hasattr(self, '_m_trigger_levels'):
                pass
                self._m_trigger_levels._fetch_instances()

            _ = self.trigger_mode_code
            if hasattr(self, '_m_trigger_mode_code'):
                pass

            _ = self.trigger_source_primary
            if hasattr(self, '_m_trigger_source_primary'):
                pass

            _ = self.trigger_source_shadow
            if hasattr(self, '_m_trigger_source_shadow'):
                pass


        @property
        def trigger_holdoff_ns(self):
            if hasattr(self, '_m_trigger_holdoff_ns'):
                return self._m_trigger_holdoff_ns

            if self._io.size() >= 543:
                pass
                _pos = self._io.pos()
                self._io.seek(539)
                self._m_trigger_holdoff_ns = self._io.read_u4le()
                self._io.seek(_pos)

            return getattr(self, '_m_trigger_holdoff_ns', None)

        @property
        def trigger_levels(self):
            if hasattr(self, '_m_trigger_levels'):
                return self._m_trigger_levels

            if self._io.size() >= 559:
                pass
                _pos = self._io.pos()
                self._io.seek(547)
                self._m_trigger_levels = Rigol2000Wfm.TriggerLevelBlock(self._io, self, self._root)
                self._io.seek(_pos)

            return getattr(self, '_m_trigger_levels', None)

        @property
        def trigger_mode_code(self):
            if hasattr(self, '_m_trigger_mode_code'):
                return self._m_trigger_mode_code

            if self._io.size() >= 539:
                pass
                _pos = self._io.pos()
                self._io.seek(535)
                self._m_trigger_mode_code = self._io.read_u4le()
                self._io.seek(_pos)

            return getattr(self, '_m_trigger_mode_code', None)

        @property
        def trigger_source_primary(self):
            if hasattr(self, '_m_trigger_source_primary'):
                return self._m_trigger_source_primary

            if self._io.size() >= 520:
                pass
                _pos = self._io.pos()
                self._io.seek(519)
                self._m_trigger_source_primary = KaitaiStream.resolve_enum(Rigol2000Wfm.SetupTriggerSourceEnum, self._io.read_u1())
                self._io.seek(_pos)

            return getattr(self, '_m_trigger_source_primary', None)

        @property
        def trigger_source_shadow(self):
            if hasattr(self, '_m_trigger_source_shadow'):
                return self._m_trigger_source_shadow

            if self._io.size() >= 524:
                pass
                _pos = self._io.pos()
                self._io.seek(523)
                self._m_trigger_source_shadow = KaitaiStream.resolve_enum(Rigol2000Wfm.SetupTriggerSourceEnum, self._io.read_u1())
                self._io.seek(_pos)

            return getattr(self, '_m_trigger_source_shadow', None)


    class TriggerLevelBlock(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            super(Rigol2000Wfm.TriggerLevelBlock, self).__init__(_io)
            self._parent = _parent
            self._root = _root
            self._read()

        def _read(self):
            self.ch1_level_uv = self._io.read_s4le()
            self.ch2_level_uv = self._io.read_s4le()
            self.ext_level_uv = self._io.read_s4le()


        def _fetch_instances(self):
            pass


    @property
    def header(self):
        if hasattr(self, '_m_header'):
            return self._m_header

        _pos = self._io.pos()
        self._io.seek(0)
        self._m_header = Rigol2000Wfm.Header(self._io, self, self._root)
        self._io.seek(_pos)
        return getattr(self, '_m_header', None)


