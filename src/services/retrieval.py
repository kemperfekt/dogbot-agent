# --- src/services/retrieval.py ---

from weaviate.collections.classes.config import MetadataQuery
from weaviate import WeaviateClient
from typing import List, Dict
import os

INSTINKT_KLASSEN = [
    "Jagdinstinkt",
    "Territorialinstinkt",
    "Rudelinstinkt",
    "Sexualinstinkt",
]

def get_weaviate_client() -> WeaviateClient:
    from weaviate import connect_to_local
    return connect_to_local()

def weaviate_query(query: str, limit: int = 1) -> str:
    client = get_weaviate_client()
    try:
        collection = client.collections.get("Symptom")
        result = collection.query.near_text(
            query=query,
            limit=limit,
            return_metadata=MetadataQuery(distance=True),
        )
        if result.objects:
            return result.objects[0].properties.get("instinkt_varianten", "")
        return ""
    finally:
        client.close()

def get_instinktwissen(symptom: str) -> List[Dict[str, str]]:
    client = get_weaviate_client()
    beschreibungen = []

    try:
        for klasse in INSTINKT_KLASSEN:
            try:
                collection = client.collections.get(klasse)
                result = collection.query.near_text(
                    query=symptom,
                    limit=1,
                    return_metadata=MetadataQuery(distance=True),
                )
                if result.objects:
                    obj = result.objects[0]
                    beschreibung = obj.properties["beschreibung"] if obj.properties and "beschreibung" in obj.properties else ""
                    beschreibungen.append({
                        "instinkt": klasse.replace("instinkt", "").lower(),
                        "beschreibung": beschreibung.strip()
                    })
            except Exception as e:
                print(f"⚠️ Fehler bei Abfrage von {klasse}: {e}")
    finally:
        client.close()

    return beschreibungen