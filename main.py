from __future__ import annotations

import logging
import os
from typing import Optional

import httpx
from fastapi import Depends, FastAPI, Header, HTTPException, Query, Request, status
from pydantic import BaseModel

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger("mp2ne")

app = FastAPI(title="MoviePilot-to-NextEmby Adapter Gateway")

NEXTEMBY_HOST = os.getenv("NEXTEMBY_HOST", "https://nf.js.248226785.xyz:8443")
NEXTEMBY_API_KEY = os.getenv("NEXTEMBY_API_KEY", "")
MOCK_MOVIEPILOT_TOKEN = os.getenv("MOCK_MOVIEPILOT_TOKEN", "mp_token_for_client_use")


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

    body_str = ""
    try:
        body_bytes = await request.body()
        if body_bytes:
            body_str = body_bytes.decode("utf-8", errors="ignore")
    except Exception:
        body_str = "<无法解析的二进制数据>"

    logger.info("=" * 60)
    logger.info(f"【收到请求】 核心方法: {method} | 路径: {path}")
    logger.info(f"【查询参数】 {query_params}")
    logger.info(f"【核心请求头】 {headers_to_log}")
    if body_str:
        logger.info(f"【请求体 Body】 {body_str}")
    logger.info("=" * 60)

    response = await call_next(request)
    return response


class MPSubscribeInput(BaseModel):
    tmdb_id: int
    title: str
    type: str


async def check_mp_auth(authorization: Optional[str] = Header(None)):
    expected_auth = f"Bearer {MOCK_MOVIEPILOT_TOKEN}"
    if not authorization or authorization != expected_auth:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid MoviePilot API Token",
        )
    return authorization


async def _forward_get(path: str, params: dict[str, object]) -> dict:
    if not NEXTEMBY_API_KEY:
        raise HTTPException(status_code=500, detail="NEXTEMBY_API_KEY is not configured")
    async with httpx.AsyncClient(timeout=15.0) as client:
        response = await client.get(
            f"{NEXTEMBY_HOST}{path}",
            params=params,
            headers={"X-API-Key": NEXTEMBY_API_KEY},
        )
        if response.status_code != 200:
            raise HTTPException(status_code=502, detail="NextEmby backend returned error")
        return response.json()


async def _forward_post(path: str, payload: dict) -> dict:
    if not NEXTEMBY_API_KEY:
        raise HTTPException(status_code=500, detail="NEXTEMBY_API_KEY is not configured")
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.post(
            f"{NEXTEMBY_HOST}{path}",
            json=payload,
            headers={"X-API-Key": NEXTEMBY_API_KEY},
        )
        if response.status_code not in {200, 201}:
            raise HTTPException(status_code=502, detail="NextEmby backend returned error")
        return response.json()


@app.get("/api/v1/openapi/search")
async def fake_mp_search(
    keyword: str = Query(..., description="MoviePilot search keyword"),
    authorization: str = Depends(check_mp_auth),
):
    _ = authorization
    nextemby_json = await _forward_get(
        "/api/openapi/search",
        {"query": keyword, "type": "全部", "page": 1},
    )

    raw_results = nextemby_json.get("data", []) or nextemby_json.get("results", [])
    mp_styled_list = []
    for element in raw_results:
        raw_type = element.get("media_type") or element.get("raw_type") or "movie"
        mp_styled_list.append(
            {
                "title": element.get("title") or element.get("name"),
                "tmdb_id": element.get("tmdb_id") or element.get("id"),
                "type": str(raw_type).upper(),
                "poster_path": element.get("poster_path") or element.get("poster", ""),
                "release_date": element.get("release_date") or element.get("year", ""),
                "vote_average": element.get("vote_average", 0.0),
            }
        )

    return {"code": 0, "msg": "success", "data": mp_styled_list}


@app.post("/api/v1/openapi/subscribe")
async def fake_mp_subscribe(
    payload: MPSubscribeInput,
    authorization: str = Depends(check_mp_auth),
):
    _ = authorization
    await _forward_post(
        "/api/openapi/subscriptions/add",
        {
            "tmdb_id": payload.tmdb_id,
            "title": payload.title,
            "media_type": str(payload.type).lower(),
        },
    )
    return {"code": 0, "msg": "订阅成功", "data": {}}


@app.get("/api/v1/openapi/subscribe")
async def fake_mp_get_subscriptions(
    page: Optional[int] = Query(1, description="页码"),
    page_size: Optional[int] = Query(20, description="每页条数"),
    authorization: str = Depends(check_mp_auth),
):
    _ = authorization
    nextemby_json = await _forward_get(
        "/api/discover",
        {
            "type": "全部",
            "sort": "更新",
            "region": "全部",
            "year": "全部",
            "genre": "全部",
            "status": "订阅中",
            "channel": "全部",
            "page": page,
            "page_size": page_size,
        },
    )

    raw_data_list = nextemby_json.get("data", [])
    mp_styled_subscriptions = []
    for item in raw_data_list:
        raw_id = item.get("id", "0")
        try:
            tmdb_id_int = int(raw_id)
        except (TypeError, ValueError):
            tmdb_id_int = 0
        raw_type = item.get("media_type") or item.get("raw_type") or "tv"
        mp_styled_subscriptions.append(
            {
                "id": tmdb_id_int,
                "tmdb_id": tmdb_id_int,
                "title": item.get("title", ""),
                "type": str(raw_type).upper(),
                "poster_path": item.get("poster_path") or item.get("poster", ""),
                "year": item.get("year", ""),
                "vote_average": item.get("vote_average", 0.0),
                "status": "N",
            }
        )

    return {"code": 0, "msg": "success", "data": mp_styled_subscriptions}
