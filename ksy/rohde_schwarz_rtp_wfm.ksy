meta:
  id: rohde_schwarz_rtp_wfm
  title: Rohde & Schwarz RTP Waveform Payload
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
