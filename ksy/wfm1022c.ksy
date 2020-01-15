meta:
  id: wfm1022c
  file-extension: wfm
  endian: le

doc: |
   Format for Rigol DS1022C oscilloscope waveform files. Very minimal and the author
   mentions using the Matlab script for the DS1102D.

doc-ref:  http://nsweb.tn.tudelft.nl/~gsteele/rigol2dat/rigol2dat.C

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
      - id: unknown_1
        size: 28
      - id: npts
        type: u4
      - id: unknown_2
        size: 4
      - id: ch1sc
        type: u4
      - id: ch1pos
        type: u4
      - id: unknown_3
        size: 5
      - id: ch1rec
        type: u1
      - id: unknown_4
        size: 10
      - id: ch2sc
        type: u4
      - id: ch2pos
        type: u4
      - id: unknown_5
        size: 5
      - id: ch2rec
        type: u1

  channel_data:
    seq:
      - id: channel_1
        type: u1
        repeat: expr
        repeat-expr: _root.header.ch1rec * _root.header.npts

      - id: channel_2
        type: u1
        repeat: expr
        repeat-expr: _root.header.ch2rec * _root.header.npts
