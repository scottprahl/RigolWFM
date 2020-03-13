PYTHON_PARSERS = RigolWFM/wfm1000c.py RigolWFM/wfm1000e.py RigolWFM/wfm1000z.py \
                 RigolWFM/wfm2000.py RigolWFM/wfm4000.py RigolWFM/wfm6000.py

KSC ?= kaitai-struct-compiler

KSY_OPTIONS = --verbose=all --outdir RigolWFM
KSY_OPTIONS = --outdir RigolWFM

KSY_PYTHON_OPTIONS = -t python $(KSY_OPTIONS)
KSY_C_OPTIONS = -t cpp_stl --cpp-standard 11  $(KSY_OPTIONS)

YAML_LINT_OPTIONS = -d "{extends: default, rules: {document-start: disable}}"

export PYTHONPATH ?= .

all: $(PYTHON_PARSERS)

RigolWFM/wfm1000c.py: ksy/wfm1000c.ksy
	$(KSC) $(KSY_PYTHON_OPTIONS) $<

RigolWFM/wfm1000e.py: ksy/wfm1000e.ksy
	$(KSC) $(KSY_PYTHON_OPTIONS) $<

RigolWFM/wfm1000z.py: ksy/wfm1000z.ksy
	$(KSC) $(KSY_PYTHON_OPTIONS) $<

RigolWFM/wfm2000.py: ksy/wfm2000.ksy
	$(KSC) $(KSY_PYTHON_OPTIONS) $<

RigolWFM/wfm4000.py: ksy/wfm4000.ksy
	$(KSC) $(KSY_PYTHON_OPTIONS) $<

RigolWFM/wfm6000.py: ksy/wfm6000.ksy
	$(KSC) $(KSY_PYTHON_OPTIONS) $<

yamlcheck:
	yamllint $(YAML_LINT_OPTIONS) ksy/wfm1000c.ksy
	yamllint $(YAML_LINT_OPTIONS) ksy/wfm1000e.ksy
	yamllint $(YAML_LINT_OPTIONS) ksy/wfm1000z.ksy
	yamllint $(YAML_LINT_OPTIONS) ksy/wfm2000.ksy
	yamllint $(YAML_LINT_OPTIONS) ksy/wfm4000.ksy
	yamllint $(YAML_LINT_OPTIONS) ksy/wfm6000.ksy

ksycheck:
	ksylint ksy/wfm1000c.ksy
	ksylint ksy/wfm1000e.ksy
	ksylint ksy/wfm1000z.ksy
	ksylint ksy/wfm2000.ksy
	ksylint ksy/wfm4000.ksy
	ksylint ksy/wfm6000.ksy

check:
	make yamlcheck
	make ksycheck

teste:
	RigolWFM/wfm_parser.py --model E info wfm/DS1102E-A.wfm
	RigolWFM/wfm_parser.py --model E info wfm/DS1102E-B.wfm
	RigolWFM/wfm_parser.py --model E info wfm/DS1102E-C.wfm
	RigolWFM/wfm_parser.py --model E info wfm/DS1102E-D.wfm
	RigolWFM/wfm_parser.py --model E info wfm/DS1052E.wfm

testz:
	RigolWFM/wfm_parser.py --model Z info wfm/MSO1104.wfm
	RigolWFM/wfm_parser.py --model Z info wfm/DS1074Z-A.wfm
	RigolWFM/wfm_parser.py --model Z info wfm/DS1074Z-B.wfm

test4:
	RigolWFM/wfm_parser.py --model 4 info wfm/DS4022-A.wfm
	RigolWFM/wfm_parser.py --model 4 info wfm/DS4022-B.wfm
	RigolWFM/wfm_parser.py --model 4 info wfm/DS4024-A.wfm
	RigolWFM/wfm_parser.py --model 4 info wfm/DS4024-B.wfm

test: $(PYTHON_PARSERS)
	make teste
	make testz
	make test4
	make csv
	make wav
	make info

csv:
	RigolWFM/wfm_parser.py --model E csv wfm/DS1102E-A.wfm test/DS1102E-A.csv
	RigolWFM/wfm_parser.py --model Z csv wfm/MSO1104.wfm test/MSO1104.csv
	RigolWFM/wfm_parser.py --model 4 csv wfm/DS4022-A.wfm test/DS4022-A.csv

wav:
	RigolWFM/wfm_parser.py --model E wav wfm/DS1102E-A.wfm test/DS1102E-A.wav
	RigolWFM/wfm_parser.py --model Z wav wfm/MSO1104.wfm test/MSO1104.wav
	RigolWFM/wfm_parser.py --model 4 wav wfm/DS4022-A.wfm test/DS4022-A.wav

info:
	RigolWFM/wfm_parser.py --model E info wfm/DS1102E-A.wfm test/DS1102E-A.txt
	RigolWFM/wfm_parser.py --model Z info wfm/MSO1104.wfm test/MSO1104.txt
	RigolWFM/wfm_parser.py --model 4 info wfm/DS4022-A.wfm test/DS4022-A.txt
	
clean:
	rm -rf dist
	rm -rf RigolWFM.egg-info
	rm -rf doc/github.com
	rm -rf RigolWFM/__pycache__
	rm -f test/*

realclean:
	make clean
	rm -f RigolWFM/wfm1000c.py 
	rm -f RigolWFM/wfm1000e.py 
	rm -f RigolWFM/wfm1000z.py 
	rm -f RigolWFM/wfm2000.py
	rm -f RigolWFM/wfm4000.py
	rm -f RigolWFM/wfm6000.py

	
.PHONY: clean realclean test check all ksycheck yamlcheck teste testz test4 test csv wav