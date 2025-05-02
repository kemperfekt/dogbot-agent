# services/instinct_classifier.py

from openai import OpenAI
from pydantic import BaseModel
from typing import List, Literal

from src.prompts.prompt_hundliche_wahrnehmung import hundliche_wahrnehmung
from src.prompts.system_prompt_diagnose import diagnose_instinktklassifikation


# Antwortmodell für GPT Function Calling
class InstinctClassification(BaseModel):
    jagd: int  # 0–100
    rudel: int
    territorial: int
    sexual: int
    kommentar: str

# GPT Function Definition
INSTINCT_FUNCTION_DEF = {
    "name": "classify_instincts",
    "description": "Schätzt das Instinktprofil des Hundes basierend auf der Beschreibung.",
    "parameters": InstinctClassification.schema(),
}

def classify_instincts(text: str, client: OpenAI) -> InstinctClassification:
    system_prompt = hundliche_wahrnehmung + "\n\n" + diagnose_instinktklassifikation

    response = client.chat.completions.create(
        model="gpt-4",
        temperature=0,
        tools=[{"type": "function", "function": INSTINCT_FUNCTION_DEF}],
        tool_choice={"type": "function", "function": {"name": "classify_instincts"}},
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": text},
        ]
    )

    tool_call = response.choices[0].message.tool_calls[0]
    result = InstinctClassification.model_validate_json(tool_call.function.arguments)
    return result