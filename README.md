# Log Analyzer

A Sitecore log investigator: it collects and parses Sitecore/CDN log files, stores parsed
events in DuckDB, and surfaces diagnostics (soft/hard 404s, publish activity, anomalies,
failure clusters) through a FastAPI backend and a Streamlit dashboard. An optional local
LLM (via [Ollama](https://ollama.com)) powers root-cause-analysis and natural-language
querying of the log data.

## Architecture

```
app/
  main.py                 FastAPI app entrypoint
  api/routes.py            API routes
  models/schema.py         Pydantic request models
  services/
    log_collector.py       Reads & filters raw log files from data/logs
    parser.py               Parses individual log lines
    correlation_engine.py   Soft/hard 404 diagnosis heuristics
    duckdb_service.py       DuckDB schema + inserts
    clustering.py           TF-IDF + KMeans clustering of past diagnoses
    anomaly.py              Simple statistical anomaly detection on event volume
    llm_service.py          Builds RCA prompt, calls the LLM
    ollama_client.py        HTTP client for a local Ollama server
    query_service.py        Natural-language -> SQL (via LLM) over the events table
dashboard.py               Streamlit UI (upload logs, analyze, charts, ask questions)
data/                      Uploaded logs + DuckDB database (gitignored, created at runtime)
```

## Prerequisites

- Python 3.11+
- [Ollama](https://ollama.com) running locally, with a model pulled (the code defaults to
  `llama3`) — only required for the RCA and "Ask Questions" features; everything else
  (upload, analyze, charts) works without it.

## Setup

```powershell
python -m venv venv
venv\Scripts\python.exe -m pip install -r requirements.txt
```

## Running

Start the backend and dashboard in separate terminals:

```powershell
# Backend API (port 8800)
venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8800 --reload

# Dashboard (port 8801)
venv\Scripts\python.exe -m streamlit run dashboard.py --server.port 8801
```

Then open http://localhost:8801 in a browser.

If you want RCA / AI-investigator features, make sure Ollama is running and has the model
pulled:

```powershell
ollama pull llama3
```

## API

| Method | Route          | Description                                    |
|--------|----------------|-------------------------------------------------|
| GET    | `/`            | Health check                                    |
| POST   | `/upload-logs` | Upload a raw log file into `data/logs`          |
| POST   | `/analyze`     | Filter logs by URL/keyword and diagnose issues  |
| GET    | `/clusters`    | Cluster past diagnoses (TF-IDF + KMeans)        |
| GET    | `/anomalies`   | Detect volume anomalies over time               |
| POST   | `/rca`         | LLM-generated root cause analysis               |
| POST   | `/ask`         | Natural-language question -> SQL over the events table |

## Notes

- `data/` (uploaded logs and the DuckDB database) is gitignored since it can contain
  real client log data.
