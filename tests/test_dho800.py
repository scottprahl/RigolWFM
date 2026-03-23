"""
Tests for Rigol DHO800 parsing through `RigolWFM.wfm`.

Validates that the normalized DHO path correctly handles DHO800 `.bin` and `.wfm` files,
including multi-channel captures and WFM vs BIN voltage correlation.

Test files (in wfm/ directory, captured from a DHO824 oscilloscope):
    wfm/DHO824-ch1.bin    wfm/DHO824-ch1.wfm    - CH1 only
    wfm/DHO824-ch12.bin   wfm/DHO824-ch12.wfm   - CH1 + CH2
    wfm/DHO824-ch1234.bin wfm/DHO824-ch1234.wfm - CH1-CH4

DHO800 WFM format differences vs DHO1000 (reverse-engineered):
    - CH calibration block type: 9 (DHO1000) → 5 (DHO800)
    - Scale divisor: 750_000_000_000 → 7_500_000_000_000
    - v_center: from type=6 block / 1e8 → from type=5 block bytes[38:42], negated, /1e9
    - Data section u64: n_pts+64 (DHO1000) → n_pts_total (DHO800)
    - Multi-channel: samples interleaved as [CH1, CH2, ..., CHn, CH1, ...]
"""

import importlib
import os
import sys
import unittest
import numpy as np

_TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
_REPO_ROOT = os.path.dirname(_TESTS_DIR)
_WFM_DIR = os.path.join(_REPO_ROOT, "wfm")

sys.path.insert(0, _REPO_ROOT)


def _p(fname):
    """Return the absolute path to a waveform fixture in `wfm/`."""
    return os.path.join(_WFM_DIR, fname)


# Fixture paths
CH1_BIN = _p("DHO824-ch1.bin")
CH1_WFM = _p("DHO824-ch1.wfm")
CH12_BIN = _p("DHO824-ch12.bin")
CH12_WFM = _p("DHO824-ch12.wfm")
CH1234_BIN = _p("DHO824-ch1234.bin")
CH1234_WFM = _p("DHO824-ch1234.wfm")

HAS_CH1 = os.path.exists(CH1_BIN) and os.path.exists(CH1_WFM)
HAS_CH12 = os.path.exists(CH12_BIN) and os.path.exists(CH12_WFM)
HAS_CH1234 = os.path.exists(CH1234_BIN) and os.path.exists(CH1234_WFM)

_CORRELATION_THRESHOLD = 0.99
_RMS_THRESHOLD_MV = 0.1


def _import_parsers():
    """Import the top-level WFM module used by these tests."""
    return importlib.import_module("RigolWFM.wfm")


class TestDho800BinParser(unittest.TestCase):
    """DHO800 `.bin` files should normalize correctly through `RigolWFM.wfm`."""

    @classmethod
    def setUpClass(cls):
        """Load the parser module once for all BIN parser tests."""
        cls.m = _import_parsers()

    @unittest.skipUnless(HAS_CH1, "DHO800 ch1/data.bin not found")
    def test_ch1_bin_cookie(self):
        """DHO800 .bin should have 'RG' cookie."""
        obj = self.m.dho_from_file(CH1_BIN)
        self.assertEqual(obj.header.cookie, "RG")

    @unittest.skipUnless(HAS_CH1, "DHO800 ch1/data.bin not found")
    def test_ch1_bin_sample_count(self):
        """DHO800 ch1/data.bin should have 10000 samples."""
        obj = self.m.dho_from_file(CH1_BIN)
        self.assertEqual(obj.header.n_pts, 10000)

    @unittest.skipUnless(HAS_CH1, "DHO800 ch1/data.bin not found")
    def test_ch1_bin_channel1_data(self):
        """DHO800 ch1/data.bin CH1 should have 10000 float32 samples."""
        obj = self.m.dho_from_file(CH1_BIN)
        data = obj.header.channel_data[0]
        self.assertIsNotNone(data)
        self.assertEqual(len(data), 10000)
        self.assertEqual(data.dtype, np.float32)

    @unittest.skipUnless(HAS_CH1, "DHO800 ch1/data.bin not found")
    def test_ch1_bin_voltage_range(self):
        """DHO800 ch1/data.bin voltages should be in ±10V range."""
        obj = self.m.dho_from_file(CH1_BIN)
        v = obj.header.channel_data[0]
        self.assertGreater(float(v.max()), -10.0)
        self.assertLess(float(v.max()), 10.0)

    @unittest.skipUnless(HAS_CH1234, "DHO800 ch1234/data.bin not found")
    def test_ch1234_bin_all_channels(self):
        """DHO800 ch1234/data.bin should have 4 enabled channels."""
        obj = self.m.dho_from_file(CH1234_BIN)
        self.assertEqual(obj.header.n_waveforms, 4)
        for i in range(4):
            data = obj.header.channel_data[i]
            self.assertIsNotNone(data, f"CH{i+1} data should not be None")
            self.assertEqual(len(data), 10000)


