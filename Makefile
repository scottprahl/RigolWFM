python_parsers = RigolWFM/wfm1000c.py RigolWFM/wfm1000e.py RigolWFM/wfm1000z.py \
                 RigolWFM/wfm4000.py RigolWFM/wfm6000.py

KSY_OPTIONS = --verbose=all --outdir RigolWFM
KSY_OPTIONS = --outdir RigolWFM

YAML_LINT_OPTIONS = -d "{extends: default, rules: {document-start: disable}}"

export PYTHONPATH ?= .

all: $(python_parsers)

RigolWFM/wfm1000c.py: ksy/wfm1000c.ksy
	kaitai-struct-compiler -t python $(KSY_OPTIONS) ksy/wfm1000c.ksy

RigolWFM/wfm1000e.py: ksy/wfm1000e.ksy
	kaitai-struct-compiler -t python $(KSY_OPTIONS) ksy/wfm1000e.ksy

RigolWFM/wfm1000z.py: ksy/wfm1000z.ksy
	kaitai-struct-compiler -t python $(KSY_OPTIONS) ksy/wfm1000z.ksy

RigolWFM/wfm4000.py: ksy/wfm4000.ksy
	kaitai-struct-compiler -t python $(KSY_OPTIONS) ksy/wfm4000.ksy

RigolWFM/wfm6000.py: ksy/wfm6000.ksy
	kaitai-struct-compiler -t python $(KSY_OPTIONS) ksy/wfm6000.ksy

yamlcheck:
	yamllint $(YAML_LINT_OPTIONS) ksy/wfm1000c.ksy
	yamllint $(YAML_LINT_OPTIONS) ksy/wfm1000e.ksy
	yamllint $(YAML_LINT_OPTIONS) ksy/wfm1000z.ksy
	yamllint $(YAML_LINT_OPTIONS) ksy/wfm4000.ksy
	yamllint $(YAML_LINT_OPTIONS) ksy/wfm6000.ksy

ksycheck:
	ksylint ksy/wfm1000c.ksy
	ksylint ksy/wfm1000e.ksy
	ksylint ksy/wfm1000z.ksy
	ksylint ksy/wfm4000.ksy
	ksylint ksy/wfm6000.ksy

check:
	make yamlcheck
	make ksycheck

teste:
	RigolWFM/wfm_parser.py -a info -t 1000e wfm/DS1102E-A.wfm
	RigolWFM/wfm_parser.py -a info -t 1000e wfm/DS1102E-B.wfm
	RigolWFM/wfm_parser.py -a info -t 1000e wfm/DS1102E-C.wfm
	RigolWFM/wfm_parser.py -a info -t 1000e wfm/DS1102E-D.wfm
	RigolWFM/wfm_parser.py -a info -t 1000e wfm/DS1052E.wfm

testz:
	RigolWFM/wfm_parser.py -a info -t 1000z wfm/MSO1104.wfm
	RigolWFM/wfm_parser.py -a info -t 1000z wfm/DS1074Z-A.wfm
	RigolWFM/wfm_parser.py -a info -t 1000z wfm/DS1074Z-B.wfm

test4:
	RigolWFM/wfm_parser.py -a info -t 4000 wfm/DS4022-A.wfm
	RigolWFM/wfm_parser.py -a info -t 4000 wfm/DS4022-B.wfm
	RigolWFM/wfm_parser.py -a info -t 4000 wfm/DS4024-A.wfm
	RigolWFM/wfm_parser.py -a info -t 4000 wfm/DS4024-B.wfm

test:
	make teste
	make testz
	make test4
	
clean:
	rm -rf dist
	rm -rf RigolWFM.egg-info
	rm -rf doc/github.com
	rm -rf RigolWFM/__pycache__

realclean:
	make clean
	rm -f RigolWFM/wfm1000c.py 
	rm -f RigolWFM/wfm1000e.py 
	rm -f RigolWFM/wfm1000z.py 
	rm -f RigolWFM/wfm4000.py
	rm -f RigolWFM/wfm6000.py
	
.PHONY: clean realclean test check all ksycheck yamlcheck teste testz test4 test