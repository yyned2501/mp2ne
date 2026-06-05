# mp2ne

MoviePilot API 转 NextEmby 适配代理。

## 说明
- 对外暴露 MoviePilot 风格 OpenAPI
- 转发到 NextEmby/NextFind 后端
- 使用 Bearer Token 做客户端鉴权

## 环境变量
- `NEXTEMBY_HOST`: NextEmby 后端地址
- `NEXTEMBY_API_KEY`: NextEmby 后端 API Key
- `MOCK_MOVIEPILOT_TOKEN`: 允许客户端使用的 MoviePilot Token

## 启动
```bash
export NEXTEMBY_HOST="https://example.com"
export NEXTEMBY_API_KEY="your_key"
export MOCK_MOVIEPILOT_TOKEN="mp_token_for_client_use"
uvicorn main:app --host 0.0.0.0 --port 8000
```
