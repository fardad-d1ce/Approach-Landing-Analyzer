import re
import tomllib
from pathlib import Path

# Load the configuration file from the backend root.
config_path = Path(__file__).parent.parent / "config.toml"
with config_path.open('rb') as f:
    config = tomllib.load(f)

PILOT_CALLSIGN_REGEX = config["squadron"]["PILOT_CALLSIGN_REGEX"]

def extract_pilot_name(pilot):
    """Extracts the pilot's name, removing the leading '< 404 > ' or '< 404C > ' if present."""
    match = re.match(PILOT_CALLSIGN_REGEX, pilot)
    if match:
        return match.group(1).lstrip()
    return pilot  # Return original name if no match

# replace < and > with ( and )
def replace_angles(text):
    return text.replace('<', '(').replace('>', ')')

def extract_date_name_tacview(path: Path):
    """
    Extracts the date and mission name from a Tacview filename.
    Returns None, None if the filename does not match the expected format.
    Example filename: "Tacview-20230801-123456-789012-DCS-Host-mission_name.zip"
    Returns: ("20230801", "mission name")
    """
    TACVIEW_PATTERN = r"Tacview-(\d{8})-\d+-[^-]+-(?:Host|Client)-(.*)"
    extracted_filename = path.stem
    match = re.search(TACVIEW_PATTERN, extracted_filename)
    try:
        if match:
            extracted_date = match.group(1)
            extracted_mission_name = match.group(2)
            return extracted_date, extracted_mission_name
    except IndexError:
        print(f"Filename {extracted_filename} does not match the expected format.")
        return None, None

def format_seconds(seconds: float, pos=None) -> str:
    '''Converts seconds into HH:MM:SS format for time axis.'''
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds = seconds % 60
    return f'{hours:02}:{minutes:02}:{seconds:05.2f}'
