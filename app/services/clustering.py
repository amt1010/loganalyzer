import duckdb
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans

def cluster_failures():
    conn = duckdb.connect("data/diagnostics.duckdb")

    df = conn.execute("""
        SELECT diagnosis FROM events
    """).df()

    if len(df) < 3:
        return {"message": "Not enough data for clustering"}

    vectorizer = TfidfVectorizer()
    X = vectorizer.fit_transform(df["diagnosis"])

    kmeans = KMeans(n_clusters=2, random_state=42)
    df["cluster"] = kmeans.fit_predict(X)

    return df.to_dict(orient="records")