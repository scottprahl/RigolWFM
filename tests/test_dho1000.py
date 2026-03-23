"""
Tests for Rigol DHO800/DHO1000 series parsers.

Tests both the .bin parser and the .wfm parser from wfmdho1000.py.
Validates sample count, voltage range, time axis, and channel count.

Test files:
    wfm/DHO1074.bin   (10000 samples, 4 channels enabled, DHO1074)
    wfm/DHO1074.wfm   (10000 samples per channel, 4 channels enabled, DHO1074)
"""

import importlib
import os
import sys
import unittest
import numpy as np

# Allow running from repository root or tests/ directory
_TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
_REPO_ROOT = os.path.dirname(_TESTS_DIR)
_WFM_DIR = os.path.join(_REPO_ROOT, "wfm")

# Locate actual test files (search several possible locations)
_SEARCH_PATHS = [
    _WFM_DIR,
    os.path.join(os.path.dirname(_REPO_ROOT), "rigol", "rigol.hdo1k"),
    "/mnt/c/work/domotel/rigol/rigol.hdo1k",
]


def _find_file(name):
    """Search for a test file in known locations."""
    for d in _SEARCH_PATHS:
        path = os.path.join(d, name)
        if os.path.exists(path):
            return path
    return None


DHO1074_BIN = _find_file("DHO1074.bin")
DHO1074_WFM = _find_file("DHO1074.wfm")

HAS_DHO1074_BIN = DHO1074_BIN is not None
HAS_DHO1074_WFM = DHO1074_WFM is not None

# Correlation tests require a matching .bin/.wfm pair from the same capture.
# DHO1074.bin and DHO1074.wfm are different captures, so correlation is not expected.
HAS_MATCHING_PAIR = False


def _import_parsers():
    """Import DHO parsers, adding RigolWFM to path if needed."""
    sys.path.insert(0, _REPO_ROOT)
    wfmdho1000 = importlib.import_module("RigolWFM.wfmdho1000")
    return wfmdho1000, wfmdho1000


class TestDho1000BinParser(unittest.TestCase):
    """Tests for the .bin file parser (Dho1000 class in wfmdho1000.py)."""

    @classmethod
    def setUpClass(cls):
        """Load the BIN parser module once for this test class."""
        wfmdho1000, _ = _import_parsers()
        cls.dho1000 = wfmdho1000

    @unittest.skipUnless(HAS_DHO1074_BIN, "DHO1074.bin not found")
    def test_dho1074_bin_sample_count(self):
        """DHO1074.bin should have exactly 10000 samples."""
        obj = self.dho1000.Dho1000.from_file(DHO1074_BIN)
        self.assertEqual(obj.header.n_pts, 10000)

    @unittest.skipUnless(HAS_DHO1074_BIN, "DHO1074.bin not found")
    def test_dho1074_bin_cookie(self):
        """DHO1074.bin should have 'RG' cookie."""
        obj = self.dho1000.Dho1000.from_file(DHO1074_BIN)
        self.assertEqual(obj.header.cookie, "RG")

    @unittest.skipUnless(HAS_DHO1074_BIN, "DHO1074.bin not found")
    def test_dho1074_bin_all_channels_enabled(self):
        """DHO1074.bin should have all 4 channels enabled."""
        obj = self.dho1000.Dho1000.from_file(DHO1074_BIN)
        enabled = [ch for ch in obj.header.ch if ch.enabled]
        self.assertEqual(len(enabled), 4)

    @unittest.skipUnless(HAS_DHO1074_BIN, "DHO1074.bin not found")
    def test_dho1074_bin_channel_count(self):
        """DHO1074.bin should have exactly 4 channel headers."""
        obj = self.dho1000.Dho1000.from_file(DHO1074_BIN)
        self.assertEqual(len(obj.header.ch), 4)
        self.assertEqual(obj.header.n_waveforms, 4)

    @unittest.skipUnless(HAS_DHO1074_BIN, "DHO1074.bin not found")
    def test_dho1074_bin_all_channel_data(self):
        """DHO1074.bin should have voltage data for all 4 channels."""
        obj = self.dho1000.Dho1000.from_file(DHO1074_BIN)
        self.assertEqual(len(obj.header.channel_data), 4)
        for i, data in enumerate(obj.header.channel_data):
            self.assertEqual(len(data), 10000, f"CH{i+1} should have 10000 samples")

    @unittest.skipUnless(HAS_DHO1074_BIN, "DHO1074.bin not found")
    def test_dho1074_bin_time_axis(self):
        """DHO1074.bin x_origin is stored positive in .bin format; x_increment positive."""
        obj = self.dho1000.Dho1000.from_file(DHO1074_BIN)
        # .bin stores x_origin as a positive distance from trigger to first sample;
        # channel.py negates it to get actual t[0] (pre-trigger = negative time).
        self.assertGreater(obj.header.x_origin, 0.0,
                           "x_origin in .bin format is stored as positive distance")
        self.assertGreater(obj.header.x_increment, 0.0,
                           "x_increment must be positive")
        self.assertGreater(obj.header.x_increment, 1e-12)
        self.assertLess(obj.header.x_increment, 1.0)

    @unittest.skipUnless(HAS_DHO1074_BIN, "DHO1074.bin not found")
    def test_dho1074_bin_str_parser_name(self):
        """str(obj) should contain 'dho1000' for parser name extraction."""
        obj = self.dho1000.Dho1000.from_file(DHO1074_BIN)
        self.assertIn("dho1000", str(obj))


