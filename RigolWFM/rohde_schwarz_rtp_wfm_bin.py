# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild
# type: ignore

import kaitaistruct
from kaitaistruct import KaitaiStruct, KaitaiStream, BytesIO
from enum import IntEnum


if getattr(kaitaistruct, 'API_VERSION', (0, 9)) < (0, 11):
    raise Exception("Incompatible Kaitai Struct Python API: 0.11 or later is required, but you have %s" % (kaitaistruct.__version__))

class RohdeSchwarzRtpWfmBin(KaitaiStruct):
    """Rohde & Schwarz oscilloscope waveform payload file used alongside an XML
    metadata file with the same basename and a `.bin` extension.
    
    The binary file starts with an 8-byte little-endian header followed by the
    raw waveform payload. The companion XML file describes the signal format,
    channel layout, acquisition count, scaling, and timing needed to interpret
    the payload.
    
    Sources used for this KSY binary format: the checked-in RTP XML / payload /
    CSV fixtures under `tests/files/rs`, plus the vendor readers in
    `docs/vendors/rohde_schwarz/rs_file_reader-main`,
    `docs/vendors/rohde_schwarz/RS_scope_waveform.m`, and
    `docs/vendors/rohde_schwarz/readtrc`.
    
    Tested file formats: real repo fixtures `rs_rtp_01` through `rs_rtp_05`
    metadata `.bin` files with matching `.Wfm.bin` payloads and vendor
    `.Wfm.csv` reference exports, plus `rs_rtp_history_01.bin` as a negative
    multi-acquisition / history case.
    
    Oscilloscope models this format may apply to: Rohde & Schwarz `RTP` family
    oscilloscopes and likely closely related R&S instruments that export XML
    metadata plus `.Wfm.bin` float32 payloads; only RTP-style captures are
    checked in today.
    """

    class FormatCodeEnum(IntEnum):
        int8bit = 0
        int16bit = 1
        float32 = 4
        xydoublefloat = 6
    def __init__(self, _io, _parent=None, _root=None):
        super(RohdeSchwarzRtpWfmBin, self).__init__(_io)
        self._parent = _parent
        self._root = _root or self
        self._read()

    def _read(self):
        self.format_code = KaitaiStream.resolve_enum(RohdeSchwarzRtpWfmBin.FormatCodeEnum, self._io.read_u4le())
        self.record_length = self._io.read_u4le()
        self.payload = self._io.read_bytes_full()


    def _fetch_instances(self):
        pass

    @property
    def payload_size(self):
        """Number of raw waveform bytes stored after the 8-byte file header."""
        if hasattr(self, '_m_payload_size'):
            return self._m_payload_size

        self._m_payload_size = len(self.payload)
        return getattr(self, '_m_payload_size', None)


