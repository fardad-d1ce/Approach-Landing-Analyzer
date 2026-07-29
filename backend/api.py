import json
from urllib.parse import quote

from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from run_analysis import RESULTS_DIR, main as run_pipeline
import shutil
import tempfile
from pathlib import Path

app = FastAPI(title="Landing Analyzer API")

# This allows your Vue frontend (running on port 5173) to talk to this Python API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

RESULTS_ROOT = Path(RESULTS_DIR)
app.mount("/results", StaticFiles(directory=RESULTS_ROOT), name="results")


def build_results_url(folder_name: str, filename: str) -> str:
    if not filename:
        return ""
    relative_path = f"{folder_name}/{filename}"
    return f"/results/{quote(relative_path, safe='/')}"

def enrich_manifest(manifest_data: dict) -> dict:
    """Dynamically adds the /results/ API routing URLs to the raw manifest data."""
    folder_name = manifest_data["folder_name"]
    
    landing_charts = []
    for chart in manifest_data.get("landing_charts", []):
        new_chart = chart.copy()
        new_chart["url"] = build_results_url(folder_name, chart.get("filename", ""))
        landing_charts.append(new_chart)
        
    return {
        "folder_name": folder_name,
        "folder_url": f"/results/{quote(folder_name)}",
        "evaluation_table_html_url": build_results_url(folder_name, manifest_data.get("evaluation_table_html", "")),
        "evaluation_table_image_url": build_results_url(folder_name, manifest_data.get("evaluation_table_image", "")),
        "landing_charts": landing_charts,
    }

@app.get("/")
def health_check():
    return {"status": "online", "message": "Backend API is ready"}

@app.post("/analyze")
def trigger_analysis(file: UploadFile = File(None)):
    try:
        if file:
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir) / file.filename
                with temp_path.open("wb") as buffer:
                    shutil.copyfileobj(file.file, buffer)
                
                manifest_data = run_pipeline(csv_path=temp_path)
        else:
            manifest_data = run_pipeline()

        # Build final manifest with URLs for the frontend
        final_manifest = enrich_manifest(manifest_data)

        return {
            "status": "success",
            "message": f"Analysis completed successfully.",
            "results": final_manifest,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e

@app.get("/latest")
def get_latest_results():
    latest_manifest_path = RESULTS_ROOT / "latest_manifest.json"
    if not latest_manifest_path.exists():
        raise HTTPException(status_code=404, 
                            detail="No previous results found. Run an analysis first.")
    
    try:
        with latest_manifest_path.open("r", encoding="utf-8") as f:
            manifest_data = json.load(f)
            
        final_manifest = enrich_manifest(manifest_data)
            
        return {
            "status": "success",
            "message": "Loaded latest results from cache.",
            "results": final_manifest,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load cache: {str(e)}")
