from pathlib import Path
import pandas as pd
import config


def load_sd_file(path):
    path = Path(path)

    # 1. Open the box
    df = pd.read_excel(path, sheet_name=config.SD_SHEET)

    # 2. Tidy the labels (remove stray spaces at the ends of the names)
    df.columns = [str(c).strip() for c in df.columns]

    # 3. Tick off the order sheet. Fail loudly if anything is missing
    missing = [c for c in config.SD_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(f"{path.name}: missing columns {missing}")

    # 4. Keep only the columns we ordered
    df = df[config.SD_COLUMNS].copy()

    # 5. Relabel to SQL-friendly names (no spaces, lower case)
    df = df.rename(columns=config.SD_RENAME)

    # 6. Make sure the timestamp is a real date, then add the barcode
    df["local_time"] = pd.to_datetime(df["local_time"])
    df["utc"] = df["local_time"] - pd.to_timedelta(df["gmt_offset"], unit="h")

    # 7. Note which lorry it came from
    df["source_file"] = path.name
    return df

def load_all_sd():
    # 1. Find every System Data workbook, skipping Excel's temporary "~$" lock files
    files = sorted(
        f for f in config.RAW_SD_DIR.glob("*.xlsx") if not f.name.startswith("~$")
    )
    if not files:
        raise FileNotFoundError(f"No System Data files found in {config.RAW_SD_DIR}")

    # 2. Unload each lorry with the tested one-file procedure
    frames = [load_sd_file(f) for f in files]

    # 3. Stack everything in one bay, then sort by the utc barcode
    df = pd.concat(frames, ignore_index=True)
    return df.sort_values("utc").reset_index(drop=True)