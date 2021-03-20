meta:
  id: wfm2000
  title: Rigol DS2000 oscilloscope waveform file format
  file-extension: wfm
  endian: le

instances:
  header:
    pos: 0
    type: header

types:
  header:
    seq:
      - id: magic
        contents: [0xa5, 0xa5, 0x38, 0x00]
        doc: The last two bytes is the size of the header 0x38=56

      - id: model_number
        size: 20
        type: str
        terminator: 0
        encoding: ascii

      - id: firmware_version
        size: 20
        type: str
        terminator: 0
        encoding: ascii

      - id: block_num
        contents: [0x01, 0x00]

      - id: file_version
        type: u2

      - id: unused_1
        size: 8

      - id: crc
        type: u4

      - id: structure_size
        type: u2

      - id: structure_version
        type: u2

      - id: enabled
        type: channel_mask

      - id: extra_1a
        size: 2
        doc: not in pdf specification

      - id: channel_offset
        type: u4
        repeat: expr
        repeat-expr: 4

      - id: acquisition_mode
        type: u2
        enum: acquisition_enum

      - id: average_time
        type: u2
        doc: average time 2-8192

      - id: sample_mode
        type: u2
        doc: equ or real

      - id: extra_1b
        size: 2
        doc: not in pdf specification

      - id: mem_depth
        type: u4
        doc: storage depth

      - id: sample_rate_hz
        type: f4

      - id: extra_1c
        size: 2
        doc: not in pdf specification

      - id: time_mode
        type: u2
        enum: time_enum

      - id: time_scale_ps
        type: u8
        doc: horizontal timebase in picoseconds

      - id: time_offset_ps
        type: s8
        doc: horizontal offset in picoseconds

      - id: ch
        type: channel_header
        repeat: expr
        repeat-expr: 4

      - id: setup_size
        type: u4
      - id: setup_offset
        type: u4
      - id: wfm_offset
        type: u4
      - id: storage_depth
        type: u4
      - id: z_pt_offset
        type: u4
        doc: offset of valid waveform relative to start of storage waveform

      - id: wfm_len
        type: u4
        doc: real waveform storage depth

      - id: equ_coarse
        type: u2
        repeat: expr
        repeat-expr: 2

      - id: equ_fine
        type: u2
        repeat: expr
        repeat-expr: 2

      - id: mem_start_addr
        type: u4
        repeat: expr
        repeat-expr: 2

      - id: mem_last_addr
        type: u4

      - id: mem_length
        type: u4

      - id: channel_depth
        type: u4

      - id: bank_size
        type: u4

      - id: bank_offset
        type: u4

      - id: real_offset
        type: u4

      - id: real_ch_offset
        type: u4

      - id: horiz_slow_force_stop_frame_boolean
        type: u1

      - id: get_spu_dig_data_status_boolean
        type: u1

      - id: spu_load_data_status_boolean
        type: u1

      - id: trig_delay_mem_offset
        type: s8

      - id: trig_delay_view_offset
        type: s8

      - id: mem_offset_compensate
        type: s8

      - id: slow_delta_wave_length
        type: s8

      - id: channel_pos_max_delay
        type: s8

      - id: channel_neg_min_delay
        type: s8

      - id: real_sa_dot_period
        type: u8

      - id: mem_offset_base
        type: u8

      - id: trig_type_delta_delay
        type: s4

      - id: ch1_delay
        type: s4

      - id: ch2_delay
        type: s4

      - id: channel_delay_to_mem_len
        type: u4

      - id: spu_mem_bank_size
        type: u4

      - id: roll_scrn_wave_length
        type: u2

      - id: trigger_source
        type: u1

      - id: cal_index
        type: u1

      - id: record_frame_index
        type: u4

      - id: frame_cur
        type: u4

    instances:
      seconds_per_point:
        value: 1/sample_rate_hz
      time_scale:
        value: 1.0e-12 * time_scale_ps
      time_offset:
        value: 1.0e-12 * time_offset_ps
      points:
        value: _root.header.mem_depth
      raw_1:
        io: _root._io
        pos: channel_offset[0]
        size: storage_depth
        if: channel_offset[0] > 0

      raw_2:
        io: _root._io
        pos: channel_offset[1]
        size: storage_depth 
        if: channel_offset[1] > 0

      raw_3:
        io: _root._io
        pos: channel_offset[2]
        size: storage_depth
        if: channel_offset[2] > 0

      raw_4:
        io: _root._io
        pos: channel_offset[3]
        size: storage_depth
        if: channel_offset[3] > 0


  channel_header:
    seq:
      - id: enabled_temp
        type: u1

      - id: coupling
        type: b2
        enum: coupling_enum

      - id: skip_coupling
        type: b6

      - id: bandwidth_limit
        type: u1
        enum: bandwidth_enum

      - id: probe_type
        type: u1
        enum: probe_type_enum

      - id: probe_ratio
        type: u1
        enum: probe_ratio_enum

      - id: probe_diff
        type: u1
        enum: probe_enum

      - id: probe_signal
        type: u1
        enum: probe_enum

      - id: probe_impedance
        type: u1
        enum: impedance_enum

      - id: volt_per_division
        type: f4

      - id: volt_offset
        type: f4

      - id: inverted_temp
        type: u1

      - id: unit_temp
        type: u1

      - id: filter_enabled
        type: u1

      - id: filter_type
        type: u1

      - id: filter_high
        type: u4

      - id: filter_low
        type: u4

    instances:
      enabled:
        value: "enabled_temp != 0 ? true : false"

      probe_value:
        value: "(probe_ratio == probe_ratio_enum::x0_01 ? 0.01 :
                 probe_ratio == probe_ratio_enum::x0_02 ? 0.02 :
                 probe_ratio == probe_ratio_enum::x0_05 ? 0.05 :
                 probe_ratio == probe_ratio_enum::x0_1 ? 0.1 :
                 probe_ratio == probe_ratio_enum::x0_2 ? 0.2 :
                 probe_ratio == probe_ratio_enum::x0_5 ? 0.5 :
                 probe_ratio == probe_ratio_enum::x1 ? 1.0 :
                 probe_ratio == probe_ratio_enum::x2 ? 2.0 :
                 probe_ratio == probe_ratio_enum::x5 ? 5.0 :
                 probe_ratio == probe_ratio_enum::x10 ? 10.0 :
                 probe_ratio == probe_ratio_enum::x20 ? 20.0 :
                 probe_ratio == probe_ratio_enum::x50 ? 50.0 :
                 probe_ratio == probe_ratio_enum::x100 ? 100.0 :
                 probe_ratio == probe_ratio_enum::x200 ? 200.0 :
                 probe_ratio == probe_ratio_enum::x500 ? 500.0 : 1000.0)"

      inverted_actual:
        value: "enabled_temp == 1 ? inverted_temp : unit_temp"

      unit_actual:
        value: "enabled_temp == 1 ? unit_temp : inverted_temp"

      inverted:
        value: "inverted_actual == 1 ? true : false"

      unit:
        value: unit_actual

      volt_signed:
        value: "inverted ?
                -1.0 * volt_per_division:
                +1.0 * volt_per_division"
      volt_scale:
        value: volt_signed/25.0

  channel_mask:
    seq:
      - id: unused_1
        type: b4
      - id: channel_4
        type: b1
      - id: channel_3
        type: b1
      - id: channel_2
        type: b1
      - id: channel_1
        type: b1
      - id: unused_2
        type: b7
      - id: interwoven
        type: b1

enums:
  acquisition_enum:
    0: normal
    1: average
    2: peak
    3: high_resolution

  bandwidth_enum:
    0: no_limit
    1: mhz_20
    2: mhz_100
    3: mhz_200
    4: mhz_250

  coupling_enum:
    0: dc
    1: ac
    2: gnd

  filter_enum:
    0: low_pass
    1: high_pass
    2: band_pass
    3: band_reject

  impedance_enum:
    0: ohm_50
    1: ohm_1meg

  probe_enum:
    0: single
    1: diff

  probe_ratio_enum:
    0: x0_01
    1: x0_02
    2: x0_05
    3: x0_1
    4: x0_2
    5: x0_5
    6: x1
    7: x2
    8: x5
    9: x10
    10: x20
    11: x50
    12: x100
    13: x200
    14: x500
    15: x1000

  probe_type_enum:
    0: normal_type
    1: differential

  time_enum:
    0: yt
    1: xy
    2: roll

  unit_enum:
    0: w
    1: a
    2: v
    3: u