class TestDho800WfmParser(unittest.TestCase):
    """DHO800 `.wfm` files should normalize correctly through `RigolWFM.wfm`."""

    @classmethod
    def setUpClass(cls):
        """Load the parser module once for all WFM parser tests."""
        cls.m = _import_parsers()

    @unittest.skipUnless(HAS_CH1, "DHO800 ch1/data.wfm not found")
    def test_ch1_wfm_parse(self):
        """DHO800 ch1/data.wfm should parse without errors."""
        obj = self.m.dho_from_file(CH1_WFM)
        self.assertIsNotNone(obj)
        self.assertIsNotNone(obj.header)

    @unittest.skipUnless(HAS_CH1, "DHO800 ch1/data.wfm not found")
    def test_ch1_wfm_sample_count(self):
        """DHO800 ch1/data.wfm should have 10000 samples per channel."""
        obj = self.m.dho_from_file(CH1_WFM)
        self.assertEqual(obj.header.n_pts, 10000)

    @unittest.skipUnless(HAS_CH1, "DHO800 ch1/data.wfm not found")
    def test_ch1_wfm_channel_data_structure(self):
        """DHO800 ch1/data.wfm: channel_data is a 4-slot list; slot 0 has data."""
        obj = self.m.dho_from_file(CH1_WFM)
        self.assertEqual(len(obj.header.channel_data), 4)
        self.assertIsNotNone(obj.header.channel_data[0])
        self.assertEqual(len(obj.header.channel_data[0]), 10000)

    @unittest.skipUnless(HAS_CH1, "DHO800 ch1/data.wfm not found")
    def test_ch1_wfm_channel_headers(self):
        """DHO800 ch1/data.wfm should have 4 headers: 1 enabled, 3 disabled."""
        obj = self.m.dho_from_file(CH1_WFM)
        self.assertEqual(len(obj.header.ch), 4)
        self.assertTrue(obj.header.ch[0].enabled)
        for i in range(1, 4):
            self.assertFalse(obj.header.ch[i].enabled)

    @unittest.skipUnless(HAS_CH1, "DHO800 ch1/data.wfm not found")
    def test_ch1_wfm_time_axis(self):
        """DHO800 ch1/data.wfm time parameters should be physically plausible."""
        obj = self.m.dho_from_file(CH1_WFM)
        self.assertGreater(obj.header.x_increment, 1e-12)
        self.assertLess(obj.header.x_increment, 1.0)

    @unittest.skipUnless(HAS_CH1, "DHO800 ch1/data.wfm not found")
    def test_ch1_wfm_raw_data(self):
        """DHO800 ch1/data.wfm raw_data[0] should be uint16 with 10000 samples."""
        obj = self.m.dho_from_file(CH1_WFM)
        self.assertIsNotNone(obj.header.raw_data)
        raw_ch1 = obj.header.raw_data[0]
        self.assertIsNotNone(raw_ch1)
        self.assertEqual(raw_ch1.dtype, np.dtype("<u2"))
        self.assertEqual(len(raw_ch1), 10000)

    @unittest.skipUnless(HAS_CH12, "DHO800 ch12/data.wfm not found")
    def test_ch12_wfm_two_channels(self):
        """DHO800 ch12/data.wfm should have 2 enabled channels."""
        obj = self.m.dho_from_file(CH12_WFM)
        self.assertEqual(obj.header.n_pts, 10000)
        self.assertIsNotNone(obj.header.channel_data[0])
        self.assertIsNotNone(obj.header.channel_data[1])
        enabled = [ch for ch in obj.header.ch if ch.enabled]
        self.assertEqual(len(enabled), 2)

    @unittest.skipUnless(HAS_CH1234, "DHO800 ch1234/data.wfm not found")
    def test_ch1234_wfm_four_channels(self):
        """DHO800 ch1234/data.wfm should have 4 enabled channels."""
        obj = self.m.dho_from_file(CH1234_WFM)
        self.assertEqual(obj.header.n_pts, 10000)
        for i in range(4):
            self.assertIsNotNone(obj.header.channel_data[i], f"CH{i+1} data missing")
        enabled = [ch for ch in obj.header.ch if ch.enabled]
        self.assertEqual(len(enabled), 4)

    @unittest.skipUnless(HAS_CH1, "DHO800 ch1/data.wfm not found")
    def test_ch1_wfm_str_parser_name(self):
        """str(obj) should contain 'dho1000' for parser name extraction."""
        obj = self.m.dho_from_file(CH1_WFM)
        self.assertIn("dho1000", str(obj))


