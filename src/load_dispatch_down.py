from pathlib import Path
import pandas as pd
import config


def load_dd_file(path):
    path = Path(path)

    # 1. Open the box
    df = pd.read_excel(path, sheet_name=config.DD_SHEET)

    # 2. Tidy the labels ("Sum of AV_MWH" becomes "AV_MWH")
    df.columns = [str(c).replace("Sum of ", "").strip() for c in df.columns]

    # 3. Tick off the order sheet. Fail loudly if anything is missing
    missing = [c for c in config.DD_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(f"{path.name}: missing columns {missing}")

    # 4. Keep only the columns we ordered
    df = df[config.DD_COLUMNS].copy()

    # 5. Keep only the plant types we decided to work with (Wind). Fail loudly if none are left
    df = df[df["UT_TYPE"].isin(config.DD_UT_TYPES)].copy()
    if df.empty:
        raise ValueError(f"{path.name}: no rows left for types {config.DD_UT_TYPES}")

    # 6. Make sure the timestamp is a real date, then add the barcode
    df["HH_TIMESTAMP"] = pd.to_datetime(df["HH_TIMESTAMP"])
    df["utc"] = df["HH_TIMESTAMP"] - pd.to_timedelta(df["GMT_OFFSET"], unit="h")

    # 7. Note which lorry it came from
    df["source_file"] = path.name
    return df

def load_all_dd():
    files = sorted(config.RAW_DD_DIR.glob("DD-HH*.xlsx"))
    if not files:
        raise FileNotFoundError(f"No dispatch-down files found in {config.RAW_DD_DIR}")

    frames = [load_dd_file(f) for f in files]
    df = pd.concat(frames, ignore_index=True)

    return df.sort_values(["UT_TYPE", "JURISDICTION", "utc"]).reset_index(drop=True)