# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild
# type: ignore

import kaitaistruct
from kaitaistruct import KaitaiStruct, KaitaiStream, BytesIO
from enum import IntEnum


if getattr(kaitaistruct, 'API_VERSION', (0, 9)) < (0, 11):
    raise Exception("Incompatible Kaitai Struct Python API: 0.11 or later is required, but you have %s" % (kaitaistruct.__version__))

class RigolDho8001000Wfm(KaitaiStruct):
    """Proprietary waveform format used by Rigol DHO800/DHO1000 series
    oscilloscopes (reverse-engineered from DHO1074 and DHO824 captures).
    
    File layout:
      [File Header:      24 bytes  - partially unknown]
      [Metadata blocks:  variable  - 12-byte header + zlib-compressed content each]
      [Zero padding:     variable  - null bytes between block region and data]
      [Data section:     variable  - 40-byte header + uint16 ADC samples]
    
    ---- Metadata blocks ----
    Each block has a 12-byte header (six u16 LE fields) followed by len_content_raw
    bytes of content.  When comp_size < decomp_size the content bytes
    [0 .. comp_size-1] are zlib-compressed; the remainder is zero padding.
    Blocks are read until a terminator block where len_content_raw == 0.
    
    Key blocks (identified by block_id and block_type):
      block_id=1..4, block_type=9  (~88-96 bytes decompressed)
        Offset  1..8  - int64 LE - voltage scale numerator
        scale = i64 / 750_000_000_000
        Offset 38..45 - int64 LE - channel voltage centre x 1e8
        v_center = i64 / 1e8
    
      block_type=6  (~1628 bytes decompressed)
        Offset 36..39 - int32 LE - CH1 voltage centre x 1e8
        Legacy fallback for older single-channel captures.
    
    ---- Voltage calibration ----
      scale    = i64_channel / 750_000_000_000
      v_center = i64_channel / 1e8
      offset   = -v_center - scale * 32768
      volts[i] = scale * raw_uint16[i] + offset
    
    ---- Data section ----
    The data section starts after the zero-padding region that follows the
    last metadata block.  Its offset cannot be determined statically; a
    sequential scan for the first non-zero byte is required.
    
    Data section header (40 bytes):
      offset+ 0:  u64 LE  - raw total sample count across all enabled channels.
                             DHO1000 firmware stores a value slightly larger than
                             the true total (~+64 samples); n_ch is recovered via
                             round(n_pts_u64 / n_pts_per_channel) rather than
                             exact division.
      offset+ 8:  8 bytes - capture marker (opaque)
      offset+16:  u32 LE  - x_increment in ADC ticks (see below)
      offset+20:  u32 LE  - unknown (observed: 77)
      offset+24:  u32 LE  - n_pts per enabled channel
      offset+28:  u32 LE  - n_pts per enabled channel (repeated)
      offset+32:  u32 LE  - timestamp / unknown
      offset+36:  u32 LE  - unknown (observed: 120 for single-channel, 0 for multi)
      offset+40:  uint16 LE samples begin (n_pts_per_channel × n_channels × 2 bytes)
    
    ---- Time axis ----
    The x_increment field stores the sampling interval as an integer count of
    ADC clock ticks.  The tick duration is a fixed hardware property:
    
      DHO800  (e.g. DHO824):  0.8 ns / tick  — one cycle of the 1.25 GSa/s ADC
      DHO1000 (e.g. DHO1074): 10 ns / tick   — one cycle of a 100 MHz reference clock
    
    x_origin is not stored explicitly.  For the common case of a centered
    trigger (trigger at 50% of the capture window, which is the scope default):
      x_origin = -(n_pts_per_channel / 2) * x_increment
      t[i]     =  x_origin + i * x_increment
    
    Trigger position as a percentage of the capture window is likely encoded
    in the metadata block with id=282, u32 at byte offset 12 (observed: 50 for
    center trigger in all available DHO800 and DHO1000 test captures).
    
    LIMITATION: This KSY describes the block region only.  The zero-padding
    region and the data section require sequential runtime scanning and cannot
    be expressed as fixed-offset KSY instances.
    
    Sources used for this KSY binary format: reverse-engineering from the
    checked-in `DHO1074.wfm`, `DHO824-ch1.wfm`, `DHO824-ch12.wfm`, and
    `DHO824-ch1234.wfm` captures, cross-checked against matching `.bin` exports
    from the same scopes.
    
    Tested file formats: real repo fixtures `DHO1074.wfm`, `DHO824-ch1.wfm`,
    `DHO824-ch12.wfm`, and `DHO824-ch1234.wfm`, with matching `.bin`
    comparisons used for time-axis and voltage-correlation regressions.
    
    Oscilloscope models this format may apply to: `DHO804`, `DHO812`, `DHO814`,
    `DHO824`, `DHO1072`, `DHO1074`, `DHO1102`, `DHO1202`, and related
    `DHO800` / `DHO1000` family scopes that write this proprietary `.wfm`
    container.
    """

    class BlockTypeEnum(IntEnum):
        dho800_channel_params = 5
        settings = 6
        channel_params = 9
    def __init__(self, _io, _parent=None, _root=None):
        super(RigolDho8001000Wfm, self).__init__(_io)
        self._parent = _parent
        self._root = _root or self
        self._read()

    def _read(self):
        self.file_header = RigolDho8001000Wfm.FileHeader(self._io, self, self._root)
        self.blocks = []
        i = 0
        while True:
            _ = RigolDho8001000Wfm.Block(self._io, self, self._root)
            self.blocks.append(_)
            if  ((_.len_content_raw == 0) and (_.comp_size == 0)) :
                break
            i += 1


    def _fetch_instances(self):
        pass
        self.file_header._fetch_instances()
        for i in range(len(self.blocks)):
            pass
            self.blocks[i]._fetch_instances()


    class Block(KaitaiStruct):
        """One metadata block.  A block with len_content_raw == 0 and comp_size == 0
        signals the end of the metadata region.
        """
        def __init__(self, _io, _parent=None, _root=None):
            super(RigolDho8001000Wfm.Block, self).__init__(_io)
            self._parent = _parent
            self._root = _root
            self._read()

        def _read(self):
            self.block_id = self._io.read_u2le()
            self.block_type = KaitaiStream.resolve_enum(RigolDho8001000Wfm.BlockTypeEnum, self._io.read_u2le())
            self.decomp_size = self._io.read_u2le()
            self.comp_size = self._io.read_u2le()
            self.len_content_raw = self._io.read_u2le()
            self.reserved = self._io.read_u2le()
            self.content_raw = self._io.read_bytes(self.len_content_raw)


        def _fetch_instances(self):
            pass

        @property
        def is_channel_params(self):
            """True for one of the per-channel parameter blocks.
            Decompressed content bytes [1..8] hold an int64 LE voltage scale
            numerator, and bytes [38..45] hold an int64 LE channel center.
            """
            if hasattr(self, '_m_is_channel_params'):
                return self._m_is_channel_params

            self._m_is_channel_params =  ((self.block_type == RigolDho8001000Wfm.BlockTypeEnum.channel_params) and (self.block_id >= 1) and (self.block_id <= 4)) 
            return getattr(self, '_m_is_channel_params', None)

        @property
        def is_settings(self):
            """True for the trigger/display settings block.
            Decompressed content bytes [36..39] hold an int32 LE voltage centre
            value: v_center = i32 / 1e8.
            """
            if hasattr(self, '_m_is_settings'):
                return self._m_is_settings

            self._m_is_settings = self.block_type == RigolDho8001000Wfm.BlockTypeEnum.settings
            return getattr(self, '_m_is_settings', None)

        @property
        def is_terminator(self):
            """True for the sentinel block that ends the metadata region."""
            if hasattr(self, '_m_is_terminator'):
                return self._m_is_terminator

            self._m_is_terminator =  ((self.len_content_raw == 0) and (self.comp_size == 0)) 
            return getattr(self, '_m_is_terminator', None)


    class Dho1000ChannelParams(KaitaiStruct):
        """DHO1000 per-channel parameter payload after optional zlib decompression.
        Observed channel blocks store the displayed vertical center with the
        opposite sign from the sample reconstruction offset.
        """
        def __init__(self, _io, _parent=None, _root=None):
            super(RigolDho8001000Wfm.Dho1000ChannelParams, self).__init__(_io)
            self._parent = _parent
            self._root = _root
            self._read()

        def _read(self):
            self.reserved_0 = self._io.read_bytes(1)
            self.scale_numerator = self._io.read_s8le()
            self.reserved_1 = self._io.read_bytes(29)
            self.v_center_raw = self._io.read_s8le()
            self.reserved_2 = self._io.read_bytes_full()


        def _fetch_instances(self):
            pass

        @property
        def offset(self):
            if hasattr(self, '_m_offset'):
                return self._m_offset

            self._m_offset = -(self.v_center) - self.scale * 32768
            return getattr(self, '_m_offset', None)

        @property
        def scale(self):
            if hasattr(self, '_m_scale'):
                return self._m_scale

            self._m_scale = self.scale_numerator / 750000000000.0
            return getattr(self, '_m_scale', None)

        @property
        def v_center(self):
            if hasattr(self, '_m_v_center'):
                return self._m_v_center

            self._m_v_center = self.v_center_raw / 1.0E+8
            return getattr(self, '_m_v_center', None)


    class Dho800ChannelParams(KaitaiStruct):
        """DHO800 per-channel parameter payload after optional zlib decompression.
        The stored center value is negated and scaled in 1e-9 volt units.
        """
        def __init__(self, _io, _parent=None, _root=None):
            super(RigolDho8001000Wfm.Dho800ChannelParams, self).__init__(_io)
            self._parent = _parent
            self._root = _root
            self._read()

        def _read(self):
            self.reserved_0 = self._io.read_bytes(1)
            self.scale_numerator = self._io.read_s8le()
            self.reserved_1 = self._io.read_bytes(29)
            self.v_center_raw = self._io.read_s4le()
            self.reserved_2 = self._io.read_bytes_full()


        def _fetch_instances(self):
            pass

        @property
        def offset(self):
            if hasattr(self, '_m_offset'):
                return self._m_offset

            self._m_offset = self.v_center - self.scale * 32768
            return getattr(self, '_m_offset', None)

        @property
        def scale(self):
            if hasattr(self, '_m_scale'):
                return self._m_scale

            self._m_scale = self.scale_numerator / 7500000000000.0
            return getattr(self, '_m_scale', None)

        @property
        def v_center(self):
            if hasattr(self, '_m_v_center'):
                return self._m_v_center

            self._m_v_center = -(self.v_center_raw) / 1.0E+9
            return getattr(self, '_m_v_center', None)


    class FileHeader(KaitaiStruct):
        """24-byte file header.  Internal structure not fully reverse-engineered;
        treated as opaque.
        """
        def __init__(self, _io, _parent=None, _root=None):
            super(RigolDho8001000Wfm.FileHeader, self).__init__(_io)
            self._parent = _parent
            self._root = _root
            self._read()

        def _read(self):
            self.reserved = self._io.read_bytes(24)


        def _fetch_instances(self):
            pass


    class SettingsBlock(KaitaiStruct):
        """Trigger/display settings payload after optional zlib decompression.
        Older single-channel captures expose only the CH1 vertical center here.
        """
        def __init__(self, _io, _parent=None, _root=None):
            super(RigolDho8001000Wfm.SettingsBlock, self).__init__(_io)
            self._parent = _parent
            self._root = _root
            self._read()

        def _read(self):
            self.reserved_0 = self._io.read_bytes(36)
            self.v_center_raw = self._io.read_s4le()
            self.reserved_1 = self._io.read_bytes_full()


        def _fetch_instances(self):
            pass

        @property
        def v_center(self):
            if hasattr(self, '_m_v_center'):
                return self._m_v_center

            self._m_v_center = self.v_center_raw / 1.0E+8
            return getattr(self, '_m_v_center', None)



