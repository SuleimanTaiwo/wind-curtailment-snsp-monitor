import logging

import pandas as pd

import config
import load_system_data as loader
import validate_system_data as v

# 1. The list of inspectors: a label for the logbook, plus the function to call
CHECKS = [
    ("duplicate keys", v.check_duplicate_keys),
    ("nulls", v.check_nulls),
    ("negatives", v.check_negatives),
    ("snsp range", v.check_snsp_range),
    ("wind not above total", v.check_wind_not_above_total),
]


def run():
    # 2. Make sure the output folders exist (create them on the first run)
    for folder in [config.LOG_DIR, config.REJECTED_DIR, config.PROCESSED_DIR]:
        folder.mkdir(parents=True, exist_ok=True)

    # 3. Name the two output files once, so every step uses the same names
    rejected_path = config.REJECTED_DIR / "rejected_rows_system_data.csv"
    clean_path = config.PROCESSED_DIR / "system_data_clean.csv"

    # 4. Throw away outputs from any earlier run, so a failed run can never leave an old "clean" file that looks current
    rejected_path.unlink(missing_ok=True)
    clean_path.unlink(missing_ok=True)

    # 5. Open the logbook: every line goes to a file AND to the screen, with the time
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s  %(message)s",
        handlers=[
            logging.FileHandler(config.LOG_DIR / "stage1_system_data.log"),
            logging.StreamHandler(),
        ],
    )

    # 6. Unload all the lorries and write down what arrived
    df = loader.load_all_sd()
    logging.info("loaded %s rows from %s files", len(df), df["source_file"].nunique())

    # 7. Send each inspector down the bay and keep every bad pallet he finds
    rejected_parts = []
    for name, check in CHECKS:
        bad = check(df)
        logging.info("check '%s': %s bad rows", name, len(bad))
        if len(bad) > 0:
            rejected_parts.append(bad)

    # 8. If any bad pallets were found: lock them in quarantine, shout, and stop
    if rejected_parts:
        rejected = pd.concat(rejected_parts, ignore_index=True)
        rejected.to_csv(rejected_path, index=False)
        logging.error("%s rows rejected, saved to %s", len(rejected), rejected_path)
        raise ValueError(f"Stage 1 stopped: {len(rejected)} rows failed validation")

    # 9. All clear: sign off and save the clean table for PostgreSQL
    df.to_csv(clean_path, index=False)
    logging.info("all checks passed; saved %s rows to %s", len(df), clean_path)


if __name__ == "__main__":
    run()