class TestWfmDho1000Parser(unittest.TestCase):
    """Tests for the .wfm file parser (WfmDho1000 class in wfmdho1000.py)."""

    @classmethod
    def setUpClass(cls):
        """Load the WFM parser module once for this test class."""
        _, wfmdho1000 = _import_parsers()
        cls.wfmdho1000 = wfmdho1000

    @unittest.skipUnless(HAS_DHO1074_WFM, "DHO1074.wfm not found")
    def test_dho1047_wfm_parse(self):
        """DHO1074.wfm should parse without errors."""
        obj = self.wfmdho1000.WfmDho1000.from_file(DHO1074_WFM)
        self.assertIsNotNone(obj)
        self.assertIsNotNone(obj.header)

    @unittest.skipUnless(HAS_DHO1074_WFM, "DHO1074.wfm not found")
    def test_dho1047_wfm_sample_count(self):
        """DHO1074.wfm should have 10000 samples."""
        obj = self.wfmdho1000.WfmDho1000.from_file(DHO1074_WFM)
        self.assertEqual(obj.header.n_pts, 10000)

    @unittest.skipUnless(HAS_DHO1074_WFM, "DHO1074.wfm not found")
    def test_dho1047_wfm_channel_data(self):
        """DHO1074.wfm should expose calibrated voltage data for all four channels."""
        obj = self.wfmdho1000.WfmDho1000.from_file(DHO1074_WFM)
        self.assertEqual(len(obj.header.channel_data), 4)
        for i, volts in enumerate(obj.header.channel_data):
            self.assertIsNotNone(volts, f"CH{i+1} voltage data should not be None")
            self.assertEqual(len(volts), 10000)

    @unittest.skipUnless(HAS_DHO1074_WFM, "DHO1074.wfm not found")
    def test_dho1047_wfm_raw_data(self):
        """DHO1074.wfm raw_data should contain four uint16 arrays of 10000 samples."""
        obj = self.wfmdho1000.WfmDho1000.from_file(DHO1074_WFM)
        self.assertIsNotNone(obj.header.raw_data)
        for i, raw in enumerate(obj.header.raw_data):
            self.assertIsNotNone(raw, f"CH{i+1} raw data should not be None")
            self.assertEqual(raw.dtype, np.dtype("<u2"))
            self.assertEqual(len(raw), 10000)

    @unittest.skipUnless(HAS_DHO1074_WFM, "DHO1074.wfm not found")
    def test_dho1047_wfm_voltage_range(self):
        """DHO1074.wfm voltages should match the four-channel screenshot capture."""
        obj = self.wfmdho1000.WfmDho1000.from_file(DHO1074_WFM)
        ch1, ch2, ch3, ch4 = obj.header.channel_data
        for i, volts in enumerate((ch1, ch2, ch3, ch4), start=1):
            self.assertTrue(np.isfinite(volts).all(), f"CH{i} should not contain NaNs")

        self.assertGreater(float(ch1.mean()), 250.0)
        self.assertGreater(float(ch2.mean()), 10.0)
        self.assertLess(float(ch3.mean()), -4.0)
        self.assertLess(float(ch4.mean()), -100.0)

        self.assertGreater(float(ch1.max() - ch1.min()), 40.0)
        self.assertGreater(float(ch2.max() - ch2.min()), 40.0)
        self.assertGreater(float(ch3.max() - ch3.min()), 2.0)
        self.assertGreater(float(ch4.max() - ch4.min()), 20.0)

    @unittest.skipUnless(HAS_DHO1074_WFM, "DHO1074.wfm not found")
    def test_dho1047_wfm_time_axis(self):
        """DHO1074.wfm time parameters should match the 200 kSa/s capture."""
        obj = self.wfmdho1000.WfmDho1000.from_file(DHO1074_WFM)
        self.assertEqual(obj.header.n_pts, 10000)
        self.assertAlmostEqual(obj.header.x_increment, 5e-6)
        self.assertAlmostEqual(obj.header.x_origin, -0.025)

    @unittest.skipUnless(HAS_DHO1074_WFM, "DHO1074.wfm not found")
    def test_dho1047_wfm_channel_headers(self):
        """DHO1074.wfm should have 4 enabled channel headers labeled CH1-CH4."""
        obj = self.wfmdho1000.WfmDho1000.from_file(DHO1074_WFM)
        self.assertEqual(len(obj.header.ch), 4)
        for i, ch in enumerate(obj.header.ch, start=1):
            self.assertTrue(ch.enabled, f"CH{i} should be enabled")
            self.assertEqual(ch.name, f"CH{i}")

    @unittest.skipUnless(HAS_DHO1074_WFM, "DHO1074.wfm not found")
    def test_dho1047_wfm_str_parser_name(self):
        """str(obj) should contain 'wfmdho1000' for parser name extraction."""
        obj = self.wfmdho1000.WfmDho1000.from_file(DHO1074_WFM)
        self.assertIn("wfmdho1000", str(obj))


