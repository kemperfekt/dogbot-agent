from connect_weaviate import get_weaviate_client
from weaviate.classes.query import Filter

def get_symptom_info(symptom_name: str) -> dict:
    client = get_weaviate_client()
    col = client.collections.get("Symptom")
    result = col.query.fetch_objects(
        filters=Filter.by_property("symptom_name").equal(symptom_name),
        limit=1
    )
    client.close()

    if result.objects:
        return result.objects[0].properties
    return {"fehler": f"Kein Symptom mit dem Namen '{symptom_name}' gefunden."}
