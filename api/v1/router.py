from __future__ import annotations

from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Query
from pydantic import BaseModel, ConfigDict, Field

from core.client import nextemby_client
from core.logger import logger

router = APIRouter()


def _log_route_result(route: str, result: Any) -> None:
    if isinstance(result, MPResponse):
        payload = {
            "success": result.success,
            "message": result.message,
            "data_keys": sorted(result.data.keys()) if isinstance(result.data, dict) else type(result.data).__name__,
        }
    elif isinstance(result, dict):
        payload = {
            "keys": sorted(result.keys()),
            "summary": {k: type(v).__name__ for k, v in result.items()},
        }
    elif isinstance(result, list):
        payload = {
            "type": "list",
            "len": len(result),
            "first_keys": sorted(result[0].keys()) if result and isinstance(result[0], dict) else None,
        }
    else:
        payload = {"type": type(result).__name__}
    logger.info(f"【路由返回】 {route} => {payload}")


def _empty_subscribe_response() -> dict:
    return {
        "id": None,
        "name": None,
        "year": None,
        "type": None,
        "keyword": None,
        "tmdbid": None,
        "doubanid": None,
        "bangumiid": None,
        "mediaid": None,
        "season": None,
        "poster": None,
        "backdrop": None,
        "vote": None,
        "description": None,
        "filter": None,
        "include": None,
        "exclude": None,
        "quality": None,
        "resolution": None,
        "effect": None,
        "total_episode": None,
        "start_episode": None,
        "lack_episode": None,
        "completed_episode": None,
        "note": None,
        "state": None,
        "last_update": None,
        "username": None,
        "sites": None,
        "downloader": None,
        "best_version": None,
        "best_version_full": None,
        "current_priority": None,
        "episode_priority": None,
        "save_path": None,
        "search_imdbid": None,
        "date": None,
        "custom_words": None,
        "media_category": None,
        "filter_groups": None,
        "episode_group": None,
    }


def _build_subscribe_detail(item: dict) -> dict:
    result = _empty_subscribe_response()
    raw_type = item.get("media_type") or item.get("raw_type") or item.get("type")
    type_text = "电影" if str(raw_type).lower() in {"movie", "电影"} else "电视剧"
    total_episode = item.get("total_episode")
    if total_episode is None:
        total_episode = item.get("total_episodes")
    lack_episode = item.get("lack_episode")
    if lack_episode is None and total_episode is not None:
        try:
            total_val = int(total_episode)
            local_val = int(item.get("local_episodes", 0) or 0)
            lack_episode = max(total_val - local_val, 0)
        except (TypeError, ValueError):
            lack_episode = None
    completed_episode = item.get("completed_episode")
    if completed_episode is None and total_episode is not None and lack_episode is not None:
        try:
            completed_episode = max(int(total_episode) - int(lack_episode), 0)
        except (TypeError, ValueError):
            completed_episode = None
    result.update(
        {
            "id": item.get("id"),
            "name": item.get("title") or item.get("name"),
            "year": item.get("year"),
            "type": type_text,
            "tmdbid": item.get("tmdb_id") or item.get("tmdbid") or item.get("id"),
            "doubanid": item.get("doubanid"),
            "bangumiid": item.get("bangumiid"),
            "mediaid": item.get("mediaid"),
            "season": item.get("season"),
            "poster": item.get("poster_path") or item.get("poster"),
            "backdrop": item.get("backdrop_path") or item.get("backdrop"),
            "vote": item.get("vote_average") if item.get("vote_average") is not None else item.get("vote"),
            "description": item.get("overview") or item.get("description"),
            "filter": item.get("filter"),
            "include": item.get("include"),
            "exclude": item.get("exclude"),
            "quality": item.get("quality"),
            "resolution": item.get("resolution"),
            "effect": item.get("effect"),
            "total_episode": total_episode,
            "start_episode": item.get("start_episode", 0),
            "lack_episode": lack_episode,
            "completed_episode": completed_episode,
            "note": item.get("note"),
            "state": item.get("state", "R"),
            "last_update": item.get("last_update"),
            "username": item.get("username"),
            "sites": item.get("sites"),
            "downloader": item.get("downloader"),
            "best_version": item.get("best_version", 0),
            "best_version_full": item.get("best_version_full", 0),
            "current_priority": item.get("current_priority"),
            "episode_priority": item.get("episode_priority"),
            "save_path": item.get("save_path"),
            "search_imdbid": item.get("search_imdbid", 0),
            "date": item.get("date") or item.get("created_at") or item.get("updated_at"),
            "custom_words": item.get("custom_words"),
            "media_category": item.get("media_category"),
            "filter_groups": item.get("filter_groups"),
            "episode_group": item.get("episode_group"),
        }
    )
    return result


