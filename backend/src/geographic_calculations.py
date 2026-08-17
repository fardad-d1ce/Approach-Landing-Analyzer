import numpy as np
import pandas as pd
from pathlib import Path
import tomllib

def haversine (lat1,lon1,lat2,lon2):
    '''Calculates the Haversine distance between two coordinates.'''
    R = 6371  # Radius of the Earth in km
    delta_lat = np.radians(lat2 - lat1)
    delta_lon = np.radians(lon2 - lon1)
    a = np.sin(delta_lat/2) ** 2 + np.cos(np.radians(lat1)) * np.cos(np.radians(lat2)) * np.sin(delta_lon/2) ** 2   
    dist = 2 * R * np.arcsin(np.sqrt(a)) * 3280.84  # convert to ft
    return dist

def l1_distance(lat1,lon1,lat2,lon2):
    '''Calculates the L1 Manhattan distance between two lat/lon coordinates.'''
    return np.abs(lat1 - lat2) + np.abs(lon1 - lon2)

def bearing_true(lat1,lon1,lat2,lon2):
    '''Calculates the approx. bearing between two "close" coordinates in degrees.'''
    delta_lat = np.radians(lat2 - lat1) 
    delta_lon = np.radians(lon2 - lon1)
    bearing = np.arctan2(delta_lon, delta_lat) * 180 / np.pi
    return bearing % 360

def find_closest_runway(lat, lon, heading, runway_db: pd.DataFrame) -> dict:
    '''Returns the closest runway threshold to a given point.

    Args:
        lat: Latitude of the query point, e.g. touchdown point.
        lon: Longitude of the query point.
        heading: Heading of the query aircraft.
        runway_db: DataFrame containing runway threshold database.

    Returns:
        dict: Airport, runway, threshold coordinates, and distance in feet.
    '''

    distances_ft = haversine(lat, lon, runway_db['lat'].values, runway_db['lon'].values)
    
    if len(distances_ft) == 0:
        raise ValueError("No runway thresholds provided in runway_db")
        
    min_idx = np.nanargmin(distances_ft)
    closest_distance_ft = distances_ft[min_idx]
    MAX_FEASIBLE_DISTANCE_FT = 10000

    if closest_distance_ft > MAX_FEASIBLE_DISTANCE_FT:
        closest_match = {
            "airport": None,
            "runway": None,
            "runway_coordinates": None,
            "distance_ft": None,
        }
        return closest_match
    
    # 1. Detect the closest airport by finding the closest runway threshold
    closest_airport_row = runway_db.iloc[min_idx]

    # 2. Filter the runway_db to that specific airport
    airport_mask = runway_db["airport_name"] == closest_airport_row["airport_name"]
        
    closest_airport_runways = runway_db[airport_mask]
    
    # 3. Find the runway whose direction to the touchdown point is most aligned with its heading
    best_runway = closest_airport_row
    min_heading_diff = float('inf')

    for _, row in closest_airport_runways.iterrows():
        if 'heading_T' not in row or pd.isna(row['heading_T']):
            continue

        heading_diff = abs(row['heading_T'] - heading)
        heading_diff = min(heading_diff, 360 - heading_diff)
        if heading_diff > 90:
            continue
        # Calculate heading from threshold to touchdown point
        bearing = bearing_true(row['lat'], row['lon'], lat, lon)
            
        # Calculate angular difference
        diff = abs(bearing - row['heading_T'])
        diff = min(diff, 360 - diff)
        
        if diff < min_heading_diff:
            min_heading_diff = diff
            best_runway = row
            
    # Recalculate distance to the newly selected best runway threshold
    best_distance_ft = haversine(lat, lon, best_runway['lat'], best_runway['lon'])

    closest_match = {
        "airport": ( # icao_code or iata_code or airport_name
                        best_runway[["icao_code",
                                        "iata_code",
                                        "airport_name"]].dropna().iloc[0]
        ),
        "runway": best_runway["runway_name"],
        "runway_coordinates": (best_runway["lat"], best_runway["lon"]),
        "distance_ft": best_distance_ft,
    }

    return closest_match

