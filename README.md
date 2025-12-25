# Self-Healing LLM Security Pipeline

This repository implements a minimal LLM gateway with two targets:
* **Target A (baseline):** `/generate`
* **Target B (patched):** `/generate_patched` (patching comes later)

Week 1 delivers the service skeleton + Docker + config loading.
Week 2 integrates **Garak** and produces **raw logs + normalized summaries** per run.

## Repository Structure

src/
  main.py
  api/
    generate.py
  core/
    llm.py
  models/
    schemas.py
configs/
  config.yaml
  garak_rest_config.json
scripts/
  run_baseline.py
  normalize_garak.py
results/
  <run_id>/
    raw/
      garak.report.jsonl
    summary.json
    summary.csv
tests/ 

# Week 1 — Service skeleton + Docker + config
## 1 Setup (Local) 
### Run API locally
If `uvicorn` is not recognized, use:
python -m uvicorn src.main:app --reload
API docs:
* [http://127.0.0.1:8000/docs]
## API Endpoints
### Target A (baseline)
`POST /generate`

Request:
{"prompt":"hello"}

Response:
{"response":"...","target":"A"}

### Target B (patched gateway)
`POST /generate_patched`

Response: 
{"response":"...","target":"B"}

## Docker Build
powershell
docker build -t self-healing-llm .

### Docker Run
powershell
docker run -p 8000:8000 self-healing-llm

Open:
http://localhost:8000/docs
If you see the docs page, Docker + FastAPI is correct.

## Quick “hello” request (PowerShell recommended)
Invoke-RestMethod -Uri http://localhost:8000/generate -Method POST -ContentType "application/json" -Body '{"prompt":"hello"}'
### curl (Windows)
Use `curl.exe` (not the PowerShell alias):
curl.exe -X POST http://localhost:8000/generate -H "Content-Type: application/json" -d "{\"prompt\":\"hello\"}"

### LLM Backend Selection (Week 1)
As an initial test in the first week, I used a deterministic echo backend to validate the pipeline.
This will be replaced by an API-based or local model in the next step.
The stub implements the same generate(prompt) interface expected from a real LLM, but returns a predictable echo-style response.

Rationale:
- Isolates infrastructure and API correctness from model behavior
- Enables fast, deterministic debugging
- Avoids external dependencies during early development
- Ensures Dockerized reproducibility

The backend is abstracted behind an LLMClient interface, allowing transparent replacement with API-based or local open-source LLMs
in later stages without changes to the API or patching logic.

#### Week 1 Checklist

* [x] Repo structure created
* [x] FastAPI skeleton + `/generate` and `/generate_patched`
* [x] Docker builds and runs
* [x] YAML config loading
* [x] “hello” request works locally + in Docker

#### Week 2 — Garak integration + baseline scan pipeline

## Goal
One command should:

1. Run Garak against **Target A**
2. Save raw outputs under `results/<run_id>/raw/`
3. Generate a normalized summary (`CSV` or `JSON`) with:

   * `run_id, target, probe_id, outcome, category`

## First lets create garak environment
Install Garak in a dedicated env (recommended):

python -m venv garak_env .\garak_env\Scripts\Activate.ps1

pip install garak

Check:
python -m garak --version

## Important Windows + Docker note (Target URL)
When Garak runs from Windows and API is in Docker, use the correct bridge address:
* `http://host.docker.internal:8000/generate`

## Garak REST generator config
I used JSON rather than YAML after there was an issue with garak with yaml based config
The issue was raised on official github and json was recommended since it is more reliable than YAML on Windows:

## One-command baseline scan (repo script)
Run: python scripts/run_baseline.py

This should create:
results/<run_id>/raw/garak.report.jsonl
results/<run_id>/summary.json
results/<run_id>/summary.csv

## Normalized summary format
### CSV columns (required)

* `run_id`
* `target`
* `probe_id`
* `outcome` (PASS/FAIL/UNKNOWN)
* `category` (prompt_injection / jailbreak / unsafe_content / etc.)

## Known Issues / Troubleshooting

### Garak says “No REST endpoint URI definition…”
Fix: Put the endpoint in `configs/garak_rest_config.json` under `"uri"`.
     Use `--target_type rest` (not `rest.RestGenerator`).

### ReadTimeout / model hangs (Phi-3)
DAN probes can be slow/hang on CPU/offload. Start with:
* `--probes promptinject`

## Week 2 Checklist

* [x] Garak configured for REST target
* [x] One-command run script works
* [x] Raw report saved per run
* [x] Normalized summary produced (CSV/JSON) 



###  LLM backend (local model)

I selected Phi-3-mini-4k-instruct model, since it is a "mini" model, it is designed to run on my limited hardware.
This ensures my Docker container remains lightweight and performs well locally.

To check the end-to-end chekpoint I run the following bash on the garak_env on the host powershell

Invoke-RestMethod -Uri http://host.docker.internal:8000/generate -Method POST -ContentType "application/json" -Body '{"prompt":"hello"}'

Output obtained:

response               target
--------               ------
[stub-llm] Echo: hello A

# The output proven
1. FastAPI is reachable from garak_env environment
2. POST /generate works over Docker networking
3. JSON schema matches expectations
4. Target A (baseline) is callable end-to-end

This shows the FastAPI and the garak communicate perfectly

After installing garak locally, I write a script to run the garak for testing
for this week i just use promptinject attack due to resourse intensity of DAN and other tests
