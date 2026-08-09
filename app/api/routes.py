from fastapi import APIRouter, Body, UploadFile, File
import os

from app.models.schema import AnalyzeRequest
from app.services.log_collector import collect_logs
from app.services.correlation_engine import analyze_logs
from app.services.duckdb_service import insert_event
from app.services.llm_service import generate_rca
from app.services.clustering import cluster_failures
from app.services.anomaly import detect_anomalies
from app.services.query_service import handle_query

router = APIRouter()

UPLOAD_DIR = "data/logs"


# =========================
# HEALTH CHECK
# =========================
@router.get("/")
def health():
    return {"status": "running"}


# =========================
# ANALYZE PAGE
# =========================
@router.post("/analyze")
def analyze(request: AnalyzeRequest = Body(...)):
    url = request.url

    parsed_logs = collect_logs(url)

    if not parsed_logs:
        return {"message": "No logs found"}

    raw_lines = [log["raw"] for log in parsed_logs]
    result = analyze_logs(raw_lines)

    for log in parsed_logs:
        insert_event(
            url=log["url"],
            diagnosis=result,
            user_id=log["user"],
            status=log["status"],
            raw_log=log["raw"],
            is_noidahealth=log["is_noidahealth"],
            log_level=log["log_level"],
            is_publish=log["is_publish"]
        )

    return {
        "url": url,
        "diagnosis": result,
        "log_count": len(parsed_logs)
    }

# =========================
# CLUSTERING
# =========================
@router.get("/clusters")
def get_clusters():
    return cluster_failures()


# =========================
# ANOMALY DETECTION
# =========================
@router.get("/anomalies")
def anomalies():
    return detect_anomalies()


# =========================
# RCA (AI DIAGNOSIS)
# =========================
@router.post("/rca")
def rca(request: AnalyzeRequest = Body(...)):
    url = request.url

    parsed_logs = collect_logs(url)

    if not parsed_logs:
        return {"message": "No logs found"}

    raw_lines = [log["raw"] for log in parsed_logs]
    result = analyze_logs(raw_lines)

    clusters = cluster_failures()
    anomalies = detect_anomalies()

    rca_result = generate_rca(result, clusters, anomalies)

    return {
        "url": url,
        "rca": rca_result
    }


# =========================
# UPLOAD LOG FILE
# =========================
@router.post("/upload-logs")
async def upload_logs(file: UploadFile = File(...)):
    os.makedirs(UPLOAD_DIR, exist_ok=True)

    file_path = os.path.join(UPLOAD_DIR, file.filename)

    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)

    return {"message": f"{file.filename} uploaded successfully"}


# =========================
# INVESTIGATOR QUERY (LLM → SQL)
# =========================
@router.post("/ask")
def ask_question(request: dict = Body(...)):
    question = request.get("question", "")
    return handle_query(question)