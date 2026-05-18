from __future__ import annotations

import os
from pathlib import Path

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates

from agent.storage import Storage
from agent.workflow import AgentWorkflow


router = APIRouter()
templates = Jinja2Templates(directory="templates")
ROOT = Path(__file__).resolve().parents[1]
ALLOWED_EXTRACTOR_MODES = ["text_fixture", "llm_text", "llm_vision"]
SCREENSHOT_BY_SNAPSHOT = {
    "10am": ROOT / "data" / "screenshots" / "wechat_10am.png",
    "12pm": ROOT / "data" / "screenshots" / "wechat_12pm.png",
    "2pm": ROOT / "data" / "screenshots" / "wechat_2pm.png",
}


def get_storage() -> Storage:
    return Storage()


@router.get("/", response_class=HTMLResponse)
def index(request: Request):
    storage = get_storage()
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={**storage.dashboard_data()},
    )


@router.get("/partials/dashboard", response_class=HTMLResponse)
def dashboard_partial(request: Request):
    storage = get_storage()
    return templates.TemplateResponse(
        request=request,
        name="partials/overview.html",
        context={**storage.dashboard_data()},
    )


@router.get("/api/summary")
def summary():
    return get_storage().qa_summary_counts()


@router.get("/api/config")
def config():
    return {
        "openai_key_configured": bool(os.getenv("OPENAI_API_KEY")),
        "default_extractor_mode": os.getenv("EXTRACTOR_MODE", "text_fixture"),
        "allowed_extractor_modes": ALLOWED_EXTRACTOR_MODES,
        "openai_model": os.getenv("OPENAI_MODEL", "gpt-5.5"),
    }


@router.post("/api/ingest/{snapshot_id}")
def ingest(snapshot_id: str, extractor_mode: str | None = None):
    if extractor_mode is not None and extractor_mode not in ALLOWED_EXTRACTOR_MODES:
        raise HTTPException(status_code=400, detail="Invalid extractor_mode.")
    summary = AgentWorkflow(get_storage()).ingest(snapshot_id, extractor_mode=extractor_mode)
    status_code = 200 if summary.status == "success" else 500
    return JSONResponse(summary.model_dump(), status_code=status_code)


@router.post("/api/reset")
def reset():
    get_storage().reset()
    return {"status": "reset"}


@router.get("/evidence/screenshot/{snapshot_id}")
def evidence_screenshot(snapshot_id: str):
    path = SCREENSHOT_BY_SNAPSHOT.get(snapshot_id)
    if not path or not path.exists():
        raise HTTPException(status_code=404, detail="Screenshot evidence is not available for this snapshot.")
    return FileResponse(path)
