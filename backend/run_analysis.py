import tomllib
from pathlib import Path

from src.data_loaders import read_telemetry_csv, load_runway_db
from src.parsers import extract_date_name_tacview
from src.transformer_plotter import (transform_telemetry, 
                                    touchdown_discovery,
                                    style_result_table,
                                    plot_landing_profile,
                                    touchdown_plotter)

# Load the configuration file relative to this script so the entrypoint works
# whether it is launched from the repo root or from the backend folder.
config_path = Path(__file__).with_name("config.toml")
with config_path.open('rb') as f:
    config = tomllib.load(f)

PROJECT_ROOT = config_path.parent.parent

def resolve_project_path(value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else PROJECT_ROOT / path

CSV_PATH            = resolve_project_path(config['input']['CSV_PATH'])
THRESHOLDS_DB_PATH  = resolve_project_path(config["db_path"]["THRESHOLDS_DB_PATH"])
RESULTS_DIR         = resolve_project_path(config["output"]["RESULTS_DIR"])

def main():

    # extract date and mission name
    record_date, mission_name = extract_date_name_tacview(CSV_PATH)

    # Make the output path
    plots_output_path = RESULTS_DIR/f"[{record_date}] {mission_name}"
    detailed_td_path = plots_output_path/"Detailed Touchdowns"
    detailed_td_path.mkdir(parents=True, exist_ok=True)


    # 1. Load DB
    runway_db = load_runway_db(THRESHOLDS_DB_PATH)

    # 2. Touchdown Discovery
    # Read the telemetry data
    df = read_telemetry_csv(CSV_PATH)
    # clean and transform the data
    df_sub = transform_telemetry(df)
    # Discover the touch downs
    df_result = touchdown_discovery(df_sub, runway_db)

    # 3. CSS Stylized Results Table
    style_result_table(df_result, plots_output_path, record_date)

    # 4. Plot Approach Profiles
    # 5. Detailed Touchdowns (optional)
    for pilot in df_result['Pilot'].unique():
        for sortie_num in df_result[df_result['Pilot'] == pilot]['sortie_num'].unique():
            plot_landing_profile(   df_sub, df_result, pilot, sortie_num, 
                                    plots_output_path, record_date)
            # optional:
            touchdown_plotter(  df_sub, df_result, pilot, sortie_num, 
                                detailed_td_path, record_date)


if __name__ == "__main__":
    main()
