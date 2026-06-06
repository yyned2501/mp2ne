# mp2ne

MoviePilot API 转 NextEmby 适配代理。

## 功能
- 对外提供 MoviePilot 风格接口
- 转发到 NextEmby / NextFind 后端
- 兼容订阅列表、订阅详情、添加订阅、删除订阅、搜索等常用链路
- 运行时会把客户端请求、NextEmby 请求、NextEmby 返回和本地路由返回都写入日志，便于调试对齐

## 当前支持的接口
- `GET /`
- `GET /health`
- `GET /api/v1/media/search`
- `GET /api/v1/subscribe/`
- `GET /api/v1/subscribe/user`
- `GET /api/v1/subscribe/user/`
- `GET /api/v1/subscribe/user/{username}`
- `POST /api/v1/subscribe/`
- `GET /api/v1/subscribe/media/{mediaid}`
- `DELETE /api/v1/subscribe/media/{mediaid}`
- `GET /api/v1/openapi/subscribe`

## 环境变量
- `NEXTEMBY_HOST`: NextEmby / NextFind 后端地址
- `NEXTEMBY_API_KEY`: OpenAPI 写接口使用的 API Key（用于添加订阅、删除订阅等 openapi 请求）
- `NEXTEMBY_SESSION_COOKIE`: 订阅列表查询使用的 Cookie，例如 `nextmedia_session=authenticated`
- `MP2NE_DEBUG_LOGGING`: 是否输出调试日志，默认 `1`
- `MP2NE_TIMEOUT_SECONDS`: GET 请求超时，默认 `15`
- `MP2NE_POST_TIMEOUT_SECONDS`: POST 请求超时，默认 `10`

## 本地运行
```bash
cp .env.example .env
# 编辑 .env，填写自己的后端地址、OpenAPI API Key，以及订阅列表查询所需的 session cookie
uv run --active uvicorn main:app --host 0.0.0.0 --port 8010
```

## 日志
- 控制台：标准输出
- 文件：`logs/mp2ne.log`

## 说明
- 订阅相关返回值会尽量按 MoviePilot 的实际返回形状对齐
- `/api/v1/subscribe/media/{mediaid}` 会根据 `NextEmby /api/discover` 里的数据构造 MoviePilot 风格详情；没有的数据会保持为空
- 订阅列表查询走 `/api/discover`，使用 `NEXTEMBY_SESSION_COOKIE`
- 添加订阅与删除订阅走 openapi，使用 `NEXTEMBY_API_KEY`
- `DELETE /api/v1/subscribe/media/{mediaid}` 会转发到 `POST /api/openapi/subscriptions/remove`
- 如果删除订阅返回 `无效的 OpenAPI 密钥`，优先检查 `.env` 中的 `NEXTEMBY_API_KEY` 是否缺失或写错
- 当前项目不再依赖 `MOCK_MOVIEPILOT_TOKEN`
