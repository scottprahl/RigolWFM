py:
	kaitai-struct-compiler -t python --outdir RigolWFM ksy/wfm1020cd.ksy
	kaitai-struct-compiler -t python --outdir RigolWFM ksy/wfm1022c.ksy
	kaitai-struct-compiler -t python --outdir RigolWFM ksy/wfm1102d.ksy
	kaitai-struct-compiler -t python --outdir RigolWFM ksy/wfm4022c.ksy
	kaitai-struct-compiler -t python --outdir RigolWFM ksy/wfm1102e.ksy

check:
	ksylint ksy/wfm1102e.ksy
	ksylint ksy/wfm1020cd.ksy
	ksylint ksy/wfm1022c.ksy
	ksylint ksy/wfm1102d.ksy
	ksylint ksy/wfm4022c.ksy

clean:
	rm -f RigolWFM/wfm1020cd.py 
	rm -f RigolWFM/wfm1022c.py 
	rm -f RigolWFM/wfm1102d.py 
	rm -f RigolWFM/wfm4022c.py
	rm -rf dist
	rm -rf RigolWFM.egg-info
	rm -rf RigolWFM/__pycache__
	
