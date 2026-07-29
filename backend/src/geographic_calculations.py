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


def find_closest_runway(lat, lon, runway_db: pd.DataFrame) -> dict:
    '''Returns the closest runway threshold to a given point.

    Args:
        lat: Latitude of the query point.
        lon: Longitude of the query point.
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
    else:
        closest_airport = runway_db.iloc[min_idx]
        closest_match = {
            "airport": ( # icao_code or iata_code or airport_name
                            closest_airport[["icao_code",
                                            "iata_code",
                                            "airport_name"]].dropna().iloc[0]
            ),
            "runway": closest_airport["runway_name"],
            "runway_coordinates": (closest_airport["lat"], closest_airport["lon"]),
            "distance_ft": closest_distance_ft,
    }

    return closest_match

