"""Tests for trimming waveforms to a window around the displayed point."""

from pathlib import Path

import pytest

import RigolWFM.wfm
from RigolWFM.wfmconvert import _parse_si
from tests.cli_helpers import run_command, run_command_failure

_ROOT = Path(__file__).resolve().parents[1]
_ANALOG = str(_ROOT / "tests" / "files" / "wfm" / "DS1102E-A.wfm")
_MIXED = str(_ROOT / "tests" / "files" / "wfm" / "DS1074Z-D.wfm")
_LOGIC_ONLY = str(_ROOT / "tests" / "files" / "wfm-tek" / "digital_waveform.wfm")


@pytest.mark.parametrize(
    "text, expected",
    [
        ("1", 1.0),
        ("1.5", 1.5),
        ("1e-3", 1e-3),
        ("-4", -4.0),
        ("5m", 5e-3),
        ("5ms", 5e-3),  # the form a user is far more likely to type
        ("200us", 200e-6),
        ("200µs", 200e-6),
        ("1s", 1.0),
        ("2.5M", 2.5e6),  # M is mega, m is milli
    ],
)
def test_parse_si_accepts_numbers_with_prefixes(text, expected):
    """SI prefixes and an optional unit should both be understood."""
    assert _parse_si(text) == pytest.approx(expected)


@pytest.mark.parametrize("text", ["", "abc", "5x", "5nonsense", "m"])
def test_parse_si_rejects_junk(text):
    """Anything that is not a number with an optional prefix should be refused."""
    with pytest.raises(ValueError, match="Invalid number format"):
        _parse_si(text)


def test_trim_keeps_a_window_around_the_displayed_point():
    """The kept window should be centered on the channel's time offset."""
    waveform = RigolWFM.wfm.Wfm.from_file(_ANALOG, "E")
    channel = waveform.channels[0]
    full_points = channel.points
    offset = channel.time_offset

    channel.trim(1e-3)

    assert channel.points < full_points
    assert len(channel.times) == channel.points  # points must track the arrays
    assert len(channel.volts) == channel.points
    assert channel.times[-1] - channel.times[0] <= 1e-3
    assert channel.times[0] <= offset <= channel.times[-1]


def test_trim_updates_the_reported_point_count():
    """`points` feeds the info output and exports, so it must follow the trim."""
    waveform = RigolWFM.wfm.Wfm.from_file(_ANALOG, "E")
    full_points = waveform.channels[0].points

    waveform.trim(1e-3)
    trimmed = waveform.channels[0].points

    assert trimmed < full_points
    described = waveform.describe()
    assert "Points = %8d" % trimmed in described
    assert "Points = %8d" % full_points not in described


def test_trim_slides_a_window_that_would_run_off_the_end():
    """A window near an edge slides inside the record instead of being clipped."""
    waveform = RigolWFM.wfm.Wfm.from_file(_ANALOG, "E")
    channel = waveform.channels[0]
    first, last = float(channel.times[0]), float(channel.times[-1])
    duration = (last - first) / 4

    channel.time_offset = last  # displayed point sitting on the final sample
    channel.trim(duration)

    assert channel.times[-1] == pytest.approx(last)
    assert channel.times[0] >= first
    assert channel.times[-1] - channel.times[0] == pytest.approx(duration, rel=0.01)


def test_trim_longer_than_the_record_keeps_everything():
    """Asking for more than was captured is not an error."""
    waveform = RigolWFM.wfm.Wfm.from_file(_ANALOG, "E")
    channel = waveform.channels[0]
    full_points = channel.points

    channel.trim(1e6)

    assert channel.points == full_points


def test_trim_keeps_analog_and_logic_aligned():
    """Logic traces share the analog window, or an export would pair wrong rows."""
    waveform = RigolWFM.wfm.Wfm.from_file(_MIXED)
    assert waveform.channels and waveform.logic_channels  # guard the fixture

    waveform.trim(1e-4)
    channel = waveform.channels[0]

    assert len(waveform.logic_times) == channel.points
    assert waveform.logic_times[0] == pytest.approx(float(channel.times[0]))
    assert waveform.logic_times[-1] == pytest.approx(float(channel.times[-1]))
    for trace in waveform.logic_channels.values():
        assert len(trace) == channel.points


def test_trim_works_on_a_capture_with_no_analog_channel():
    """A logic-only capture still trims, using its own time axis."""
    waveform = RigolWFM.wfm.Wfm.from_file(_LOGIC_ONLY)
    assert not waveform.channels

    waveform.trim(20e-9)

    assert len(waveform.logic_times) == 501
    span = float(waveform.logic_times[-1] - waveform.logic_times[0])
    assert span == pytest.approx(20e-9, rel=0.05)
    for trace in waveform.logic_channels.values():
        assert len(trace) == len(waveform.logic_times)


def test_trim_is_applied_by_the_command_line(tmp_path):
    """`--trim` should shorten the exported file."""
    run_command(f"wfmconvert --model E --output-dir {tmp_path} csv {_ANALOG}")
    full_rows = len((tmp_path / "DS1102E-A.csv").read_text(encoding="utf-8").splitlines())

    run_command(f"wfmconvert --model E --force --output-dir {tmp_path} --trim 1ms csv {_ANALOG}")
    trimmed_rows = len((tmp_path / "DS1102E-A.csv").read_text(encoding="utf-8").splitlines())

    assert trimmed_rows < full_rows
    assert trimmed_rows > 2  # header lines plus some data


@pytest.mark.parametrize("duration", ["bogus", "0", "-1ms"])
def test_command_line_rejects_a_bad_trim_duration(tmp_path, duration):
    """A duration that is not a positive number should fail loudly."""
    result = run_command_failure(f"wfmconvert --model E --output-dir {tmp_path} --trim {duration} csv {_ANALOG}")

    assert "wfmconvert error" in result.stderr
    assert not list(Path(tmp_path).glob("*.csv"))
