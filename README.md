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
- `NEXTEMBY_HOST`: NextEmby 后端地址
- `NEXTEMBY_API_KEY`: NextEmby 后端 API Key
- `MP2NE_DEBUG_LOGGING`: 是否输出调试日志，默认 `1`
- `MP2NE_TIMEOUT_SECONDS`: GET 请求超时，默认 `15`
- `MP2NE_POST_TIMEOUT_SECONDS`: POST 请求超时，默认 `10`

## 本地运行
```bash
cp .env.example .env
# 编辑 .env，填写自己的 NextEmby 地址和 API Key
uv run --active uvicorn main:app --host 0.0.0.0 --port 8010
```

## 日志
- 控制台：标准输出
- 文件：`logs/mp2ne.log`

## 说明
- 订阅相关返回值会尽量按 MoviePilot 的实际返回形状对齐
- `/api/v1/subscribe/media/{mediaid}` 会根据 `NextEmby /api/discover` 里的数据构造 MoviePilot 风格详情；没有的数据会保持为空
- `DELETE /api/v1/subscribe/media/{mediaid}` 会转发到 `POST /api/subscriptions/remove`
- 当前项目不再依赖 `MOCK_MOVIEPILOT_TOKEN`
