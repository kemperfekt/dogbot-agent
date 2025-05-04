# --- src/services/retrieval.py ---

from weaviate.classes.query import MetadataQuery, Filter
from src.services.weaviate_client import get_weaviate_client


def weaviate_query(query: dict) -> list[dict]:
    client = get_weaviate_client()
    class_name = query["class"]
    properties = query["properties"]
    limit = query.get("limit", 1)

    collection = client.collections.get(class_name)

    if "filter" in query:
        f = query["filter"]
        filter_expr = Filter.by_property(f["path"][0]).equal(f["valueText"])
        response = collection.query.fetch_objects(
            filters=filter_expr,
            limit=limit
        )
    elif "nearText" in query:
        response = collection.query.near_text(
            query=query["nearText"]["concepts"][0],
            limit=limit,
            return_metadata=MetadataQuery(distance=True)
        )
    else:
        response = collection.query.fetch_objects(limit=limit)

    return [obj.properties for obj in response.objects]


def get_schnelldiagnose(symptom: str) -> str:
    query = {
        "class": "Symptom",
        "properties": ["beschreibung"],
        "nearText": {
            "concepts": [symptom],
            "certainty": 0.7
        },
        "limit": 1
    }
    result = weaviate_query(query)
    if result and "beschreibung" in result[0]:
        return result[0]["beschreibung"]
    return "(keine passende Beschreibung gefunden)"


def get_instinktwissen(symptom: str) -> list[dict]:
    query = {
        "class": "Instinktvariante",
        "properties": ["instinkt", "beschreibung"],
        "nearText": {
            "concepts": [symptom],
            "certainty": 0.7
        },
        "limit": 4
    }
    return weaviate_query(query)


def get_erste_hilfe(instinkt: str, symptom: str) -> str:
    query = {
        "class": "ErsteHilfe",
        "properties": ["text"],
        "nearText": {
            "concepts": [instinkt, symptom],
            "certainty": 0.65
        },
        "limit": 1
    }
    result = weaviate_query(query)
    if result and "text" in result[0]:
        return result[0]["text"]
    return "(keine Erste-Hilfe-Maßnahme gefunden)"