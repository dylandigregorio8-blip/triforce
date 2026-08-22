import os
from typing import List, Tuple
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from regex_detector import regex_detector
from replace import replace, restore
from local_ai import local_ai

load_dotenv()

app = FastAPI(title="Airlock middleware")

class PromptRequest(BaseModel):
    prompt: str  # String with action, expected to be done
    context: str # String with additional information. 

def call_gemini(prompt: str, context: str) -> str:
    """Send prompt and redacted context to Gemini LLM."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise HTTPException(
            status_code=500,
            detail="GEMINI_API_KEY environment variable is not set."
        )

    model_name = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")
    full_prompt = f"Context:\n{context}\n\nTask:\n{prompt}"

    try:
        from google import genai
        from google.genai import types

        client = genai.Client(api_key=api_key)

        config = types.GenerateContentConfig(
            temperature=1.0,
            max_output_tokens=400,
            top_p=0.95,
        )

        response = client.models.generate_content(
            model=model_name,
            contents=full_prompt,
            config=config,
        )
        return response.text or ""
    except ImportError:
        raise HTTPException(
            status_code=500,
            detail="'google-genai' package is not installed."
        )
    except Exception as e:
        raise HTTPException(
            status_code=502,
            detail=f"Error communicating with Gemini: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=502,
            detail=f"Error communicating with Gemini: {str(e)}"
        )


@app.post("/process_v1")
async def process_prompt(data: PromptRequest):
    document = data.context

    regex_identifiers = regex_detector(document)

    ai_identifiers = local_ai(document)

    safe_regex = [str(x) for x in regex_identifiers if x is not None]
    safe_ai = [str(x) for x in ai_identifiers if x is not None]

    combined_identifiers = sorted(
        set(safe_regex + safe_ai), 
        key=len, 
        reverse=True
    )

    replacement_result, replacements_mapping = replace(combined_identifiers, document)

    # Call Gemini with prompt and redacted context
    llm_response = call_gemini(prompt=data.prompt, context=replacement_result)

    # Reverse replacement: restore original values from tags
    restored_response = restore(replacements_mapping, llm_response)

    print("--- Processing Debug ---")
    print(f"Found Identifiers: {combined_identifiers}")
    print(f"Replacement Result (Redacted Context): {replacement_result}")
    print(f"Replacements Mapping: {replacements_mapping}")
    print(f"Gemini Raw Response: {llm_response}")
    print(f"Restored Response: {restored_response}")
    print("------------------------")

    return {
        "status": "ok", 
        "result": restored_response,
    }