import json
import os
from typing import List, Tuple
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from regex_detector import regex_detector

load_dotenv()

app = FastAPI(title="Airlock middleware")

class PromptRequest(BaseModel):
    prompt: str  # String with action, expected to be done
    context: str # String with additional information. Should come in format '{"key": "value"}'

# --- Stub Functions ---

def local_ai(document: str) -> List[str]:
    # TODO: Implement local AI extraction
    return ["Swisscom AG", "Dr. Ursula Meier", "Coop Supermarkt Bern"]

def replace(identifiers: List[str], document: str) -> Tuple[str, List[Tuple[str, str]]]:
    # TODO: Replace items in document and return (replacement_result, list_of_replacements)
    # Return type structure: (String, List[(Original_String, Replacement_Tag)])
    return document, []


@app.post("/process_v1")
async def process_prompt(data: PromptRequest):
    try:
        # Validate that context is a valid JSON string
        parsed_context = json.loads(data.context)
    except json.JSONDecodeError as e:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid JSON string inside 'context': {str(e)}"
        )

    document = data.context

    regex_identifiers = regex_detector(document)

    ai_identifiers = local_ai(document)

    combined_identifiers = combined_identifiers = sorted(
        set(regex_identifiers + ai_identifiers), 
        key=len, 
        reverse=True
    )

    replacement_result, replacements_mapping = replace(combined_identifiers, document)

    # TODO: everything else

    print("--- Processing Debug ---")
    print(f"Regex Identifiers: {regex_identifiers}")
    print(f"Combined Identifiers: {combined_identifiers}")
    print(f"Replacement Result: {replacement_result}")
    print(f"Replacements Mapping: {replacements_mapping}")
    print("------------------------")

    return {
        "status": "ok", 
        "result": "processed",
        "replacement_result": replacement_result,
        "replacements": replacements_mapping
    }