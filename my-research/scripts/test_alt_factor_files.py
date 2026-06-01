#!/usr/bin/env python3
"""
Smoke tests for reusable altcoin factor files.

These tests intentionally execute factor files the same way the research
scripts do: by providing df/params in a namespace and reading new columns back.
"""

from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
FACTOR_DIR = ROOT / "factors"


EXPECTED_COLUMNS = {
    "factor_funding_extreme.py": [
        "funding_z",
        "price_z",
        "funding_extreme_trigger",
        "funding_extreme_score",
    ],
    "factor_funding_bottom_fisher.py": [
        "funding_bottom_price_z",
        "funding_bottom_trigger",
        "funding_bottom_score",
    ],
    "factor_liq_wick_sweep.py": [
        "liq_wick_sweep_trigger",
        "liq_wick_sweep_strength",
        "liq_wick_sweep_score",
    ],
    "factor_sfp_reversal.py": [
        "sfp_reversal_trigger",
        "sfp_reversal_strength",
        "sfp_reversal_score",
    ],
    "factor_vol_climax_bottom.py": [
        "vol_climax_bottom_trigger",
        "vol_climax_bottom_strength",
        "vol_climax_bottom_score",
    ],
    "factor_funding_liq_wick.py": [
        "funding_liq_wick_trigger",
        "funding_liq_wick_strength",
        "funding_liq_wick_score",
    ],
}


def sample_df() -> pd.DataFrame:
    index = pd.date_range("2026-01-01", periods=140, freq="4h")
    close = pd.Series(np.linspace(120, 100, len(index)), index=index)
    open_ = close.shift(1).fillna(close.iloc[0])
    high = pd.concat([open_, close], axis=1).max(axis=1) + 1
    low = pd.concat([open_, close], axis=1).min(axis=1) - 1
    volume = pd.Series(1000.0, index=index)
    funding = pd.Series(0.0001, index=index)

    # Funding capitulation bar for funding-only factors.
    i = index[-2]
    open_.loc[i] = 100
    close.loc[i] = 80
    high.loc[i] = 101
    low.loc[i] = 78
    volume.loc[i] = 2500
    funding.loc[i] = -0.003

    # Stop-hunt recovery bar for wick/SFP/climax factors.
    i = index[-1]
    open_.loc[i] = 82
    close.loc[i] = 96
    high.loc[i] = 98
    low.loc[i] = 70
    volume.loc[i] = 7000
    funding.loc[i] = -0.004

    df = pd.DataFrame(
        {
            "open": open_,
            "high": high,
            "low": low,
            "close": close,
            "volume": volume,
            "funding_rate": funding,
        }
    )
    return df


def execute_factor(path: Path, df: pd.DataFrame):
    namespace = {"df": df.copy(), "params": {}, "pd": pd, "np": np}
    exec(path.read_text(encoding="utf-8"), namespace)
    return namespace["df"]


def main() -> int:
    df = sample_df()
    failures = []
    for filename, columns in EXPECTED_COLUMNS.items():
        path = FACTOR_DIR / filename
        if not path.exists():
            failures.append(f"{filename}: missing")
            continue

        out = execute_factor(path, df)
        for col in columns:
            if col not in out.columns:
                failures.append(f"{filename}: missing column {col}")
            elif not pd.api.types.is_numeric_dtype(out[col]):
                failures.append(f"{filename}: column {col} is not numeric")

        score_cols = [c for c in columns if c.endswith("_score")]
        if score_cols and not any(float(out[c].abs().sum()) > 0 for c in score_cols):
            failures.append(f"{filename}: score columns never fire on sample event")

    if failures:
        print("\n".join(failures))
        return 1

    print(f"ok - {len(EXPECTED_COLUMNS)} alt factor files executed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
