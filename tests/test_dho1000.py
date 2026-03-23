"""
Tests for Rigol DHO800/DHO1000 parsing through `RigolWFM.dho`.

Validates normalized DHO sample count, voltage range, time axis, and channel
count for both `.bin` and `.wfm` inputs.

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

# DHO1074.bin and DHO1074.wfm align sample-for-sample with the current parsers,
# so they can be used as a matching validation pair.
HAS_MATCHING_PAIR = HAS_DHO1074_BIN and HAS_DHO1074_WFM


def _import_parsers():
    """Import the DHO adapter module, adding RigolWFM to path if needed."""
    sys.path.insert(0, _REPO_ROOT)
    return importlib.import_module("RigolWFM.dho")


class TestDho1000BinParser(unittest.TestCase):
    """Tests for normalized DHO `.bin` parsing in `RigolWFM.dho`."""

    @classmethod
    def setUpClass(cls):
        """Load the DHO normalization helpers once for this test class."""
        cls.wfm_module = _import_parsers()

    @unittest.skipUnless(HAS_DHO1074_BIN, "DHO1074.bin not found")
    def test_dho1074_bin_sample_count(self):
        """DHO1074.bin should have exactly 10000 samples."""
        obj = self.wfm_module.dho_from_file(DHO1074_BIN)
        self.assertEqual(obj.header.n_pts, 10000)

    @unittest.skipUnless(HAS_DHO1074_BIN, "DHO1074.bin not found")
    def test_dho1074_bin_cookie(self):
        """DHO1074.bin should have 'RG' cookie."""
        obj = self.wfm_module.dho_from_file(DHO1074_BIN)
        self.assertEqual(obj.header.cookie, "RG")

    @unittest.skipUnless(HAS_DHO1074_BIN, "DHO1074.bin not found")
    def test_dho1074_bin_all_channels_enabled(self):
        """DHO1074.bin should have all 4 channels enabled."""
        obj = self.wfm_module.dho_from_file(DHO1074_BIN)
        enabled = [ch for ch in obj.header.ch if ch.enabled]
        self.assertEqual(len(enabled), 4)

    @unittest.skipUnless(HAS_DHO1074_BIN, "DHO1074.bin not found")
    def test_dho1074_bin_channel_count(self):
        """DHO1074.bin should have exactly 4 channel headers."""
        obj = self.wfm_module.dho_from_file(DHO1074_BIN)
        self.assertEqual(len(obj.header.ch), 4)
        self.assertEqual(obj.header.n_waveforms, 4)

    @unittest.skipUnless(HAS_DHO1074_BIN, "DHO1074.bin not found")
    def test_dho1074_bin_all_channel_data(self):
        """DHO1074.bin should have voltage data for all 4 channels."""
        obj = self.wfm_module.dho_from_file(DHO1074_BIN)
        self.assertEqual(len(obj.header.channel_data), 4)
        for i, data in enumerate(obj.header.channel_data):
            self.assertEqual(len(data), 10000, f"CH{i+1} should have 10000 samples")

    @unittest.skipUnless(HAS_DHO1074_BIN, "DHO1074.bin not found")
    def test_dho1074_bin_time_axis(self):
        """DHO1074.bin should expose normalized negative pre-trigger time."""
        obj = self.wfm_module.dho_from_file(DHO1074_BIN)
        self.assertLess(obj.header.x_origin, 0.0,
                        "x_origin should be normalized to the first sample time")
        self.assertGreater(obj.header.x_increment, 0.0,
                           "x_increment must be positive")
        self.assertGreater(obj.header.x_increment, 1e-12)
        self.assertLess(obj.header.x_increment, 1.0)

    @unittest.skipUnless(HAS_DHO1074_BIN, "DHO1074.bin not found")
    def test_dho1074_bin_str_parser_name(self):
        """str(obj) should contain 'dho1000' for parser name extraction."""
        obj = self.wfm_module.dho_from_file(DHO1074_BIN)
        self.assertIn("dho1000", str(obj))


class TestWfmDho1000Parser(unittest.TestCase):
    """Tests for normalized DHO `.wfm` parsing in `RigolWFM.dho`."""

    @classmethod
    def setUpClass(cls):
        """Load the DHO normalization helpers once for this test class."""
        cls.wfm_module = _import_parsers()

    @unittest.skipUnless(HAS_DHO1074_WFM, "DHO1074.wfm not found")
    def test_dho1047_wfm_parse(self):
        """DHO1074.wfm should parse without errors."""
        obj = self.wfm_module.dho_from_file(DHO1074_WFM)
        self.assertIsNotNone(obj)
        self.assertIsNotNone(obj.header)

    @unittest.skipUnless(HAS_DHO1074_WFM, "DHO1074.wfm not found")
    def test_dho1047_wfm_sample_count(self):
        """DHO1074.wfm should have 10000 samples."""
        obj = self.wfm_module.dho_from_file(DHO1074_WFM)
        self.assertEqual(obj.header.n_pts, 10000)

    @unittest.skipUnless(HAS_DHO1074_WFM, "DHO1074.wfm not found")
    def test_dho1047_wfm_channel_data(self):
        """DHO1074.wfm should expose calibrated voltage data for all four channels."""
        obj = self.wfm_module.dho_from_file(DHO1074_WFM)
        self.assertEqual(len(obj.header.channel_data), 4)
        for i, volts in enumerate(obj.header.channel_data):
            self.assertIsNotNone(volts, f"CH{i+1} voltage data should not be None")
            self.assertEqual(len(volts), 10000)

    @unittest.skipUnless(HAS_DHO1074_WFM, "DHO1074.wfm not found")
    def test_dho1047_wfm_raw_data(self):
        """DHO1074.wfm raw_data should contain four uint16 arrays of 10000 samples."""
        obj = self.wfm_module.dho_from_file(DHO1074_WFM)
        self.assertIsNotNone(obj.header.raw_data)
        for i, raw in enumerate(obj.header.raw_data):
            self.assertIsNotNone(raw, f"CH{i+1} raw data should not be None")
            self.assertEqual(raw.dtype, np.dtype("<u2"))
            self.assertEqual(len(raw), 10000)

    @unittest.skipUnless(HAS_DHO1074_WFM, "DHO1074.wfm not found")
    def test_dho1047_wfm_voltage_range(self):
        """DHO1074.wfm should expose finite, nontrivial voltage traces for all channels."""
        obj = self.wfm_module.dho_from_file(DHO1074_WFM)
        ch1, ch2, ch3, ch4 = obj.header.channel_data
        for i, volts in enumerate((ch1, ch2, ch3, ch4), start=1):
            self.assertTrue(np.isfinite(volts).all(), f"CH{i} should not contain NaNs")

        self.assertGreater(float(ch1.max() - ch1.min()), 40.0)
        self.assertGreater(float(ch2.max() - ch2.min()), 40.0)
        self.assertGreater(float(ch3.max() - ch3.min()), 2.0)
        self.assertGreater(float(ch4.max() - ch4.min()), 20.0)

    @unittest.skipUnless(HAS_DHO1074_WFM, "DHO1074.wfm not found")
    def test_dho1047_wfm_channel_offsets(self):
        """DHO1074.wfm channel headers should preserve the displayed vertical centers."""
        obj = self.wfm_module.dho_from_file(DHO1074_WFM)
        expected_offsets = [154.0, 19.2, -3.76, -71.2]
        for i, (ch, expected) in enumerate(zip(obj.header.ch, expected_offsets), start=1):
            self.assertTrue(ch.enabled, f"CH{i} should be enabled")
            self.assertAlmostEqual(ch.volt_offset, expected, places=2)

    @unittest.skipUnless(HAS_DHO1074_WFM, "DHO1074.wfm not found")
    def test_dho1047_wfm_time_axis(self):
        """DHO1074.wfm time parameters should match the 200 kSa/s capture."""
        obj = self.wfm_module.dho_from_file(DHO1074_WFM)
        self.assertEqual(obj.header.n_pts, 10000)
        self.assertAlmostEqual(obj.header.x_increment, 5e-6)
        self.assertAlmostEqual(obj.header.x_origin, -0.025)

    @unittest.skipUnless(HAS_DHO1074_WFM, "DHO1074.wfm not found")
    def test_dho1047_wfm_channel_headers(self):
        """DHO1074.wfm should have 4 enabled channel headers labeled CH1-CH4."""
        obj = self.wfm_module.dho_from_file(DHO1074_WFM)
        self.assertEqual(len(obj.header.ch), 4)
        for i, ch in enumerate(obj.header.ch, start=1):
            self.assertTrue(ch.enabled, f"CH{i} should be enabled")
            self.assertEqual(ch.name, f"CH{i}")

    @unittest.skipUnless(HAS_DHO1074_WFM, "DHO1074.wfm not found")
    def test_dho1047_wfm_str_parser_name(self):
        """str(obj) should contain 'dho1000' for parser name extraction."""
        obj = self.wfm_module.dho_from_file(DHO1074_WFM)
        self.assertIn("dho1000", str(obj))


class TestWfmBinCorrelation(unittest.TestCase):
    """Cross-validation: compare DHO1074 WFM and BIN voltage data."""

    @classmethod
    def setUpClass(cls):
        """Load the DHO normalization helpers for correlation-based comparisons."""
        cls.wfm_module = _import_parsers()

    @unittest.skipUnless(HAS_MATCHING_PAIR, "No matching .bin/.wfm pair available")
    def test_wfm_bin_rms_error(self):
        """Each DHO1074 channel should match BIN to within 10mV RMS."""
        wfm_obj = self.wfm_module.dho_from_file(DHO1074_WFM)
        bin_obj = self.wfm_module.dho_from_file(DHO1074_BIN)
        for i, (wfm_v, bin_v) in enumerate(
            zip(wfm_obj.header.channel_data, bin_obj.header.channel_data),
            start=1,
        ):
            wfm_arr = wfm_v.astype(np.float64)
            bin_arr = bin_v.astype(np.float64)
            n = min(len(wfm_arr), len(bin_arr))
            rms = np.sqrt(np.mean((wfm_arr[:n] - bin_arr[:n])**2))
            self.assertLess(rms, 0.01, f"CH{i} RMS error {rms:.6f} V exceeds 10mV.")

    @unittest.skipUnless(HAS_MATCHING_PAIR, "No matching .bin/.wfm pair available")
    def test_wfm_bin_correlation(self):
        """Each DHO1074 channel should correlate with BIN at r > 0.999999."""
        wfm_obj = self.wfm_module.dho_from_file(DHO1074_WFM)
        bin_obj = self.wfm_module.dho_from_file(DHO1074_BIN)
        for i, (wfm_v, bin_v) in enumerate(
            zip(wfm_obj.header.channel_data, bin_obj.header.channel_data),
            start=1,
        ):
            wfm_arr = wfm_v.astype(np.float64)
            bin_arr = bin_v.astype(np.float64)
            n = min(len(wfm_arr), len(bin_arr))
            corr = np.corrcoef(wfm_arr[:n], bin_arr[:n])[0, 1]
            self.assertGreater(corr, 0.999999, f"CH{i} correlation {corr:.9f} is too low.")

    @unittest.skipUnless(HAS_MATCHING_PAIR, "No matching .bin/.wfm pair available")
    def test_wfm_bin_max_error(self):
        """Each DHO1074 channel should stay within 10mV sample-wise error."""
        wfm_obj = self.wfm_module.dho_from_file(DHO1074_WFM)
        bin_obj = self.wfm_module.dho_from_file(DHO1074_BIN)
        for i, (wfm_v, bin_v) in enumerate(
            zip(wfm_obj.header.channel_data, bin_obj.header.channel_data),
            start=1,
        ):
            wfm_arr = wfm_v.astype(np.float64)
            bin_arr = bin_v.astype(np.float64)
            n = min(len(wfm_arr), len(bin_arr))
            max_err = np.max(np.abs(wfm_arr[:n] - bin_arr[:n]))
            self.assertLess(max_err, 0.01, f"CH{i} max error {max_err:.6f} V exceeds 10mV.")


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
                        "First sample time should be negative (pre-trigger).")

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
