  channel_header:
    seq:
      - id: enabled
        type: u1
      - id: unknown_1
        size: 7
      - id: scale
        type: 4f
      - id: shift
        type: 4f
      - id: inverted
        type: u1
      - id: unknown_2
        size: 11

  channel_subheader:
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
        type: strz
        size: 4
      - id: unknown_5
        size: 10

  wfm_header:
    seq:
      - id: magic
        contents: [0xff,0x01]
      - id: unknown_2
        size: 6
      - id: model
        type: strz
        size: 20
      - id: fw_version
        type: strz
        size: 20
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

      - id: ch1_head
        type: channel_header

      - id: ch2_head
        type: channel_header

      - id: ch3_head
        type: channel_header

      - id: ch4_head
        type: channel_header

      - id: unknown_5
        size: 1759
        
      - id: unknown_5a
        if: fw_version == "00.04.02.SP4"
        size: 40
      - id: unknown_5b
        if: fw_version == "00.04.03.SP2"
        size: 55

      - id: ch4_subhead
        type: channel_subheader
      - id: ch3_subhead
        type: channel_subheader
      - id: ch2_subhead
        type: channel_subheader
      - id: ch1_subhead
        type: channel_subheader

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
        if: fw_version != "00.04.01.SP2"
        size: 4

      - id: sample_count
        type: u4

      - id: unknown_8a
        size: 148
      - id: unknown_8b
        if: fw_version == "00.04.01.SP2"
        size: 4
