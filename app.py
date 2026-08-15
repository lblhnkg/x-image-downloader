# ============================================================
# app.py - 主入口（挂载路由 + 静态页）
# v5.0test + MissAV 集成（基于 missAV_api 官方库）
# ============================================================

import os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, RedirectResponse

from shared import database, init_db

# 导入各模块路由
from x_routes import router as x_router
from missav_routes import router as missav_router
from bilibili_routes import router as bilibili_router

# 创建主应用
app = FastAPI(title="万能媒体下载器")

# CORS（自用可放宽，部署后建议收窄到你的域名）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================
# 启动 / 关闭事件
# ============================================================
@app.on_event("startup")
async def startup():
    await database.connect()
    await init_db()
    print("[DB] 数据库连接成功")

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()
    print("[DB] 数据库已断开")

# ============================================================
# 注册路由
# ============================================================
app.include_router(x_router)        # X API（/api/*）
app.include_router(missav_router)   # MissAV API（/missav/*）
app.include_router(bilibili_router) # Bilibili API（/bilibili/*）

# ============================================================
# 兼容旧前端路径
# 旧版 missav.html 写死了 /api/video-stream 和 /api/video-download
# 这里做一层薄薄的转发，让它继续可用，无需改前端
# ============================================================

import re
from urllib.parse import urlparse

@app.get("/api/video-stream")
async def compat_video_stream(url: str = ""):
    """
    兼容旧前端：/api/video-stream?url=https://...m3u8...
    从 URL 中抠出番号，转发到 /missav/stream
    """
    from missav_routes import missav_stream
    m = re.search(r"/([A-Z]{2,6}-\d{3,5})", url, re.I)
    video_id = m.group(1) if m else url
    return await missav_stream(video_id=video_id, quality="best")

@app.get("/api/video-download")
async def compat_video_download(url: str = "", filename: str = ""):
    """
    兼容旧前端：/api/video-download?url=...&filename=...
    转发到 /missav/download
    """
    from missav_routes import missav_download
    m = re.search(r"/([A-Z]{2,6}-\d{3,5})", url, re.I)
    video_id = m.group(1) if m else url
    return await missav_download(video_id=video_id, quality="best")

# ============================================================
# 静态页面（每个站独立）
# ============================================================
@app.get("/")
async def root():
    """首页：登录 + 三个卡片入口"""
    return FileResponse("static/index.html")

@app.get("/x")
async def x_page():
    """X 下载器完整页面"""
    return FileResponse("static/x.html")

@app.get("/missav")
async def missav_page():
    """MissAV 下载器完整页面"""
    return FileResponse("static/missav.html")

@app.get("/bilibili")
async def bilibili_page():
    """Bilibili 下载器占位页面"""
    return FileResponse("static/bilibili.html")

@app.get("/health")
async def health():
    return {"status": "ok"}

# ============================================================
# 本地直接运行
# ============================================================
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", "8000")))
