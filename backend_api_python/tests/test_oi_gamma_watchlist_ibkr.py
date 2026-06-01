"""Tests for the local IBKR OI/gamma watchlist script."""

import importlib.util
import tempfile
import unittest
from datetime import date
from pathlib import Path
from types import SimpleNamespace


SCRIPT_PATH = Path(__file__).resolve().parents[2] / "my-research" / "scripts" / "oi_gamma_watchlist_ibkr.py"
SPEC = importlib.util.spec_from_file_location("oi_gamma_watchlist_ibkr", SCRIPT_PATH)
mod = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(mod)


def q(strike, right, oi, volume=10, gamma=0.01, expiration="20260605"):
    return mod.OptionQuote(
        ticker="NVDA",
        expiration=expiration,
        strike=strike,
        right=right,
        bid=1.0,
        ask=1.2,
        last=1.1,
        volume=volume,
        open_interest=oi,
        implied_volatility=0.45,
        delta=0.4 if right == "C" else -0.3,
        gamma=gamma,
        theta=-0.02,
        vega=0.05,
    )


class OiGammaWatchlistIbkrTests(unittest.TestCase):
    def test_select_expirations_prefers_nearest_and_next_monthly(self):
        expirations = ["20260605", "20260612", "20260619", "20260717"]

        selected = mod.select_expirations(expirations, today=date(2026, 6, 1))

        self.assertEqual(selected, ["20260605", "20260619"])

    def test_select_strikes_keeps_spot_window_and_side_limit(self):
        strikes = [80, 85, 90, 95, 100, 105, 110, 115, 120]

        selected = mod.select_strikes(strikes, spot=100, pct_window=0.05, max_each_side=2)

        self.assertEqual(selected, [90.0, 95.0, 100.0, 105.0])

    def test_compute_max_pain_uses_call_and_put_oi(self):
        quotes = [
            q(90, "P", 100),
            q(100, "C", 50),
            q(100, "P", 50),
            q(110, "C", 100),
        ]

        self.assertEqual(mod.compute_max_pain(quotes), 100)

    def test_scan_ticker_from_quotes_marks_watch_near_call_wall(self):
        quotes = [
            q(100, "C", 100),
            q(105, "C", 300),
            q(110, "C", 200),
            q(95, "P", 250),
            q(90, "P", 100),
        ]

        scan = mod.scan_ticker_from_quotes("NVDA", 104.0, quotes)

        self.assertEqual(scan.status, "WATCH")
        self.assertEqual(scan.setup, "GAMMA_BREAKOUT")
        self.assertEqual(scan.nearest_call_wall, 105)
        self.assertEqual(scan.next_call_wall, 110)
        self.assertEqual(scan.largest_put_oi_strike, 95)
        self.assertIsNotNone(scan.max_pain)

    def test_ticker_to_quote_preserves_signed_greeks(self):
        provider = mod.IBKROptionsProvider("127.0.0.1", 4002, 99)
        contract = SimpleNamespace(
            right="P",
            lastTradeDateOrContractMonth="20260605",
            strike=100,
        )
        greeks = SimpleNamespace(impliedVol=0.5, delta=-0.42, gamma=0.012, theta=-0.03, vega=0.07)
        market = SimpleNamespace(
            contract=contract,
            bid=2.0,
            ask=2.2,
            last=2.1,
            putVolume=123,
            putOpenInterest=456,
            modelGreeks=greeks,
        )

        quote = provider._ticker_to_quote("NVDA", market)

        self.assertEqual(quote.right, "P")
        self.assertEqual(quote.volume, 123)
        self.assertEqual(quote.open_interest, 456)
        self.assertEqual(quote.delta, -0.42)
        self.assertEqual(quote.theta, -0.03)

    def test_markdown_and_csv_writers_create_artifacts(self):
        scan = mod.scan_ticker_from_quotes("NVDA", 104.0, [q(105, "C", 300), q(95, "P", 200)])
        with tempfile.TemporaryDirectory() as tmpdir:
            md_path = Path(tmpdir) / "scan.md"
            csv_path = Path(tmpdir) / "scan.csv"

            mod.write_markdown(str(md_path), date(2026, 6, 1), [scan])
            mod.write_csv(str(csv_path), date(2026, 6, 1), [scan])

            self.assertIn("# Daily OI Gamma Watchlist - 2026-06-01", md_path.read_text())
            self.assertIn("NVDA", csv_path.read_text())


if __name__ == "__main__":
    unittest.main()
