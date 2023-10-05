import subprocess


def test_wfmconvert_info():
    commands = [
        "wfmconvert B info tests/DS1204B-A.wfm",
        "wfmconvert C info tests/DS1202CA-A.wfm",
        "wfmconvert D info tests/DS1102D-A.wfm",
        "wfmconvert E info tests/DS1102E-A.wfm",
        "wfmconvert Z info tests/MSO1104.wfm",
        "wfmconvert 2 info tests/DS2202.wfm",
        "wfmconvert 4 info tests/DS4022-A.wfm"
    ]

    for command in commands:
        result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        assert result.returncode == 0

def test_wfmconvert_csv():
    commands = [
        "wfmconvert --force B csv tests/DS1204B-A.wfm",
        "wfmconvert --force C csv tests/DS1202CA-A.wfm",
        "wfmconvert --force D csv tests/DS1102D-A.wfm",
        "wfmconvert --force E csv tests/DS1102E-A.wfm",
        "wfmconvert --force Z csv tests/MSO1104.wfm",
        "wfmconvert --force 2 csv tests/DS2202.wfm",
        "wfmconvert --force 4 csv tests/DS4022-A.wfm"
    ]

    for command in commands:
        result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        assert result.returncode == 0

def test_wfmconvert_wav():
    commands = [
        "wfmconvert --force B wav tests/DS1204B-A.wfm",
        "wfmconvert --force C wav tests/DS1202CA-A.wfm",
        "wfmconvert --force D wav tests/DS1102D-A.wfm",
        "wfmconvert --force E wav tests/DS1102E-A.wfm",
        "wfmconvert --force Z wav tests/MSO1104.wfm",
        "wfmconvert --force 2 wav tests/DS2202.wfm",
        "wfmconvert --force 4 wav tests/DS4022-A.wfm"
    ]

    for command in commands:
        result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        assert result.returncode == 0

def test_wfmconvert_vcsv():
    commands = [
        "wfmconvert --force B vcsv tests/DS1204B-A.wfm",
        "wfmconvert --force C vcsv tests/DS1202CA-A.wfm",
        "wfmconvert --force D vcsv tests/DS1102D-A.wfm",
        "wfmconvert --force E vcsv tests/DS1102E-A.wfm",
        "wfmconvert --force Z vcsv tests/MSO1104.wfm",
        "wfmconvert --force 2 vcsv tests/DS2202.wfm",
        "wfmconvert --force 4 vcsv tests/DS4022-A.wfm"
    ]

    for command in commands:
        result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        assert result.returncode == 0

# Run the tests
if __name__ == "__main__":
    test_wfmconvert_info()
    test_wfmconvert_csv()
    test_wfmconvert_wav()
    test_wfmconvert_vcsv()
    print("All tests passed!")