class TestDho800WfmBinCorrelation(unittest.TestCase):
    """Cross-validation: WFM vs BIN voltage data from the same capture."""

    @classmethod
    def setUpClass(cls):
        """Load the parser module once for WFM-vs-BIN correlation checks."""
        cls.m = _import_parsers()

    def _check_correlation(self, wfm_path, bin_path, n_ch):
        """Assert that matching WFM and BIN channel voltages closely agree."""
        wfm = self.m.dho_from_file(wfm_path)
        bin_obj = self.m.dho_from_file(bin_path)
        for i in range(n_ch):
            v_wfm = wfm.header.channel_data[i]
            v_bin = bin_obj.header.channel_data[i]
            self.assertIsNotNone(v_wfm, f"WFM CH{i+1} data is None")
            self.assertIsNotNone(v_bin, f"BIN CH{i+1} data is None")
            n = min(len(v_wfm), len(v_bin))
            vw = v_wfm[:n].astype(np.float64)
            vb = v_bin[:n].astype(np.float64)
            corr = float(np.corrcoef(vw, vb)[0, 1])
            rms = float(np.sqrt(np.mean((vw - vb) ** 2))) * 1000
            self.assertGreater(
                corr, _CORRELATION_THRESHOLD,
                f"CH{i+1}: correlation {corr:.6f} < {_CORRELATION_THRESHOLD}"
            )
            self.assertLess(
                rms, _RMS_THRESHOLD_MV,
                f"CH{i+1}: RMS {rms:.4f} mV exceeds {_RMS_THRESHOLD_MV} mV"
            )

    @unittest.skipUnless(HAS_CH1, "DHO800 ch1 files not found")
    def test_ch1_wfm_bin_correlation(self):
        """CH1 WFM vs BIN: correlation > 0.99, RMS < 0.1 mV."""
        self._check_correlation(CH1_WFM, CH1_BIN, 1)

    @unittest.skipUnless(HAS_CH12, "DHO800 ch12 files not found")
    def test_ch12_wfm_bin_correlation(self):
        """CH1+CH2 WFM vs BIN: correlation > 0.99, RMS < 0.1 mV each."""
        self._check_correlation(CH12_WFM, CH12_BIN, 2)

    @unittest.skipUnless(HAS_CH1234, "DHO800 ch1234 files not found")
    def test_ch1234_wfm_bin_correlation(self):
        """CH1-CH4 WFM vs BIN: correlation > 0.99, RMS < 0.1 mV each."""
        self._check_correlation(CH1234_WFM, CH1234_BIN, 4)


