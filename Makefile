python_parsers = RigolWFM/wfm1000d.py RigolWFM/wfm1000e.py RigolWFM/wfm1000z.py RigolWFM/wfm4000c.py

all: $(python_parsers)

RigolWFM/wfm1000d.py: ksy/wfm1000d.ksy
	kaitai-struct-compiler -t python --outdir RigolWFM ksy/wfm1000d.ksy

RigolWFM/wfm1000e.py: ksy/wfm1000e.ksy
	kaitai-struct-compiler -t python --outdir RigolWFM ksy/wfm1000e.ksy

RigolWFM/wfm1000z.py: ksy/wfm1000z.ksy
	kaitai-struct-compiler -t python --outdir RigolWFM ksy/wfm1000z.ksy

RigolWFM/wfm4000c.py: ksy/wfm4000c.ksy
	kaitai-struct-compiler -t python --outdir RigolWFM ksy/wfm4000c.ksy

check:
	ksylint ksy/wfm1000d.ksy
	ksylint ksy/wfm1000e.ksy
	ksylint ksy/wfm1000z.ksy
	ksylint ksy/wfm4000c.ksy

test:
	python3 RigolWFM/wfm_parser.py -t e wfm/DS1102E-A.wfm
	python3 RigolWFM/wfm_parser.py -t e wfm/DS1102E-B.wfm
	python3 RigolWFM/wfm_parser.py -t e wfm/DS1102E-C.wfm
	python3 RigolWFM/wfm_parser.py -t e wfm/DS1102E-D.wfm
	python3 RigolWFM/wfm_parser.py -t e wfm/DS1052E.wfm
	python3 RigolWFM/wfm_parser.py -t c wfm/DS4022-A.wfm
	python3 RigolWFM/wfm_parser.py -t c wfm/DS4022-B.wfm
	python3 RigolWFM/wfm_parser.py -t z wfm/MSO1104.wfm
	python3 RigolWFM/wfm_parser.py -t z wfm/DS1074Z-A.wfm 
	python3 RigolWFM/wfm_parser.py -t z wfm/DS1074Z-B.wfm 

teste:
	python3 RigolWFM/wfm_parser2.py -t 1000e wfm/DS1102E-A.wfm
	python3 RigolWFM/wfm_parser2.py -t 1000e wfm/DS1102E-B.wfm
	python3 RigolWFM/wfm_parser2.py -t 1000e wfm/DS1102E-C.wfm
	python3 RigolWFM/wfm_parser2.py -t 1000e wfm/DS1102E-D.wfm
	python3 RigolWFM/wfm_parser2.py -t 1000e wfm/DS1052E.wfm

testz:
	python3 RigolWFM/wfm_parser2.py -t 1000z wfm/MSO1104.wfm
	python3 RigolWFM/wfm_parser2.py -t 1000z wfm/DS1074Z-A.wfm
#	python3 RigolWFM/wfm_parser2.py -t 1000z wfm/DS1074Z-B.wfm

clean:
	rm -f RigolWFM/wfm1000d.py 
	rm -f RigolWFM/wfm1000e.py 
	rm -f RigolWFM/wfm1000z.py 
	rm -f RigolWFM/wfm4000c.py
	rm -rf dist
	rm -rf RigolWFM.egg-info
	rm -rf RigolWFM/__pycache__
	
.PHONY: clean test check all