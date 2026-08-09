from app.services.ollama_client import ask_llm

def generate_rca(current_issue, clusters, anomalies):
    prompt = f"""
Analyze Sitecore issue:

Current Issue:
{current_issue}

Historical Patterns:
{clusters}

Anomalies:
{anomalies}

Answer:
1. Root cause
2. Issue type (Soft 404 / Hard 404 / CDN / Publish)
3. Confidence %
4. Fix steps
5. Preventive actions
"""

    return ask_llm(prompt)