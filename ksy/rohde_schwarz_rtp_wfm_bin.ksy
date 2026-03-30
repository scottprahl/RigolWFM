meta:
  id: rohde_schwarz_rtp_wfm_bin
  title: Rohde & Schwarz RTP WFM.BIN Binary Format
  ks-version: 0.9
  endian: le
  application:
    - Rohde & Schwarz RTP / RTO / RTM oscilloscope waveform exports
  file-extension:
    - Wfm.bin
doc: |
  Rohde & Schwarz oscilloscope waveform payload file used alongside an XML
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

seq:
  - id: format_code
    type: u4
    enum: format_code_enum
    doc: |
      R&S waveform format code observed in vendor fixtures.
      0 = int8 raw ADC samples
      1 = int16 raw ADC samples
      4 = float32 voltage samples
      6 = XYDOUBLEFLOAT records (float64 time + float32 channel values)
  - id: record_length
    type: u4
    doc: |
      Hardware record length reported in the payload file header. In vendor
      samples this matches the XML `SignalHardwareRecordLength` value.
  - id: payload
    size-eos: true
    doc: Raw waveform bytes; interpretation depends on the XML metadata.

instances:
  payload_size:
    value: payload.size
    doc: Number of raw waveform bytes stored after the 8-byte file header.

enums:
  format_code_enum:
    0: int8bit
    1: int16bit
    4: float32
    6: xydoublefloat
