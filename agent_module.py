import json
import os
from openai import OpenAI
from symptom_models import SymptomInfo, RueckfrageAntwort
from weaviate_ops.symptom_tools import get_symptom_info

api_key = os.getenv("OPENAI_APIKEY")
if not api_key:
    raise EnvironmentError("OPENAI_APIKEY ist nicht gesetzt.")

client = OpenAI(api_key=api_key)

def run_diagnose_agent(symptom_input: str) -> str:
    system_prompt = (
        "Du bist ein Diagnose-Agent. Deine Aufgabe ist es, aus den Informationen, die du über das Tool get_symptom_info erhältst, "
        "gezielte Ja-/Nein-Rückfragen zu formulieren. Nutze dafür die Instinktvarianten, die dort als Textbeschreibungen vorkommen. "
        "Formuliere pro Instinkt maximal eine Rückfrage, neutral und direkt an den Menschen gestellt."
    )

    # Tool-Call vorbereiten
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Symptom: {symptom_input}"}
        ],
        tools=[
            {
                "type": "function",
                "function": {
                    "name": "get_symptom_info",
                    "description": "Liefert strukturierte Informationen zu einem Symptom inkl. Instinktvarianten.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "symptom_name": {"type": "string"}
                        },
                        "required": ["symptom_name"]
                    }
                }
            }
        ],
        tool_choice="auto"
    )

    message = response.choices[0].message
    if not message.tool_calls:
        return message.content or "Fehler beim Tool-Call."

    # Tool aufrufen
    args = json.loads(message.tool_calls[0].function.arguments)
    symptom_name = args.get("symptom_name")
    tool_response_dict = get_symptom_info(symptom_name)
    tool_response = SymptomInfo.from_dict(tool_response_dict)

    # Rückfragen formulieren
    follow_up = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Symptom: {symptom_input}"},
            message,
            {
                "role": "tool",
                "tool_call_id": message.tool_calls[0].id,
                "name": message.tool_calls[0].function.name,
                "content": json.dumps(tool_response_dict, ensure_ascii=False)
            },
            {
                "role": "assistant",
                "content": (
                    "Dies sind die Instinktvarianten, aus denen du Rückfragen formulieren sollst:\n"
                    + json.dumps(tool_response.instinktvarianten.model_dump(), ensure_ascii=False)
                )
            }
        ]
    )

    rückfragen = [f for f in follow_up.choices[0].message.content.split("\n") if f.strip()]

    diagnose_prompt = (
        "Du bist ein Diagnose-Agent. Deine Aufgabe ist es, auf Grundlage der folgenden Antworten den wahrscheinlich führenden Instinkt (oder mehrere bei Gleichstand) zu bestimmen. "
        "Erlaube dir keine eigenen Interpretationen über nicht gestellte Rückfragen. Nutze ausschließlich diese vier Instinkte: Jagdinstinkt, Rudelinstinkt, Territorialinstinkt, Sexualinstinkt."
    )

    antworten = [RueckfrageAntwort(frage=q, antwort="Unklar") for q in rückfragen]  # placeholder, frontend liefert später echte Antworten

    diagnose_response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": diagnose_prompt},
            {"role": "user", "content": f"Antworten: {[a.model_dump() for a in antworten]}"}
        ]
    )

    return diagnose_response.choices[0].message.content