class MPResponse(BaseModel):
    success: bool = True
    message: str = "success"
    data: Any = Field(default_factory=dict)


class MoviePilotSubscribeInput(BaseModel):
    model_config = ConfigDict(extra="allow")

    id: Optional[int] = None
    name: Optional[str] = None
    year: Optional[str] = None
    type: Optional[str] = None
    keyword: Optional[str] = None
    tmdbid: Optional[int] = None
    doubanid: Optional[str] = None
    bangumiid: Optional[int] = None
    mediaid: Optional[str] = None
    season: Optional[int] = None
    poster: Optional[str] = None
    backdrop: Optional[str] = None
    vote: Optional[float] = 0.0
    description: Optional[str] = None
    filter: Optional[str] = None
    include: Optional[str] = None
    exclude: Optional[str] = None
    quality: Optional[str] = None
    resolution: Optional[str] = None
    effect: Optional[str] = None
    total_episode: Optional[int] = 0
    start_episode: Optional[int] = 0
    lack_episode: Optional[int] = 0
    note: Optional[Any] = None
    state: Optional[str] = None
    last_update: Optional[str] = None
    username: Optional[str] = None
    sites: Optional[List[int]] = Field(default_factory=list)
    downloader: Optional[str] = None
    best_version: Optional[int] = 0
    best_version_full: Optional[int] = 0
    current_priority: Optional[int] = None
    episode_priority: Optional[Dict[str, int]] = None
    save_path: Optional[str] = None
    search_imdbid: Optional[int] = 0
    date: Optional[str] = None
    custom_words: Optional[str] = None
    media_category: Optional[str] = None
    filter_groups: Optional[List[str]] = Field(default_factory=list)
    episode_group: Optional[str] = None


def _normalize_media_type(value: Optional[str]) -> str:
    if value in {"movie", "电影"}:
        return "movie"
    return "tv"



@router.get("/api/v1/media/search", response_model=List[dict])
async def moviepilot_media_search(
    title: str,
    type: Optional[str] = "media",
    page: int = 1,
    count: int = 8,
) -> Any:
    backend_json = await nextemby_client.get(
        "/api/openapi/search",
        {"query": title, "type": type, "page": page, "count": count},
    )
    if not backend_json:
        return []

    raw_results = backend_json.get("data", []) or backend_json.get("results", [])
    result: List[dict] = []
    for element in raw_results:
        result.append(
            {
                "title": element.get("title") or element.get("name"),
                "en_title": element.get("en_title") or element.get("original_title"),
                "year": element.get("year") or element.get("release_date", "")[:4],
                "type": element.get("type") or element.get("media_type") or type,
                "season": element.get("season"),
                "tmdb_id": element.get("tmdb_id") or element.get("id"),
                "imdb_id": element.get("imdb_id"),
                "douban_id": element.get("douban_id"),
                "overview": element.get("overview"),
                "vote_average": element.get("vote_average", 0.0),
                "poster_path": element.get("poster_path") or element.get("poster", ""),
                "detail_link": element.get("detail_link"),
            }
        )
    final = result[:count]
    _log_route_result("GET /api/v1/media/search", final)
    return final


