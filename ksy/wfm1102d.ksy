meta:
  id: wfm1102d
  title: Rigol DS1102D oscilloscope waveform file format
  file-extension: wfm
  endian: le

doc: Rigol DS1102D scope .wmf format abstracted from Matlab script.

doc-ref: https://www.mathworks.com/matlabcentral/fileexchange/18999-read-binary-rigol-waveforms

instances:
  header:
    pos: 0
    type: header
  data:
    pos: 272
    type: channel_data

types:
  header:
    seq:
      - id: magic           # 00 (file pos)
        contents: [0xa5, 0xa5]
      - id: serial_number   # 02 unverified
        size: 16
        type: str
        encoding: ascii
      - id: unknown_1       # 18
        size: 4
      - id: firmware_version # 22 unverified
        size: 16
        type: str
        encoding: ascii
      - id: npts            # 28
        type: u4
      - id: unknown_2       # 32
        size: 4
      - id: ch1_desc        # 36
        type: channel_desc
      - id: unknown_3       # 50
        size: 10
      - id: ch2_desc        # 60
        type: channel_desc
      - id: unknown_4       # 74
        size: 10
      - id: time_scale      # 84
        type: u8
      - id: time_delay      # 92
        type: s8
      - id: samp_freq       # 100
        type: f4
      - id: unknown_5       # 104
        size: 38
      - id: trigger_mode    # 142
        type: u2
        enum: mode
      - id: trigger_source  # 144
        type: u1
        enum: source

  channel_desc:  # 14 bytes total
    seq:
      - id: scale
        type: u4
      - id: position
        type: u4
      - id: unknown_1
        size: 1
      - id: probe
        type : u2
        enum: probe_attenuation
      - id: unknown_2
        size: 1
      - id: enabled
        type: u1

  channel_data:
    seq:
      - id: channel_1
        type: u1
        repeat: expr
        repeat-expr: _root.header.ch1_desc.enabled * _root.header.npts

      - id: channel_2
        type: u1
        repeat: expr
        repeat-expr: _root.header.ch2_desc.enabled * _root.header.npts

enums:
  probe_attenuation:
    0x3F80: x1
    0x4120: x10
    0x42C8: x100
    0x447A: x1000

  source:
    0 : ch1
    1 : ch2
    2 : ext
    3 : ext5
    5 : ac_line
    7 : dig_ch

  mode:
    0x0000 : edge
    0x0101 : pulse
    0x0202 : slope
    0x0303 : video
    0x0004 : alt
    0x0505 : pattern
    0x0606 : duration
