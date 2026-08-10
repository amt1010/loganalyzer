import streamlit as st
import requests
import duckdb
import pandas as pd

st.set_page_config(layout="wide")

st.title("🧠 Sitecore Log Investigator")

# =====================
# Upload Logs
# =====================
uploaded_file = st.file_uploader("Upload Log File")

if uploaded_file:
    files = {"file": (uploaded_file.name, uploaded_file.getvalue())}
    res = requests.post("http://127.0.0.1:8800/upload-logs", files=files)
    st.success("Uploaded")

# =====================
# Analyze
# =====================
url = st.text_input("Enter URL / keyword", "noidahealth")

if st.button("Analyze"):
    res = requests.post(
        "http://127.0.0.1:8800/analyze",
        json={"url": url}
    )
    st.json(res.json())

# =====================
# DB Insights
# =====================
st.header("📊 Insights")

try:
    with duckdb.connect("data/diagnostics.duckdb") as conn:
        df = conn.execute("SELECT * FROM events").df()

    if len(df) == 0:
        st.warning("No data yet")
    else:
        # =====================
        # Log Level Chart
        # =====================
        st.subheader("📊 Log Level Distribution")
        log_chart = df["log_level"].value_counts()
        st.bar_chart(log_chart)

        # =====================
        # Status Chart
        # =====================
        st.subheader("📊 HTTP Status Distribution")
        status_chart = df["status"].value_counts()
        st.bar_chart(status_chart)

        # =====================
        # Publish Activity
        # =====================
        st.subheader("🚀 Publish Activity (AUDIT Logs)")
        publish_df = df[df["is_publish"] == True]

        if len(publish_df) > 0:
            pub = publish_df["user_id"].value_counts()
            st.bar_chart(pub)
        else:
            st.info("No publish events detected")

        # =====================
        # Noidahealth Insights
        # =====================
        st.subheader("🏥 Noidahealth Insights")

        nh = df[df["is_noidahealth"] == True]

        if len(nh) > 0:
            summary = nh.groupby("user_id").agg({
                "status": lambda x: (x == 404).sum()
            }).rename(columns={"status": "404_errors"})

            st.dataframe(summary)
        else:
            st.info("No Noidahealth logs found")

        # =====================
        # 🧠 LLM QUERY (INVESTIGATOR MODE)
        # =====================
        st.header("🧠 Ask Questions (AI Investigator)")

        question = st.text_input(
            "Ask about logs",
            "How many pages were published by sumit.bhatia@noidahealth.org?"
        )

        if st.button("Run Query"):
            res = requests.post(
                "http://127.0.0.1:8800/ask",
                json={"question": question}
            )

            result = res.json()

            if "error" in result:
                st.error(result["error"])
                st.code(result.get("generated_sql", ""), language="sql")
            else:
                st.subheader("Generated SQL")
                st.code(result["sql"], language="sql")

                st.subheader("Result")
                import pandas as pd

                st.dataframe(pd.DataFrame(result["result"]))

except Exception as e:
    st.warning("⚠️ DB not ready yet. Run /analyze first.")