import pandas as pd
import config

# 1. The barcode that must be unique: plant type + jurisdiction + utc
KEY = ["UT_TYPE", "JURISDICTION", "utc"]


def check_duplicate_keys(df):
    # 2. Mark EVERY row whose barcode appears more than once (keep=False marks all copies, not just the later ones)
    dup_mask = df.duplicated(subset=KEY, keep=False)

    # 3. Pull out those rows and write down why they are bad
    bad = df[dup_mask].copy()
    bad["reason"] = "duplicate key (type + jurisdiction + utc)"

    # 4. Return the bad pallets. An empty table means the check passed
    return bad

def check_nulls(df):
    # 1. List the columns that must never be empty: everything we ordered, plus the utc barcode
    required = config.DD_COLUMNS + ["utc"]

    # 2. Mark every row that has at least one empty cell in those columns
    null_mask = df[required].isna().any(axis=1)

    # 3. Pull out those rows and write down why they are bad
    bad = df[null_mask].copy()
    bad["reason"] = "null value in a required column"

    # 4. Return the bad pallets. An empty table means the check passed
    return bad

def check_negatives(df):
    # 1. Pick every energy column (the ones whose name ends in _MWH)
    mwh_cols = [c for c in config.DD_COLUMNS if c.endswith("_MWH")]

    # 2. Mark every row where any energy value is below zero
    neg_mask = (df[mwh_cols] < 0).any(axis=1)

    # 3. Pull out those rows and write down why they are bad
    bad = df[neg_mask].copy()
    bad["reason"] = "negative MWh value"

    # 4. Return the bad pallets. An empty table means the check passed
    return bad

def check_totals_add_up(df):
    # 1. Write down the packing-slip rules: each total and the parts it must equal
    rules = {
        "DD_MWH": ["CONSTRAINTS_MWH", "CURTAILMENTS_MWH"],
        "CONSTRAINTS_MWH": ["TRANS_CONSTR_MWH", "TSO_TEST_MWH"],
        "CURTAILMENTS_MWH": ["HI_FRQ_MIN_GEN_MWH", "ROCOF_INERTIA_MWH", "SNSP_MWH"],
    }

    # 2. Start with "no row is bad", then mark rows as each rule is tested
    bad_mask = pd.Series(False, index=df.index)

    for total, parts in rules.items():
        # 3. How far is the stated total from the sum of its parts?
        difference = (df[total] - df[parts].sum(axis=1)).abs()

        # 4. A row is bad if the difference is bigger than our tolerance
        bad_mask = bad_mask | (difference > config.SUM_TOLERANCE)

    # 5. Pull out the bad rows and write down why they are bad
    bad = df[bad_mask].copy()
    bad["reason"] = "a total does not equal the sum of its parts"

    # 6. Return the bad pallets. An empty table means the check passed
    return bad

def check_output_not_above_availability(df):
    # 1. Output is what was produced and availability is what could have been produced,
    #    so output should never be meaningfully bigger than availability
    over_mask = df["AO_MWH"] > df["AV_MWH"] + config.AO_TOLERANCE

    # 2. Pull out those rows and write down why they are bad
    bad = df[over_mask].copy()
    bad["reason"] = "output above availability"

    # 3. Return the bad pallets. An empty table means the check passed
    return bad