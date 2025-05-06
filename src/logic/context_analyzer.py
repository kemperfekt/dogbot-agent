from openai import OpenAI
import json
from src.models.context_models import ContextInfo


class ContextAnalyzer:
    """
    Nutzt GPT, um zu prüfen, ob folgende Kontextelemente in einer Nutzernachricht enthalten sind:
    - Ort
    - Beteiligte
    - Zeit davor
    - Zeit danach
    - Ressourcen (z.B. Ball, Leckerli)

    Gibt ein ContextInfo-Objekt zurück mit "enthalten" / "nicht enthalten".
    """

    SYSTEM_PROMPT = """
    Du hilfst dabei, die Situation eines Hundeverhaltens besser zu verstehen.
    Analysiere die folgende Nachricht und bewerte, ob die folgenden Aspekte bereits erwähnt oder erkennbar sind:

    - Ort (z.B. Straße, Wohnung, Wald)
    - Beteiligte (andere Menschen oder Tiere)
    - Zeit_davor (was kurz vorher passiert ist)
    - Zeit_danach (was danach passiert ist)
    - Ressourcen (Spielzeug, Futter, Objekt, Leckerli etc.)

    Gib deine Antwort **ausschließlich** im folgenden JSON-Format zurück:
    {
      "Ort": "...",
      "Beteiligte": "...",
      "Zeit_davor": "...",
      "Zeit_danach": "...",
      "Ressourcen": "..."
    }

    Verwende **nur** die Werte "enthalten" oder "nicht enthalten".
    """

    def __init__(self, client: OpenAI):
        self.client = client

    def analyze(self, user_message: str) -> ContextInfo:
        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": self.SYSTEM_PROMPT},
                {"role": "user", "content": user_message}
            ],
            temperature=0
        )
        try:
            raw = json.loads(response.choices[0].message.content)
            return ContextInfo.model_validate(raw)
        except Exception:
            return ContextInfo.model_construct(
                Ort="nicht enthalten",
                Beteiligte="nicht enthalten",
                Zeit_davor="nicht enthalten",
                Zeit_danach="nicht enthalten",
                Ressourcen="nicht enthalten"
            )

def extract_breed_from_history(history: list) -> str | None:
    """
    Extrahiert die vermutete Rasse aus dem bisherigen Gesprächsverlauf.
    Sucht die erste Erwähnung von 'Rasse:' in einer Bot-Antwort.
    """
    for message in reversed(history):
        if isinstance(message, dict):
            text = message.get("text", "")
        else:
            text = getattr(message, "text", "")
        if "Rasse:" in text:
            parts = text.split("Rasse:")
            if len(parts) > 1:
                return parts[1].split("\n")[0].strip()
    return None

def analyze_context(user_message: str, client: OpenAI) -> ContextInfo:
    analyzer = ContextAnalyzer(client)
    return analyzer.analyze(user_message)
