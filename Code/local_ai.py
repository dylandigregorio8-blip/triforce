import os
import requests

def local_ai(document1: str) -> list[str]:
    STONEY_KEY = os.getenv("STONEY_KEY")
    MODEL = 'apertus-ai/Apertus-v1.5-8B'
    PROMPT = "hello"
    MAX_TOKENS = 100

    url = 'https://llm.stoney-cloud.com/v1/chat/completions'
    headers = {
        "Authorization": f"Bearer {STONEY_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": MODEL,
        "message": [{"role": "user", "content": PROMPT + ": " + document1}],
        "max_tokens": MAX_TOKENS,

    }

    response = requests.request("POST", url, headers=headers, json=payload)
    response.raise_for_status()
    return response.json()["completions"]
