"""FastAPI entrypoint: wires together the recruiter chat UI, admin UI, and API routes."""

from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.api import admin, chat

FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"

app = FastAPI(title="Personal Recruiter AI Chatbot")

app.include_router(chat.router)
app.include_router(admin.router)

app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")


@app.get("/")
def recruiter_ui():
    return FileResponse(FRONTEND_DIR / "index.html")


@app.get("/admin")
def admin_ui():
    return FileResponse(FRONTEND_DIR / "admin.html")
