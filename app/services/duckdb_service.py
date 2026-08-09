import duckdb
import datetime

DB_PATH = "data/diagnostics.duckdb"


def init_db():

    print("🚀 init_db() started")

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

    print("✅ events table created (or already exists)")


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
    """
    Insert parsed log into DuckDB
    """
    with duckdb.connect(DB_PATH) as conn:
        conn.execute(
            """
            INSERT INTO events 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
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


def fetch_all_events():
    """
    Utility function for debugging / testing
    """
    with duckdb.connect(DB_PATH) as conn:
        return conn.execute("SELECT * FROM events").fetchall()