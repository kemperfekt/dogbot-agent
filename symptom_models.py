from pydantic import BaseModel
from typing import Optional, List

class RueckfrageAntwort(BaseModel):
    frage: str
    antwort: str

class DiagnoseAntwort(BaseModel):
    symptom: str
    rueckfragen: List[RueckfrageAntwort]

class Instinktvarianten(BaseModel):
    jagdinstinkt: Optional[str] = None
    rudelinstinkt: Optional[str] = None
    territorialinstinkt: Optional[str] = None
    sexualinstinkt: Optional[str] = None

class SymptomInfo(BaseModel):
    symptom_name: str
    beschreibung: Optional[str] = None
    instinktvarianten: Instinktvarianten

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            symptom_name=data.get("symptom_name", ""),
            beschreibung=data.get("beschreibung"),
            instinktvarianten=Instinktvarianten(**data.get("instinktvarianten", {}))
        )
