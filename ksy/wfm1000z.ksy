meta:
  id: wfm1000z
  title: Rigol DS1000E oscilloscope waveform file format
  file-extension: wfm
  endian: le

doc: |
  Rigol DS1054Z scope .wmf format abstracted from a python script

instances:
  header:
    type: wfm_header
  data:
    type: raw_data

types:
  wfm_header:
    seq:
      - id: magic
        contents: [0xff,0x01]
      - id: unknown_2
        size: 6
      - id: model
        type: str
        size: 20
        terminator: 0
        encoding: UTF-8
      - id: fw_version
        type: str
        size: 20
        terminator: 0
        encoding: UTF-8
      - id: unknown_3
        size: 16

      - id: scale_d
        type: s8
      - id: time_delay
        type: s8
      - id: unknown_4
        size: 40
      - id: sample_rate
        type: f4

      - id: ch1
        type: channel_head

      - id: ch2
        type: channel_head

      - id: ch3
        type: channel_head

      - id: ch4
        type: channel_head

      - id: unknown_5
        size: 1759
        
      - id: unknown_5a
        size: 40
        if: fw_version == "00.04.02.SP4"
      - id: unknown_5b
        size: 55
        if: fw_version == "00.04.03.SP2"

      - id: ch4_subhead
        type: channel_subhead
      - id: ch3_subhead
        type: channel_subhead
      - id: ch2_subhead
        type: channel_subhead
      - id: ch1_subhead
        type: channel_subhead

      - id: unknown_6
        size: 475

      - id: ch1_range
        type: u4
      - id: ch2_range
        type: u4
      - id: ch3_range
        type: u4
      - id: ch4_range
        type: u4

      - id: ch1_shift
        type: s8
      - id: ch2_shift
        type: s8
      - id: ch3_shift
        type: s8
      - id: ch4_shift
        type: s8

      - id: unknown_7a
        size: 244
      - id: unknown_7b
        size: 4
        if: fw_version != "00.04.01.SP2"

      - id: npts
        type: u4

      - id: unknown_8a
        size: 148
      - id: unknown_8b
        if: fw_version == "00.04.01.SP2"
        size: 4

  channel_head:
    seq:
      - id: enabled
        type: u1
      - id: unknown_1
        size: 7
      - id: scale
        type: f4
      - id: shift
        type: f4
      - id: inverted
        type: u1
      - id: unknown_2
        size: 11

  channel_subhead:
    seq:
      - id: unknown_1
        size: 3
      - id: enabled
        type: u1
      - id: unknown_2
        size: 7
      - id: inverted
        type: u1
      - id: unknown_3
        size: 10
      - id: probe_attenuation
        type: s8
      - id: unknown_4
        size: 16
      - id: label
        type: str
        size: 4
        terminator: 0
        encoding: UTF-8
      - id: unknown_5
        size: 10

  raw_data:
    seq:
      - id: ch4
        type: u1
        repeat: expr
        repeat-expr: _root.header.npts
        if: _root.header.ch4.enabled > 0

      - id: ch3
        type: u1
        repeat: expr
        repeat-expr: _root.header.npts
        if: _root.header.ch3.enabled > 0

      - id: ch2
        type: u1
        repeat: expr
        repeat-expr: _root.header.npts
        if: _root.header.ch2.enabled > 0

      - id: ch1
        type: u1
        repeat: expr
        repeat-expr: _root.header.npts
        if: _root.header.ch1.enabled > 0
