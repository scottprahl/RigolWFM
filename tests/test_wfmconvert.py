import subprocess


def test_wfmconvert_info():
    commands = [
        "wfmconvert B info wfm/DS1204B-A.wfm",
        "wfmconvert C info wfm/DS1202CA-A.wfm",
        "wfmconvert D info wfm/DS1102D-A.wfm",
        "wfmconvert E info wfm/DS1102E-A.wfm",
        "wfmconvert Z info wfm/MSO1104.wfm",
        "wfmconvert 2 info wfm/DS2202.wfm",
        "wfmconvert 4 info wfm/DS4022-A.wfm"
    ]

    for command in commands:
        result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        assert result.returncode == 0

def test_wfmconvert_csv():
    commands = [
        "wfmconvert --force B csv wfm/DS1204B-A.wfm",
        "wfmconvert --force C csv wfm/DS1202CA-A.wfm",
        "wfmconvert --force D csv wfm/DS1102D-A.wfm",
        "wfmconvert --force E csv wfm/DS1102E-A.wfm",
        "wfmconvert --force Z csv wfm/MSO1104.wfm",
        "wfmconvert --force 2 csv wfm/DS2202.wfm",
        "wfmconvert --force 4 csv wfm/DS4022-A.wfm"
    ]

    for command in commands:
        result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        assert result.returncode == 0

def test_wfmconvert_wav():
    commands = [
        "wfmconvert --force B wav wfm/DS1204B-A.wfm",
        "wfmconvert --force C wav wfm/DS1202CA-A.wfm",
        "wfmconvert --force D wav wfm/DS1102D-A.wfm",
        "wfmconvert --force E wav wfm/DS1102E-A.wfm",
        "wfmconvert --force Z wav wfm/MSO1104.wfm",
        "wfmconvert --force 2 wav wfm/DS2202.wfm",
        "wfmconvert --force 4 wav wfm/DS4022-A.wfm"
    ]

    for command in commands:
        result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        assert result.returncode == 0

def test_wfmconvert_vcsv():
    commands = [
        "wfmconvert --force B vcsv wfm/DS1204B-A.wfm",
        "wfmconvert --force C vcsv wfm/DS1202CA-A.wfm",
        "wfmconvert --force D vcsv wfm/DS1102D-A.wfm",
        "wfmconvert --force E vcsv wfm/DS1102E-A.wfm",
        "wfmconvert --force Z vcsv wfm/MSO1104.wfm",
        "wfmconvert --force 2 vcsv wfm/DS2202.wfm",
        "wfmconvert --force 4 vcsv wfm/DS4022-A.wfm"
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

