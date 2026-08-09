import requests

def ask_llm(prompt: str):
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "llama3",  # you can change later
                "prompt": prompt,
                "stream": False
            },
            timeout=120
        )

        return response.json().get("response", "No response from LLM")

    except Exception as e:
        return f"LLM error: {str(e)}"