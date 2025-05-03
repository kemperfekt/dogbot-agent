from pydantic import BaseModel, field_validator
from typing import Literal

Status = Literal["enthalten", "nicht enthalten"]

class ContextInfo(BaseModel):
    Ort: Status
    Beteiligte: Status
    Zeit_davor: Status
    Zeit_danach: Status
    Ressourcen: Status

    @field_validator("*", mode="before")
    @classmethod
    def normalize_status(cls, v: str) -> str:
        """
        Normalisiert GPT-Antworten auf gültige Statuswerte.
        Erlaubt z. B. 'ja', 'nicht genannt' oder Varianten von 'enthalten'.
        """
        v = str(v).strip().lower()
        if "enthalten" in v or "ja" in v or "genannt" in v:
            return "enthalten"
        return "nicht enthalten"