class TestWfmBinCorrelation(unittest.TestCase):
    """Cross-validation: compare WFM and BIN voltage data.

    These tests require a matching .bin and .wfm pair from the same capture.
    DHO1074.bin and DHO1074.wfm are different captures, so tests are skipped.
    To enable: provide matching files and set HAS_MATCHING_PAIR = True.
    """

    @classmethod
    def setUpClass(cls):
        """Load shared parser modules for correlation-based comparisons."""
        wfmdho1000, _ = _import_parsers()
        cls.dho1000 = wfmdho1000
        cls.wfmdho1000 = wfmdho1000

    @unittest.skipUnless(HAS_MATCHING_PAIR, "No matching .bin/.wfm pair available")
    def test_wfm_bin_rms_error(self):
        """WFM voltage calibration should match BIN to within 1mV RMS."""
        wfm_obj = self.wfmdho1000.WfmDho1000.from_file(DHO1074_WFM)
        bin_obj = self.dho1000.Dho1000.from_file(DHO1074_BIN)
        wfm_v = wfm_obj.header.channel_data[0].astype(np.float64)
        bin_v = bin_obj.header.channel_data[0].astype(np.float64)
        n = min(len(wfm_v), len(bin_v))
        rms = np.sqrt(np.mean((wfm_v[:n] - bin_v[:n])**2))
        self.assertLess(rms, 0.001, f"RMS error {rms*1000:.3f} mV exceeds 1mV threshold.")

    @unittest.skipUnless(HAS_MATCHING_PAIR, "No matching .bin/.wfm pair available")
    def test_wfm_bin_correlation(self):
        """WFM and BIN voltage data should be highly correlated (r > 0.9999)."""
        wfm_obj = self.wfmdho1000.WfmDho1000.from_file(DHO1074_WFM)
        bin_obj = self.dho1000.Dho1000.from_file(DHO1074_BIN)
        wfm_v = wfm_obj.header.channel_data[0].astype(np.float64)
        bin_v = bin_obj.header.channel_data[0].astype(np.float64)
        n = min(len(wfm_v), len(bin_v))
        corr = np.corrcoef(wfm_v[:n], bin_v[:n])[0, 1]
        self.assertGreater(corr, 0.9999, f"Correlation {corr:.6f} < 0.9999.")

    @unittest.skipUnless(HAS_MATCHING_PAIR, "No matching .bin/.wfm pair available")
    def test_wfm_bin_max_error(self):
        """Maximum per-sample error should be less than 5mV."""
        wfm_obj = self.wfmdho1000.WfmDho1000.from_file(DHO1074_WFM)
        bin_obj = self.dho1000.Dho1000.from_file(DHO1074_BIN)
        wfm_v = wfm_obj.header.channel_data[0].astype(np.float64)
        bin_v = bin_obj.header.channel_data[0].astype(np.float64)
        n = min(len(wfm_v), len(bin_v))
        max_err = np.max(np.abs(wfm_v[:n] - bin_v[:n]))
        self.assertLess(max_err, 0.005, f"Max error {max_err*1000:.3f} mV exceeds 5mV.")


