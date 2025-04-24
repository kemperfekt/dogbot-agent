from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from agent_module import run_diagnose_agent

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class SymptomInput(BaseModel):
    symptom: str

@app.post("/agent")
async def diagnose(symptom_input: SymptomInput):
    result = run_diagnose_agent(symptom_input.symptom)
    return {"response": result}
