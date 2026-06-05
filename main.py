from __future__ import annotations

from fastapi import FastAPI, Request

from api.v1.router import router as v1_router
from core.config import settings
from core.logger import logger

app = FastAPI(title="MoviePilot-to-NextEmby Adapter Gateway")
app.include_router(v1_router)


@app.middleware("http")
async def log_incoming_requests(request: Request, call_next):
    method = request.method
    path = request.url.path
    query_params = dict(request.query_params)

    headers_to_log = {}
    auth_header = request.headers.get("authorization")
    if auth_header:
        headers_to_log["Authorization"] = auth_header

    api_key_header = request.headers.get("x-api-key")
    if api_key_header:
        headers_to_log["X-API-Key"] = api_key_header

    logger.info("=" * 60)
    logger.info(f"【收到请求】 核心方法: {method} | 路径: {path}")
    logger.info(f"【查询参数】 {query_params}")
    logger.info(f"【核心请求头】 {headers_to_log}")
    logger.info("=" * 60)

    response = await call_next(request)
    return response


@app.get("/")
async def root() -> dict:
    return {
        "name": "mp2ne",
        "status": "ok",
        "backend_configured": bool(settings.nextemby_api_key),
    }


@app.get("/health")
async def health() -> dict:
    return {
        "status": "ok",
        "backend_configured": bool(settings.nextemby_api_key),
    }
