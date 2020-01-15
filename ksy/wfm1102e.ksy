meta:
  id: wfm1102e
  title: Rigol DS1102E oscilloscope waveform file format
  file-extension: wfm
  endian: le

doc: |
  Rigol DS1102E scope .wmf format abstracted from a python script

doc-ref: !
  The Matlab script is from
  https://www.mathworks.com/matlabcentral/fileexchange/18999-read-binary-rigol-waveforms
  The Pascal program is from
  https://sourceforge.net/projects/wfmreader/files/WFMReaderV2_FullSourceWithReqLibsAndCompiledDemo.zip
  The DS4000 parser is from
  https://github.com/Cat-Ion/rigol-ds4000-wfm

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
      - id: magic            # 00 (file pos)
        contents: [0xa5, 0xa5]
      - id: padding1         # 02
        contents: [0x00, 0x00]
      - id: unused1          # 04 unverified
        size: 4
      - id: unused2          # 08 unverified
        size: 4
      - id: unused3          # 12 unverified
        size: 4
      - id: adc_mode         # 16
        type: u1
      - id: padding2         # 17
        size: 3
      - id: roll_stop        # 20
        type: u4
      - id: unused4          # 24
        size: 4
      - id: npts             # 28
        type: u4
      - id: active_channel   # 32
        type: u1
      - id: padding3         # 33
        size: 3
      - id: ch1              # 36
        type: channel_header
      - id: ch2              # 60
        type: channel_header
      - id: time_scale       # 84
        type: u8
      - id: time_delay       # 92
        type: s8
      - id: samp_freq        # 100
        type: f4
      - id: unknown_5        # 104
        size: 38
      - id: trigger_mode     # 142
        type: u1
        enum: mode
      - id: unknown_6        # 143
        size: 1
      - id: trigger_source   # 144
        type: u1
        enum: source

  channel_header:   # 24 bytes total
    seq:
      - id: scale            # 36, 60
        type: u4
      - id: position         # 40, 64
        type: u4
      - id: unknown_1        # 44, 68
        size: 2
      - id: probe            # 46, 70
        type: u2
        enum: probe_attenuation
      - id: inverted         # 48, 72
        size: 1
      - id: enabled          # 49, 73
        type: u1
      - id: unknown_2        # 50, 74
        size: 2
      - id: scale_orig       # 52, 76
        type: u4
      - id: position_orig    # 56, 80
        type: u4
        

  channel_data:
    seq:
      - id: ch1
        type: u1
        repeat: expr
        repeat-expr: _root.header.ch1.enabled * _root.header.npts

      - id: ch2
        type: u1
        repeat: expr
        repeat-expr: _root.header.ch2.enabled * _root.header.npts

enums:
  probe_attenuation:
    0x3F80: x1
    0x4120: x10
    0x42C8: x100
    0x43FA: x500
    0x447A: x1000

  source:
    0 : ch1
    1 : ch2
    2 : ext
    3 : ext5
    5 : ac_line
    7 : dig_ch

  mode:
    0 : edge
    1 : pulse
    2 : slope
    3 : video
    4 : alt
    5 : pattern
    6 : duration
