Repository: Approach-Landing-Analyzer — Copilot helper notes

Quick commands (dev)
- Backend (requires Python 3.13+ and `uv`):
  - Install deps & venv:  cd backend && uv sync
  - Run API (dev hot reload):  cd backend && uv run uvicorn api:app --reload
  - Run pipeline (standalone):  cd backend && uv run run_analysis.py
  - Run pipeline for a single CSV (from repo root) using Python API:
    uv run python -c "from backend.run_analysis import main; main(r'ABSOLUTE\\PATH\\TO\\file.csv')"
  - Jupyter (notebook): cd backend && uv run jupyter lab

- Frontend (Node + npm)
  - Install: cd frontend && npm install
  - Dev server: cd frontend && npm run dev
  - Build: cd frontend && npm run build
  - Preview build: cd frontend && npm run preview

Lint & format
- Frontend lint: cd frontend && npm run lint
  - Run only eslint: npm run lint:eslint
  - Run only oxlint: npm run lint:oxlint
- Format: cd frontend && npm run format

Tests
- There is no top-level automated test suite in this repository. Use the notebook or run the pipeline with sample CSVs under data/raw/ for validation.

High-level architecture (big picture)
- Frontend: Vue 3 + Vite app (frontend/) — UI to upload telemetry and display results.
  - Communicates with backend endpoints: POST /analyze (file upload) and GET /latest.
  - Expects backend served on localhost:8000 and frontend on port 5173 (CORS allowed in api.py).
- Backend: FastAPI app (backend/) exposing the API and a static mount at /results (api.py).
  - Main orchestrator: backend/run_analysis.py
  - Pipeline modules live under backend/src/:
    - src.data_loaders: read_telemetry_csv, runway DB loader
    - src.parsers: helpers for filename/metadata
    - src.transformer_plotter: transform_telemetry, touchdown_discovery, plotting, HTML/CSS result generation
  - Config: backend/config.toml controls CSV_PATH, REF_PATH, RESULTS_DIR. run_analysis resolves these paths relative to repo root.
  - Output: Results written into RESULTS_DIR with folders named "[YYYYMMDD] MissionName". A per-run manifest.json and a global latest_manifest.json are written for UI consumption.

Important conventions & patterns (repository-specific)
- Path/config conventions
  - Edit backend/config.toml for I/O paths. Values may be relative — run_analysis resolves them against the project root.
- Results manifest
  - Manifest keys used by the UI: folder_name, evaluation_table_html, evaluation_table_image, landing_charts (each chart: filename, title, pilot, sortie).
  - latest_manifest.json is used by the frontend GET /latest endpoint for quick previews.
- Filenames & safe names
  - Charts follow: {DATE}_{safe_pilot}_landing_{sortie}.png. Use src.parsers.replace_angles() to sanitize pilot strings when building filenames.
- Analysis flow
  - CSV -> read_telemetry_csv -> transform_telemetry -> touchdown_discovery -> style_result_table + plot_landing_profile + touchdown_plotter -> manifest
- Development tooling
  - Backend expects Python 3.13+. The project uses `uv` (Astral) to manage venv and running commands; prefer `uv sync` and `uv run` as shown in README.
  - Frontend uses Node (see package.json engines) and relies on oxlint + eslint + prettier for linting/format.

Where to look quickly
- Entrypoints: backend/api.py (API routes), backend/run_analysis.py (analysis pipeline)
- Config: backend/config.toml
- Data: data/raw/ (input examples), data/results/ (output artifacts and manifests)
- Frontend UI: frontend/src and frontend/package.json (scripts)

Notes for Copilot sessions
- Prefer editing backend/config.toml when changing paths/behavior.
- For reproducing results quickly, run backend API and POST a CSV to /analyze from frontend or use the Python invocation shown above.
- When generating or refactoring code that changes manifest shape, update both run_analysis.py and api.enrich_manifest in backend/api.py.

MCP servers
- This is a web + API project. If useful, Playwright (browser automation/testing) could be configured as an MCP server for end-to-end UI testing. Ask if you want a Playwright server added to the project helpers.

If you want this file adjusted (more details on modules, sample cURL commands, or Playwright config), say which area to expand.
