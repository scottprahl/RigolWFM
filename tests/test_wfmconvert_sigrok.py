import subprocess

def test_wfmconvert_sigrok():
    commands = [
#        "wfmconvert --force B sigrok tests/DS1204B-A.wfm",
#        "wfmconvert --force C sigrok tests/DS1202CA-A.wfm",
        "wfmconvert --force D sigrok tests/DS1102D-A.wfm",
#        "wfmconvert --force E sigrok tests/DS1102E-A.wfm",
#        "wfmconvert --force Z sigrok tests/MSO1104.wfm",
#        "wfmconvert --force 2 sigrok tests/DS2202.wfm",
#        "wfmconvert --force 4 sigrok tests/DS4022-A.wfm"
    ]

    for command in commands:
        result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        assert result.returncode == 0

# Run the tests
if __name__ == "__main__":
    test_wfmconvert_sigrok()
    print("All tests passed!")

