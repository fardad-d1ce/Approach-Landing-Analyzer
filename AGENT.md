# AGENT.md

This file is for coding agents working in `Approach-Landing-Analyzer`.

## Purpose

This repository analyzes flight telemetry for approach and landing performance.
It has:

- a Python backend and analysis pipeline in `backend/`
- a Vue frontend in `frontend/`
- telemetry input data in `data/raw/`
- generated outputs in `data/results/`

The main user-facing workflow is: upload a CSV in the frontend, run the backend analysis, then render the returned manifest and generated artifacts in the UI.

## Stack

- Backend: Python 3.13+, `uv`, FastAPI, pandas, NumPy, matplotlib
- Frontend: Vue 3, Vite, npm
- Data references: `data/reference/airports.csv` and `data/reference/runways.csv`

## Local Commands

Run these from the repo root unless noted otherwise.

### Backend

- Install deps & venv:  `cd backend && uv sync`
- Run API (dev hot reload):  `cd backend && uv run uvicorn api:app --reload`
- Run pipeline (standalone): `cd backend && uv run run_analysis.py`
- Run pipeline for a single CSV:
  `cd backend && uv python -c "from run_analysis import main; main(r'ABSOLUTE\\PATH\\TO\\file.csv')"`

### Frontend

- Install: `cd frontend && npm install`
- Dev server: `cd frontend && npm run dev`
- Build: `cd frontend && npm run build`
- Lint: `cd frontend && npm run lint`
  - Run only eslint: `npm run lint:eslint`
  - Run only oxlint: `npm run lint:oxlint`
- Format: `cd frontend && npm run format`

Tests
- There is no top-level automated test suite in this repository. Use the notebook or run the pipeline with sample CSVs under data/raw/ for validation.

## High-level Architecture (Big Picture)

- Backend (`backend/`):
  - Main orchestrator and manifest writer: `backend/run_analysis.py`
  - Pipeline modules live under `backend/src/`:  
    - `data_loaders.py`: `read_telemetry_csv`, runway DB loader
    - `geographic_calculations.py`: runway-matching calculations
    - `parsers.py`: helpers for filename/metadata
    - `transformer_plotter.py`: `transform_telemetry`, `touchdown_discovery`, CSS-styled result table, plotting result charts
  - FastAPI app: `backend/api.py` 
    - serves on port `8000` and exposes:
      - `/analyze` POST endpoint
      - `/latest` cache GET endpoint
      - static `/results` mount
    - Uses the `tempfile.TemporaryDirectory()` upload pattern to handle CSV uploads.
  - Config: `backend/config.toml` controls CSV_PATH, REF_PATH, RESULTS_DIR.
- Frontend (`frontend/`):
  - Main UI: `frontend/src/App.vue` for uploading telemetry and displaying results.
  - Communicates with backend endpoints: 
    - POST `/analyze` to trigger analysis
    - GET `/latest` cached analysis results
  - frontend served on port `5173` (CORS allowed in `api.py`).
- Output: Results written into `RESULTS_DIR` with folders named `[YYYYMMDD] MissionName`. A per-run `manifest.json` and a global `latest_manifest.json` are written for UI consumption.

## Important conventions & patterns (repository-specific)
- Path/config conventions
  - Edit `backend/config.toml` for I/O paths. Values may be relative — `run_analysis.py` resolves them against the project root.
- Results manifest
  - Manifest keys used by the UI: `folder_name`, `evaluation_table_html`, `evaluation_table_image`, `landing_charts` (each chart: `filename`, `title`, `pilot`, `sortie`).
  - `latest_manifest.json` is used by the frontend GET `/latest` endpoint for quick previews.
- Filenames & safe names
  - Charts follow: `{DATE}_{safe_pilot}_landing_{sortie}.png`. Use `src.parsers.replace_angles()` to sanitize pilot name when building filenames.
- Analysis flow
  - CSV -> `read_telemetry_csv` -> `transform_telemetry` -> `touchdown_discovery` -> `style_result_table` + `plot_landing_profile` + `touchdown_plotter` -> manifest
- Development tooling
  - Backend expects Python 3.13+. The project uses `uv` (Astral) to manage venv and running commands; prefer `uv sync` and `uv run` as shown in `README.md`.
  - Frontend uses Node.js (see `package.json` engines) and relies on oxlint + eslint + prettier for linting/formatting.

## Where to look quickly
- Entrypoints: `backend/api.py` (API routes), `backend/run_analysis.py` (analysis pipeline)
- Config: `backend/config.toml`
- Data: `data/raw/` (input examples), `data/results/` (output artifacts and manifests)
- Frontend UI: `frontend/src/` and `frontend/package.json` (scripts)

## Notes for Agent sessions
- Prefer editing `backend/config.toml` when changing paths/behavior.
- For reproducing results quickly, run backend API and POST a CSV to `/analyze` from frontend or use the Python invocation shown above.
- When generating or refactoring code that changes manifest shape, update both `run_analysis.py` and `api.enrich_manifest` in `backend/api.py`.
