from pathlib import Path
import json
import pandas as pd

REQUIRED_COLUMNS = [
    "ISO time", # for Timestamps
    "Latitude", # Latitude: degrees
    "Longitude", # Longitude: degrees
    "Altitude", # ASL: m
    "Name", # Aircraft Type
    "Pilot", # Pilot name
    "CAS", # Calibrated Air Speed in knots: half of kts
    "AGL", # AGL: m
    "VS" # Vertical Speed: m/s
]

class CSVInputError(ValueError):
    pass

def read_telemetry_csv(file_path: str | Path) -> pd.DataFrame:
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"CSV file not found: {path}")

    try:
        df = pd.read_csv(path)
    except Exception as exc:
        raise CSVInputError(f"Failed to read CSV file: {path}") from exc

    missing = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing:
        raise CSVInputError(
            "CSV schema mismatch. Missing required columns: "
            + ", ".join(missing)
        )

    return df

def load_runway_db(db_path: Path | str):
    '''Loads the runway threshold database from a JSON file.'''
    
    db_path = Path(db_path)
    if not db_path.exists():
        raise FileNotFoundError(f"Runway DB file not found: {db_path}")

    with db_path.open("r", encoding="utf-8") as f:
        runway_db = json.load(f)

    if not runway_db:
        raise ValueError(f"Runway DB is empty: {db_path}")

    return runway_db