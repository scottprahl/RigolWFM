import subprocess


def test_wfmconvert_info():
    commands = [
        "RigolWFM/wfmconvert.py B info tests/DS1204B-A.wfm",
        "RigolWFM/wfmconvert.py C info tests/DS1202CA-A.wfm",
        "RigolWFM/wfmconvert.py D info tests/DS1102D-A.wfm",
        "RigolWFM/wfmconvert.py E info tests/DS1052E.wfm",
        "RigolWFM/wfmconvert.py Z info tests/DS1054Z-A.wfm",
        "RigolWFM/wfmconvert.py 2 info tests/DS2000-A.wfm",
        "RigolWFM/wfmconvert.py 4 info tests/DS4024-A.wfm"
    ]

    for command in commands:
        result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        assert result.returncode == 0

def test_wfmconvert_csv():
    commands = [
        "RigolWFM/wfmconvert.py --force B csv tests/DS1204B-A.wfm",
        "RigolWFM/wfmconvert.py --force C csv tests/DS1202CA-A.wfm",
        "RigolWFM/wfmconvert.py --force D csv tests/DS1102D-A.wfm",
        "RigolWFM/wfmconvert.py --force E csv tests/DS1102E-A.wfm",
        "RigolWFM/wfmconvert.py --force Z csv tests/MSO1104.wfm",
        "RigolWFM/wfmconvert.py --force 2 csv tests/DS2202.wfm",
        "RigolWFM/wfmconvert.py --force 4 csv tests/DS4022-A.wfm"
    ]

    for command in commands:
        result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        assert result.returncode == 0

def test_wfmconvert_wav():
    commands = [
        "RigolWFM/wfmconvert.py --force B wav tests/DS1204B-A.wfm",
        "RigolWFM/wfmconvert.py --force C wav tests/DS1202CA-A.wfm",
        "RigolWFM/wfmconvert.py --force D wav tests/DS1102D-A.wfm",
        "RigolWFM/wfmconvert.py --force E wav tests/DS1102E-A.wfm",
        "RigolWFM/wfmconvert.py --force Z wav tests/MSO1104.wfm",
        "RigolWFM/wfmconvert.py --force 2 wav tests/DS2202.wfm",
        "RigolWFM/wfmconvert.py --force 4 wav tests/DS4022-A.wfm"
    ]

    for command in commands:
        result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        assert result.returncode == 0

def test_wfmconvert_vcsv():
    commands = [
        "RigolWFM/wfmconvert.py --force B vcsv tests/DS1204B-A.wfm",
        "RigolWFM/wfmconvert.py --force C vcsv tests/DS1202CA-A.wfm",
        "RigolWFM/wfmconvert.py --force D vcsv tests/DS1102D-A.wfm",
        "RigolWFM/wfmconvert.py --force E vcsv tests/DS1102E-A.wfm",
        "RigolWFM/wfmconvert.py --force Z vcsv tests/MSO1104.wfm",
        "RigolWFM/wfmconvert.py --force 2 vcsv tests/DS2202.wfm",
        "RigolWFM/wfmconvert.py --force 4 vcsv tests/DS4022-A.wfm"
    ]

    for command in commands:
        result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        assert result.returncode == 0

def test_wfmconvert_sigrok():
    commands = [
        "RigolWFM/wfmconvert.py --force B sigrok tests/DS1204B-A.wfm",
        "RigolWFM/wfmconvert.py --force C sigrok tests/DS1202CA-A.wfm",
        "RigolWFM/wfmconvert.py --force D sigrok tests/DS1102D-A.wfm",
        "RigolWFM/wfmconvert.py --force E sigrok tests/DS1102E-A.wfm",
        "RigolWFM/wfmconvert.py --force Z sigrok tests/MSO1104.wfm",
        "RigolWFM/wfmconvert.py --force 2 sigrok tests/DS2202.wfm",
        "RigolWFM/wfmconvert.py --force 4 sigrok tests/DS4022-A.wfm"
    ]

    for command in commands:
        result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        assert result.returncode == 0
