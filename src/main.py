# src/main.py

from fastapi import FastAPI
from src.routers import flow_router

app = FastAPI()

# Binde die neue Flow-Logik ein
app.include_router(flow_router.router)
