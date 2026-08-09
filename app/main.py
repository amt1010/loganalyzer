from fastapi import FastAPI
from app.api.routes import router
from app.services.duckdb_service import init_db

app = FastAPI()

@app.on_event("startup")
def startup():
    init_db()   # ✅ safe here

app.include_router(router)