_WFM_MODULE = None
_INTEGRATION_ERROR = None

try:
    _WFM_MODULE = importlib.import_module("RigolWFM.wfm")
except ImportError as _e:
    _INTEGRATION_ERROR = str(_e)


@unittest.skipIf(_INTEGRATION_ERROR is not None,
                 f"RigolWFM.wfm import failed: {_INTEGRATION_ERROR}")
class TestDho800ChannelIntegration(unittest.TestCase):
    """Integration tests: Wfm.from_file() builds correct Channel objects for DHO824."""

    @classmethod
    def setUpClass(cls):
        """Cache the top-level WFM module for integration tests."""
        cls.wfm = _WFM_MODULE

    @unittest.skipUnless(HAS_CH1, "DHO824-ch1.bin not found in wfm/")
    def test_bin_ch1_times_and_volts(self):
        """Wfm.from_file() on DHO824-ch1.bin returns valid times and volts."""
        w = self.wfm.Wfm.from_file(CH1_BIN, "DHO", "1")
        ch = w.channels[0]
        self.assertIsNotNone(ch.volts)
        self.assertIsNotNone(ch.times)
        self.assertEqual(len(ch.volts), len(ch.times))

    @unittest.skipUnless(HAS_CH1, "DHO824-ch1.bin not found in wfm/")
    def test_bin_ch1_times_start_negative(self):
        """DHO824-ch1.bin: first sample time should be negative (pre-trigger)."""
        w = self.wfm.Wfm.from_file(CH1_BIN, "DHO", "1")
        self.assertLess(w.channels[0].times[0], 0.0)

    @unittest.skipUnless(HAS_CH1234, "DHO824-ch1234.bin not found in wfm/")
    def test_bin_ch1234_all_channels(self):
        """Wfm.from_file() with '1234' returns 4 channels with volts/times."""
        w = self.wfm.Wfm.from_file(CH1234_BIN, "DHO", "1234")
        self.assertEqual(len(w.channels), 4)
        for ch in w.channels:
            self.assertIsNotNone(ch.volts)
            self.assertIsNotNone(ch.times)

    @unittest.skipUnless(HAS_CH1, "DHO824-ch1.wfm not found in wfm/")
    def test_wfm_ch1_times_and_volts(self):
        """Wfm.from_file() on DHO824-ch1.wfm returns valid times and volts."""
        w = self.wfm.Wfm.from_file(CH1_WFM, "DHO", "1")
        ch = w.channels[0]
        self.assertIsNotNone(ch.volts)
        self.assertIsNotNone(ch.times)
        self.assertGreater(len(ch.volts), 0)

    @unittest.skipUnless(HAS_CH12, "DHO824-ch12.wfm not found in wfm/")
    def test_wfm_ch12_two_channels(self):
        """Wfm.from_file() on DHO824-ch12.wfm with '12' returns 2 channels."""
        w = self.wfm.Wfm.from_file(CH12_WFM, "DHO", "12")
        self.assertEqual(len(w.channels), 2)
        for ch in w.channels:
            self.assertIsNotNone(ch.volts)

    @unittest.skipUnless(HAS_CH1234, "DHO824-ch1234.wfm not found in wfm/")
    def test_wfm_ch1234_four_channels(self):
        """Wfm.from_file() on DHO824-ch1234.wfm with '1234' returns 4 channels."""
        w = self.wfm.Wfm.from_file(CH1234_WFM, "DHO", "1234")
        self.assertEqual(len(w.channels), 4)
        for ch in w.channels:
            self.assertIsNotNone(ch.volts)


if __name__ == "__main__":
    print("DHO800 test file dir:", _WFM_DIR)
    print(f"  HAS_CH1={HAS_CH1}, HAS_CH12={HAS_CH12}, HAS_CH1234={HAS_CH1234}")
    print()
    unittest.main(verbosity=2)
