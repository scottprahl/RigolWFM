meta:
  id: wfm1000c
  title: Rigol DS1020C oscilloscope waveform file format
  file-extension: wfm
  endian: le

doc: |
  Rigol DS2000 .wmf format abstracted from a python script.

doc-ref: |
  https://www.tablix.org/~avian/blog/archives/2019/08/quick_and_ugly_wfm_data_export_for_rigol_ds2072a/#comment_0000

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
      - id: ch1_offset       # 68
        pos: 0x44
        type: u4
      - id: ch2_offset       # 72
        pos: 0x48
        type: u4
      - id: points           # 92
        pos: 0x5c
        type: u4
      - id: sample_rate_hz   # 380
        pos: 0x17c
        type: u4

    instances:
      seconds_per_point:
        value: 1.0/sample_rate_hz

  raw_data:
    seq:
      - id: ch1
        pos: _root.header.ch1_offset
        type: u1
        repeat: expr
        repeat-expr: _root.header.points

      - id: ch2
        pos: _root.header.ch2_offset
        type: u1
        repeat: expr
        repeat-expr: _root.header.points

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
