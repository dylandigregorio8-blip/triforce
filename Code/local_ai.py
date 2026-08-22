import os
import requests

def local_ai(document1: str) -> list[str]:
    STONEY_KEY = os.getenv("STONEY_KEY")
    MODEL = 'apertus-ai/Apertus-v1.5-8B'
    PROMPT = "Please write any information from the text in the format of a json list of info values, drop keys and give out only values" #[\"Jane\", \"Doe\"]."
    MAX_TOKENS = 200

    url = 'https://llm.stoney-cloud.com/v1/chat/completions'
    headers = {
        "Authorization": f"Bearer {STONEY_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": MODEL,
        "messages": [{"role": "system", "content": PROMPT}, {"role": "user","content": "Here is the text: " + document1}],
        "max_tokens": MAX_TOKENS,

    }

    response = requests.request("POST", url, headers=headers, json=payload)
    response.raise_for_status()
    return response.json()
