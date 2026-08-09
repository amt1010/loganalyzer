import duckdb

def detect_anomalies():
    conn = duckdb.connect("data/diagnostics.duckdb")

    df = conn.execute("""
        SELECT 
            date_trunc('minute', timestamp) AS minute,
            COUNT(*) AS count
        FROM events
        GROUP BY minute
        ORDER BY minute
    """).df()

    if len(df) < 5:
        return {"message": "Not enough data for anomaly detection"}

    mean = df["count"].mean()
    std = df["count"].std()

    threshold = mean + 2 * std

    anomalies = df[df["count"] > threshold]

    return {
        "threshold": threshold,
        "data": df.to_dict(orient="records"),
        "anomalies": anomalies.to_dict(orient="records")
    }