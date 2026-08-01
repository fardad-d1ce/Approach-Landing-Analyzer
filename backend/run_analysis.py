import json
import tomllib
from datetime import date
from pathlib import Path

from src.data_loaders import read_telemetry_csv, load_runway_db
from src.parsers import extract_date_name_tacview, replace_angles
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
REF_PATH             = resolve_project_path(config["db_path"]["REF_PATH"])
RESULTS_DIR         = resolve_project_path(config["output"]["RESULTS_DIR"])

def main(csv_path: Path | str | None = None):
    # Use the provided csv_path or fallback to the config default
    active_csv_path = Path(csv_path) if csv_path else CSV_PATH
    if not active_csv_path.exists():
        raise FileNotFoundError(f"CSV file not found: {active_csv_path}")

    # extract date and mission name
    record_date, mission_name = extract_date_name_tacview(active_csv_path)
    if record_date is None:
        record_date = date.today().strftime("%Y%m%d")

    # Make the output path
    plots_output_path = RESULTS_DIR/f"[{record_date}] {mission_name}"
    detailed_td_path = plots_output_path/"Detailed Touchdowns"
    detailed_td_path.mkdir(parents=True, exist_ok=True)

    # 1. Load DB
    runway_db = load_runway_db(REF_PATH)

    # 2. Touchdown Discovery
    # Read the telemetry data
    df = read_telemetry_csv(active_csv_path)
    # clean and transform the data
    df_sub = transform_telemetry(df)
    # Discover the touch downs
    df_result = touchdown_discovery(df_sub, runway_db)

    # 3. CSS Stylized Results Table
    style_result_table(df_result, plots_output_path, record_date)

    # 4. Plot Approach Profiles
    # 5. Detailed Touchdowns (optional)
    landing_charts = []
    for pilot in df_result['Pilot'].sort_values().unique():
        for sortie_num in df_result[df_result['Pilot'] == pilot]['sortie_num'].unique():
            is_sortie = plot_landing_profile(   df_sub, df_result, pilot, sortie_num, 
                                    plots_output_path, record_date, 
                                    close_fig = True)            
            # optional:
            touchdown_plotter(  df_sub, df_result, pilot, sortie_num, 
                                detailed_td_path, record_date, 
                                close_fig = True)
            if not is_sortie:
                continue
            
            # Record the generated chart for the manifest
            safe_pilot = replace_angles(pilot)
            chart_filename = f"{record_date}_{safe_pilot}_landing_{sortie_num}.png"
            landing_charts.append({
                "filename": chart_filename,
                "title": f"{pilot} - Landing {sortie_num}",
                "pilot": pilot,
                "sortie": int(sortie_num)
            })

    manifest = {
        "folder_name": plots_output_path.name,
        "evaluation_table_html": f"[{record_date}] landing_results.html",
        "evaluation_table_image": f"[{record_date}] landing_results.png",
        "landing_charts": landing_charts
    }

    # Save manifest to the specific run folder
    with (plots_output_path / "manifest.json").open("w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=4)

    # Update the global latest manifest for quick UI testing
    with (RESULTS_DIR / "latest_manifest.json").open("w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=4)

    return manifest


if __name__ == "__main__":
    main()
