meta:
  id: wfm2000
  title: Rigol DS2000 oscilloscope waveform file format
  file-extension: wfm
  endian: le

doc: |
  Rigol DS2000 .wmf format abstracted from a python script.  This is very far
  from complete.

doc-ref: |
  https://www.tablix.org/~avian/blog/archives/2019/08/quick_and_ugly_wfm_data_export_for_rigol_ds2072a/#comment_0000

instances:
  header:
    pos: 0
    type: header

types:
  header:
    seq:
      - id: magic            # 00 (file pos)
        contents: [0xa5, 0xa5, 0x00, 0x00]
      - id: skip1            #  4
        size: 64
      - id: ch1_location     # 68
        type: u4
      - id: ch2_location     # 72
        type: u4
      - id: skip_2           # 76
        size: 16
      - id: points           # 92
        type: u4
      - id: skip_3           # 96
        size: 284
      - id: sample_rate_hz   # 380
        type: u4

    instances:
      seconds_per_point:
        value: 1.0/sample_rate_hz
      time_scale:
        value: sample_rate_hz*points/10.0
      time_offset:
        value: 0.0

      raw_1:
        pos: ch1_location
        type: u1
        repeat: expr
        repeat-expr: points

      raw_2:
        pos: ch2_location
        type: u1
        repeat: expr
        repeat-expr: points

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
