"""Reusable backend calculations for the 2024 Chase California county screen.

The source is the canonical Phase 2 county_metrics_2024.csv on main.
Only counties with at least one mapped CFPB mortgage complaint appear in it.
"""
from pathlib import Path

import numpy as np
import pandas as pd

DATA_FILE = Path(__file__).resolve().parent / "county_metrics_2024.csv"
COUNTY_ID = "GEOID_COUNTY_20"
COUNTY_NAME = "NAMELSAD_COUNTY_20"
COMPLAINTS = "complaints"
ORIGINATIONS = "originations"
RATE = "complaints_per_1000_originations"
REQUIRED = [COUNTY_ID, COUNTY_NAME, COMPLAINTS, ORIGINATIONS, RATE]


def load_county_metrics(csv_path=DATA_FILE):
    """Read and validate the fixed 2024 Chase CA county-level analysis file."""
    frame = pd.read_csv(csv_path, dtype={COUNTY_ID: "string", COUNTY_NAME: "string"})
    missing_columns = sorted(set(REQUIRED) - set(frame.columns))
    if missing_columns:
        raise ValueError(f"Missing required columns: {missing_columns}")
    frame = frame[REQUIRED].copy()
    frame[COUNTY_NAME] = frame[COUNTY_NAME].str.strip()
    if frame[REQUIRED].isna().any().any() or frame[COUNTY_NAME].eq("").any():
        raise ValueError("Missing county keys, names, or metric values")
    if not frame[COUNTY_ID].str.fullmatch(r"06\d{3}").all():
        raise ValueError("County FIPS must be five-digit California codes")
    if frame[COUNTY_ID].duplicated().any():
        raise ValueError("The analysis must have one row per county")
    for column in [COMPLAINTS, ORIGINATIONS, RATE]:
        frame[column] = pd.to_numeric(frame[column], errors="raise")
    for column in [COMPLAINTS, ORIGINATIONS]:
        if (frame[column] % 1 != 0).any() or (frame[column] < 0).any():
            raise ValueError(f"{column} must be a nonnegative whole-number count")
        frame[column] = frame[column].astype("int64")
    if (frame[ORIGINATIONS] == 0).any():
        raise ValueError("This source stores a rate for every row; zero denominators are invalid")
    expected = 1000 * frame[COMPLAINTS] / frame[ORIGINATIONS]
    if not np.isclose(frame[RATE].to_numpy(), expected.to_numpy(), rtol=1e-10, atol=1e-8).all():
        raise ValueError("At least one county rate disagrees with complaints / originations * 1000")
    return frame


def overview_metrics(frame):
    """Return a labeled summary of ONLY the counties represented in the file."""
    mapped = int(frame[COMPLAINTS].sum())
    originated = int(frame[ORIGINATIONS].sum())
    return {
        "counties_with_mapped_complaints": int(len(frame)),
        "mapped_complaints": mapped,
        "originations_in_these_counties": originated,
        "pooled_complaints_per_1000_originations": 1000 * mapped / originated if originated else None,
    }


def rank_counties(frame, min_originations=0, limit=None):
    """Return counties sorted by observed rate; optional denominator floor."""
    if not isinstance(min_originations, int) or min_originations < 0:
        raise ValueError("min_originations must be a nonnegative integer")
    if limit is not None and (not isinstance(limit, int) or limit < 1):
        raise ValueError("limit must be a positive integer or None")
    ranked = frame.loc[frame[ORIGINATIONS] >= min_originations, REQUIRED].sort_values(
        [RATE, COUNTY_ID], ascending=[False, True], kind="stable"
    )
    if limit is not None:
        ranked = ranked.head(limit)
    return ranked.reset_index(drop=True)


def county_detail(frame, county_fips):
    """Return a one-row DataFrame for a specified five-digit county FIPS code."""
    result = frame.loc[frame[COUNTY_ID].eq(str(county_fips)), REQUIRED]
    if result.empty:
        raise KeyError(f"County {county_fips!r} is not present in the 25-county dataset")
    return result.reset_index(drop=True).copy()
