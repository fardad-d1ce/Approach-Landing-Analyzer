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
    relative_path = f"{folder_name}/{filename}"
    return f"/results/{quote(relative_path, safe='/')}"

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
                
                result_dir, manifest_data = run_pipeline(csv_path=temp_path)
        else:
            result_dir, manifest_data = run_pipeline()

        # Build final manifest with URLs for the frontend
        folder_name = manifest_data["folder_name"]
        
        for chart in manifest_data["landing_charts"]:
            chart["url"] = build_results_url(folder_name, chart["filename"])
            
        final_manifest = {
            "folder_name": folder_name,
            "folder_url": f"/results/{quote(folder_name)}",
            "evaluation_table_html_url": build_results_url(folder_name, manifest_data["evaluation_table_html"]),
            "evaluation_table_image_url": build_results_url(folder_name, manifest_data["evaluation_table_image"]),
            "landing_charts": manifest_data["landing_charts"],
        }

        return {
            "status": "success",
            "message": f"Analysis completed successfully.",
            "results": final_manifest,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e
