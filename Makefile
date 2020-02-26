python_parsers = RigolWFM/wfm1000d.py RigolWFM/wfm1000e.py RigolWFM/wfm1000z.py \
                 RigolWFM/wfm4000.py RigolWFM/wfm6000.py

KSY_OPTIONS = --verbose=all --outdir RigolWFM
KSY_OPTIONS = --outdir RigolWFM

YAML_LINT_OPTIONS = -d "{extends: default, rules: {document-start: disable}}"

all: $(python_parsers)

RigolWFM/wfm1000d.py: ksy/wfm1000d.ksy
	kaitai-struct-compiler -t python $(KSY_OPTIONS) ksy/wfm1000d.ksy

RigolWFM/wfm1000e.py: ksy/wfm1000e.ksy
	kaitai-struct-compiler -t python $(KSY_OPTIONS) ksy/wfm1000e.ksy

RigolWFM/wfm1000z.py: ksy/wfm1000z.ksy
	kaitai-struct-compiler -t python $(KSY_OPTIONS) ksy/wfm1000z.ksy

RigolWFM/wfm4000.py: ksy/wfm4000.ksy
	kaitai-struct-compiler -t python $(KSY_OPTIONS) ksy/wfm4000.ksy

RigolWFM/wfm6000.py: ksy/wfm6000.ksy
	kaitai-struct-compiler -t python $(KSY_OPTIONS) ksy/wfm6000.ksy

yamlcheck:
	yamllint $(YAML_LINT_OPTIONS) ksy/wfm1000d.ksy
	yamllint $(YAML_LINT_OPTIONS) ksy/wfm1000e.ksy
	yamllint $(YAML_LINT_OPTIONS) ksy/wfm1000z.ksy
	yamllint $(YAML_LINT_OPTIONS) ksy/wfm4000.ksy
	yamllint $(YAML_LINT_OPTIONS) ksy/wfm6000.ksy

ksycheck:
	ksylint ksy/wfm1000d.ksy
	ksylint ksy/wfm1000e.ksy
	ksylint ksy/wfm1000z.ksy
	ksylint ksy/wfm4000.ksy
	ksylint ksy/wfm6000.ksy

check:
	make yamlcheck
	make ksycheck

oldtest:
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
	python3 RigolWFM/wfm_parser2.py -t 1000z wfm/DS1074Z-B.wfm

test4:
	python3 RigolWFM/wfm_parser2.py -t 4000 wfm/DS4022-A.wfm
	python3 RigolWFM/wfm_parser2.py -t 4000 wfm/DS4022-B.wfm
	python3 RigolWFM/wfm_parser2.py -t 4000 wfm/DS4024-A.wfm
	python3 RigolWFM/wfm_parser2.py -t 4000 wfm/DS4024-B.wfm

test:
	make teste
	make testz
	make test4
	
clean:
	rm -f RigolWFM/wfm1000d.py 
	rm -f RigolWFM/wfm1000e.py 
	rm -f RigolWFM/wfm1000z.py 
	rm -f RigolWFM/wfm4000.py
	rm -f RigolWFM/wfm6000.py
	rm -rf dist
	rm -rf RigolWFM.egg-info
	rm -rf RigolWFM/__pycache__
	
.PHONY: clean test check all ksycheck yamlcheck teste testz test4 test