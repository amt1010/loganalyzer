import duckdb
from app.services.ollama_client import ask_llm

DB_PATH = "data/diagnostics.duckdb"


def handle_query(question: str):
    """
    Converts natural language question into SQL,
    executes safely on DuckDB, and returns results.
    """

    # 🔹 Define schema for LLM
    schema = """
    Table: events
    Columns:
    - timestamp (TIMESTAMP)
    - url (TEXT)
    - user_id (TEXT)
    - diagnosis (TEXT)
    """

    # 🔹 Prompt for LLM
    prompt = f"""
    You are a Sitecore log analyst using DuckDB.

    Convert the user question into a SQL query.

    ====================
    DATABASE SCHEMA
    ====================
    Table: events

    Columns:
    - timestamp (TIMESTAMP)
    - url (TEXT)
    - user_id (TEXT) → contains email like sumit.bhatia@noidahealth.org
    - diagnosis (TEXT)
    - status (INTEGER) → HTTP status (200, 404, etc.)
    - raw_log (TEXT)
    - is_noidahealth (BOOLEAN)
    - log_level (TEXT) → INFO, ERROR, WARN
    - is_publish (BOOLEAN) → TRUE = publish event (AUDIT log)

    ====================
    IMPORTANT RULES
    ====================
    - ONLY generate SELECT queries
    - DO NOT use DELETE / UPDATE / DROP
    - Always use correct column names
    - When user asks about "published pages":
        → use is_publish = TRUE
    - When user asks about users:
        → extract email using regexp_extract()

    Use this pattern for user extraction:
    regexp_extract(user_id, '([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+)', 1)

    - When counting updates:
        → use COUNT(*)
    - When grouping:
        → GROUP BY user and/or url

    ====================
    EXAMPLES
    ====================

    Q: How many pages were published by sumit?
    SQL:
    SELECT COUNT(*) 
    FROM events
    WHERE is_publish = TRUE 
    AND user_id LIKE '%sumit%';


    Q: Show users and pages they updated
    SQL:
    SELECT 
        regexp_extract(user_id, '([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+)', 1) AS user,
        url,
        COUNT(*) AS updates
    FROM events
    WHERE is_publish = TRUE
    GROUP BY user, url
    ORDER BY updates DESC;


    Q: Top publishers
    SQL:
    SELECT 
        regexp_extract(user_id, '([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+)', 1) AS user,
        COUNT(*) AS total_updates
    FROM events
    WHERE is_publish = TRUE
    GROUP BY user
    ORDER BY total_updates DESC;


    ====================
    QUESTION
    ====================
    {question}

    Return ONLY SQL.
    """

    # 🔹 Call LLM
    sql = ask_llm(prompt).strip()

    print("\n🧠 User Question:", question)
    print("⚙️ Generated SQL:", sql)

    # 🔒 SAFETY CHECKS
    sql_upper = sql.upper()

    # Allow only SELECT queries
    if not sql_upper.startswith("SELECT"):
        return {
            "error": "Only SELECT queries are allowed",
            "generated_sql": sql
        }

    # Block dangerous operations
    blocked_keywords = ["DROP", "DELETE", "UPDATE", "INSERT", "ALTER", "TRUNCATE"]
    if any(keyword in sql_upper for keyword in blocked_keywords):
        return {
            "error": "Unsafe query blocked",
            "generated_sql": sql
        }

    # 🔹 Execute SQL safely
    try:
        with duckdb.connect(DB_PATH) as conn:
            df = conn.execute(sql).df()

        return {
            "question": question,
            "sql": sql,
            "result": df.to_dict(orient="records")
        }

    except Exception as e:
        return {
            "error": str(e),
            "generated_sql": sql
        }