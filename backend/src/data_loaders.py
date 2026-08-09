from pathlib import Path

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
        dtype={'Id': str}
        df = pd.read_csv(path, dtype=dtype)
    except Exception as exc:
        raise CSVInputError(f"Failed to read CSV file: {path}") from exc

    missing = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing:
        raise CSVInputError(
            "CSV schema mismatch. Missing required columns: "
            + ", ".join(missing)
        )
    print(f"Successfully read CSV file: {path}")
    print("Pilots:", df['Pilot'].unique())
    return df

def load_runway_db(ref_dir: Path | str) -> pd.DataFrame:
    '''Loads the runway threshold database from airports and runways CSV files.'''
    
    # Use the parent directory of the original db_path to locate the CSVs
    ref_dir = Path(ref_dir)
    airports_path = ref_dir / "airports.csv"
    runways_path = ref_dir / "runways.csv"
    
    if not airports_path.exists():
        raise FileNotFoundError(f"Airports DB file not found: {airports_path}")
    if not runways_path.exists():
        raise FileNotFoundError(f"Runways DB file not found: {runways_path}")

    # Load dataframes with only necessary columns to save memory
    df_airports = pd.read_csv(airports_path, usecols=['id', 'name', 'ident', 
                                                    'iata_code', 'icao_code'])
    df_runways = pd.read_csv(runways_path, 
                                usecols=['airport_ref', 
                                        'le_ident', 'le_latitude_deg', 'le_longitude_deg', 
                                        'he_ident', 'he_latitude_deg', 'he_longitude_deg'])

    # Merge airports with runways
    df_merged = pd.merge(df_runways, df_airports,   left_on='airport_ref', 
                                                    right_on='id', 
                                                    how='inner')

    # Unpivot the runways so that each threshold (le and he) gets its own row
    df_le = df_merged[['name', 'iata_code', 'icao_code', 
                        'le_ident', 'le_latitude_deg', 'le_longitude_deg']].copy()
    df_le.rename(columns={'le_ident': 'runway_name', 'le_latitude_deg': 'lat', 
                            'le_longitude_deg': 'lon'}, inplace=True)

    df_he = df_merged[['name', 'iata_code', 'icao_code', 
                        'he_ident', 'he_latitude_deg', 'he_longitude_deg']].copy()
    df_he.rename(columns={'he_ident': 'runway_name', 'he_latitude_deg': 'lat', 
                            'he_longitude_deg': 'lon'}, inplace=True)

    # Combine both ends
    runway_db = pd.concat([df_le, df_he], ignore_index=True)

    # Drop thresholds without coordinates and rename columns for consistency
    runway_db.dropna(subset=['lat', 'lon'], inplace=True)
    runway_db.rename(columns={'name': 'airport_name'}, inplace=True)

    if runway_db.empty:
        raise ValueError(f"Runway DB is empty after processing CSVs in {ref_dir}")

    print("Runway DB loaded successfully.")
    return runway_db