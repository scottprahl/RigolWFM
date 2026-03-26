"""Integration checks for `wfmconvert` sigrok export."""

from tests.cli_helpers import run_command


def test_wfmconvert_sigrok(tmp_path):
    """Verify sigrok export succeeds for representative scopes."""
    cases = [
        ("B", "wfm/DS1204B-A.wfm"),
        ("C", "wfm/DS1202CA-A.wfm"),
        ("D", "wfm/DS1102D-A.wfm"),
        ("E", "wfm/DS1102E-A.wfm"),
        ("Z", "wfm/MSO1104.wfm"),
        ("2", "wfm/DS2202.wfm"),
        ("4", "wfm/DS4022-A.wfm"),
    ]

    for scope, path in cases:
        run_command(f"wfmconvert --model {scope} --output-dir {tmp_path} sigrok {path}")


# Run the tests
if __name__ == "__main__":
    test_wfmconvert_sigrok()
    print("All tests passed!")
