import numpy as np
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


def find_closest_runway(lat, lon, runway_db: dict):
    '''Returns the closest runway threshold to a given point.

    Args:
        lat: Latitude of the query point.
        lon: Longitude of the query point.
        runway_db: Dictionary containing runway threshold database.

    Returns:
        dict: Airport, runway, threshold coordinates, and distance in feet.
    '''
    from pathlib import Path
    import json


    closest_match = None
    closest_distance_ft = float("inf")

    for airport_name, airport_data in runway_db.items():
        for runway_name, runway_coords in airport_data.get("Runways", {}).items():
            runway_lat, runway_lon = runway_coords
            distance_ft = haversine(lat, lon, runway_lat, runway_lon)

            if distance_ft < closest_distance_ft:
                closest_distance_ft = distance_ft
                closest_match = {
                    "airport_name": airport_name,
                    "runway": runway_name,
                    "runway_coordinates": (runway_lat, runway_lon),
                    "distance_ft": distance_ft,
                }

    if closest_match is None:
        raise ValueError(f"No runway thresholds found in {db_path}")

    return closest_match

