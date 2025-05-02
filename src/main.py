# src/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.routers import flow_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # oder ["http://localhost:3000"] für gezielte Freigabe
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Binde die neue Flow-Logik ein
app.include_router(flow_router.router)
