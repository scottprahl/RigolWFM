"""Integration checks for `wfmconvert` sigrok export."""

from tests.cli_helpers import run_command


def test_wfmconvert_sigrok():
    """Verify sigrok export succeeds for representative scopes."""
    commands = [
        "wfmconvert --force --model B sigrok wfm/DS1204B-A.wfm",
        "wfmconvert --force --model C sigrok wfm/DS1202CA-A.wfm",
        "wfmconvert --force --model D sigrok wfm/DS1102D-A.wfm",
        "wfmconvert --force --model E sigrok wfm/DS1102E-A.wfm",
        "wfmconvert --force --model Z sigrok wfm/MSO1104.wfm",
        "wfmconvert --force --model 2 sigrok wfm/DS2202.wfm",
        "wfmconvert --force --model 4 sigrok wfm/DS4022-A.wfm",
    ]

    for command in commands:
        run_command(command)


# Run the tests
if __name__ == "__main__":
    test_wfmconvert_sigrok()
    print("All tests passed!")
