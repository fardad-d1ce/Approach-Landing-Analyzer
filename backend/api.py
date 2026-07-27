from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from run_analysis import main as run_pipeline
import shutil
import tempfile
from pathlib import Path

app = FastAPI(title="Landing Analyzer API")

# This allows your Vue frontend (running on port 5173) to talk to this Python API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"], # Allows Vue frontend to talk to this API
    # allow_origins=["*"], # Allows all origins for local development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
                
                run_pipeline(csv_path=temp_path)
            return {"status": "success", "message": f"Analysis of {file.filename} completed successfully."}
        else:
            run_pipeline()
            return {"status": "success", "message": "Analysis of default CSV completed successfully."}
    except Exception as e:
        return {"status": "error", "message": str(e)}