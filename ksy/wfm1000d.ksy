meta:
  id: wfm1000d
  title: Rigol DS1020CD oscilloscope waveform file format
  file-extension: wfm
  endian: le

doc: |
  Rigol DS1020CD .wmf format abstracted from a Matlab script with the addition
  of a few fields found in a Pascal program.  Neither program really examines
  the header closely (meaning that they skip 26 bytes).

doc-ref: !
  The Matlab script is from
  https://www.mathworks.com/matlabcentral/fileexchange/18999-read-binary-rigol-waveforms
  The Pascal program is from
  https://sourceforge.net/projects/wfmreader/
  The DS4000 parser is from
  https://github.com/Cat-Ion/rigol-ds4000-wfm

instances:
  header:
    pos: 0
    type: header
  data:
    pos: 272
    type: raw_data

types:
  header:
    seq:
      - id: magic            # 00 (file pos)
        contents: [0xa5, 0xa5, 0x00, 0x00]
      - id: unknown_1        # 04
        type: u4
        repeat: expr
        repeat-expr: 6
      - id: ch1_points       # 28
        type: u4
      - id: active_channel   # 32
        type: u1
      - id: unknown_2        # 33
        size: 3
      - id: ch1              # 36
        type: channel_header
      - id: ch2              # 60
        type: channel_header
      - id: time_scale       # 84
        type: u8
      - id: time_delay       # 92
        type: s8
      - id: sample_frequency  # 100
        type: f4
      - id: unknown_3        # 104
        type: u4
        repeat: expr
        repeat-expr: 9
      - id: unknown_4        # 140
        type: u2
      - id: trigger_mode     # 142
        type: u1
        enum: trigger_mode_enum
      - id: unknown_6        # 143
        size: 1
      - id: trigger_source   # 144
        type: u1
        enum: trigger_source_enum

  channel_header:   # 24 bytes total
    seq:
      - id: scale            # 36, 60
        type: u4
      - id: position         # 40, 64
        type: u4
      - id: probe            # 44, 68
        type: f4
      - id: unused_bits_1    # 48, 72
        type: b7
      - id: inverted
        type: b1
      - id: unused_bits_2    # 49, 73
        type: b7
      - id: enabled
        type: b1
      - id: unknown_2        # 50, 74
        size: 2
      - id: scale_orig       # 52, 76
        type: u4
      - id: position_orig    # 56, 80
        type: u4

  raw_data:
    seq:
      - id: ch1
        type: u1
        repeat: expr
        repeat-expr: _root.header.npts
        if: _root.header.ch1.enabled

      - id: ch2
        type: u1
        repeat: expr
        repeat-expr: _root.header.npts
        if: _root.header.ch2.enabled

enums:
  trigger_source_enum:
    0: ch1
    1: ch2
    2: ext
    3: ext5
    5: ac_line
    7: dig_ch

  trigger_mode_enum:
    0: edge
    1: pulse
    2: slope
    3: video
    4: alt
    5: pattern
    6: duration
