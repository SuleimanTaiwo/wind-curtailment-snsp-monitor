from pathlib import Path

# Repo root = the folder above src/
ROOT = Path(__file__).resolve().parents[1]

RAW_DD_DIR = ROOT / "data" / "raw" / "dispatch_down"
RAW_SD_DIR = ROOT / "data" / "raw" / "system_data"
PROCESSED_DIR = ROOT / "data" / "processed"
REJECTED_DIR = ROOT / "data" / "rejected"
LOG_DIR = ROOT / "logs"

DD_SHEET = "DD HH"
SD_SHEET = "System Data"
# Plant types we work with (add "Solar" here later if we ever want it)
DD_UT_TYPES = ["Wind"]

DD_COLUMNS = ["UT_TYPE", "JURISDICTION", "HH_TIMESTAMP", "GMT_OFFSET",
              "AV_MWH", "AO_MWH", "HI_FRQ_MIN_GEN_MWH", "ROCOF_INERTIA_MWH",
              "SNSP_MWH", "TRANS_CONSTR_MWH", "TSO_TEST_MWH",
              "DD_MWH", "CURTAILMENTS_MWH", "CONSTRAINTS_MWH", "OTHER_MWH"]

SD_COLUMNS = ["DateTime", "GMT Offset", "IE Demand", "NI Demand",
              "IE Wind Availability", "NI Wind Availability",
              "IE Wind Generation", "NI Wind Generation", "SNSP",
              "IE Generation", "NI Generation"]

# Tidy SQL-friendly names for the System Data columns (no spaces, lower case)
SD_RENAME = {
    "DateTime": "local_time",
    "GMT Offset": "gmt_offset",
    "IE Demand": "ie_demand",
    "NI Demand": "ni_demand",
    "IE Wind Availability": "ie_wind_availability",
    "NI Wind Availability": "ni_wind_availability",
    "IE Wind Generation": "ie_wind_generation",
    "NI Wind Generation": "ni_wind_generation",
    "SNSP": "snsp",
    "IE Generation": "ie_generation",
    "NI Generation": "ni_generation",
}


# How far two totals may differ before we call it a mismatch (MWh).
# Set to 0.1 because the source files show rounding differences of up to
# 0.041 MWh on about 0.5% of rows, spread across every file and year.
SUM_TOLERANCE = 0.1

# How far output (AO_MWH) may exceed availability (AV_MWH) before we call it a fault (MWh).
# Set to 0.5 because the only exception in 198,620 rows was one NI row in 2025, 0.13 MWh above.
AO_TOLERANCE = 0.5
