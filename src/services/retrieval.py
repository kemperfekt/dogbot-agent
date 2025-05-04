from weaviate import WeaviateClient
from typing import List, Dict
import os

from src.services.weaviate_client import get_weaviate_client

INSTINKT_KLASSEN = [
    "Jagdinstinkt",
    "Territorialinstinkt",
    "Rudelinstinkt",
    "Sexualinstinkt",
]

def weaviate_query(query: str, limit: int = 1) -> str:
    client = get_weaviate_client()
    try:
        collection = client.collections.get("Symptom")
        result = collection.query.near_text(
            query=query,
            limit=limit,
            return_metadata=["distance"],
        )
        if result.objects:
            return result.objects[0].properties.get("instinkt_varianten", "")
        return ""
    finally:
        client.close()

def get_instinktwissen(symptom: str) -> List[Dict[str, str]]:
    client = get_weaviate_client()
    try:
        collection = client.collections.get("Symptom")
        result = collection.query.near_text(
            query=symptom,
            limit=1,
            return_metadata=["distance"]
        )
        if result.objects:
            variants = result.objects[0].properties.get("instinkt_varianten", {})
            return [
                {"instinkt": key, "beschreibung": variants[key]}
                for key in ["jagd", "rudel", "territorial", "sexual"]
                if key in variants
            ]
        return []
    finally:
        client.close()

def get_erste_hilfe(instinkt: str, symptom: str) -> str:
    client = get_weaviate_client()
    try:
        collection = client.collections.get("ErsteHilfe")
        result = collection.query.near_text(
            query=f"{instinkt} {symptom}",
            limit=1,
        )
        if result.objects:
            eintrag = result.objects[0].properties.get("text", "")
            return eintrag.strip()
        return "(keine Maßnahme gefunden)"
    except Exception as e:
        print(f"⚠️ Fehler bei Erste-Hilfe-Abfrage: {e}")
        return "(Fehler bei Abfrage)"
    finally:
        client.close()