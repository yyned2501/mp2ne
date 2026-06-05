from __future__ import annotations

import json
from json import JSONDecodeError
from typing import Any, Dict, Optional

import httpx

from core.config import settings
from core.logger import logger


def _summarize_payload(payload: Any) -> Dict[str, Any]:
    if isinstance(payload, dict):
        return {
            "type": "dict",
            "keys": sorted(payload.keys()),
            "summary": {k: type(v).__name__ for k, v in payload.items()},
        }
    if isinstance(payload, list):
        return {
            "type": "list",
            "len": len(payload),
            "first_keys": sorted(payload[0].keys()) if payload and isinstance(payload[0], dict) else None,
        }
    return {"type": type(payload).__name__}


class NextEmbyClient:
    def __init__(self) -> None:
        self.base_url = settings.nextemby_host.rstrip("/")
        self.api_key = settings.nextemby_api_key
        self.timeout_seconds = settings.request_timeout_seconds
        self.post_timeout_seconds = settings.post_timeout_seconds

    def configured(self) -> bool:
        return bool(self.api_key)

    async def get(self, path: str, params: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        if not self.configured():
            logger.warning("NEXTEMBY_API_KEY 未配置，当前请求进入兼容模式，不转发到后端")
            return None

        if settings.debug_logging:
            logger.info(f"【NE请求】 GET {path} params={params}")

        async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
            response = await client.get(
                f"{self.base_url}{path}",
                params=params,
                headers={"X-API-Key": self.api_key},
            )
            if response.status_code != 200:
                raise httpx.HTTPStatusError(
                    "NextEmby backend returned error",
                    request=response.request,
                    response=response,
                )
            try:
                result = response.json()
                if settings.debug_logging:
                    logger.info(f"【NE返回】 GET {path} => {_summarize_payload(result)}")
                return result
            except JSONDecodeError:
                events = []
                for raw_line in response.text.splitlines():
                    line = raw_line.strip()
                    if not line:
                        continue
                    try:
                        events.append(json.loads(line))
                    except Exception:
                        logger.warning(f"NextEmby 返回了无法解析的行: {line[:120]}")
                if not events:
                    raise
                latest_with_data = next(
                    (
                        event
                        for event in reversed(events)
                        if isinstance(event, dict) and event.get("data")
                    ),
                    events[-1],
                )
                if isinstance(latest_with_data, dict):
                    latest_with_data = dict(latest_with_data)
                    latest_with_data["__events__"] = events
                if settings.debug_logging:
                    logger.info(f"【NE返回】 GET {path} => {_summarize_payload(latest_with_data)}")
                return latest_with_data

    async def post(self, path: str, payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        if not self.configured():
            logger.warning("NEXTEMBY_API_KEY 未配置，当前请求进入兼容模式，不转发到后端")
            return None

        if settings.debug_logging:
            logger.info(f"【NE请求】 POST {path} payload={payload}")

        async with httpx.AsyncClient(timeout=self.post_timeout_seconds) as client:
            response = await client.post(
                f"{self.base_url}{path}",
                json=payload,
                headers={"X-API-Key": self.api_key},
            )
            if response.status_code not in {200, 201}:
                error_detail: Dict[str, Any]
                try:
                    error_detail = response.json()
                except Exception:
                    error_detail = {"message": response.text}
                return {
                    "success": False,
                    "status_code": response.status_code,
                    "message": error_detail.get("message") or error_detail.get("detail") or "NextEmby backend returned error",
                    "data": error_detail.get("data") if isinstance(error_detail.get("data"), dict) else {},
                }
            try:
                result = response.json()
                if settings.debug_logging:
                    logger.info(f"【NE返回】 POST {path} => {_summarize_payload(result)}")
                return result
            except JSONDecodeError:
                result = {"success": True, "message": "success", "data": {}}
                if settings.debug_logging:
                    logger.info(f"【NE返回】 POST {path} => {_summarize_payload(result)}")
                return result



nextemby_client = NextEmbyClient()

__all__ = ["NextEmbyClient", "nextemby_client"]
