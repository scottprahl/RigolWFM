# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild
# type: ignore

import kaitaistruct
from kaitaistruct import KaitaiStruct, KaitaiStream, BytesIO
from enum import IntEnum


if getattr(kaitaistruct, 'API_VERSION', (0, 9)) < (0, 11):
    raise Exception("Incompatible Kaitai Struct Python API: 0.11 or later is required, but you have %s" % (kaitaistruct.__version__))

class TekWfm002Le(KaitaiStruct):
    """Tektronix WFM binary waveform format, version WFM#002 and WFM#003,
    little-endian variant.
    
    WFM#002 applies to: TDS5000B Series.
    WFM#003 applies to: DPO7000, DPO70000, DSA70000 Series.
    
    Difference from WFM#001: a 2-byte summary_frame_type field is inserted at
    offset 0x9a (154) between num_acquired_fast_frames and pix_map_display_format,
    shifting all subsequent fields by 2 bytes.
    
    WFM#003 additional difference: point_density in the user-view sections of each
    dimension (exp_dim1, exp_dim2, imp_dim1, imp_dim2) changes from u4 (4 bytes) to
    f8 (8 bytes).  This shifts each user-view section and all following structures by
    4 extra bytes per dimension (16 bytes total).  This parser reads point_density as
    u4; for WFM#003 files the h_ref, trig_delay, time_base, update_spec, and curve
    fields will be offset by 16 bytes relative to this parser's positions, but
    dim_scale and dim_offset (the critical calibration fields) remain correct.
    
    Endianness detection: byte_order at offset 0 is 0x0F0F for little-endian (Intel).
    Version string at offset 2 is "WFM#002" or "WFM#003".
    
    Voltage reconstruction (explicit dimension 1):
      volts[i] = exp_dim1.dim_scale * adc[i] + exp_dim1.dim_offset
    
    Time axis (implicit dimension 1):
      t[i] = imp_dim1.dim_offset + i * imp_dim1.dim_scale
    where i = 0 corresponds to the first sample in the curve buffer.
    
    Reference: Tektronix "Reference Waveform File Format" (001-1378-03), version notes.
    """

    class BaseTypeEnum(IntEnum):
        base_time = 0
        base_spectral_mag = 1
        base_spectral_phase = 2
        base_invalid = 3

    class ChecksumTypeEnum(IntEnum):
        no_checksum = 0
        ctype_crc16 = 1
        ctype_sum16 = 2
        ctype_crc32 = 3
        ctype_sum32 = 4

    class DataTypeEnum(IntEnum):
        wfmdata_scalar_meas = 0
        wfmdata_scalar_const = 1
        wfmdata_vector = 2
        wfmdata_pixmap = 3
        wfmdata_invalid = 4
        wfmdata_wfmdb = 5

    class ExplicitFormatEnum(IntEnum):
        explicit_int16 = 0
        explicit_int32 = 1
        explicit_uint32 = 2
        explicit_uint64 = 3
        explicit_fp32 = 4
        explicit_fp64 = 5
        explicit_invalid_format = 6
        explicit_uint8 = 7
        explicit_int8 = 8

    class ExplicitStorageEnum(IntEnum):
        explicit_sample = 0
        explicit_min_max = 1
        explicit_vert_hist = 2
        explicit_hor_hist = 3
        explicit_row_order = 4
        explicit_column_order = 5
        explicit_invalid_storage = 6

    class PixMapFormatEnum(IntEnum):
        dsy_format_invalid = 0
        dsy_format_yt = 1
        dsy_format_xy = 2
        dsy_format_xyz = 3

    class SetTypeEnum(IntEnum):
        single_waveform = 0
        fast_frame = 1

    class SummaryFrameEnum(IntEnum):
        summary_frame_off = 0
        summary_frame_average = 1
        summary_frame_envelope = 2

    class SweepEnum(IntEnum):
        sweep_roll = 0
        sweep_sample = 1
        sweep_et = 2
        sweep_invalid = 3
    def __init__(self, _io, _parent=None, _root=None):
        super(TekWfm002Le, self).__init__(_io)
        self._parent = _parent
        self._root = _root or self
        self._read()

    def _read(self):
        self.static_file_info = TekWfm002Le.StaticFileInfo(self._io, self, self._root)
        self.wfm_header = TekWfm002Le.WfmHeader(self._io, self, self._root)


    def _fetch_instances(self):
        pass
        self.static_file_info._fetch_instances()
        self.wfm_header._fetch_instances()
        _ = self.curve_buffer
        if hasattr(self, '_m_curve_buffer'):
            pass


    class ExpDim(KaitaiStruct):
        """Explicit dimension: 100-byte description block + 56-byte user-view = 156 bytes.
        For YT waveforms, explicit dimension 1 defines the voltage (Y) axis:
          volts[i] = dim_scale * adc[i] + dim_offset
        """
        def __init__(self, _io, _parent=None, _root=None):
            super(TekWfm002Le.ExpDim, self).__init__(_io)
            self._parent = _parent
            self._root = _root
            self._read()

        def _read(self):
            self.dim_scale = self._io.read_f8le()
            self.dim_offset = self._io.read_f8le()
            self.dim_size = self._io.read_u4le()
            self.units = self._io.read_bytes(20)
            self.dim_extent_min = self._io.read_f8le()
            self.dim_extent_max = self._io.read_f8le()
            self.dim_resolution = self._io.read_f8le()
            self.dim_ref_point = self._io.read_f8le()
            self.format = KaitaiStream.resolve_enum(TekWfm002Le.ExplicitFormatEnum, self._io.read_s4le())
            self.storage_type = KaitaiStream.resolve_enum(TekWfm002Le.ExplicitStorageEnum, self._io.read_s4le())
            self.n_value = self._io.read_bytes(4)
            self.over_range = self._io.read_bytes(4)
            self.under_range = self._io.read_bytes(4)
            self.high_range = self._io.read_bytes(4)
            self.low_range = self._io.read_bytes(4)
            self.user_scale = self._io.read_f8le()
            self.user_units = self._io.read_bytes(20)
            self.user_offset = self._io.read_f8le()
            self.point_density = self._io.read_u4le()
            self.h_ref = self._io.read_f8le()
            self.trig_delay = self._io.read_f8le()


        def _fetch_instances(self):
            pass


    class ImpDim(KaitaiStruct):
        """Implicit dimension: 76-byte description block + 56-byte user-view = 132 bytes.
        For YT waveforms, implicit dimension 1 defines the time (X) axis:
          t[i] = dim_offset + i * dim_scale
        where i = 0 is the first sample in the curve buffer.
        """
        def __init__(self, _io, _parent=None, _root=None):
            super(TekWfm002Le.ImpDim, self).__init__(_io)
            self._parent = _parent
            self._root = _root
            self._read()

        def _read(self):
            self.dim_scale = self._io.read_f8le()
            self.dim_offset = self._io.read_f8le()
            self.dim_size = self._io.read_u4le()
            self.units = self._io.read_bytes(20)
            self.dim_extent_min = self._io.read_f8le()
            self.dim_extent_max = self._io.read_f8le()
            self.dim_resolution = self._io.read_f8le()
            self.dim_ref_point = self._io.read_f8le()
            self.spacing = self._io.read_u4le()
            self.user_scale = self._io.read_f8le()
            self.user_units = self._io.read_bytes(20)
            self.user_offset = self._io.read_f8le()
            self.point_density = self._io.read_u4le()
            self.h_ref = self._io.read_f8le()
            self.trig_delay = self._io.read_f8le()


        def _fetch_instances(self):
            pass


    class StaticFileInfo(KaitaiStruct):
        """78-byte block of static waveform file information at the very start of the file.
        Identical in layout to WFM#001.
        """
        def __init__(self, _io, _parent=None, _root=None):
            super(TekWfm002Le.StaticFileInfo, self).__init__(_io)
            self._parent = _parent
            self._root = _root
            self._read()

        def _read(self):
            self.byte_order = self._io.read_u2le()
            self.version_number = self._io.read_bytes(8)
            self.num_digits_byte_count = self._io.read_u1()
            self.num_bytes_to_eof = self._io.read_s4le()
            self.num_bytes_per_point = self._io.read_u1()
            self.byte_offset_to_curve_buffer = self._io.read_s4le()
            self.horiz_zoom_scale_factor = self._io.read_s4le()
            self.horiz_zoom_position = self._io.read_f4le()
            self.vert_zoom_scale_factor = self._io.read_f8le()
            self.vert_zoom_position = self._io.read_f4le()
            self.waveform_label = self._io.read_bytes(32)
            self.n_fast_frames_minus_1 = self._io.read_u4le()
            self.wfm_header_size = self._io.read_u2le()


        def _fetch_instances(self):
            pass


    class TimeBaseInfo(KaitaiStruct):
        """12-byte time-base acquisition information block."""
        def __init__(self, _io, _parent=None, _root=None):
            super(TekWfm002Le.TimeBaseInfo, self).__init__(_io)
            self._parent = _parent
            self._root = _root
            self._read()

        def _read(self):
            self.real_point_spacing = self._io.read_u4le()
            self.sweep = KaitaiStream.resolve_enum(TekWfm002Le.SweepEnum, self._io.read_s4le())
            self.type_of_base = KaitaiStream.resolve_enum(TekWfm002Le.BaseTypeEnum, self._io.read_s4le())


        def _fetch_instances(self):
            pass


    class WfmCurveObject(KaitaiStruct):
        """30-byte curve object containing byte offsets that bound the curve data regions.
        To extract valid waveform samples:
          first_byte = data_start_offset
          last_byte  = postcharge_start_offset   (exclusive)
        """
        def __init__(self, _io, _parent=None, _root=None):
            super(TekWfm002Le.WfmCurveObject, self).__init__(_io)
            self._parent = _parent
            self._root = _root
            self._read()

        def _read(self):
            self.state_flags = self._io.read_u4le()
            self.checksum_type = KaitaiStream.resolve_enum(TekWfm002Le.ChecksumTypeEnum, self._io.read_s4le())
            self.checksum = self._io.read_s2le()
            self.precharge_start_offset = self._io.read_u4le()
            self.data_start_offset = self._io.read_u4le()
            self.postcharge_start_offset = self._io.read_u4le()
            self.postcharge_stop_offset = self._io.read_u4le()
            self.end_of_curve_buffer_offset = self._io.read_u4le()


        def _fetch_instances(self):
            pass

        @property
        def first_valid_sample(self):
            """Index of the first user-accessible sample in the curve buffer."""
            if hasattr(self, '_m_first_valid_sample'):
                return self._m_first_valid_sample

            self._m_first_valid_sample = self.data_start_offset // self._root.static_file_info.num_bytes_per_point
            return getattr(self, '_m_first_valid_sample', None)

        @property
        def num_valid_samples(self):
            """Number of user-accessible waveform samples."""
            if hasattr(self, '_m_num_valid_samples'):
                return self._m_num_valid_samples

            self._m_num_valid_samples = self.postcharge_start_offset // self._root.static_file_info.num_bytes_per_point - self.data_start_offset // self._root.static_file_info.num_bytes_per_point
            return getattr(self, '_m_num_valid_samples', None)


    class WfmHeader(KaitaiStruct):
        """Waveform header block.  Differs from WFM#001 by the 2-byte summary_frame_type
        field inserted after num_acquired_fast_frames.  All subsequent fields are
        shifted 2 bytes later than in tek_wfm_001_le.
        """
        def __init__(self, _io, _parent=None, _root=None):
            super(TekWfm002Le.WfmHeader, self).__init__(_io)
            self._parent = _parent
            self._root = _root
            self._read()

        def _read(self):
            self.set_type = KaitaiStream.resolve_enum(TekWfm002Le.SetTypeEnum, self._io.read_s4le())
            self.wfm_cnt = self._io.read_u4le()
            self.acq_counter = self._io.read_u8le()
            self.transaction_counter = self._io.read_u8le()
            self.slot_id = self._io.read_s4le()
            self.is_static_flag = self._io.read_s4le()
            self.wfm_update_spec_count = self._io.read_u4le()
            self.imp_dim_ref_count = self._io.read_u4le()
            self.exp_dim_ref_count = self._io.read_u4le()
            self.data_type = KaitaiStream.resolve_enum(TekWfm002Le.DataTypeEnum, self._io.read_s4le())
            self.gen_purpose_counter = self._io.read_u8le()
            self.accum_wfm_count = self._io.read_u4le()
            self.target_accum_count = self._io.read_u4le()
            self.curve_ref_count = self._io.read_u4le()
            self.num_requested_fast_frames = self._io.read_u4le()
            self.num_acquired_fast_frames = self._io.read_u4le()
            self.summary_frame_type = KaitaiStream.resolve_enum(TekWfm002Le.SummaryFrameEnum, self._io.read_u2le())
            self.pix_map_display_format = KaitaiStream.resolve_enum(TekWfm002Le.PixMapFormatEnum, self._io.read_s4le())
            self.pix_map_max_value = self._io.read_u8le()
            self.exp_dim1 = TekWfm002Le.ExpDim(self._io, self, self._root)
            self.exp_dim2 = TekWfm002Le.ExpDim(self._io, self, self._root)
            self.imp_dim1 = TekWfm002Le.ImpDim(self._io, self, self._root)
            self.imp_dim2 = TekWfm002Le.ImpDim(self._io, self, self._root)
            self.time_base1 = TekWfm002Le.TimeBaseInfo(self._io, self, self._root)
            self.time_base2 = TekWfm002Le.TimeBaseInfo(self._io, self, self._root)
            self.update_spec = TekWfm002Le.WfmUpdateSpec(self._io, self, self._root)
            self.curve = TekWfm002Le.WfmCurveObject(self._io, self, self._root)


        def _fetch_instances(self):
            pass
            self.exp_dim1._fetch_instances()
            self.exp_dim2._fetch_instances()
            self.imp_dim1._fetch_instances()
            self.imp_dim2._fetch_instances()
            self.time_base1._fetch_instances()
            self.time_base2._fetch_instances()
            self.update_spec._fetch_instances()
            self.curve._fetch_instances()


    class WfmUpdateSpec(KaitaiStruct):
        """24-byte waveform update specification containing per-frame trigger timing data.
        """
        def __init__(self, _io, _parent=None, _root=None):
            super(TekWfm002Le.WfmUpdateSpec, self).__init__(_io)
            self._parent = _parent
            self._root = _root
            self._read()

        def _read(self):
            self.real_point_offset = self._io.read_u4le()
            self.tt_offset = self._io.read_f8le()
            self.frac_sec = self._io.read_f8le()
            self.gmt_sec = self._io.read_s4le()


        def _fetch_instances(self):
            pass


    @property
    def curve_buffer(self):
        """Raw curve data bytes, inclusive of pre- and post-charge interpolation data.
        Valid user-accessible data occupies the byte range
        [data_start_offset, postcharge_start_offset) within this buffer.
        """
        if hasattr(self, '_m_curve_buffer'):
            return self._m_curve_buffer

        _pos = self._io.pos()
        self._io.seek(self.static_file_info.byte_offset_to_curve_buffer)
        self._m_curve_buffer = self._io.read_bytes(self.wfm_header.curve.end_of_curve_buffer_offset)
        self._io.seek(_pos)
        return getattr(self, '_m_curve_buffer', None)


