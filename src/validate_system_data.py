import pandas as pd
import config

# 1. The barcode that must be unique: the utc quarter-hour
KEY = ["utc"]


def check_duplicate_keys(df):
    # 2. Mark EVERY row whose barcode appears more than once
    dup_mask = df.duplicated(subset=KEY, keep=False)

    # 3. Pull out those rows and write down why they are bad
    bad = df[dup_mask].copy()
    bad["reason"] = "duplicate key (utc)"

    # 4. Return the bad pallets. An empty table means the check passed
    return bad


def check_nulls(df):
    # 5. List the columns that must never be empty: every tidy column we ordered, plus utc
    required = list(config.SD_RENAME.values()) + ["utc"]

    # 6. Mark every row that has at least one empty cell in those columns
    null_mask = df[required].isna().any(axis=1)

    # 7. Pull out those rows and write down why they are bad
    bad = df[null_mask].copy()
    bad["reason"] = "null value in a required column"

    # 8. Return the bad pallets. An empty table means the check passed
    return bad

def check_negatives(df):
    # 1. Pick every number column (the tidy names, except the date)
    num_cols = [c for c in config.SD_RENAME.values() if c != "local_time"]

    # 2. Mark every row where any value is below zero
    neg_mask = (df[num_cols] < 0).any(axis=1)

    # 3. Pull out those rows and write down why they are bad
    bad = df[neg_mask].copy()
    bad["reason"] = "negative value"

    # 4. Return the bad pallets. An empty table means the check passed
    return bad


def check_snsp_range(df):
    # 5. SNSP is stored as a fraction (0.6375 = 63.75%), so it must lie between 0 and 1
    out_mask = (df["snsp"] < 0) | (df["snsp"] > 1)

    # 6. Pull out those rows and write down why they are bad
    bad = df[out_mask].copy()
    bad["reason"] = "snsp outside 0 to 1"

    # 7. Return the bad pallets
    return bad


def check_wind_not_above_total(df):
    # 8. Start with "no row is bad", then test each jurisdiction
    bad_mask = pd.Series(False, index=df.index)

    for j in ["ie", "ni"]:
        # 9. Wind is a slice of total generation, so it can never be bigger than the total
        #    (small allowance for rounding, the same tolerance as the dispatch-down totals check)
        wind = df[f"{j}_wind_generation"]
        total = df[f"{j}_generation"]
        bad_mask = bad_mask | (wind > total + config.SUM_TOLERANCE)

    # 10. Pull out those rows and write down why they are bad
    bad = df[bad_mask].copy()
    bad["reason"] = "wind generation above total generation"

    # 11. Return the bad pallets
    return bad