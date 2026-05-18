from __future__ import annotations

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from agent.env import load_local_env
from agent.logging_utils import configure_logging


load_local_env()

from app.routes import router


configure_logging()

app = FastAPI(title="WeChat Task Agent Demo")
app.mount("/static", StaticFiles(directory="static"), name="static")
app.include_router(router)