_WFM_MODULE = None
_CHANNEL_MODULE = None
_INTEGRATION_ERROR = None

try:
    sys.path.insert(0, _REPO_ROOT)
    _WFM_MODULE = importlib.import_module("RigolWFM.wfm")
    _CHANNEL_MODULE = importlib.import_module("RigolWFM.channel")
except ImportError as _e:
    _INTEGRATION_ERROR = str(_e)


@unittest.skipIf(_INTEGRATION_ERROR is not None,
                 f"RigolWFM.wfm import failed: {_INTEGRATION_ERROR}")
class TestChannelIntegration(unittest.TestCase):
    """Integration tests: verify Channel objects are built correctly."""

    @classmethod
    def setUpClass(cls):
        """Cache imported integration modules used by `Wfm.from_file()` tests."""
        cls.wfm_module = _WFM_MODULE
        cls.channel_module = _CHANNEL_MODULE

    @unittest.skipUnless(HAS_DHO1074_BIN, "DHO1074.bin not found")
    def test_wfm_from_file_bin(self):
        """Wfm.from_file() should return enabled channels for DHO BIN input."""
        wfm = self.wfm_module.Wfm.from_file(DHO1074_BIN, "DHO", "1")
        # All 4 channels are enabled in the file, all are returned
        self.assertEqual(len(wfm.channels), 4)
        # Only the selected channel (CH1) has volts/times populated
        ch = wfm.channels[0]
        self.assertIsNotNone(ch.volts)
        self.assertIsNotNone(ch.times)
        self.assertEqual(len(ch.volts), len(ch.times))

    @unittest.skipUnless(HAS_DHO1074_BIN, "DHO1074.bin not found")
    def test_channel_times_start_negative(self):
        """Channel times should start at a negative value (pre-trigger)."""
        wfm = self.wfm_module.Wfm.from_file(DHO1074_BIN, "DHO", "1")
        ch = wfm.channels[0]
        self.assertLess(ch.times[0], 0.0,
                        "First sample time should be negative (pre-trigger). "
                        "Check time axis sign convention in dho1000() method.")

    @unittest.skipUnless(HAS_DHO1074_BIN, "DHO1074.bin not found")
    def test_channel_times_monotonic(self):
        """Channel times should be strictly monotonically increasing."""
        wfm = self.wfm_module.Wfm.from_file(DHO1074_BIN, "DHO", "1")
        ch = wfm.channels[0]
        diffs = np.diff(ch.times)
        self.assertTrue(np.all(diffs > 0), "Times should be strictly increasing")

    @unittest.skipUnless(HAS_DHO1074_BIN, "DHO1074.bin not found")
    def test_wfm_from_file_bin_multichannel(self):
        """Wfm.from_file() with channel '1234' should return all 4 channels."""
        wfm = self.wfm_module.Wfm.from_file(DHO1074_BIN, "DHO", "1234")
        self.assertEqual(len(wfm.channels), 4)
        for ch in wfm.channels:
            self.assertIsNotNone(ch.volts)
            self.assertIsNotNone(ch.times)

    @unittest.skipUnless(HAS_DHO1074_WFM, "DHO1074.wfm not found")
    def test_wfm_from_file_wfm_format(self):
        """Wfm.from_file() should keep all enabled DHO WFM channels and select CH1 data."""
        wfm = self.wfm_module.Wfm.from_file(DHO1074_WFM, "DHO", "1")
        self.assertEqual(len(wfm.channels), 4)
        ch = wfm.channels[0]
        self.assertIsNotNone(ch.volts)
        self.assertIsNotNone(ch.times)
        self.assertEqual(len(ch.volts), 10000)
        for ch in wfm.channels[1:]:
            self.assertIsNone(ch.volts)
            self.assertIsNone(ch.times)


if __name__ == "__main__":
    print("Test file locations:")
    print(f"  DHO1074_BIN: {DHO1074_BIN}")
    print(f"  DHO1074_WFM: {DHO1074_WFM}")
    print()
    unittest.main(verbosity=2)