@router.get("/api/v1/subscribe/", response_model=List[dict])
async def moviepilot_list_subscribes() -> Any:
    backend_json = await nextemby_client.get(
        "/api/discover",
        {
            "type": "全部",
            "sort": "更新",
            "region": "全部",
            "year": "全部",
            "genre": "全部",
            "status": "订阅中",
            "channel": "全部",
            "page": 1,
            "page_size": 100,
        },
    )
    if not backend_json:
        return []

    records: List[dict] = []
    if isinstance(backend_json, dict):
        events = backend_json.get("__events__")
        if isinstance(events, list) and events:
            candidate_lists: List[List[dict]] = []
            for event in events:
                if not isinstance(event, dict):
                    continue
                data = event.get("data")
                if isinstance(data, list):
                    candidate_lists.append(data)
                    continue
                if isinstance(data, dict):
                    nested = data.get("data")
                    if isinstance(nested, list):
                        candidate_lists.append(nested)
            if candidate_lists:
                records.extend(candidate_lists[-1])
        if not records:
            data = backend_json.get("data", [])
            if isinstance(data, list):
                records.extend(data)
            elif isinstance(data, dict):
                nested = data.get("data")
                if isinstance(nested, list):
                    records.extend(nested)
    elif isinstance(backend_json, list):
        records.extend(backend_json)

    subscribes: List[dict] = []
    for item in records:
        if not isinstance(item, dict):
            continue
        raw_id = item.get("id", 0)
        try:
            subscribe_id = int(raw_id)
        except (TypeError, ValueError):
            subscribe_id = 0
        subscribes.append(
            {
                "id": subscribe_id,
                "name": item.get("title", ""),
                "year": item.get("year", ""),
                "type": str(item.get("media_type") or item.get("raw_type") or "tv"),
                "season": item.get("season"),
                "tmdbid": subscribe_id,
                "poster": item.get("poster_path") or item.get("poster", ""),
                "vote": item.get("vote_average", 0.0),
                "state": item.get("state", "R"),
            }
        )
    _log_route_result("GET /api/v1/subscribe/", subscribes)
    return subscribes


@router.get("/api/v1/subscribe/user", response_model=List[dict])
@router.get("/api/v1/subscribe/user/", response_model=List[dict])
@router.get("/api/v1/subscribe/user/{username}", response_model=List[dict])
async def moviepilot_list_user_subscribes(
    username: Optional[str] = None,
) -> Any:
    effective_username = username or ""
    subscribes = await moviepilot_list_subscribes()
    if not effective_username:
        _log_route_result("GET /api/v1/subscribe/user", subscribes)
        return subscribes

    has_user_fields = any(
        isinstance(item, dict) and (item.get("username") or item.get("user") or item.get("owner"))
        for item in subscribes
    )
    if not has_user_fields:
        annotated: List[dict] = []
        for item in subscribes:
            if not isinstance(item, dict):
                continue
            row = dict(item)
            row.setdefault("username", effective_username)
            annotated.append(row)
        _log_route_result("GET /api/v1/subscribe/user/{username}", annotated)
        return annotated

    filtered: List[dict] = []
    for item in subscribes:
        if not isinstance(item, dict):
            continue
        item_username = item.get("username") or item.get("user") or item.get("owner")
        if item_username == effective_username:
            filtered.append(item)
    _log_route_result("GET /api/v1/subscribe/user/{username}", filtered)
    return filtered


@router.post("/api/v1/subscribe/", response_model=MPResponse)
async def moviepilot_add_subscribe(
    subscribe_in: MoviePilotSubscribeInput,
) -> MPResponse:
    tmdbid = subscribe_in.tmdbid or 0
    media_type = _normalize_media_type(subscribe_in.type)
    mediaid = subscribe_in.mediaid or ""

    if not tmdbid and mediaid.startswith("tmdb:"):
        raw_tmdbid = mediaid[5:]
        if raw_tmdbid.isdigit():
            tmdbid = int(raw_tmdbid)

    if tmdbid <= 0 and not mediaid:
        return MPResponse(success=False, message="tmdbid 或 mediaid 无效", data={})

    if media_type in {"movie", "电影"}:
        media_type = "movie"
    else:
        media_type = "tv"

    payload = {
        "tmdb_id": tmdbid if tmdbid > 0 else None,
        "title": subscribe_in.name or subscribe_in.keyword or subscribe_in.mediaid or "",
        "media_type": media_type,
        "year": subscribe_in.year or "",
        "season": subscribe_in.season or 1,
    }
    backend_json = await nextemby_client.post("/api/openapi/subscriptions/add", payload)
    if not backend_json:
        return MPResponse(
            success=True,
            message="订阅请求已接收（兼容模式，未配置 NextEmby API Key）",
            data={"id": tmdbid},
        )

    if isinstance(backend_json, dict) and backend_json.get("success") is False:
        return MPResponse(
            success=False,
            message=backend_json.get("message") or "订阅失败",
            data=backend_json.get("data") if isinstance(backend_json.get("data"), dict) else {},
        )

    backend_data = backend_json.get("data") if isinstance(backend_json, dict) else None
    if isinstance(backend_data, dict):
        subscribe_id = backend_data.get("id") or backend_data.get("subscribe_id") or tmdbid
    else:
        subscribe_id = tmdbid

    message = backend_json.get("message") if isinstance(backend_json, dict) else None
    result = MPResponse(
        success=True,
        message=message or "订阅成功",
        data={"id": subscribe_id},
    )
    _log_route_result("POST /api/v1/subscribe/", result)
    return result


