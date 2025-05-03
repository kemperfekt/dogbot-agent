from pydantic import BaseModel, field_validator
from typing import List, Dict, Any, Optional

# Diagnosemodell
class Diagnose(BaseModel):
    instinkt: str
    kommentar: str


# Modell für eine Instinktvariante eines Symptoms
class Instinktvariante(BaseModel):
    instinkt: str
    beschreibung: str


# Modell für allgemeine Informationen zu einem Symptom
class SymptomInfo(BaseModel):
    symptom_name: str
    beschreibung: Optional[str] = None
    erste_hilfe: Optional[str] = None
    hypothese_zuhause: Optional[str] = None
    instinktvarianten: List[Instinktvariante]

    class Config:
        populate_by_name = True

    @field_validator("instinktvarianten", mode="before")
    @classmethod
    def normalize_variants(cls, v: Any) -> Any:
        if not v:
            return []
        if isinstance(v, dict):
            return [{"instinkt": name, "beschreibung": desc} for name, desc in v.items()]
        if isinstance(v, list) and v and isinstance(v[0], str):
            return [{"instinkt": "", "beschreibung": item} for item in v]
        return v