# mp2ne

MoviePilot API 转 NextEmby 适配代理。

## 功能
- 冒充 MoviePilot 的 OpenAPI 接口
- 将 MoviePilot 请求转发到 NextEmby/NextFind 后端
- 统一鉴权与日志输出

## 启动
```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```