@router.get("/api/v1/subscribe/media/{mediaid}", response_model=dict)
async def moviepilot_query_subscribe(
    mediaid: str,
    season: Optional[int] = None,
    title: Optional[str] = None,
) -> dict:
    if mediaid.startswith("tmdb:"):
        tmdbid = mediaid[5:]
        if not tmdbid.isdigit():
            result = _empty_subscribe_response()
            _log_route_result("GET /api/v1/subscribe/media/{mediaid}", result)
            return result
        subscribes = await moviepilot_list_subscribes()
        matched = next(
            (
                item for item in subscribes
                if isinstance(item, dict)
                and item.get("tmdbid") == int(tmdbid)
            ),
            None,
        )
        result = _build_subscribe_detail(matched) if matched else _empty_subscribe_response()
        _log_route_result("GET /api/v1/subscribe/media/{mediaid}", result)
        return result

    if mediaid.startswith("douban:") or mediaid.startswith("bangumi:"):
        result = _empty_subscribe_response()
        _log_route_result("GET /api/v1/subscribe/media/{mediaid}", result)
        return result

    result = _empty_subscribe_response()
    _log_route_result("GET /api/v1/subscribe/media/{mediaid}", result)
    return result


@router.delete("/api/v1/subscribe/media/{mediaid}", response_model=MPResponse)
async def moviepilot_delete_subscribe_by_mediaid(
    mediaid: str,
    season: Optional[int] = None,
) -> MPResponse:
    if not mediaid.startswith("tmdb:"):
        result = MPResponse(success=False, message="仅支持 tmdb: 媒体删除", data={})
        _log_route_result("DELETE /api/v1/subscribe/media/{mediaid}", result)
        return result

    raw_tmdbid = mediaid[5:]
    if not raw_tmdbid.isdigit():
        result = MPResponse(success=False, message="tmdbid 无效", data={})
        _log_route_result("DELETE /api/v1/subscribe/media/{mediaid}", result)
        return result

    subscribes = await moviepilot_list_subscribes()
    matched = next(
        (
            item for item in subscribes
            if isinstance(item, dict)
            and item.get("tmdbid") == int(raw_tmdbid)
        ),
        None,
    )

    payload = {
        "tmdb_id": str(raw_tmdbid),
        "title": matched.get("name") if isinstance(matched, dict) else "",
        "media_type": _normalize_media_type(matched.get("type") if isinstance(matched, dict) else None),
        "poster_path": matched.get("poster") if isinstance(matched, dict) else "",
    }
    backend_json = await nextemby_client.post("/api/subscriptions/remove", payload)
    if isinstance(backend_json, dict) and backend_json.get("success") is False:
        result = MPResponse(
            success=False,
            message=backend_json.get("message") or "删除订阅失败",
            data=backend_json.get("data") if isinstance(backend_json.get("data"), dict) else {},
        )
        _log_route_result("DELETE /api/v1/subscribe/media/{mediaid}", result)
        return result

    message = backend_json.get("message") if isinstance(backend_json, dict) else None
    result = MPResponse(success=True, message=message or "删除订阅成功", data={})
    _log_route_result("DELETE /api/v1/subscribe/media/{mediaid}", result)
    return result


@router.get("/api/v1/openapi/subscribe")
async def openapi_list_subscribe() -> dict:
    data = await moviepilot_list_subscribes()
    result = {"code": 0, "msg": "success", "data": data}
    _log_route_result("GET /api/v1/openapi/subscribe", result)
    return result

