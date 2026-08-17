# ============================================================
# app.py - 主入口（只负责挂载路由和静态页）
# ============================================================

import os
import re
import httpx
from urllib.parse import quote
import requests
from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from shared import database, init_db, missav_db

# 导入各模块路由
from x_routes import router as x_router
from jable_routes import router as jable_router
from bilibili_routes import router as bilibili_router

# 创建主应用
app = FastAPI(title="万能媒体下载器")

# 挂载静态文件目录
app.mount("/static", StaticFiles(directory="static"), name="static")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================
# 预热函数
# ============================================================
def warm_up_proxy():
    """在应用启动时预热 sing-box 的 urltest，确保节点选择已完成"""
    proxy_url = "http://127.0.0.1:1081"
    try:
        print("[预热] 正在通过代理预热 urltest...")
        resp = requests.get(
            "https://www.google.com",
            proxies={"http": proxy_url, "https": proxy_url},
            timeout=10
        )
        if resp.status_code == 200:
            print("[预热] urltest 预热成功，节点已选择")
        else:
            print(f"[预热] 预热返回状态码 {resp.status_code}，但继续启动")
    except Exception as e:
        print(f"[预热] 预热失败（不影响启动）: {e}")

# ============================================================
# 启动/关闭事件
# ============================================================
@app.on_event("startup")
async def startup():
    await database.connect()
    await init_db()
    if missav_db is not None:
        await missav_db.connect()
        print("[MissAV DB] 连接成功")
    else:
        print("[MissAV DB] 未配置，跳过")
    print("[DB] 主数据库连接成功")

    # 预热 sing-box 的 urltest（非阻塞，但会等待最多 10 秒）
    warm_up_proxy()

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()
    if missav_db is not None:
        await missav_db.disconnect()
        print("[MissAV DB] 已断开")
    print("[DB] 主数据库已断开")

# ============================================================
# 注册路由
# ============================================================

app.include_router(x_router)          # X API（/api/*）
app.include_router(jable_router)      # Jable API（/api/jable/*）
app.include_router(bilibili_router)   # Bilibili API（/bilibili/*）

# ============================================================
# 代理路由（为 M3U8 工具提供 CORS 绕过 + 解密支持）
# ============================================================

# 创建两个客户端：一个走代理，一个不走代理
proxy_client = httpx.AsyncClient(proxy="http://127.0.0.1:1081", timeout=30.0)
direct_client = httpx.AsyncClient(timeout=30.0)

@app.get("/proxy/m3u8")
async def proxy_m3u8(url: str):
    try:
        resp = await proxy_client.get(url)
        content = resp.text
    except Exception as e:
        print(f"[代理] 获取 m3u8 失败 (代理): {e}, 尝试直连")
        resp = await direct_client.get(url)
        content = resp.text
    
    def repl_ts(m):
        ts_url = m.group(0)
        if not ts_url.startswith("http"):
            base = "/".join(url.split("/")[:-1]) + "/"
            ts_url = base + ts_url
        return f'/proxy/ts?url={quote(ts_url)}'
    content = re.sub(r'(https?://[^\s"\']+\.ts|[\w\-./]+\.ts)', repl_ts, content)
    
    def repl_key(m):
        key_url = m.group(1)
        if not key_url.startswith("http"):
            base = "/".join(url.split("/")[:-1]) + "/"
            key_url = base + key_url
        return f'URI="/proxy/key?url={quote(key_url)}"'
    content = re.sub(r'URI="([^"]+)"', repl_key, content)
    
    return Response(content=content, media_type="application/vnd.apple.mpegurl")

@app.get("/proxy/ts")
async def proxy_ts(url: str):
    """获取 ts 分片：优先走代理，失败则降级到直连"""
    try:
        resp = await proxy_client.get(url)
        return Response(content=resp.content, media_type="video/MP2T")
    except Exception as e:
        print(f"[代理] 代理请求 ts 失败: {e}, 降级到直连")
        resp = await direct_client.get(url)
        return Response(content=resp.content, media_type="video/MP2T")

@app.get("/proxy/key")
async def proxy_key(url: str):
    """获取密钥：优先走代理，失败则降级到直连"""
    try:
        resp = await proxy_client.get(url)
        return Response(content=resp.content, media_type="application/octet-stream")
    except Exception as e:
        print(f"[代理] 代理请求 key 失败: {e}, 降级到直连")
        resp = await direct_client.get(url)
        return Response(content=resp.content, media_type="application/octet-stream")

# ============================================================
# 静态页面
# ============================================================

@app.get("/")
async def root():
    return FileResponse("static/index.html")

@app.get("/x")
async def x_page():
    return FileResponse("static/x.html")

@app.get("/missav")
async def missav_page():
    return FileResponse("static/missav.html")

@app.get("/bilibili")
async def bilibili_page():
    return FileResponse("static/bilibili.html")

@app.get("/m3u8")
async def m3u8_page():
    return FileResponse("static/m3u8.html")

@app.get("/health")
async def health():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", "8000")))
