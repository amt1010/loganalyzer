import duckdb
import datetime
import time

DB_PATH = "data/diagnostics.duckdb"


def init_db(retries=5, delay=1):
    for attempt in range(retries):
        try:
            with duckdb.connect(DB_PATH) as conn:
                conn.execute("""
                CREATE TABLE IF NOT EXISTS events (
                    timestamp TIMESTAMP,
                    url TEXT,
                    user_id TEXT,
                    diagnosis TEXT,
                    status INTEGER,
                    raw_log TEXT,
                    is_noidahealth BOOLEAN,
                    log_level TEXT,
                    is_publish BOOLEAN
                )
                """)
            print("✅ Database initialized successfully")
            return
        except Exception as e:
            print(f"⚠️ DB init failed (attempt {attempt+1}): {e}")
            time.sleep(delay)


def insert_event(
    url,
    diagnosis,
    user_id="unknown",
    status=None,
    raw_log="",
    is_noidahealth=False,
    log_level="UNKNOWN",
    is_publish=False
):
    with duckdb.connect(DB_PATH) as conn:
        conn.execute(
            """
            INSERT INTO events VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                datetime.datetime.now(),
                url,
                user_id,
                diagnosis,
                status,
                raw_log,
                is_noidahealth,
                log_level,
                is_publish
            )
        )